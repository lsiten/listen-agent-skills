#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP指令和结果处理模块
生成MCP调用指令，加载和处理MCP查询结果
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from utils import (
    get_ticket_dir,
    load_json_file,
    save_json_file
)
from signoz_schema import (
    build_field_spec,
    DEFAULT_QUERY_FIELDS,
    SEVERITY_ERROR_VALUES,
    is_error_severity
)


def extract_features_from_results(mcp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    从MCP查询结果中提取特征信息
    
    提取的特征包括：
    - 设备信息（user.client_id）
    - 用户信息（user.id）
    - IP地址（source.address）
    - 地理位置（geo.city_name, geo.country_name等）
    - 浏览器版本（browser.name, browser.version）
    - 应用版本（service.version）
    
    Args:
        mcp_results: MCP查询结果
    
    Returns:
        提取的特征信息字典
    """
    features = {
        'device_info': {},
        'user_info': {},
        'ip_addresses': set(),
        'geo_info': {},
        'browser_info': {},
        'app_version': None,
        'service_names': set()
    }
    
    if not mcp_results or 'queries_executed' not in mcp_results:
        return features
    
    # 遍历所有查询结果
    for query_result in mcp_results.get('queries_executed', []):
        result_data = query_result.get('result', {})
        
        # 处理rows数据（Query Builder v5格式）
        rows = result_data.get('rows')
        if rows and isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                
                # 提取设备ID（user.client_id）
                client_id = (
                    row.get('user.client_id') or
                    row.get('attributes', {}).get('user', {}).get('client_id') or
                    row.get('attributes', {}).get('user.client_id')
                )
                if client_id and not features['device_info'].get('user.client_id'):
                    features['device_info']['user.client_id'] = str(client_id)
                    features['device_info']['client_id'] = str(client_id)
                    features['device_info']['device_id'] = str(client_id)
                
                # 提取用户ID（user.id）
                user_id = (
                    row.get('user.id') or
                    row.get('attributes', {}).get('user', {}).get('id') or
                    row.get('attributes', {}).get('user.id')
                )
                if user_id and not features['user_info'].get('user.id'):
                    try:
                        # 确保user.id是int64类型
                        user_id_value = int(user_id) if isinstance(user_id, str) else user_id
                        features['user_info']['user.id'] = user_id_value
                        features['user_info']['user_id'] = user_id_value
                    except (ValueError, TypeError):
                        features['user_info']['user.id'] = user_id
                        features['user_info']['user_id'] = user_id
                
                # 提取IP地址（source.address）
                ip_address = (
                    row.get('source.address') or
                    row.get('attributes', {}).get('source', {}).get('address') or
                    row.get('attributes', {}).get('source.address')
                )
                if ip_address:
                    features['ip_addresses'].add(str(ip_address))
                
                # 提取地理位置信息
                city_name = (
                    row.get('geo.city_name') or
                    row.get('attributes', {}).get('geo', {}).get('city_name') or
                    row.get('attributes', {}).get('geo.city_name')
                )
                if city_name and not features['geo_info'].get('city'):
                    features['geo_info']['city'] = str(city_name)
                    features['geo_info']['geo.city_name'] = str(city_name)
                
                country_name = (
                    row.get('geo.country_name') or
                    row.get('attributes', {}).get('geo', {}).get('country_name') or
                    row.get('attributes', {}).get('geo.country_name')
                )
                if country_name and not features['geo_info'].get('country'):
                    features['geo_info']['country'] = str(country_name)
                    features['geo_info']['geo.country_name'] = str(country_name)
                
                # 提取浏览器信息
                browser_name = (
                    row.get('browser.name') or
                    row.get('attributes', {}).get('browser', {}).get('name') or
                    row.get('attributes', {}).get('browser.name')
                )
                if browser_name and not features['browser_info'].get('browser.name'):
                    features['browser_info']['browser.name'] = str(browser_name)
                
                browser_version = (
                    row.get('browser.version') or
                    row.get('attributes', {}).get('browser', {}).get('version') or
                    row.get('attributes', {}).get('browser.version')
                )
                if browser_version and not features['browser_info'].get('browser.version'):
                    features['browser_info']['browser.version'] = str(browser_version)
                
                # 提取应用版本（service.version）
                app_version = (
                    row.get('service.version') or
                    row.get('resources', {}).get('service', {}).get('version') or
                    row.get('resources', {}).get('service.version') or
                    row.get('resource', {}).get('service', {}).get('version')
                )
                if app_version and not features['app_version']:
                    features['app_version'] = str(app_version)
                
                # 提取服务名称
                service_name = (
                    row.get('service.name') or
                    row.get('resources', {}).get('service', {}).get('name') or
                    row.get('resources', {}).get('service.name') or
                    row.get('resource', {}).get('service', {}).get('name')
                )
                if service_name:
                    features['service_names'].add(str(service_name))
        
        # 处理data数据（list_services格式）
        data = result_data.get('data')
        if data and isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    service_name = item.get('serviceName') or item.get('service_name') or item.get('name')
                    if service_name:
                        features['service_names'].add(str(service_name))
    
    # 转换set为list以便JSON序列化
    features['ip_addresses'] = list(features['ip_addresses'])
    features['service_names'] = list(features['service_names'])
    
    return features


def update_ticket_info_with_features(ticket_info: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用从查询结果中提取的特征信息更新工单信息
    
    ⚠️ 重要：如果没有用户ID，可以根据特征信息（如设备ID）更新工单信息
    
    Args:
        ticket_info: 原始工单信息
        features: 从查询结果中提取的特征信息
    
    Returns:
        更新后的工单信息
    """
    updated_info = ticket_info.copy()
    
    # 更新设备信息（如果没有用户ID，优先使用设备ID）
    if features.get('device_info'):
        device_info = features['device_info']
        if not updated_info.get('device_info'):
            updated_info['device_info'] = {}
        
        # 如果工单中没有设备ID，使用提取的设备ID
        if not updated_info['device_info'].get('user.client_id') and device_info.get('user.client_id'):
            updated_info['device_info'].update(device_info)
            print(f"✅ 从查询结果中提取到设备ID: {device_info.get('user.client_id')}", file=sys.stderr)
    
    # 更新用户信息
    if features.get('user_info'):
        user_info = features['user_info']
        if not updated_info.get('user_info'):
            updated_info['user_info'] = {}
        
        # 如果工单中没有用户ID，使用提取的用户ID
        if not updated_info['user_info'].get('user.id') and user_info.get('user.id'):
            updated_info['user_info'].update(user_info)
            print(f"✅ 从查询结果中提取到用户ID: {user_info.get('user.id')}", file=sys.stderr)
    
    # 更新IP地址信息
    if features.get('ip_addresses'):
        ip_addresses = features['ip_addresses']
        if not updated_info.get('ip_info'):
            updated_info['ip_info'] = {}
        updated_info['ip_info']['ip_addresses'] = ip_addresses
        if ip_addresses:
            print(f"✅ 从查询结果中提取到IP地址: {', '.join(ip_addresses[:3])}{'...' if len(ip_addresses) > 3 else ''}", file=sys.stderr)
    
    # 更新地理位置信息
    if features.get('geo_info'):
        geo_info = features['geo_info']
        if not updated_info.get('region_info'):
            updated_info['region_info'] = {}
        
        # 如果工单中没有地理位置信息，使用提取的地理位置信息
        if not updated_info['region_info'].get('city') and geo_info.get('city'):
            updated_info['region_info']['city'] = geo_info['city']
        if not updated_info['region_info'].get('country') and geo_info.get('country'):
            updated_info['region_info']['country'] = geo_info['country']
        
        if geo_info.get('city') or geo_info.get('country'):
            print(f"✅ 从查询结果中提取到地理位置: {geo_info.get('city', '')}, {geo_info.get('country', '')}", file=sys.stderr)
    
    # 更新浏览器信息
    if features.get('browser_info'):
        browser_info = features['browser_info']
        if not updated_info.get('browser_info'):
            updated_info['browser_info'] = {}
        updated_info['browser_info'].update(browser_info)
        if browser_info.get('browser.name') or browser_info.get('browser.version'):
            print(f"✅ 从查询结果中提取到浏览器信息: {browser_info.get('browser.name', '')} {browser_info.get('browser.version', '')}", file=sys.stderr)
    
    # 更新应用版本信息
    if features.get('app_version'):
        if not updated_info.get('app_info'):
            updated_info['app_info'] = {}
        updated_info['app_info']['app_version'] = features['app_version']
        print(f"✅ 从查询结果中提取到应用版本: {features['app_version']}", file=sys.stderr)
    
    # 更新服务名称列表
    if features.get('service_names'):
        service_names = features['service_names']
        if not updated_info.get('services'):
            updated_info['services'] = []
        # 合并服务名称，去重
        existing_services = set(updated_info['services'])
        new_services = [s for s in service_names if s not in existing_services]
        if new_services:
            updated_info['services'].extend(new_services)
            print(f"✅ 从查询结果中提取到服务名称: {', '.join(new_services[:3])}{'...' if len(new_services) > 3 else ''}", file=sys.stderr)
    
    return updated_info


def generate_mcp_instructions(
    ticket_context: Dict[str, Any],
    project_path: str,
    ticket_id: str,
    previous_results: Optional[Dict[str, Any]] = None
) -> Optional[Path]:
    """
    生成MCP调用指令
    
    ⚠️ 重要：支持迭代式查询
    - 如果提供了previous_results，会从中提取特征信息并更新查询条件
    - 如果没有用户ID，可以根据特征信息（如设备ID）进行查询
    
    Args:
        ticket_context: 工单上下文（包含ticket_info和time_range）
        project_path: 项目根目录路径
        ticket_id: 工单ID
        previous_results: 之前的查询结果（用于迭代查询）
    
    Returns:
        MCP指令文件路径，如果生成失败则返回None
    """
    ticket_info = ticket_context.get('ticket_info', {})
    time_range = ticket_context.get('time_range', {})
    
    # 如果提供了之前的查询结果，从中提取特征信息并更新工单信息
    if previous_results:
        features = extract_features_from_results(previous_results)
        ticket_info = update_ticket_info_with_features(ticket_info, features)
        print("🔄 基于之前的查询结果更新了工单信息，将生成更精确的查询", file=sys.stderr)
    
    # 加载项目配置
    project_context_file = Path(project_path) / '.production-issue-analyzer' / 'project_context.json'
    signoz_config_file = Path(project_path) / '.production-issue-analyzer' / 'signoz_config.json'
    
    project_context = load_json_file(project_context_file)
    signoz_config = load_json_file(signoz_config_file)
    
    # 获取工单目录
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    instructions_file = ticket_dir / 'mcp_instructions.json'
    
    # 验证时间范围
    if not time_range.get('start') or not time_range.get('end'):
        print("⚠️  时间范围不完整，无法生成查询指令", file=sys.stderr)
        return None
    
    # 构建MCP指令
    instructions = {
        'ticket_id': ticket_id,
        'time_range': {
            'start': time_range.get('start'),
            'end': time_range.get('end'),
            'start_display': time_range.get('start_display'),
            'end_display': time_range.get('end_display'),
            'source': time_range.get('source')
        },
        'services': ticket_info.get('services', []),
        'queries': [],
        'notes': ''
    }
    
    # 生成查询指令列表
    queries = []
    
    # 查询1：获取服务列表（必须，优先级最高）
    # 使用验证后的时间范围
    if time_range.get('start') and time_range.get('end'):
        queries.append({
            'priority': 1,
            'tool': 'list_services',
            'params': {
                'timeRange': calculate_time_range_string(
                    time_range.get('start'),
                    time_range.get('end')
                ),
                'start': time_range.get('start'),
                'end': time_range.get('end')
            },
            'description': '获取服务列表，确认服务名称（必须首先执行）'
        })
    
    # 查询2：查询错误日志
    if ticket_info.get('keywords') and any(kw in ['错误', 'error', '异常', 'exception'] for kw in ticket_info.get('keywords', [])):
        if time_range.get('start') and time_range.get('end'):
            # 使用Query Builder v5查询错误日志
            query_builder = build_error_logs_query(
                ticket_info,
                time_range,
                signoz_config
            )
            if query_builder:
                queries.append({
                    'priority': 2,
                    'tool': 'execute_builder_query',
                    'params': {
                        'query': query_builder
                    },
                    'description': '查询错误日志（使用Query Builder v5）'
                })
    
    # 查询3：按服务查询日志
    services = ticket_info.get('services', [])
    if not services:
        # 如果没有指定服务，优先从SigNoz配置中获取
        if signoz_config and signoz_config.get('service_names'):
            service_names = signoz_config.get('service_names', {})
            services = list(service_names.keys())
        # 如果还是没有，使用项目上下文中的服务列表
        if not services and project_context:
            services = project_context.get('services', [])
    
    if services and time_range.get('start') and time_range.get('end'):
        for service in services[:5]:  # 限制服务数量
            query_builder = build_service_logs_query(
                service,
                ticket_info,
                time_range,
                signoz_config
            )
            if query_builder:
                queries.append({
                    'priority': 3,
                    'tool': 'execute_builder_query',
                    'params': {
                        'query': query_builder
                    },
                    'description': f'查询服务 {service} 的日志'
                })
    
    instructions['queries'] = queries
    
    # 添加说明
    instructions['notes'] = """请按照优先级顺序执行查询：
1. 必须首先执行 list_services 获取服务列表，确认服务名称
2. 根据服务名称和查询条件，使用 execute_builder_query 执行具体查询
3. 在Query Builder中添加 service.name 过滤条件，提高查询成功率
4. ⚠️ 重要：查询时不要添加fieldContext字段，SigNoz会自动识别字段上下文
5. ⚠️ 重要：确保formatTableResultForUI设置为true，以便正确显示结果
6. ⚠️ 重要：如果查询结果为空，尝试：
   - 检查时间范围是否正确
   - 检查服务名称是否准确（使用list_services获取的实际服务名）
   - 检查字段名称是否正确（如user.id是int64类型，确保值类型匹配）
   - 尝试简化查询条件，逐步添加过滤条件
7. ⚠️ 迭代查询：如果查询结果不为空，可以从结果中提取特征信息（设备ID、用户ID、IP、地理位置、浏览器版本、应用版本等），然后基于这些特征信息进行更精确的查询
8. ⚠️ 如果没有用户ID，可以根据工单中的特征信息（如设备ID）查询到的数据更新设备ID信息
9. 查询结果保存到 mcp_results.json 文件中
"""
    
    # 保存指令文件
    if save_json_file(instructions_file, instructions):
        return instructions_file
    return None


def calculate_time_range_string(start_ms: int, end_ms: int) -> str:
    """
    计算时间范围字符串（用于timeRange参数）
    
    Args:
        start_ms: 开始时间（毫秒时间戳）
        end_ms: 结束时间（毫秒时间戳）
    
    Returns:
        时间范围字符串（如 "1h", "2h", "30m"）
    """
    duration_ms = end_ms - start_ms
    duration_seconds = duration_ms / 1000
    duration_minutes = duration_seconds / 60
    duration_hours = duration_minutes / 60
    
    if duration_hours >= 1:
        hours = int(duration_hours)
        if hours == 1:
            return "1h"
        else:
            return f"{hours}h"
    else:
        minutes = int(duration_minutes)
        if minutes == 1:
            return "1m"
        else:
            return f"{minutes}m"


def build_error_logs_query(
    ticket_info: Dict[str, Any],
    time_range: Dict[str, Any],
    signoz_config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """构建错误日志查询（Query Builder v5格式）"""
    start_ms = time_range.get('start')
    end_ms = time_range.get('end')
    
    if not start_ms or not end_ms:
        return None
    
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
                        'limit': 100,
                        'offset': 0,
                        'order': [
                            {
                                'key': {
                                    'name': 'timestamp',
                                    'fieldDataType': 'int64',
                                    'signal': 'logs'
                                },
                                'direction': 'desc'
                            }
                        ],
                        'selectFields': [
                            build_field_spec('service.name', 'logs'),
                            build_field_spec('body', 'logs'),  # 添加body字段，这是最常用的日志内容字段
                            build_field_spec('pathname', 'logs'),
                            build_field_spec('request.pathname', 'logs'),  # 添加request.pathname，用于API路径查询
                            build_field_spec('message', 'logs'),
                            build_field_spec('stack', 'logs'),
                            build_field_spec('severity_text', 'logs'),
                            build_field_spec('severity_number', 'logs'),
                            build_field_spec('timestamp', 'logs'),
                            build_field_spec('user.id', 'logs'),
                            build_field_spec('user.client_id', 'logs'),  # 添加设备ID字段
                            build_field_spec('source.address', 'logs'),  # 添加IP地址字段
                            build_field_spec('geo.city_name', 'logs'),  # 添加地理位置字段
                            build_field_spec('browser.name', 'logs'),  # 添加浏览器名称字段
                            build_field_spec('browser.version', 'logs'),  # 添加浏览器版本字段
                            build_field_spec('service.version', 'logs'),  # 添加应用版本字段
                            build_field_spec('trace_id', 'logs')
                        ],
                        'filters': {
                            'items': [
                                {
                                    'key': build_field_spec('severity_text', 'logs'),
                                    'value': SEVERITY_ERROR_VALUES,
                                    'op': 'in'
                                }
                            ],
                            'op': 'and'
                        },
                        # 注意：平台查询支持NOT_CONTAINS和NOT_IN操作符
                        # 如果需要排除某些内容，可以添加类似以下的条件：
                        # {
                        #     'key': build_field_spec('stack', 'logs'),
                        #     'value': ['AxiosError'],
                        #     'op': 'not_contains'  # 如果Query Builder支持
                        # }
                    }
                }
            ]
        },
        'formatOptions': {
            'formatTableResultForUI': True,  # 设置为true以便平台正确显示结果
            'fillGaps': False
        },
        'variables': {}
    }
    
    # 添加服务过滤（如果有）
    # ⚠️ 注意：平台支持前缀匹配（如 service.name IN cs....），但Query Builder需要精确匹配
    # 如果有多个服务或需要前缀匹配，可以添加多个条件
    # ⚠️ 重要：如果list_services返回空，可能是时间范围问题，尝试扩大时间范围或使用最近24小时
    services = ticket_info.get('services', [])
    if services:
        # 如果服务名看起来像前缀（以点结尾），需要特殊处理
        # 但Query Builder不支持前缀匹配，所以只使用精确匹配
        # 确保服务名是列表格式
        service_values = services if isinstance(services, list) else [services]
        service_filter = {
            'key': build_field_spec('service.name', 'logs'),
            'value': service_values,
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(service_filter)
    
    # 添加用户信息过滤（如果有）
    # ⚠️ 注意：user.id字段类型是int64，但值可能是字符串或数字
    # 需要确保类型匹配，如果user_id是字符串形式的数字，需要转换为int
    user_info = ticket_info.get('user_info', {})
    user_id = user_info.get('user.id') or user_info.get('user_id')
    if user_id:
        # 尝试转换为int（因为user.id字段类型是int64）
        try:
            user_id_value = int(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            # 如果转换失败，使用原始值
            user_id_value = user_id
        
        user_filter = {
            'key': build_field_spec('user.id', 'logs'),
            'value': [user_id_value],  # 使用转换后的值
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(user_filter)
    
    # ⚠️ 重要：如果没有用户ID，可以根据设备ID进行查询
    # 添加设备信息过滤（如果有）
    # 注意：实际字段名是user.client_id，不是client_id或device_id
    device_info = ticket_info.get('device_info', {})
    client_id = device_info.get('user.client_id') or device_info.get('client_id') or device_info.get('device_id')
    if client_id:
        device_filter = {
            'key': build_field_spec('user.client_id', 'logs'),
            'value': [str(client_id)],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(device_filter)
    
    # 添加接口信息过滤（如果有）
    # ⚠️ 重要：pathname应该包含baseurl的路径部分
    # 例如：如果baseurl是 https://cs8.intsig.net/sync，api_path是 /revert_dir_list
    # 那么pathname应该是 /sync/revert_dir_list（包含baseurl的路径部分/sync）
    api_info = ticket_info.get('api_info', {})
    # 优先使用pathname（应该已经包含baseurl的路径部分），如果没有则使用api_path
    api_path = api_info.get('pathname') or api_info.get('api_path')
    if api_path:
        # 确保pathname以/开头
        if not api_path.startswith('/'):
            api_path = '/' + api_path
        
        # 如果pathname还没有包含baseurl路径，尝试从signoz_config中获取并组合
        if not api_info.get('pathname') and api_info.get('api_path'):
            # 如果只有api_path，尝试从signoz_config中获取base_url并组合
            base_url = signoz_config.get('base_url')
            if base_url:
                from urllib.parse import urlparse
                try:
                    parsed = urlparse(base_url)
                    base_path = parsed.path
                    if base_path and base_path != '/':
                        api_path = base_path.rstrip('/') + api_path
                except Exception:
                    pass
        
        api_filter = {
            'key': build_field_spec('request.pathname', 'logs'),
            'value': [api_path],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(api_filter)
    
    # 添加地区信息过滤（如果有）
    # 注意：实际字段名是geo.city_name和geo.country_name，不是city和country
    region_info = ticket_info.get('region_info', {})
    if region_info.get('city'):
        city_filter = {
            'key': build_field_spec('geo.city_name', 'logs'),
            'value': [region_info['city']],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(city_filter)
    
    if region_info.get('country'):
        country_filter = {
            'key': build_field_spec('geo.country_name', 'logs'),
            'value': [region_info['country']],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(country_filter)
    
    return query


def build_service_logs_query(
    service: str,
    ticket_info: Dict[str, Any],
    time_range: Dict[str, Any],
    signoz_config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """构建服务日志查询（Query Builder v5格式）"""
    start_ms = time_range.get('start')
    end_ms = time_range.get('end')
    
    if not start_ms or not end_ms:
        return None
    
    # 获取公共查询字段
    common_fields = signoz_config.get('common_query_fields', DEFAULT_QUERY_FIELDS)
    
    # 构建selectFields（使用signoz_schema模块）
    # 优先包含平台查询结果中常用的字段
    priority_fields = [
        'service.name',
        'body',  # 添加body字段，这是最常用的日志内容字段
        'pathname',
        'request.pathname',  # 添加request.pathname，用于API路径查询
        'message',
        'stack',
        'severity_text',
        'user.id',
        'user.client_id',  # 添加设备ID字段
        'source.address',  # 添加IP地址字段
        'geo.city_name',  # 添加地理位置字段
        'browser.name',  # 添加浏览器名称字段
        'browser.version',  # 添加浏览器版本字段
        'service.version'  # 添加应用版本字段
    ]
    
    select_fields = []
    added_fields = set()
    
    # 先添加优先级字段
    for field in priority_fields:
        if field not in added_fields:
            field_spec = build_field_spec(field, 'logs')
            select_fields.append(field_spec)
            added_fields.add(field)
    
    # 再添加其他公共字段
    for field in common_fields:
        if field not in added_fields and len(select_fields) < 20:  # 增加字段数量限制
            field_spec = build_field_spec(field, 'logs')
            select_fields.append(field_spec)
            added_fields.add(field)
    
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
                        'limit': 100,
                        'offset': 0,
                        'order': [
                            {
                                'key': {
                                    'name': 'timestamp',
                                    'fieldDataType': 'int64',
                                    'signal': 'logs'
                                },
                                'direction': 'desc'
                            }
                        ],
                        'selectFields': select_fields,
                        # 确保包含常用字段（如果不在common_fields中）
                        # 这些字段在平台查询结果中经常显示
                        'filters': {
                            'items': [
                                {
                                    'key': build_field_spec('service.name', 'logs'),
                                    'value': [service] if isinstance(service, str) else service,
                                    'op': 'in'
                                }
                            ],
                            'op': 'and'
                        }
                    }
                }
            ]
        },
        'formatOptions': {
            'formatTableResultForUI': True,  # 设置为true以便平台正确显示结果
            'fillGaps': False
        },
        'variables': {}
    }
    
    # 添加用户信息过滤（如果有）
    # ⚠️ 注意：user.id字段类型是int64，但值可能是字符串或数字
    # 需要确保类型匹配，如果user_id是字符串形式的数字，需要转换为int
    user_info = ticket_info.get('user_info', {})
    user_id = user_info.get('user.id') or user_info.get('user_id')
    if user_id:
        # 尝试转换为int（因为user.id字段类型是int64）
        try:
            user_id_value = int(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            # 如果转换失败，使用原始值
            user_id_value = user_id
        
        user_filter = {
            'key': build_field_spec('user.id', 'logs'),
            'value': [user_id_value],  # 使用转换后的值
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(user_filter)
    
    # ⚠️ 重要：如果没有用户ID，可以根据设备ID进行查询
    # 添加设备信息过滤（如果有）
    # 注意：实际字段名是user.client_id，不是client_id或device_id
    device_info = ticket_info.get('device_info', {})
    client_id = device_info.get('user.client_id') or device_info.get('client_id') or device_info.get('device_id')
    if client_id:
        device_filter = {
            'key': build_field_spec('user.client_id', 'logs'),
            'value': [str(client_id)],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(device_filter)
    
    # 添加接口信息过滤（如果有）
    api_info = ticket_info.get('api_info', {})
    api_path = api_info.get('pathname') or api_info.get('api_path')
    if api_path:
        if not api_path.startswith('/'):
            api_path = '/' + api_path
        
        api_filter = {
            'key': build_field_spec('request.pathname', 'logs'),
            'value': [api_path],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(api_filter)
    
    # 添加地区信息过滤（如果有）
    region_info = ticket_info.get('region_info', {})
    if region_info.get('city'):
        city_filter = {
            'key': build_field_spec('geo.city_name', 'logs'),
            'value': [region_info['city']],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(city_filter)
    
    if region_info.get('country'):
        country_filter = {
            'key': build_field_spec('geo.country_name', 'logs'),
            'value': [region_info['country']],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(country_filter)
    
    return query


def load_mcp_results(project_path: str, ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    加载MCP查询结果
    
    Args:
        project_path: 项目根目录路径
        ticket_id: 工单ID
    
    Returns:
        MCP查询结果，如果不存在则返回None
    """
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    results_file = ticket_dir / 'mcp_results.json'
    
    results = load_json_file(results_file)
    if results is None:
        print(f"⚠️  MCP查询结果文件不存在: {results_file}", file=sys.stderr)
        print("   请先执行MCP查询，将结果保存到该文件", file=sys.stderr)
    
    return results


def validate_mcp_instructions(instructions: Dict[str, Any]) -> tuple:
    """
    验证MCP指令格式
    
    Args:
        instructions: MCP指令数据
    
    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(instructions, dict):
        return False, "指令必须是字典格式"
    
    if 'ticket_id' not in instructions:
        return False, "缺少ticket_id字段"
    
    if 'queries' not in instructions:
        return False, "缺少queries字段"
    
    if not isinstance(instructions['queries'], list):
        return False, "queries必须是列表格式"
    
    return True, None
