#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户输入解析模块
解析用户输入（文字、图片、文件），提取工单信息
"""

import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dateutil import parser as date_parser

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


def parse_user_input(
    description: Optional[str] = None,
    image_path: Optional[str] = None,
    file_path: Optional[str] = None
) -> str:
    """
    解析用户输入，支持文字、图片、文件
    
    Args:
        description: 文字描述
        image_path: 图片路径
        file_path: 文件路径
    
    Returns:
        合并后的输入文本
    """
    text_parts = []
    
    # 处理文字描述
    if description:
        text_parts.append(description)
    
    # 处理文件
    if file_path:
        file_text = read_file(file_path)
        if file_text:
            text_parts.append(f"\n[文件内容: {file_path}]\n{file_text}")
    
    # 处理图片（OCR）
    if image_path:
        image_text = process_image(image_path)
        if image_text:
            text_parts.append(f"\n[图片识别内容: {image_path}]\n{image_text}")
    
    return "\n".join(text_parts)


def read_file(file_path: str) -> Optional[str]:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件内容，如果读取失败则返回None
    """
    try:
        file = Path(file_path)
        if not file.exists():
            print(f"⚠️  文件不存在: {file_path}", file=sys.stderr)
            return None
        
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}", file=sys.stderr)
        return None


def process_image(image_path: str) -> Optional[str]:
    """
    处理图片，使用OCR识别文字
    
    Args:
        image_path: 图片路径
    
    Returns:
        识别出的文字，如果识别失败则返回None
    """
    if not HAS_OCR:
        print("⚠️  OCR功能不可用，请安装pytesseract和Tesseract OCR引擎", file=sys.stderr)
        return None
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        return text.strip() if text.strip() else None
    except Exception as e:
        print(f"⚠️  图片OCR识别失败 {image_path}: {e}", file=sys.stderr)
        return None


def extract_ticket_info(user_input: str) -> Dict[str, Any]:
    """
    从用户输入中提取工单信息
    
    Args:
        user_input: 用户输入文本
    
    Returns:
        提取的工单信息字典
    """
    ticket_info = {
        'ticket_id': None,
        'description': user_input,
        'services': [],
        'user_info': {},
        'device_info': {},
        'api_info': {},
        'region_info': {},
        'time_info': {},
        'keywords': []
    }
    
    # 提取工单ID
    ticket_id = extract_ticket_id(user_input)
    if ticket_id:
        ticket_info['ticket_id'] = ticket_id
    
    # 提取服务信息
    services = extract_service_info(user_input)
    if services:
        ticket_info['services'] = services
    
    # 提取用户信息
    user_info = extract_user_info(user_input)
    if user_info:
        ticket_info['user_info'] = user_info
    
    # 提取设备信息
    device_info = extract_device_info(user_input)
    if device_info:
        ticket_info['device_info'] = device_info
    
    # 提取接口信息
    api_info = extract_api_info(user_input)
    if api_info:
        ticket_info['api_info'] = api_info
    
    # 提取地区信息
    region_info = extract_region_info(user_input)
    if region_info:
        ticket_info['region_info'] = region_info
    
    # 提取时间信息
    time_info = extract_time_info(user_input)
    if time_info:
        ticket_info['time_info'] = time_info
    
    # 提取关键词
    keywords = extract_keywords(user_input)
    if keywords:
        ticket_info['keywords'] = keywords
    
    return ticket_info


def extract_ticket_id(text: str) -> Optional[str]:
    """提取工单ID"""
    patterns = [
        r'工单[ID|id|Id|iD][:：]\s*([A-Za-z0-9_-]+)',
        r'[Tt]icket[ID|id|Id|iD][:：]\s*([A-Za-z0-9_-]+)',
        r'工单号[:：]\s*([A-Za-z0-9_-]+)',
        r'工单[:：]\s*([A-Za-z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


def extract_service_info(text: str) -> list:
    """提取服务信息"""
    services = []
    
    patterns = [
        r'服务[:：]\s*([^\s,，]+)',
        r'[Ss]ervice[:：]\s*([^\s,，]+)',
        r'服务名[:：]\s*([^\s,，]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        services.extend(matches)
    
    # 去重
    return list(set(services))


def extract_user_info(text: str) -> Dict[str, Any]:
    """提取用户信息"""
    user_info = {}
    
    # 用户ID（注意：实际字段名是user.id，不是user_id）
    user_id_patterns = [
        r'用户[ID|id|Id|iD][:：]\s*([^\s,，]+)',
        r'[Uu]ser[ID|id|Id|iD][:：]\s*([^\s,，]+)',
        r'用户号[:：]\s*([^\s,，]+)'
    ]
    for pattern in user_id_patterns:
        match = re.search(pattern, text)
        if match:
            # 保存为user_id用于后续处理，但实际查询时使用user.id
            user_info['user_id'] = match.group(1)
            user_info['user.id'] = match.group(1)  # 实际字段名
            break
    
    # 用户名
    username_patterns = [
        r'用户名[:：]\s*([^\s,，]+)',
        r'[Uu]sername[:：]\s*([^\s,，]+)'
    ]
    for pattern in username_patterns:
        match = re.search(pattern, text)
        if match:
            user_info['username'] = match.group(1)
            break
    
    # 用户邮箱
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    email_match = re.search(email_pattern, text)
    if email_match:
        user_info['email'] = email_match.group(1)
    
    return user_info


def extract_device_info(text: str) -> Dict[str, Any]:
    """提取设备信息"""
    device_info = {}
    
    patterns = [
        r'设备[ID|id|Id|iD][:：]\s*([^\s,，]+)',
        r'[Dd]evice[ID|id|Id|iD][:：]\s*([^\s,，]+)',
        r'[Cc]lient[ID|id|Id|iD][:：]\s*([^\s,，]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # 保存为device_id和client_id用于后续处理，但实际查询时使用user.client_id
            device_id = match.group(1)
            device_info['device_id'] = device_id
            device_info['client_id'] = device_id
            device_info['user.client_id'] = device_id  # 实际字段名
            break
    
    return device_info


def extract_api_info(text: str) -> Dict[str, Any]:
    """提取接口信息"""
    api_info = {}
    
    # 接口路径
    api_path_patterns = [
        r'接口[:：]\s*([^\s,，]+)',
        r'[Aa][Pp][Ii][:：]\s*([^\s,，]+)',
        r'[Aa][Pp][Ii][Pp]ath[:：]\s*([^\s,，]+)',
        r'[/][a-zA-Z0-9/_-]+'  # 直接匹配路径格式
    ]
    for pattern in api_path_patterns:
        match = re.search(pattern, text)
        if match:
            api_path = match.group(1) if match.lastindex else match.group(0)
            if api_path.startswith('/'):
                api_info['api_path'] = api_path
                break
    
    # 功能名称（推断接口）
    function_keywords = ['登录', '注册', '上传', '下载', '支付', '查询', '删除', '更新']
    for keyword in function_keywords:
        if keyword in text:
            api_info['function_name'] = keyword
            break
    
    return api_info


def extract_region_info(text: str) -> Dict[str, Any]:
    """提取地区信息"""
    region_info = {}
    
    # 国家
    country_patterns = [
        r'国家[:：]\s*([^\s,，]+)',
        r'[Cc]ountry[:：]\s*([^\s,，]+)'
    ]
    for pattern in country_patterns:
        match = re.search(pattern, text)
        if match:
            region_info['country'] = match.group(1)
            break
    
    # 城市
    city_patterns = [
        r'城市[:：]\s*([^\s,，]+)',
        r'[Cc]ity[:：]\s*([^\s,，]+)'
    ]
    for pattern in city_patterns:
        match = re.search(pattern, text)
        if match:
            region_info['city'] = match.group(1)
            break
    
    return region_info


def extract_time_info(text: str) -> Dict[str, Any]:
    """提取时间信息"""
    time_info = {}
    
    # 工单时间关键词
    ticket_time_keywords = ['工单时间', '上报时间', '创建时间', '提交时间', '工单创建', '工单提交']
    ticket_time = extract_time_by_keywords(text, ticket_time_keywords)
    if ticket_time:
        time_info['ticket_time'] = ticket_time
        time_info['time_type'] = 'ticket_time'
    
    # 邮件时间关键词
    email_time_keywords = ['邮件时间', '发送时间', '收到时间', '邮件发送', '邮件收到']
    email_time = extract_time_by_keywords(text, email_time_keywords)
    if email_time:
        time_info['email_time'] = email_time
        if 'time_type' not in time_info:
            time_info['time_type'] = 'email_time'
    
    # 问题时间关键词
    problem_time_keywords = ['发生时间', '出现时间', '异常时间', '问题时间']
    problem_time = extract_time_by_keywords(text, problem_time_keywords)
    if problem_time:
        time_info['problem_time'] = problem_time
        if 'time_type' not in time_info:
            time_info['time_type'] = 'problem_time'
    
    return time_info


def extract_time_by_keywords(text: str, keywords: list) -> Optional[datetime]:
    """根据关键词提取时间"""
    for keyword in keywords:
        pattern = rf'{keyword}[:：]\s*([^\s,，]+(?:\s+[^\s,，]+)?)'
        match = re.search(pattern, text)
        if match:
            time_str = match.group(1)
            dt = parse_time_string(time_str)
            if dt:
                return dt
    
    return None


def parse_time_string(time_str: str, default_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    解析时间字符串
    
    支持格式：
    - 完整时间：2025-01-20 10:00:00
    - 仅时间：10:00:00（假设为今天）
    - 关键词：今天、昨天、刚才、刚刚、最近
    """
    time_str = time_str.strip()
    
    # 处理关键词
    now = datetime.now()
    if '今天' in time_str or '刚才' in time_str or '刚刚' in time_str:
        # 提取时间部分
        time_match = re.search(r'(\d{1,2})[:：](\d{1,2})(?:[:：](\d{1,2}))?', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            second = int(time_match.group(3)) if time_match.group(3) else 0
            return now.replace(hour=hour, minute=minute, second=second, microsecond=0)
        return now
    
    if '昨天' in time_str:
        yesterday = now - timedelta(days=1)
        time_match = re.search(r'(\d{1,2})[:：](\d{1,2})(?:[:：](\d{1,2}))?', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            second = int(time_match.group(3)) if time_match.group(3) else 0
            return yesterday.replace(hour=hour, minute=minute, second=second, microsecond=0)
        return yesterday
    
    # 尝试使用dateutil解析
    try:
        dt = date_parser.parse(time_str, default=default_date or now)
        return dt
    except Exception:
        pass
    
    return None


def extract_keywords(text: str) -> list:
    """提取关键词"""
    keywords = []
    
    # 错误关键词
    error_keywords = ['错误', '异常', '失败', '超时', '500', '404', '502', '503', 'error', 'exception', 'fail', 'timeout']
    for keyword in error_keywords:
        if keyword.lower() in text.lower():
            keywords.append(keyword)
    
    # 服务关键词
    service_keywords = ['服务', '接口', 'API', 'service', 'api']
    for keyword in service_keywords:
        if keyword.lower() in text.lower():
            keywords.append(keyword)
    
    return keywords


def extract_time_range(
    ticket_info: Dict[str, Any],
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    default_range_hours: int = 1
) -> Tuple[Optional[datetime], Optional[datetime], str]:
    """
    计算查询时间范围
    
    优先级（从高到低）：
    1. 命令行参数指定的时间
    2. 工单上报时间或邮件发送时间（前后30分钟）
    3. 问题发生时间（前后30分钟）
    4. 默认：最近N小时
    
    Args:
        ticket_info: 工单信息
        start_time: 命令行指定的开始时间
        end_time: 命令行指定的结束时间
        default_range_hours: 默认时间范围（小时）
    
    Returns:
        (开始时间, 结束时间, 时间来源说明)
    """
    # 优先级1：命令行参数
    if start_time and end_time:
        start_dt = parse_time_string(start_time)
        end_dt = parse_time_string(end_time)
        if start_dt and end_dt:
            return start_dt, end_dt, "命令行参数指定"
    
    # 优先级2：工单时间或邮件时间
    time_info = ticket_info.get('time_info', {})
    if time_info.get('time_type') in ['ticket_time', 'email_time']:
        base_time = time_info.get('ticket_time') or time_info.get('email_time')
        if base_time:
            start_dt = base_time - timedelta(minutes=30)
            end_dt = base_time + timedelta(minutes=30)
            return start_dt, end_dt, f"工单/邮件时间（{time_info.get('time_type')}）前后30分钟"
    
    # 优先级3：问题发生时间
    if time_info.get('problem_time'):
        base_time = time_info.get('problem_time')
        start_dt = base_time - timedelta(minutes=30)
        end_dt = base_time + timedelta(minutes=30)
        return start_dt, end_dt, "问题发生时间前后30分钟"
    
    # 优先级4：默认时间范围
    now = datetime.now()
    start_dt = now - timedelta(hours=default_range_hours)
    end_dt = now
    return start_dt, end_dt, f"默认：最近{default_range_hours}小时"
