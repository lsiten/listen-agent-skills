#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
普遍性问题分析模块
分析工单问题是否可能是普遍性问题（某个国家/地区、某个环境一定会出现的）
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils import (
    get_ticket_dir,
    load_json_file,
    save_json_file
)
from mcp_handler import (
    generate_mcp_instructions,
    load_mcp_results,
    build_filter_expression
)
from signoz_schema import build_field_spec, SEVERITY_ERROR_VALUES


def extract_prevalence_features(ticket_info: Dict[str, Any], log_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    从工单信息和日志分析中提取用于普遍性分析的特征
    
    特征包括：
    - 国家/地区（geo.country_name, geo.city_name）
    - 环境（service.environment）
    - 服务版本（service.version）
    - 浏览器版本（browser.name, browser.version）
    - 错误类型
    - 接口路径（request.pathname）
    
    Args:
        ticket_info: 工单信息
        log_analysis: 日志分析结果
    
    Returns:
        提取的特征信息
    """
    features = {
        'geo': {},
        'environment': None,
        'service_version': None,
        'browser_info': {},
        'error_type': None,
        'api_path': None,
        'service_name': None
    }
    
    # 从工单信息中提取
    region_info = ticket_info.get('region_info', {})
    if region_info.get('country'):
        features['geo']['country'] = region_info['country']
        features['geo']['country_name'] = region_info.get('country_name') or region_info['country']
    if region_info.get('city'):
        features['geo']['city'] = region_info['city']
        features['geo']['city_name'] = region_info.get('city_name') or region_info['city']
    
    # 从日志分析中提取（如果工单信息中没有）
    if not features['geo'].get('country') and log_analysis:
        # 尝试从关键错误中提取地理位置信息
        key_errors = log_analysis.get('key_errors', [])
        for error in key_errors[:5]:
            # 这里可以尝试从错误信息中提取地理位置，但通常需要从MCP结果中提取
            pass
    
    # 提取环境信息
    app_info = ticket_info.get('app_info', {})
    if app_info.get('environment'):
        features['environment'] = app_info['environment']
    elif app_info.get('env'):
        features['environment'] = app_info['env']
    
    # 提取服务版本
    if app_info.get('app_version'):
        features['service_version'] = app_info['app_version']
    elif app_info.get('version'):
        features['service_version'] = app_info['version']
    
    # 提取浏览器信息
    browser_info = ticket_info.get('browser_info', {})
    if browser_info.get('browser.name'):
        features['browser_info']['name'] = browser_info['browser.name']
    if browser_info.get('browser.version'):
        features['browser_info']['version'] = browser_info['browser.version']
    
    # 提取错误类型
    if log_analysis and log_analysis.get('error_types'):
        # 获取最常见的错误类型
        error_types = log_analysis['error_types']
        if error_types:
            features['error_type'] = max(error_types.items(), key=lambda x: x[1])[0]
    
    # 提取接口路径
    api_info = ticket_info.get('api_info', {})
    if api_info.get('pathname'):
        features['api_path'] = api_info['pathname']
    elif api_info.get('api_path'):
        features['api_path'] = api_info['api_path']
    
    # 提取服务名称
    services = ticket_info.get('services', [])
    if services:
        features['service_name'] = services[0] if isinstance(services, list) else services
    
    return features


def build_prevalence_query(
    features: Dict[str, Any],
    time_range: Dict[str, Any],
    signoz_config: Dict[str, Any],
    expand_time_range: bool = True
) -> Optional[Dict[str, Any]]:
    """
    构建普遍性问题查询（不限定用户ID、设备ID）
    
    Args:
        features: 提取的特征信息
        time_range: 时间范围
        signoz_config: SigNoz配置
        expand_time_range: 是否扩展时间范围（用于获取更多样本）
    
    Returns:
        Query Builder v5格式的查询
    """
    start_ms = time_range.get('start')
    end_ms = time_range.get('end')
    
    if not start_ms or not end_ms:
        return None
    
    # 如果扩展时间范围，扩展到前后24小时（用于获取更多样本）
    if expand_time_range:
        from datetime import datetime
        center_ms = (start_ms + end_ms) // 2
        start_ms = center_ms - (24 * 60 * 60 * 1000)  # 24小时前
        end_ms = center_ms + (24 * 60 * 60 * 1000)  # 24小时后
        # 确保不超出当前时间
        now_ms = int(datetime.now().timestamp() * 1000)
        if end_ms > now_ms:
            end_ms = now_ms
            start_ms = end_ms - (48 * 60 * 60 * 1000)  # 确保至少48小时范围
    
    # 构建过滤条件列表（用于后续转换为expression）
    filter_items = []
    
    # 基础过滤：错误日志
    filter_items.append({
        'key': {'name': 'severity_text'},
        'value': SEVERITY_ERROR_VALUES,
        'op': 'in'
    })
    
    # 添加服务过滤（如果有）
    if features.get('service_name'):
        filter_items.append({
            'key': {'name': 'service.name'},
            'value': [features['service_name']] if isinstance(features['service_name'], str) else features['service_name'],
            'op': 'in'
        })
    
    # 添加环境过滤（如果有）
    if features.get('environment'):
        filter_items.append({
            'key': {'name': 'service.environment'},
            'value': [features['environment']],
            'op': 'in'
        })
    
    # 添加服务版本过滤（如果有）
    if features.get('service_version'):
        filter_items.append({
            'key': {'name': 'service.version'},
            'value': [features['service_version']],
            'op': 'in'
        })
    
    # 添加地理位置过滤（如果有）
    if features.get('geo', {}).get('country_name'):
        filter_items.append({
            'key': {'name': 'geo.country_name'},
            'value': [features['geo']['country_name']],
            'op': 'in'
        })
    
    if features.get('geo', {}).get('city_name'):
        filter_items.append({
            'key': {'name': 'geo.city_name'},
            'value': [features['geo']['city_name']],
            'op': 'in'
        })
    
    # 添加浏览器信息过滤（如果有）
    if features.get('browser_info', {}).get('name'):
        filter_items.append({
            'key': {'name': 'browser.name'},
            'value': [features['browser_info']['name']],
            'op': 'in'
        })
    
    if features.get('browser_info', {}).get('version'):
        filter_items.append({
            'key': {'name': 'browser.version'},
            'value': [features['browser_info']['version']],
            'op': 'in'
        })
    
    # 添加接口路径过滤（如果有）
    if features.get('api_path'):
        api_path = features['api_path']
        if not api_path.startswith('/'):
            api_path = '/' + api_path
        filter_items.append({
            'key': {'name': 'request.pathname'},
            'value': [api_path],
            'op': 'in'
        })
    
    # ⚠️ 重要：不添加用户ID和设备ID过滤，用于获取所有相关错误
    
    # 将过滤条件转换为SQL-like表达式
    filter_expression = build_filter_expression(filter_items)
    
    # 构建查询
    query = {
        'schemaVersion': 'v1',
        'start': start_ms,
        'end': end_ms,
        'requestType': 'raw',
        'compositeQuery': {
            'queries': [
                {
                    'type': 'builder_query',
                    'spec': {
                        'name': 'A',
                        'signal': 'logs',
                        'disabled': False,
                        'limit': 500,  # 增加限制以获取更多样本
                        'offset': 0,
                        'order': [
                            {
                                'key': {
                                    'name': 'timestamp'
                                },
                                'direction': 'desc'
                            }
                        ],
                        'selectFields': [
                            build_field_spec('service.name', 'logs'),
                            build_field_spec('service.environment', 'logs'),
                            build_field_spec('service.version', 'logs'),
                            build_field_spec('body', 'logs'),
                            build_field_spec('request.pathname', 'logs'),
                            build_field_spec('message', 'logs'),
                            build_field_spec('severity_text', 'logs'),
                            build_field_spec('timestamp', 'logs'),
                            build_field_spec('geo.country_name', 'logs'),
                            build_field_spec('geo.city_name', 'logs'),
                            build_field_spec('browser.name', 'logs'),
                            build_field_spec('browser.version', 'logs'),
                            build_field_spec('user.id', 'logs'),
                            build_field_spec('user.client_id', 'logs'),
                            build_field_spec('source.address', 'logs')
                        ],
                        'filter': {
                            'expression': filter_expression
                        } if filter_expression else None,
                        'having': {
                            'expression': ''
                        }
                    }
                }
            ]
        },
        'formatOptions': {
            'formatTableResultForUI': True,
            'fillGaps': False
        },
        'variables': {}
    }
    
    return query


def analyze_prevalence_results(
    prevalence_results: Dict[str, Any],
    ticket_info: Dict[str, Any],
    features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    分析普遍性查询结果，判断是否是普遍性问题
    
    Args:
        prevalence_results: 普遍性查询结果
        ticket_info: 工单信息
        features: 提取的特征信息
    
    Returns:
        普遍性分析结果
    """
    analysis = {
        'is_prevalent': False,
        'prevalence_level': 'unknown',  # 'unknown', 'low', 'medium', 'high', 'critical'
        'affected_count': 0,
        'affected_users': set(),
        'affected_devices': set(),
        'affected_countries': set(),
        'affected_cities': set(),
        'time_distribution': {},
        'key_indicators': [],
        'recommendation': ''
    }
    
    if not prevalence_results or 'queries_executed' not in prevalence_results:
        return analysis
    
    # 统计受影响的数量
    for query_result in prevalence_results.get('queries_executed', []):
        result_data = query_result.get('result', {})
        rows = result_data.get('rows', [])
        
        if rows and isinstance(rows, list):
            analysis['affected_count'] += len(rows)
            
            for row in rows:
                if not isinstance(row, dict):
                    continue
                
                # 提取用户ID
                user_id = (
                    row.get('user.id') or
                    row.get('attributes', {}).get('user', {}).get('id') or
                    row.get('attributes', {}).get('user.id')
                )
                if user_id:
                    analysis['affected_users'].add(str(user_id))
                
                # 提取设备ID
                client_id = (
                    row.get('user.client_id') or
                    row.get('attributes', {}).get('user', {}).get('client_id') or
                    row.get('attributes', {}).get('user.client_id')
                )
                if client_id:
                    analysis['affected_devices'].add(str(client_id))
                
                # 提取国家
                country = (
                    row.get('geo.country_name') or
                    row.get('attributes', {}).get('geo', {}).get('country_name') or
                    row.get('attributes', {}).get('geo.country_name')
                )
                if country:
                    analysis['affected_countries'].add(str(country))
                
                # 提取城市
                city = (
                    row.get('geo.city_name') or
                    row.get('attributes', {}).get('geo', {}).get('city_name') or
                    row.get('attributes', {}).get('geo.city_name')
                )
                if city:
                    analysis['affected_cities'].add(str(city))
                
                # 提取时间戳（用于时间分布分析）
                timestamp = row.get('timestamp')
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        hour_key = dt.strftime('%Y-%m-%d %H:00')
                        analysis['time_distribution'][hour_key] = analysis['time_distribution'].get(hour_key, 0) + 1
                    except Exception:
                        pass
    
    # 转换set为list以便JSON序列化
    analysis['affected_users'] = list(analysis['affected_users'])
    analysis['affected_devices'] = list(analysis['affected_devices'])
    analysis['affected_countries'] = list(analysis['affected_countries'])
    analysis['affected_cities'] = list(analysis['affected_cities'])
    
    # 判断普遍性级别
    unique_users = len(analysis['affected_users'])
    unique_devices = len(analysis['affected_devices'])
    unique_countries = len(analysis['affected_countries'])
    unique_cities = len(analysis['affected_cities'])
    
    # 判断是否是普遍性问题
    # 标准：
    # - 影响超过10个用户或设备
    # - 影响超过2个国家或5个城市
    # - 错误数量超过50个
    if analysis['affected_count'] >= 50 or unique_users >= 10 or unique_devices >= 10:
        analysis['is_prevalent'] = True
        if unique_countries >= 2 or unique_cities >= 5:
            analysis['prevalence_level'] = 'critical'
        elif unique_countries >= 1 or unique_cities >= 3:
            analysis['prevalence_level'] = 'high'
        else:
            analysis['prevalence_level'] = 'medium'
    elif analysis['affected_count'] >= 20 or unique_users >= 5 or unique_devices >= 5:
        analysis['is_prevalent'] = True
        analysis['prevalence_level'] = 'medium'
    elif analysis['affected_count'] >= 10 or unique_users >= 3 or unique_devices >= 3:
        analysis['is_prevalent'] = True
        analysis['prevalence_level'] = 'low'
    
    # 生成关键指标
    if analysis['is_prevalent']:
        analysis['key_indicators'].append(f"影响 {analysis['affected_count']} 个错误日志")
        if unique_users > 0:
            analysis['key_indicators'].append(f"影响 {unique_users} 个不同用户")
        if unique_devices > 0:
            analysis['key_indicators'].append(f"影响 {unique_devices} 个不同设备")
        if unique_countries > 0:
            analysis['key_indicators'].append(f"影响 {unique_countries} 个国家/地区: {', '.join(analysis['affected_countries'][:5])}")
        if unique_cities > 0:
            analysis['key_indicators'].append(f"影响 {unique_cities} 个城市: {', '.join(analysis['affected_cities'][:5])}")
    
    # 生成建议
    if analysis['is_prevalent']:
        if analysis['prevalence_level'] == 'critical':
            analysis['recommendation'] = "⚠️ **严重普遍性问题**：此问题影响多个国家/地区的大量用户，建议立即采取紧急措施，考虑回滚或发布热修复。"
        elif analysis['prevalence_level'] == 'high':
            analysis['recommendation'] = "⚠️ **高普遍性问题**：此问题影响多个用户和设备，建议优先处理，考虑发布修复版本。"
        elif analysis['prevalence_level'] == 'medium':
            analysis['recommendation'] = "⚠️ **中等普遍性问题**：此问题影响一定数量的用户，建议尽快处理。"
        else:
            analysis['recommendation'] = "⚠️ **轻微普遍性问题**：此问题影响少量用户，建议关注并处理。"
    else:
        analysis['recommendation'] = "✅ 此问题似乎是孤立事件，影响范围有限。"
    
    return analysis


def analyze_prevalence(
    ticket_info: Dict[str, Any],
    log_analysis: Dict[str, Any],
    ticket_context: Dict[str, Any],
    project_path: str,
    ticket_id: str
) -> Dict[str, Any]:
    """
    分析工单问题是否是普遍性问题
    
    Args:
        ticket_info: 工单信息
        log_analysis: 日志分析结果
        ticket_context: 工单上下文
        project_path: 项目根目录路径
        ticket_id: 工单ID
    
    Returns:
        普遍性分析结果
    """
    print("\n🔍 分析普遍性问题...")
    
    # 提取特征
    features = extract_prevalence_features(ticket_info, log_analysis)
    
    # 即使特征信息不足，也保存已提取的特征信息
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    features_file = ticket_dir / 'prevalence_features.json'
    
    features_data = {
        'ticket_id': ticket_id,
        'features': features,
        'extracted_at': datetime.now().isoformat(),
        'source': {
            'ticket_info': ticket_info,
            'log_analysis_summary': {
                'error_count': log_analysis.get('error_count', 0),
                'error_types': log_analysis.get('error_types', {}),
                'services': log_analysis.get('services', [])
            } if log_analysis else {}
        }
    }
    
    if not any([
        features.get('geo'),
        features.get('environment'),
        features.get('service_version'),
        features.get('browser_info'),
        features.get('api_path'),
        features.get('service_name')
    ]):
        print("  ⚠️  无法提取足够的特征信息进行普遍性分析")
        # 仍然保存特征信息
        if save_json_file(features_file, features_data):
            print(f"  ✅ 特征信息已保存（即使信息不足）: {features_file}")
        # 同时更新ticket_context.json
        ticket_context_file = ticket_dir / 'ticket_context.json'
        ticket_context_data = load_json_file(ticket_context_file)
        if ticket_context_data:
            if 'prevalence_features' not in ticket_context_data:
                ticket_context_data['prevalence_features'] = {}
            ticket_context_data['prevalence_features'] = features
            ticket_context_data['prevalence_features_extracted_at'] = datetime.now().isoformat()
            save_json_file(ticket_context_file, ticket_context_data)
        return {
            'is_prevalent': False,
            'prevalence_level': 'unknown',
            'reason': '特征信息不足',
            'features': features,
            'features_file': str(features_file)
        }
    
    print(f"  ✅ 提取到特征信息:")
    if features.get('geo'):
        print(f"     - 地理位置: {features['geo'].get('country_name', '')}, {features['geo'].get('city_name', '')}")
    if features.get('environment'):
        print(f"     - 环境: {features['environment']}")
    if features.get('service_version'):
        print(f"     - 服务版本: {features['service_version']}")
    if features.get('browser_info'):
        print(f"     - 浏览器: {features['browser_info'].get('name', '')} {features['browser_info'].get('version', '')}")
    if features.get('api_path'):
        print(f"     - 接口路径: {features['api_path']}")
    
    # 保存特征信息（特征信息足够的情况）
    print("  💾 保存特征信息...")
    if save_json_file(features_file, features_data):
        print(f"  ✅ 特征信息已保存: {features_file}")
    else:
        print("  ⚠️  特征信息保存失败")
    
    # 同时更新ticket_context.json，将特征信息也保存到那里
    ticket_context_file = ticket_dir / 'ticket_context.json'
    ticket_context_data = load_json_file(ticket_context_file)
    if ticket_context_data:
        if 'prevalence_features' not in ticket_context_data:
            ticket_context_data['prevalence_features'] = {}
        ticket_context_data['prevalence_features'] = features
        ticket_context_data['prevalence_features_extracted_at'] = datetime.now().isoformat()
        if save_json_file(ticket_context_file, ticket_context_data):
            print(f"  ✅ 特征信息已更新到工单上下文")
    
    # 构建普遍性查询
    time_range = ticket_context.get('time_range', {})
    signoz_config_file = Path(project_path) / '.production-issue-analyzer' / 'signoz_config.json'
    signoz_config = load_json_file(signoz_config_file)
    
    prevalence_query = build_prevalence_query(features, time_range, signoz_config, expand_time_range=True)
    
    if not prevalence_query:
        print("  ⚠️  无法构建普遍性查询")
        return {
            'is_prevalent': False,
            'prevalence_level': 'unknown',
            'reason': '无法构建查询'
        }
    
    # 生成MCP指令（用于AI执行）
    print("  📋 生成普遍性查询指令...")
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    prevalence_instructions_file = ticket_dir / 'prevalence_instructions.json'
    
    instructions = {
        'ticket_id': ticket_id,
        'query_type': 'prevalence_analysis',
        'time_range': {
            'start': prevalence_query['start'],
            'end': prevalence_query['end'],
            'start_display': datetime.fromtimestamp(prevalence_query['start'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'end_display': datetime.fromtimestamp(prevalence_query['end'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        },
        'features': features,
        'queries': [
            {
                'priority': 1,
                'tool': 'signoz_execute_builder_query',
                'params': {
                    'query': prevalence_query
                },
                'description': '普遍性问题查询（不限定用户ID和设备ID，用于分析影响范围）'
            }
        ],
        'notes': """请执行此查询以分析问题的普遍性。
此查询不限定用户ID和设备ID，用于获取所有符合特征条件的错误日志。
查询结果将用于判断问题是否是普遍性问题（影响多个用户、设备、国家/地区）。
查询结果保存到 prevalence_results.json 文件中。
"""
    }
    
    if save_json_file(prevalence_instructions_file, instructions):
        print(f"  ✅ 普遍性查询指令已生成: {prevalence_instructions_file}")
        print("  ⏳ 请AI执行此查询，将结果保存到 prevalence_results.json")
        return {
            'instructions_file': str(prevalence_instructions_file),
            'features': features,
            'features_file': str(features_file),
            'status': 'pending_ai_execution'
        }
    else:
        print("  ⚠️  普遍性查询指令生成失败")
        return {
            'is_prevalent': False,
            'prevalence_level': 'unknown',
            'reason': '指令生成失败',
            'features': features,
            'features_file': str(features_file) if 'features_file' in locals() else None
        }


def load_and_analyze_prevalence_results(
    project_path: str,
    ticket_id: str,
    ticket_info: Dict[str, Any],
    features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    加载并分析普遍性查询结果
    
    Args:
        project_path: 项目根目录路径
        ticket_id: 工单ID
        ticket_info: 工单信息
        features: 提取的特征信息
    
    Returns:
        普遍性分析结果
    """
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    prevalence_results_file = ticket_dir / 'prevalence_results.json'
    
    prevalence_results = load_json_file(prevalence_results_file)
    if not prevalence_results:
        return {
            'is_prevalent': False,
            'prevalence_level': 'unknown',
            'reason': '查询结果不存在'
        }
    
    # 分析结果
    analysis = analyze_prevalence_results(prevalence_results, ticket_info, features)
    
    return analysis
