#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段2：综合分析模块
处理MCP结果，分析代码逻辑，检索历史经验，生成解决方案
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from utils import (
    get_ticket_dir,
    load_json_file,
    save_json_file,
    save_markdown_file,
    format_datetime
)
from experience_manager import search_history_experience, save_experience
from prevalence_analyzer import (
    analyze_prevalence,
    load_and_analyze_prevalence_results
)


def check_mcp_results_empty(mcp_results: Dict[str, Any]) -> Tuple[bool, list]:
    """
    检查MCP查询结果是否为空
    
    Args:
        mcp_results: MCP查询结果
    
    Returns:
        (是否为空, 警告信息列表)
    """
    if not mcp_results:
        return True, ["MCP查询结果不存在"]
    
    is_empty = True
    warnings = []
    
    # 检查queries_executed（Query Builder v5格式）
    queries_executed = mcp_results.get('queries_executed', [])
    if queries_executed:
        for query_result in queries_executed:
            result_data = query_result.get('result', {})
            rows = result_data.get('rows', [])
            data = result_data.get('data')
            
            # 检查是否有数据
            if rows and isinstance(rows, list) and len(rows) > 0:
                is_empty = False
            elif data and isinstance(data, list) and len(data) > 0:
                is_empty = False
            
            # 检查警告信息
            if 'warnings' in result_data:
                warnings.extend(result_data['warnings'])
            if 'note' in query_result:
                warnings.append(query_result['note'])
    
    # 检查queries（旧格式）
    queries = mcp_results.get('queries', [])
    if queries:
        for query_result in queries:
            data = query_result.get('data')
            if data:
                if isinstance(data, list) and len(data) > 0:
                    is_empty = False
                elif isinstance(data, dict) and data.get('result'):
                    result_list = data['result']
                    if isinstance(result_list, list) and len(result_list) > 0:
                        is_empty = False
    
    return is_empty, warnings


def generate_preliminary_analysis(
    ticket_info: Dict[str, Any],
    ticket_context: Dict[str, Any],
    mcp_results: Dict[str, Any],
    warnings: list
) -> str:
    """
    生成初步判断（当查询结果为空时）
    
    Args:
        ticket_info: 工单信息
        ticket_context: 工单上下文
        mcp_results: MCP查询结果
        warnings: 警告信息列表
    
    Returns:
        初步判断文本
    """
    analysis_parts = []
    
    analysis_parts.append("# ⚠️ 初步判断")
    analysis_parts.append("")
    analysis_parts.append("**查询结果为空，无法生成完整解决方案。**")
    analysis_parts.append("")
    
    # 分析可能的原因
    analysis_parts.append("## 可能的原因分析")
    analysis_parts.append("")
    
    time_range = ticket_context.get('time_range', {})
    time_info = ticket_info.get('time_info', {})
    
    # 检查时间范围
    if time_range.get('start') and time_range.get('end'):
        from datetime import datetime
        start_dt = datetime.fromtimestamp(time_range['start'] / 1000)
        end_dt = datetime.fromtimestamp(time_range['end'] / 1000)
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        
        if duration_hours < 1:
            analysis_parts.append("- ⚠️ **时间范围过窄**：查询时间范围小于1小时，可能遗漏了相关日志")
        elif duration_hours > 24:
            analysis_parts.append("- ⚠️ **时间范围过宽**：查询时间范围超过24小时，可能需要更精确的时间")
        else:
            analysis_parts.append(f"- ✅ 时间范围：{time_range.get('start_display', '')} - {time_range.get('end_display', '')}（{duration_hours:.1f}小时）")
    
    # 检查服务名称
    services = ticket_info.get('services', [])
    if not services:
        analysis_parts.append("- ⚠️ **缺少服务名称**：未指定服务名称，可能查询了所有服务但未找到匹配的日志")
    else:
        analysis_parts.append(f"- ✅ 服务名称：{', '.join(services)}")
    
    # 检查用户信息
    user_info = ticket_info.get('user_info', {})
    if not user_info.get('user.id') and not user_info.get('user_id'):
        analysis_parts.append("- ⚠️ **缺少用户ID**：未提供用户ID，可能无法精确定位用户相关日志")
    else:
        user_id = user_info.get('user.id') or user_info.get('user_id')
        analysis_parts.append(f"- ✅ 用户ID：{user_id}")
    
    # 检查设备信息
    device_info = ticket_info.get('device_info', {})
    if not device_info.get('user.client_id') and not device_info.get('client_id') and not device_info.get('device_id'):
        analysis_parts.append("- ⚠️ **缺少设备ID**：未提供设备ID，可能无法精确定位设备相关日志")
    else:
        device_id = device_info.get('user.client_id') or device_info.get('client_id') or device_info.get('device_id')
        analysis_parts.append(f"- ✅ 设备ID：{device_id}")
    
    # 检查接口信息
    api_info = ticket_info.get('api_info', {})
    if not api_info.get('pathname') and not api_info.get('api_path'):
        analysis_parts.append("- ⚠️ **缺少接口路径**：未提供接口路径，可能无法精确定位接口相关日志")
    else:
        api_path = api_info.get('pathname') or api_info.get('api_path')
        analysis_parts.append(f"- ✅ 接口路径：{api_path}")
    
    # 显示警告信息
    if warnings:
        analysis_parts.append("")
        analysis_parts.append("## 查询警告信息")
        analysis_parts.append("")
        for warning in warnings:
            analysis_parts.append(f"- ⚠️ {warning}")
    
    # 提供建议
    analysis_parts.append("")
    analysis_parts.append("## 💡 建议")
    analysis_parts.append("")
    analysis_parts.append("为了获得更准确的查询结果，建议提供以下信息：")
    analysis_parts.append("")
    
    suggestions = []
    if not services:
        suggestions.append("1. **服务名称**：明确指定发生问题的服务名称")
    if not user_info.get('user.id') and not user_info.get('user_id'):
        suggestions.append("2. **用户ID**：提供用户ID，可以精确定位用户相关日志")
    if not device_info.get('user.client_id') and not device_info.get('client_id') and not device_info.get('device_id'):
        suggestions.append("3. **设备ID**：提供设备ID或客户端ID，可以精确定位设备相关日志")
    if not api_info.get('pathname') and not api_info.get('api_path'):
        suggestions.append("4. **接口路径**：提供具体的接口路径，可以精确定位接口相关日志")
    if time_range.get('start') and time_range.get('end'):
        from datetime import datetime
        start_dt = datetime.fromtimestamp(time_range['start'] / 1000)
        end_dt = datetime.fromtimestamp(time_range['end'] / 1000)
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        if duration_hours < 1:
            suggestions.append("5. **时间范围**：扩大查询时间范围（建议至少2小时）")
        elif duration_hours > 24:
            suggestions.append("5. **时间范围**：缩小查询时间范围，提供更精确的问题发生时间")
    
    if not suggestions:
        suggestions.append("1. 检查时间范围是否正确")
        suggestions.append("2. 确认服务名称是否准确（使用list_services获取实际服务名）")
        suggestions.append("3. 尝试简化查询条件，逐步添加过滤条件")
        if warnings:
            suggestions.append("4. 检查查询警告信息，可能需要明确指定字段的fieldContext和fieldDataType")
    
    for suggestion in suggestions:
        analysis_parts.append(suggestion)
    
    analysis_parts.append("")
    analysis_parts.append("## 下一步操作")
    analysis_parts.append("")
    analysis_parts.append("请根据上述建议，提供更精确的信息后，重新运行分析。")
    analysis_parts.append("")
    analysis_parts.append("或者，如果您确认信息无误，可以：")
    analysis_parts.append("1. 检查SigNoz平台，确认该时间段内是否有相关日志")
    analysis_parts.append("2. 确认服务名称、时间范围等信息是否正确")
    analysis_parts.append("3. 如果确实没有日志，可能需要扩大时间范围或检查其他服务")
    
    return "\n".join(analysis_parts)


def process_log_data(mcp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理日志数据，深度分析，提取关键错误信息
    
    注意：不发送原始日志给大模型，只提取关键信息
    
    Args:
        mcp_results: MCP查询结果
    
    Returns:
        处理后的日志分析结果
    """
    log_analysis = {
        'error_count': 0,
        'error_types': {},
        'services': set(),
        'key_errors': [],
        'time_pattern': {},
        'summary': '',
        'has_data': False
    }
    
    # 处理查询结果
    if 'queries_executed' in mcp_results:
        for query_result in mcp_results.get('queries_executed', []):
            result_data = query_result.get('result', {})
            rows = result_data.get('rows', [])
            if rows and isinstance(rows, list) and len(rows) > 0:
                log_analysis['has_data'] = True
                for row in rows:
                    process_log_entry(row, log_analysis)
    
    if 'queries' in mcp_results:
        for query_result in mcp_results.get('queries', []):
            process_query_result(query_result, log_analysis)
            if query_result.get('data'):
                data = query_result['data']
                if isinstance(data, list) and len(data) > 0:
                    log_analysis['has_data'] = True
                elif isinstance(data, dict) and data.get('result'):
                    result_list = data['result']
                    if isinstance(result_list, list) and len(result_list) > 0:
                        log_analysis['has_data'] = True
    
    # 转换set为list
    log_analysis['services'] = list(log_analysis['services'])
    
    # 生成摘要
    log_analysis['summary'] = generate_log_summary(log_analysis)
    
    return log_analysis


def process_query_result(query_result: Dict[str, Any], log_analysis: Dict[str, Any]) -> None:
    """处理单个查询结果"""
    # 处理queries_executed格式（Query Builder v5）
    if 'result' in query_result:
        result_data = query_result.get('result', {})
        rows = result_data.get('rows', [])
        if rows and isinstance(rows, list):
            for row in rows:
                process_log_entry(row, log_analysis)
            return
    
    # 处理旧格式（queries）
    if 'data' not in query_result:
        return
    
    data = query_result['data']
    
    # 处理列表类型的结果
    if isinstance(data, list):
        for entry in data:
            process_log_entry(entry, log_analysis)
    elif isinstance(data, dict):
        # 处理字典类型的结果
        if 'result' in data:
            result_data = data['result']
            if isinstance(result_data, list):
                for entry in result_data:
                    process_log_entry(entry, log_analysis)


def process_log_entry(entry: Dict[str, Any], log_analysis: Dict[str, Any]) -> None:
    """处理单个日志条目"""
    # 提取服务名（优先从resources中提取，注意实际字段是resources.service.name）
    service_name = (
        extract_field_value(entry, 'resources.service.name') or
        extract_field_value(entry, 'resource.service.name') or
        extract_field_value(entry, 'service.name') or
        extract_field_value(entry, 'service_name')
    )
    if service_name:
        log_analysis['services'].add(service_name)
    
    # 提取错误信息（从attributes中提取）
    severity = (
        extract_field_value(entry, 'attributes.severity_text') or
        extract_field_value(entry, 'severity_text') or
        extract_field_value(entry, 'severity')
    )
    body = (
        extract_field_value(entry, 'attributes.body') or
        extract_field_value(entry, 'body') or
        extract_field_value(entry, 'message')
    )
    
    # 提取严重程度数字
    severity_number_str = (
        extract_field_value(entry, 'attributes.severity_number') or
        extract_field_value(entry, 'severity_number')
    )
    severity_number = int(severity_number_str) if severity_number_str and severity_number_str.isdigit() else None
    
    # 判断是否为错误（使用signoz_schema模块）
    try:
        from signoz_schema import is_error_severity
        is_error = is_error_severity(severity, severity_number)
    except ImportError:
        # 如果模块不存在，使用简单判断
        is_error = (
            (severity and ('error' in severity.lower() or '异常' in severity or '错误' in severity)) or
            (severity_number and severity_number >= 17)  # ERROR级别及以上
        )
    
    if is_error:
        log_analysis['error_count'] += 1
        
        # 统计错误类型
        error_type = extract_error_type(body or severity)
        if error_type:
            log_analysis['error_types'][error_type] = log_analysis['error_types'].get(error_type, 0) + 1
        
        # 提取关键错误
        if body:
            key_error = {
                'service': service_name,
                'error': body[:200],  # 限制长度
                'severity': severity
            }
            log_analysis['key_errors'].append(key_error)


def extract_field_value(entry: Dict[str, Any], field_name: str) -> Optional[str]:
    """
    提取字段值（支持多种数据结构）
    
    根据SigNoz数据结构，字段可能位于：
    - resources.service.name（注意是复数resources）
    - attributes.body
    - attributes.user.id（嵌套字段）
    - attributes.user.client_id（嵌套字段）
    等位置
    """
    # 直接字段
    if field_name in entry:
        value = entry[field_name]
        if isinstance(value, (str, int, float)):
            return str(value)
    
    # 根据字段路径提取
    if '.' in field_name:
        parts = field_name.split('.')
        
        # 如果是 resources.xxx 或 attributes.xxx 格式（注意resources是复数）
        if parts[0] in ['resource', 'resources', 'attributes', 'span', 'log']:
            context = parts[0]
            field_key = '.'.join(parts[1:])
            
            # 处理resources（复数）和resource（单数）的兼容
            context_key = 'resources' if context == 'resource' else context
            if context_key in entry and isinstance(entry[context_key], dict):
                current = entry[context_key]
                # 处理嵌套字段（如 service.name, user.id）
                if '.' in field_key:
                    for part in field_key.split('.'):
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return None
                    if isinstance(current, (str, int, float)):
                        return str(current)
                else:
                    if field_key in current:
                        value = current[field_key]
                        if isinstance(value, (str, int, float)):
                            return str(value)
        else:
            # 普通嵌套字段（如 user.id, user.client_id）
            # 优先从attributes中查找
            if 'attributes' in entry and isinstance(entry['attributes'], dict):
                current = entry['attributes']
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        break
                else:
                    if isinstance(current, (str, int, float)):
                        return str(current)
            
            # 如果attributes中没有，尝试从根对象查找
            current = entry
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            if isinstance(current, (str, int, float)):
                return str(current)
    
    # 尝试从resources中提取（注意是复数）
    if 'resources' in entry and isinstance(entry['resources'], dict):
        if field_name in entry['resources']:
            value = entry['resources'][field_name]
            if isinstance(value, (str, int, float)):
                return str(value)
        # 尝试嵌套字段（如 service.name）
        if '.' in field_name:
            parts = field_name.split('.')
            if parts[0] in entry['resources']:
                current = entry['resources'][parts[0]]
                for part in parts[1:]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        break
                else:
                    if isinstance(current, (str, int, float)):
                        return str(current)
    
    # 兼容resource（单数）格式
    if 'resource' in entry and isinstance(entry['resource'], dict):
        if field_name in entry['resource']:
            value = entry['resource'][field_name]
            if isinstance(value, (str, int, float)):
                return str(value)
        # 尝试嵌套字段（如 service.name）
        if '.' in field_name:
            parts = field_name.split('.')
            if parts[0] in entry['resource']:
                current = entry['resource'][parts[0]]
                for part in parts[1:]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        break
                else:
                    if isinstance(current, (str, int, float)):
                        return str(current)
    
    # 尝试从attributes中提取
    if 'attributes' in entry and isinstance(entry['attributes'], dict):
        if field_name in entry['attributes']:
            value = entry['attributes'][field_name]
            if isinstance(value, (str, int, float)):
                return str(value)
        # 尝试嵌套字段（如 user.id, user.client_id）
        if '.' in field_name:
            parts = field_name.split('.')
            if parts[0] in entry['attributes']:
                current = entry['attributes'][parts[0]]
                for part in parts[1:]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        break
                else:
                    if isinstance(current, (str, int, float)):
                        return str(current)
    
    return None


def extract_error_type(error_text: str) -> Optional[str]:
    """提取错误类型"""
    if not error_text:
        return None
    
    error_text_lower = error_text.lower()
    
    # 常见错误类型
    error_patterns = {
        'timeout': ['timeout', '超时'],
        'connection': ['connection', '连接', 'connect'],
        'permission': ['permission', '权限', 'forbidden'],
        'not found': ['not found', '404', '未找到'],
        'server error': ['500', 'server error', '服务器错误'],
        'validation': ['validation', '验证', 'invalid'],
        'database': ['database', '数据库', 'sql']
    }
    
    for error_type, patterns in error_patterns.items():
        for pattern in patterns:
            if pattern in error_text_lower:
                return error_type
    
    return 'unknown'


def generate_log_summary(log_analysis: Dict[str, Any]) -> str:
    """生成日志分析摘要"""
    summary_parts = []
    
    if log_analysis['error_count'] > 0:
        summary_parts.append(f"发现 {log_analysis['error_count']} 个错误")
    
    if log_analysis['error_types']:
        error_types_str = ', '.join([f"{k}({v})" for k, v in log_analysis['error_types'].items()])
        summary_parts.append(f"错误类型: {error_types_str}")
    
    if log_analysis['services']:
        services_str = ', '.join(log_analysis['services'])
        summary_parts.append(f"涉及服务: {services_str}")
    
    if log_analysis['key_errors']:
        summary_parts.append(f"关键错误: {len(log_analysis['key_errors'])} 条")
    
    return "; ".join(summary_parts) if summary_parts else "未发现明显错误"


def analyze_code_logic(
    log_analysis: Dict[str, Any],
    project_path: str,
    ticket_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    分析代码逻辑，基于错误信息定位代码文件
    
    Args:
        log_analysis: 日志分析结果
        project_path: 项目根目录路径
        ticket_info: 工单信息
    
    Returns:
        代码分析结果
    """
    code_analysis = {
        'related_files': [],
        'error_locations': [],
        'suggestions': []
    }
    
    project_root = Path(project_path).resolve()
    
    # 根据错误信息定位代码文件
    key_errors = log_analysis.get('key_errors', [])
    for error in key_errors[:10]:  # 限制数量
        error_text = error.get('error', '')
        service = error.get('service', '')
        
        # 查找相关代码文件
        related_files = find_related_code_files(project_root, error_text, service)
        code_analysis['related_files'].extend(related_files)
        
        # 记录错误位置
        if related_files:
            code_analysis['error_locations'].append({
                'error': error_text[:100],
                'files': related_files
            })
    
    # 去重
    code_analysis['related_files'] = list(set(code_analysis['related_files']))
    
    return code_analysis


def find_related_code_files(project_root: Path, error_text: str, service: str) -> list:
    """查找相关代码文件"""
    related_files = []
    
    # 提取错误关键词
    keywords = extract_code_keywords(error_text)
    
    # 根据服务名查找文件
    if service:
        service_patterns = [
            f'**/{service}/**/*.py',
            f'**/{service}/**/*.js',
            f'**/{service}/**/*.ts',
            f'**/*{service}*.py',
            f'**/*{service}*.js',
            f'**/*{service}*.ts'
        ]
        
        for pattern in service_patterns:
            for file_path in project_root.rglob(pattern):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(project_root))
                    if rel_path not in related_files:
                        related_files.append(rel_path)
                    if len(related_files) >= 10:  # 限制数量
                        return related_files
    
    # 根据关键词查找文件
    for keyword in keywords[:3]:  # 限制关键词数量
        if len(keyword) < 3:  # 跳过太短的关键词
            continue
        
        patterns = [
            f'**/*{keyword}*.py',
            f'**/*{keyword}*.js',
            f'**/*{keyword}*.ts'
        ]
        
        for pattern in patterns:
            for file_path in project_root.rglob(pattern):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(project_root))
                    if rel_path not in related_files:
                        related_files.append(rel_path)
                    if len(related_files) >= 10:
                        return related_files
    
    return related_files[:10]  # 限制总数


def extract_code_keywords(error_text: str) -> list:
    """提取代码关键词"""
    keywords = []
    
    # 提取函数名、类名等
    patterns = [
        r'(\w+Error)',
        r'(\w+Exception)',
        r'(\w+Failed)',
        r'function\s+(\w+)',
        r'class\s+(\w+)',
        r'def\s+(\w+)',
        r'class\s+(\w+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, error_text, re.IGNORECASE)
        keywords.extend(matches)
    
    return list(set(keywords))


def generate_solution(
    log_analysis: Dict[str, Any],
    code_analysis: Dict[str, Any],
    ticket_info: Dict[str, Any],
    history_experiences: list,
    prevalence_analysis: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成综合解决方案
    
    Args:
        log_analysis: 日志分析结果
        code_analysis: 代码分析结果
        ticket_info: 工单信息
        history_experiences: 历史经验列表
    
    Returns:
        解决方案文本
    """
    solution_parts = []
    
    solution_parts.append("# 问题分析")
    solution_parts.append("")
    solution_parts.append(f"## 日志分析摘要")
    solution_parts.append(f"{log_analysis.get('summary', '无')}")
    solution_parts.append("")
    
    if log_analysis.get('error_types'):
        solution_parts.append("## 错误类型统计")
        for error_type, count in log_analysis['error_types'].items():
            solution_parts.append(f"- {error_type}: {count} 次")
        solution_parts.append("")
    
    if code_analysis.get('related_files'):
        solution_parts.append("## 相关代码文件")
        for file_path in code_analysis['related_files'][:10]:
            solution_parts.append(f"- {file_path}")
        solution_parts.append("")
    
    if history_experiences:
        solution_parts.append("## 参考历史经验")
        for i, exp in enumerate(history_experiences[:3], 1):
            solution_parts.append(f"### 经验 {i} (相似度: {exp.get('similarity', 0):.2%})")
            solution_parts.append(f"**问题**: {exp.get('problem_description', '')[:200]}...")
            solution_parts.append(f"**解决方案**: {exp.get('solution', '')[:200]}...")
            solution_parts.append("")
    
    # 添加普遍性问题分析
    if prevalence_analysis:
        solution_parts.append("## ⚠️ 普遍性问题分析")
        solution_parts.append("")
        if prevalence_analysis.get('is_prevalent'):
            prevalence_level = prevalence_analysis.get('prevalence_level', 'unknown')
            level_labels = {
                'critical': '🔴 严重',
                'high': '🟠 高',
                'medium': '🟡 中等',
                'low': '🟢 轻微'
            }
            level_label = level_labels.get(prevalence_level, '未知')
            solution_parts.append(f"### {level_label} 普遍性问题")
            solution_parts.append("")
            solution_parts.append("**此问题可能是普遍性问题，影响范围较广：**")
            solution_parts.append("")
            key_indicators = prevalence_analysis.get('key_indicators', [])
            for indicator in key_indicators:
                solution_parts.append(f"- {indicator}")
            solution_parts.append("")
            if prevalence_analysis.get('affected_countries'):
                countries = prevalence_analysis.get('affected_countries', [])
                solution_parts.append(f"**受影响国家/地区**: {', '.join(countries[:10])}")
                solution_parts.append("")
            if prevalence_analysis.get('affected_cities'):
                cities = prevalence_analysis.get('affected_cities', [])
                solution_parts.append(f"**受影响城市**: {', '.join(cities[:10])}")
                solution_parts.append("")
            recommendation = prevalence_analysis.get('recommendation', '')
            if recommendation:
                solution_parts.append(recommendation)
                solution_parts.append("")
        else:
            solution_parts.append("### ✅ 孤立事件")
            solution_parts.append("")
            solution_parts.append("此问题似乎是孤立事件，影响范围有限。")
            solution_parts.append("")
    
    solution_parts.append("# 解决方案建议")
    solution_parts.append("")
    solution_parts.append("基于以上分析，建议采取以下措施：")
    solution_parts.append("")
    solution_parts.append("1. 检查相关代码文件，确认错误原因")
    solution_parts.append("2. 参考历史经验，采用已验证的解决方案")
    solution_parts.append("3. 如果问题持续，考虑扩大查询时间范围或检查其他服务")
    solution_parts.append("")
    
    return "\n".join(solution_parts)


def generate_solution_document(
    solution: str,
    ticket_context: Dict[str, Any],
    project_path: str,
    ticket_id: str,
    prevalence_analysis: Optional[Dict[str, Any]] = None
) -> Optional[Path]:
    """
    生成解决方案文档
    
    Args:
        solution: 解决方案文本
        ticket_context: 工单上下文
        project_path: 项目根目录路径
        ticket_id: 工单ID
    
    Returns:
        保存的文档路径，如果保存失败则返回None
    """
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    solution_file = ticket_dir / 'solution.md'
    
    # 构建完整文档
    ticket_info = ticket_context.get('ticket_info', {})
    time_range = ticket_context.get('time_range', {})
    
    # 构建文档头部，如果是普遍性问题则特别标注
    header = "# 工单分析解决方案"
    if prevalence_analysis and prevalence_analysis.get('is_prevalent'):
        prevalence_level = prevalence_analysis.get('prevalence_level', 'unknown')
        level_labels = {
            'critical': '🔴 严重普遍性问题',
            'high': '🟠 高普遍性问题',
            'medium': '🟡 中等普遍性问题',
            'low': '🟢 轻微普遍性问题'
        }
        level_label = level_labels.get(prevalence_level, '普遍性问题')
        header = f"# 工单分析解决方案 - ⚠️ {level_label}"
    
    document = f"""{header}

## 工单信息

- **工单ID**: {ticket_id}
- **问题描述**: {ticket_info.get('description', '')[:200]}...
- **查询时间范围**: {time_range.get('start_display', '')} - {time_range.get('end_display', '')}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 如果是普遍性问题，在文档开头添加警告框
    if prevalence_analysis and prevalence_analysis.get('is_prevalent'):
        document += f"""
---

## ⚠️ 普遍性问题警告

**此问题已被识别为普遍性问题，影响范围较广，建议优先处理！**

- **普遍性级别**: {prevalence_analysis.get('prevalence_level', 'unknown')}
- **影响错误数**: {prevalence_analysis.get('affected_count', 0)}
- **影响用户数**: {len(prevalence_analysis.get('affected_users', []))}
- **影响设备数**: {len(prevalence_analysis.get('affected_devices', []))}
"""
        if prevalence_analysis.get('affected_countries'):
            countries = prevalence_analysis.get('affected_countries', [])
            document += f"- **受影响国家/地区**: {', '.join(countries[:10])}\n"
        if prevalence_analysis.get('affected_cities'):
            cities = prevalence_analysis.get('affected_cities', [])
            document += f"- **受影响城市**: {', '.join(cities[:10])}\n"
        document += f"\n**建议**: {prevalence_analysis.get('recommendation', '')}\n"
    
    document += f"""
---

{solution}

---

## 后续步骤

1. 根据解决方案建议进行问题修复
2. 验证修复效果
3. 如果问题已解决，可以将此经验保存到经验库
"""
    
    if save_markdown_file(solution_file, document):
        return solution_file
    return None


def init_phase_2(
    project_path: str,
    ticket_id: str,
    ticket_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    阶段2主函数：综合分析
    
    Args:
        project_path: 项目根目录路径
        ticket_id: 工单ID
        ticket_context: 工单上下文
    
    Returns:
        分析结果
    """
    print("\n" + "="*60)
    print("📋 阶段2：综合分析")
    print("="*60)
    
    from mcp_handler import load_mcp_results
    
    # 加载MCP查询结果
    print("\n📂 加载MCP查询结果...")
    mcp_results = load_mcp_results(project_path, ticket_id)
    if not mcp_results:
        print("  ⚠️  MCP查询结果不存在，请先执行MCP查询")
        return {}
    
    print("  ✅ 已加载MCP查询结果")
    
    # 检查查询结果是否为空
    is_empty, warnings = check_mcp_results_empty(mcp_results)
    
    if is_empty:
        print("\n⚠️  查询结果为空，生成初步判断...")
        print("  ⚠️  未找到相关日志数据")
        if warnings:
            print("  ⚠️  查询警告：")
            for warning in warnings:
                print(f"     - {warning}")
        
        # 生成初步判断
        preliminary_analysis = generate_preliminary_analysis(
            ticket_info,
            ticket_context,
            mcp_results,
            warnings
        )
        
        # 生成初步判断文档
        print("\n📝 生成初步判断文档...")
        ticket_dir = get_ticket_dir(project_path, ticket_id)
        preliminary_file = ticket_dir / 'preliminary_analysis.md'
        
        document = f"""# 工单初步判断

## 工单信息

- **工单ID**: {ticket_id}
- **问题描述**: {ticket_info.get('description', '')[:200]}...
- **查询时间范围**: {ticket_context.get('time_range', {}).get('start_display', '')} - {ticket_context.get('time_range', {}).get('end_display', '')}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{preliminary_analysis}

---

## ⚠️ 重要提示

**由于查询结果为空，无法生成完整解决方案。**

请根据上述建议提供更精确的信息，然后：
1. 更新工单信息（添加用户ID、设备ID、接口路径等）
2. 调整查询时间范围（如果需要）
3. 重新运行分析

或者，如果您确认信息无误，可以：
- 检查SigNoz平台，确认该时间段内是否有相关日志
- 确认服务名称、时间范围等信息是否正确
- 如果确实没有日志，可能需要扩大时间范围或检查其他服务
"""
        
        if save_markdown_file(preliminary_file, document):
            print(f"  ✅ 初步判断文档已保存: {preliminary_file}")
        else:
            print("  ⚠️  初步判断文档保存失败")
        
        print("\n" + "="*60)
        print("⚠️  查询结果为空，已生成初步判断")
        print("="*60)
        print("\n请查看初步判断文档，提供更精确的信息后重新运行分析。")
        print(f"文档位置: {preliminary_file}")
        
        return {
            'log_analysis': {'has_data': False, 'summary': '查询结果为空'},
            'is_empty': True,
            'preliminary_analysis': preliminary_analysis,
            'preliminary_file': str(preliminary_file),
            'warnings': warnings
        }
    
    # 处理日志数据
    print("\n📊 处理日志数据...")
    log_analysis = process_log_data(mcp_results)
    print(f"  ✅ 日志分析完成: {log_analysis.get('summary', '')}")
    
    # 分析代码逻辑
    print("\n💻 分析代码逻辑...")
    ticket_info = ticket_context.get('ticket_info', {})
    code_analysis = analyze_code_logic(log_analysis, project_path, ticket_info)
    print(f"  ✅ 代码分析完成: 发现 {len(code_analysis.get('related_files', []))} 个相关文件")
    
    # 检索历史经验
    print("\n🧠 检索历史经验...")
    problem_description = ticket_info.get('description', '')
    history_experiences = search_history_experience(project_path, problem_description)
    print(f"  ✅ 检索到 {len(history_experiences)} 条相似经验")
    
    # 分析普遍性问题
    print("\n🔍 分析普遍性问题...")
    prevalence_result = analyze_prevalence(
        ticket_info,
        log_analysis,
        ticket_context,
        project_path,
        ticket_id
    )
    
    # 如果普遍性查询指令已生成，尝试加载结果
    prevalence_analysis = None
    if prevalence_result.get('status') == 'pending_ai_execution':
        # 检查是否有查询结果
        from pathlib import Path
        ticket_dir = get_ticket_dir(project_path, ticket_id)
        prevalence_results_file = ticket_dir / 'prevalence_results.json'
        if prevalence_results_file.exists():
            print("  📊 发现普遍性查询结果，进行分析...")
            prevalence_analysis = load_and_analyze_prevalence_results(
                project_path,
                ticket_id,
                ticket_info,
                prevalence_result.get('features', {})
            )
            if prevalence_analysis.get('is_prevalent'):
                print(f"  ⚠️  检测到普遍性问题！级别: {prevalence_analysis.get('prevalence_level', 'unknown')}")
                print(f"     影响: {prevalence_analysis.get('affected_count', 0)} 个错误, {len(prevalence_analysis.get('affected_users', []))} 个用户")
            else:
                print("  ✅ 未检测到普遍性问题，似乎是孤立事件")
        else:
            print("  ⏳ 等待AI执行普遍性查询（prevalence_instructions.json）")
    
    # 检查是否有数据
    if not log_analysis.get('has_data', True):
        print("\n⚠️  日志分析未发现数据，但查询结果不为空")
        print("  可能是查询条件过于严格，建议放宽查询条件")
    
    # 生成综合解决方案
    print("\n💡 生成综合解决方案...")
    solution = generate_solution(
        log_analysis,
        code_analysis,
        ticket_info,
        history_experiences,
        prevalence_analysis
    )
    
    # 生成解决方案文档
    print("\n📝 生成解决方案文档...")
    solution_file = generate_solution_document(
        solution,
        ticket_context,
        project_path,
        ticket_id,
        prevalence_analysis
    )
    if solution_file:
        print(f"  ✅ 解决方案文档已保存: {solution_file}")
    else:
        print("  ⚠️  解决方案文档保存失败")
    
    # 保存经验（可选，需要用户确认）
    print("\n💾 保存经验...")
    services = ticket_info.get('services', [])
    tags = ticket_info.get('keywords', [])
    experience_file = save_experience(
        project_path,
        problem_description,
        solution,
        success=True,  # 可以根据实际情况设置
        services=services,
        tags=tags
    )
    if experience_file:
        print(f"  ✅ 经验已保存: {experience_file}")
    else:
        print("  ⚠️  经验保存失败")
    
    print("\n" + "="*60)
    
    return {
        'log_analysis': log_analysis,
        'code_analysis': code_analysis,
        'history_experiences': history_experiences,
        'prevalence_analysis': prevalence_analysis,
        'solution': solution,
        'solution_file': str(solution_file) if solution_file else None,
        'experience_file': str(experience_file) if experience_file else None
    }
