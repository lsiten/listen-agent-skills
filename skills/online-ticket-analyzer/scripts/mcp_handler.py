#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP指令和结果处理模块
生成MCP调用指令，加载和处理MCP查询结果
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
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


def generate_mcp_instructions(
    ticket_context: Dict[str, Any],
    project_path: str,
    ticket_id: str
) -> Optional[Path]:
    """
    生成MCP调用指令
    
    Args:
        ticket_context: 工单上下文数据
        project_path: 项目根目录路径
        ticket_id: 工单ID
    
    Returns:
        保存的指令文件路径，如果生成失败则返回None
    """
    from datetime import datetime, timedelta
    
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    instructions_file = ticket_dir / 'mcp_instructions.json'
    
    ticket_info = ticket_context.get('ticket_info', {})
    time_range = ticket_context.get('time_range', {})
    project_context = ticket_context.get('project_context', {})
    signoz_config = ticket_context.get('signoz_config', {})
    
    # 验证和优化时间范围
    start_ms = time_range.get('start')
    end_ms = time_range.get('end')
    now_ms = int(datetime.now().timestamp() * 1000)
    
    # 检查1：如果结束时间在未来（超过当前时间1小时），使用最近24小时
    if end_ms and end_ms > now_ms + 3600000:  # 1小时 = 3600000毫秒
        print(f"\n⚠️  检测到查询时间在未来（结束时间: {time_range.get('end_display')}）")
        print(f"   当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   自动调整为查询最近24小时的数据")
        
        # 使用最近24小时
        end_ms = now_ms
        start_ms = now_ms - (24 * 60 * 60 * 1000)  # 24小时前
        
        # 更新time_range
        time_range = {
            'start': start_ms,
            'end': end_ms,
            'start_display': datetime.fromtimestamp(start_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'end_display': datetime.fromtimestamp(end_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            'source': '自动调整：未来时间改为最近24小时'
        }
        
        # 更新ticket_context中的time_range
        ticket_context['time_range'] = time_range
    
    # 检查2：如果时间范围太小（小于2小时），自动扩大
    if start_ms and end_ms:
        duration_ms = end_ms - start_ms
        duration_hours = duration_ms / (1000 * 60 * 60)
        
        # 如果时间范围小于2小时，扩大到前后2小时
        if duration_hours < 2:
            base_time_ms = start_ms + (duration_ms / 2)  # 基础时间（中间点）
            # 扩大到前后2小时
            expanded_start_ms = base_time_ms - (2 * 60 * 60 * 1000)  # 2小时前
            expanded_end_ms = base_time_ms + (2 * 60 * 60 * 1000)  # 2小时后
            
            # 确保不超出当前时间
            if expanded_end_ms > now_ms:
                expanded_end_ms = now_ms
                # 如果结束时间调整了，开始时间也要相应调整
                if expanded_start_ms < expanded_end_ms - (2 * 60 * 60 * 1000):
                    expanded_start_ms = expanded_end_ms - (2 * 60 * 60 * 1000)
            
            print(f"\n⚠️  检测到时间范围较小（{duration_hours:.1f}小时），自动扩大为前后2小时")
            print(f"   原时间范围: {time_range.get('start_display')} - {time_range.get('end_display')}")
            
            # 更新time_range
            time_range = {
                'start': int(expanded_start_ms),
                'end': int(expanded_end_ms),
                'start_display': datetime.fromtimestamp(expanded_start_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'end_display': datetime.fromtimestamp(expanded_end_ms / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'source': f'{time_range.get("source", "时间范围")}（已扩大为前后2小时）'
            }
            
            print(f"   新时间范围: {time_range.get('start_display')} - {time_range.get('end_display')}")
            
            # 更新ticket_context中的time_range
            ticket_context['time_range'] = time_range
    
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
4. 查询结果保存到 mcp_results.json 文件中
"""
    
    # 保存指令文件
    if save_json_file(instructions_file, instructions):
        return instructions_file
    return None


def calculate_time_range_string(start_ms: Optional[int], end_ms: Optional[int]) -> str:
    """计算时间范围字符串（如 '1h', '30m'）"""
    if not start_ms or not end_ms:
        return '1h'
    
    duration_ms = end_ms - start_ms
    duration_hours = duration_ms / (1000 * 60 * 60)
    
    if duration_hours < 1:
        duration_minutes = int(duration_ms / (1000 * 60))
        return f'{duration_minutes}m'
    else:
        return f'{int(duration_hours)}h'


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
                                    'name': 'timestamp'
                                },
                                'direction': 'desc'
                            }
                        ],
                        'selectFields': [
                            build_field_spec('service.name', 'logs'),
                            build_field_spec('pathname', 'logs'),
                            build_field_spec('message', 'logs'),
                            build_field_spec('stack', 'logs'),
                            build_field_spec('severity_text', 'logs'),
                            build_field_spec('severity_number', 'logs'),
                            build_field_spec('timestamp', 'logs'),
                            build_field_spec('user.id', 'logs'),
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
    # 注意：平台支持前缀匹配（如 service.name IN cs....），但Query Builder需要精确匹配
    # 如果有多个服务或需要前缀匹配，可以添加多个条件
    services = ticket_info.get('services', [])
    if services:
        # 如果服务名看起来像前缀（以点结尾），需要特殊处理
        # 但Query Builder不支持前缀匹配，所以只使用精确匹配
        service_filter = {
            'key': build_field_spec('service.name', 'logs'),
            'value': services,
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(service_filter)
    
    # 添加用户信息过滤（如果有）
    # 注意：实际字段名是user.id，不是user_id
    user_info = ticket_info.get('user_info', {})
    user_id = user_info.get('user.id') or user_info.get('user_id')
    if user_id:
        user_filter = {
            'key': build_field_spec('user.id', 'logs'),
            'value': [str(user_id)],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(user_filter)
    
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
        'pathname',
        'message',
        'stack',
        'severity_text',
        'user.id'
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
        if field not in added_fields and len(select_fields) < 15:  # 限制总字段数量
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
                                    'name': 'timestamp'
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
                                    'value': [service],
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
    # 注意：实际字段名是user.id，不是user_id
    user_info = ticket_info.get('user_info', {})
    user_id = user_info.get('user.id') or user_info.get('user_id')
    if user_id:
        user_filter = {
            'key': build_field_spec('user.id', 'logs'),
            'value': [str(user_id)],
            'op': 'in'
        }
        query['compositeQuery']['queries'][0]['spec']['filters']['items'].append(user_filter)
    
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
    if 'ticket_id' not in instructions:
        return False, "缺少 ticket_id 字段"
    
    if 'queries' not in instructions:
        return False, "缺少 queries 字段"
    
    if not isinstance(instructions['queries'], list):
        return False, "queries 必须是列表"
    
    if len(instructions['queries']) == 0:
        return False, "queries 列表为空"
    
    return True, ""


def format_mcp_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化MCP结果
    
    Args:
        results: 原始MCP结果
    
    Returns:
        格式化后的结果
    """
    # 这里可以添加结果格式化逻辑
    # 例如：提取关键信息、统计错误数量等
    return results
