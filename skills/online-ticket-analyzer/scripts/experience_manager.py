#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经验管理模块
检索历史经验，保存新经验
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils import (
    get_history_dir,
    load_markdown_file,
    save_markdown_file,
    generate_experience_hash
)


def search_history_experience(
    project_path: str,
    problem_description: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    检索历史经验
    
    Args:
        project_path: 项目根目录路径
        problem_description: 问题描述
        max_results: 最大返回结果数
    
    Returns:
        相似经验列表
    """
    history_dir = get_history_dir(project_path)
    
    if not history_dir.exists():
        return []
    
    # 获取所有经验文件
    experience_files = list(history_dir.glob('experience_*.md'))
    
    if not experience_files:
        return []
    
    # 计算相似度并排序
    experiences = []
    for exp_file in experience_files:
        experience = load_experience(exp_file)
        if experience:
            similarity = calculate_similarity(
                problem_description,
                experience.get('problem_description', '')
            )
            experience['similarity'] = similarity
            experience['file_path'] = str(exp_file)
            experiences.append(experience)
    
    # 按相似度排序
    experiences.sort(key=lambda x: x.get('similarity', 0), reverse=True)
    
    # 返回前N个结果
    return experiences[:max_results]


def load_experience(experience_file: Path) -> Optional[Dict[str, Any]]:
    """
    加载经验文件
    
    Args:
        experience_file: 经验文件路径
    
    Returns:
        经验数据，如果加载失败则返回None
    """
    content = load_markdown_file(experience_file)
    if not content:
        return None
    
    # 解析Markdown内容
    experience = parse_experience_markdown(content)
    return experience


def parse_experience_markdown(content: str) -> Dict[str, Any]:
    """
    解析经验Markdown内容
    
    格式：
    # 问题描述
    ...
    
    # 解决方案
    ...
    
    # 元数据
    - 成功/失败: 成功
    - 相关服务: service1, service2
    - 时间戳: 2025-01-20 10:00:00
    - 标签: tag1, tag2
    """
    experience = {
        'problem_description': '',
        'solution': '',
        'success': True,
        'services': [],
        'timestamp': '',
        'tags': []
    }
    
    # 提取问题描述
    problem_match = re.search(r'#\s*问题描述\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    if problem_match:
        experience['problem_description'] = problem_match.group(1).strip()
    
    # 提取解决方案
    solution_match = re.search(r'#\s*解决方案\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    if solution_match:
        experience['solution'] = solution_match.group(1).strip()
    
    # 提取元数据
    metadata_match = re.search(r'#\s*元数据\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    if metadata_match:
        metadata_text = metadata_match.group(1)
        
        # 成功/失败
        success_match = re.search(r'成功/失败[:：]\s*(\w+)', metadata_text)
        if success_match:
            experience['success'] = success_match.group(1) == '成功'
        
        # 相关服务
        services_match = re.search(r'相关服务[:：]\s*([^\n]+)', metadata_text)
        if services_match:
            services_str = services_match.group(1).strip()
            experience['services'] = [s.strip() for s in services_str.split(',')]
        
        # 时间戳
        timestamp_match = re.search(r'时间戳[:：]\s*([^\n]+)', metadata_text)
        if timestamp_match:
            experience['timestamp'] = timestamp_match.group(1).strip()
        
        # 标签
        tags_match = re.search(r'标签[:：]\s*([^\n]+)', metadata_text)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            experience['tags'] = [t.strip() for t in tags_str.split(',')]
    
    return experience


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算文本相似度（简单的关键词匹配）
    
    Args:
        text1: 文本1
        text2: 文本2
    
    Returns:
        相似度分数（0-1）
    """
    if not text1 or not text2:
        return 0.0
    
    # 提取关键词
    keywords1 = set(re.findall(r'\w+', text1.lower()))
    keywords2 = set(re.findall(r'\w+', text2.lower()))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # 计算交集和并集
    intersection = keywords1 & keywords2
    union = keywords1 | keywords2
    
    if not union:
        return 0.0
    
    # Jaccard相似度
    similarity = len(intersection) / len(union)
    
    return similarity


def save_experience(
    project_path: str,
    problem_description: str,
    solution: str,
    success: bool = True,
    services: Optional[List[str]] = None,
    tags: Optional[List[str]] = None
) -> Optional[Path]:
    """
    保存经验到.production-history目录
    
    Args:
        project_path: 项目根目录路径
        problem_description: 问题描述
        solution: 解决方案
        success: 是否成功
        services: 相关服务列表
        tags: 标签列表
    
    Returns:
        保存的经验文件路径，如果保存失败则返回None
    """
    history_dir = get_history_dir(project_path)
    
    # 生成经验hash
    exp_hash = generate_experience_hash(problem_description, solution)
    
    # 构建经验文件内容
    content = f"""# 问题描述

{problem_description}

# 解决方案

{solution}

# 元数据

- 成功/失败: {'成功' if success else '失败'}
- 相关服务: {', '.join(services or [])}
- 时间戳: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 标签: {', '.join(tags or [])}
"""
    
    # 保存文件
    experience_file = history_dir / f'experience_{exp_hash}.md'
    if save_markdown_file(experience_file, content):
        return experience_file
    return None


def format_experience_for_display(experience: Dict[str, Any]) -> str:
    """
    格式化经验用于显示
    
    Args:
        experience: 经验数据
    
    Returns:
        格式化后的字符串
    """
    lines = []
    lines.append(f"相似度: {experience.get('similarity', 0):.2%}")
    lines.append(f"问题: {experience.get('problem_description', '')[:100]}...")
    lines.append(f"解决方案: {experience.get('solution', '')[:100]}...")
    lines.append(f"服务: {', '.join(experience.get('services', []))}")
    lines.append(f"时间: {experience.get('timestamp', '')}")
    
    return "\n".join(lines)
