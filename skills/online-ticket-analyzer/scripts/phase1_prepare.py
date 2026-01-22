#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段1：准备与指令生成模块
加载项目上下文和SigNoz配置，保存工单上下文
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from utils import (
    get_analyzer_dir,
    get_ticket_dir,
    load_json_file,
    save_json_file,
    format_datetime
)
from phase0_init import PROJECT_CONTEXT_FILE, SIGNOZ_CONFIG_FILE


def load_project_context(project_path: str) -> Optional[Dict[str, Any]]:
    """
    加载项目全局上下文
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        项目上下文数据，如果加载失败则返回None
    """
    analyzer_dir = get_analyzer_dir(project_path)
    context_file = analyzer_dir / PROJECT_CONTEXT_FILE
    
    context_data = load_json_file(context_file)
    if context_data is None:
        print(f"⚠️  项目上下文文件不存在: {context_file}", file=sys.stderr)
        print("   请先运行阶段0初始化项目上下文", file=sys.stderr)
    
    return context_data


def load_signoz_config(project_path: str) -> Optional[Dict[str, Any]]:
    """
    加载SigNoz配置信息
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        SigNoz配置数据，如果加载失败则返回None
    """
    analyzer_dir = get_analyzer_dir(project_path)
    config_file = analyzer_dir / SIGNOZ_CONFIG_FILE
    
    config_data = load_json_file(config_file)
    if config_data is None:
        print(f"⚠️  SigNoz配置文件不存在: {config_file}", file=sys.stderr)
        print("   请先运行阶段0初始化SigNoz配置", file=sys.stderr)
    
    return config_data


def save_ticket_context(
    ticket_context: Dict[str, Any],
    project_path: str,
    ticket_id: str
) -> Optional[Path]:
    """
    保存工单上下文
    
    Args:
        ticket_context: 工单上下文数据
        project_path: 项目根目录路径
        ticket_id: 工单ID
    
    Returns:
        保存的文件路径，如果保存失败则返回None
    """
    ticket_dir = get_ticket_dir(project_path, ticket_id)
    context_file = ticket_dir / 'ticket_context.json'
    
    # 添加时间戳
    ticket_context['created_at'] = datetime.now().isoformat()
    ticket_context['ticket_id'] = ticket_id
    
    if save_json_file(context_file, ticket_context):
        return context_file
    return None


def init_phase_1(
    project_path: str,
    ticket_info: Dict[str, Any],
    time_range: tuple,
    ticket_id: str
) -> Dict[str, Any]:
    """
    阶段1主函数：准备与指令生成
    
    Args:
        project_path: 项目根目录路径
        ticket_info: 工单信息
        time_range: 时间范围 (start_time, end_time, source)
        ticket_id: 工单ID
    
    Returns:
        工单上下文数据
    """
    print("\n" + "="*60)
    print("📋 阶段1：准备与指令生成")
    print("="*60)
    
    # 加载项目全局上下文
    print("\n📂 加载项目全局上下文...")
    project_context = load_project_context(project_path)
    if project_context:
        print(f"  ✅ 已加载项目上下文（{len(project_context.get('services', []))} 个服务）")
    else:
        print("  ⚠️  项目上下文未加载")
    
    # 加载SigNoz配置
    print("\n📂 加载SigNoz配置...")
    signoz_config = load_signoz_config(project_path)
    if signoz_config:
        print(f"  ✅ 已加载SigNoz配置")
    else:
        print("  ⚠️  SigNoz配置未加载")
    
    # 构建工单上下文
    start_time, end_time, time_source = time_range
    ticket_context = {
        'ticket_id': ticket_id,
        'ticket_info': ticket_info,
        'project_context': project_context,
        'signoz_config': signoz_config,
        'time_range': {
            'start': int(start_time.timestamp() * 1000) if start_time else None,
            'end': int(end_time.timestamp() * 1000) if end_time else None,
            'start_display': format_datetime(start_time) if start_time else None,
            'end_display': format_datetime(end_time) if end_time else None,
            'source': time_source
        },
        'created_at': datetime.now().isoformat()
    }
    
    # 保存工单上下文
    print("\n💾 保存工单上下文...")
    context_file = save_ticket_context(ticket_context, project_path, ticket_id)
    if context_file:
        print(f"  ✅ 工单上下文已保存: {context_file}")
    else:
        print("  ⚠️  工单上下文保存失败")
    
    print("\n" + "="*60)
    
    return ticket_context
