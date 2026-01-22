#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供通用的工具函数，包括文件操作、目录管理等
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 分析器工作目录名称
ANALYZER_DIR = '.production-issue-analyzer'
# 经验目录名称
HISTORY_DIR = '.production-history'
# 工单目录名称
TICKETS_DIR = 'tickets'


def get_analyzer_dir(project_path: str) -> Path:
    """
    获取分析器工作目录路径，如果不存在则创建
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        分析器工作目录路径
    """
    project_root = Path(project_path).resolve()
    analyzer_dir = project_root / ANALYZER_DIR
    analyzer_dir.mkdir(parents=True, exist_ok=True)
    return analyzer_dir


def get_history_dir(project_path: str) -> Path:
    """
    获取经验目录路径，如果不存在则创建
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        经验目录路径
    """
    project_root = Path(project_path).resolve()
    history_dir = project_root / HISTORY_DIR
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir


def get_ticket_dir(project_path: str, ticket_id: str) -> Path:
    """
    获取工单目录路径，如果不存在则创建
    
    Args:
        project_path: 项目根目录路径
        ticket_id: 工单ID
    
    Returns:
        工单目录路径
    """
    analyzer_dir = get_analyzer_dir(project_path)
    tickets_dir = analyzer_dir / TICKETS_DIR
    tickets_dir.mkdir(parents=True, exist_ok=True)
    ticket_dir = tickets_dir / ticket_id
    ticket_dir.mkdir(parents=True, exist_ok=True)
    return ticket_dir


def ensure_directory(directory: Path) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    directory.mkdir(parents=True, exist_ok=True)


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件路径
    
    Returns:
        JSON数据，如果文件不存在或读取失败则返回None
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  加载JSON文件失败 {file_path}: {e}", file=sys.stderr)
        return None


def save_json_file(file_path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
    """
    保存JSON文件
    
    Args:
        file_path: JSON文件路径
        data: 要保存的数据
        indent: JSON缩进空格数
    
    Returns:
        是否保存成功
    """
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        print(f"⚠️  保存JSON文件失败 {file_path}: {e}", file=sys.stderr)
        return False


def load_markdown_file(file_path: Path) -> Optional[str]:
    """
    加载Markdown文件
    
    Args:
        file_path: Markdown文件路径
    
    Returns:
        文件内容，如果文件不存在或读取失败则返回None
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  加载Markdown文件失败 {file_path}: {e}", file=sys.stderr)
        return None


def save_markdown_file(file_path: Path, content: str) -> bool:
    """
    保存Markdown文件
    
    Args:
        file_path: Markdown文件路径
        content: 要保存的内容
    
    Returns:
        是否保存成功
    """
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"⚠️  保存Markdown文件失败 {file_path}: {e}", file=sys.stderr)
        return False


def generate_ticket_id(user_input: str, ticket_id_from_input: Optional[str] = None) -> str:
    """
    生成工单ID
    
    优先级：
    1. 从用户输入中提取的工单ID
    2. 基于时间戳和输入内容哈希生成
    
    Args:
        user_input: 用户输入内容
        ticket_id_from_input: 从输入中提取的工单ID
    
    Returns:
        工单ID
    """
    if ticket_id_from_input:
        # 清理工单ID，只保留字母、数字、连字符和下划线
        cleaned_id = re.sub(r'[^a-zA-Z0-9_-]', '', ticket_id_from_input)
        if cleaned_id:
            return cleaned_id
    
    # 生成基于时间戳和内容哈希的ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    content_hash = hashlib.md5(user_input.encode('utf-8')).hexdigest()[:8]
    return f"ticket_{timestamp}_{content_hash}"


def generate_experience_hash(problem_description: str, solution: str) -> str:
    """
    生成经验文件hash
    
    Args:
        problem_description: 问题描述
        solution: 解决方案
    
    Returns:
        hash值（用于文件名）
    """
    content = f"{problem_description}\n{solution}"
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def validate_json_structure(data: Dict[str, Any], required_fields: list) -> tuple:
    """
    验证JSON数据结构是否包含必需字段
    
    Args:
        data: 要验证的数据
        required_fields: 必需字段列表
    
    Returns:
        (是否完整, 缺失字段列表)
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
    
    Returns:
        格式化后的字符串
    """
    return dt.strftime(format_str)


def parse_datetime(time_str: str, default_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    解析时间字符串
    
    Args:
        time_str: 时间字符串
        default_date: 默认日期（如果时间字符串只有时间部分）
    
    Returns:
        日期时间对象，如果解析失败则返回None
    """
    from dateutil import parser as date_parser
    
    try:
        dt = date_parser.parse(time_str, default=default_date)
        return dt
    except Exception:
        return None


# 导入sys用于错误输出
import sys
