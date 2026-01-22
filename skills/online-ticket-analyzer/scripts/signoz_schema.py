#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SigNoz数据结构定义模块
基于@ccint/signoz包的数据结构说明
"""

from typing import Optional

# SigNoz字段上下文类型
FIELD_CONTEXT_RESOURCE = 'resource'  # 资源级别字段
FIELD_CONTEXT_ATTRIBUTES = 'attributes'  # 属性级别字段
FIELD_CONTEXT_SPAN = 'span'  # 跨度级别字段
FIELD_CONTEXT_LOG = 'log'  # 日志级别字段

# 常见字段定义（基于@ccint/signoz包）
SIGNOZ_COMMON_FIELDS = {
    # 资源级别字段（resource）
    'service.name': {
        'name': 'service.name',
        'fieldContext': FIELD_CONTEXT_RESOURCE,
        'fieldDataType': 'string',
        'description': '应用名称（格式：事业部.小组.项目名）'
    },
    'service.version': {
        'name': 'service.version',
        'fieldContext': FIELD_CONTEXT_RESOURCE,
        'fieldDataType': 'string',
        'description': '应用版本'
    },
    'service.environment': {
        'name': 'service.environment',
        'fieldContext': FIELD_CONTEXT_RESOURCE,
        'fieldDataType': 'string',
        'description': '运行环境'
    },
    
    # 基础属性（attributes）
    'browser.name': {
        'name': 'browser.name',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '浏览器名称（Web）'
    },
    'browser.version': {
        'name': 'browser.version',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '浏览器版本（Web）'
    },
    'browser.user_agent': {
        'name': 'browser.user_agent',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '用户代理字符串（Web）'
    },
    'localTime': {
        'name': 'localTime',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '本地时间'
    },
    'path': {
        'name': 'path',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '当前页面完整路径'
    },
    'pathname': {
        'name': 'pathname',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '当前页面路径（无参数）'
    },
    'referrer': {
        'name': 'referrer',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '来源页面（Web）'
    },
    'pageStack': {
        'name': 'pageStack',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '当前页面的栈索引（小程序）'
    },
    
    # 请求日志属性（attributes）
    'request.host': {
        'name': 'request.host',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '请求域名'
    },
    'request.pathname': {
        'name': 'request.pathname',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '请求路径'
    },
    'request.query': {
        'name': 'request.query',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '查询参数'
    },
    'request.method': {
        'name': 'request.method',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '请求方法'
    },
    'request.body': {
        'name': 'request.body',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '请求体'
    },
    'response.status': {
        'name': 'response.status',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '响应状态码'
    },
    'response.time': {
        'name': 'response.time',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '响应时间（毫秒）'
    },
    'response.body': {
        'name': 'response.body',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '响应体'
    },
    'response.headers': {
        'name': 'response.headers',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '响应头（仅包含配置的错误码字段）'
    },
    'response.errno': {
        'name': 'response.errno',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '业务错误码'
    },
    
    # 错误日志属性（attributes）
    'filename': {
        'name': 'filename',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '错误文件名（Web）'
    },
    'lineNo': {
        'name': 'lineNo',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '错误行号（Web）'
    },
    'colNo': {
        'name': 'colNo',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '错误列号（Web）'
    },
    'message': {
        'name': 'message',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '错误信息'
    },
    'stack': {
        'name': 'stack',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '错误堆栈（Web）'
    },
    'name': {
        'name': 'name',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '错误类型'
    },
    
    # 性能日志属性（attributes）
    'redirect': {
        'name': 'redirect',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '重定向耗时（毫秒）'
    },
    'serviceWorkerInit': {
        'name': 'serviceWorkerInit',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'Service Worker 初始化耗时（毫秒）'
    },
    'checkCache': {
        'name': 'checkCache',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '缓存检查耗时（毫秒）'
    },
    'dns': {
        'name': 'dns',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'DNS 查询耗时（毫秒）'
    },
    'connectWait': {
        'name': 'connectWait',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '连接等待耗时（毫秒）'
    },
    'tcp': {
        'name': 'tcp',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'TCP 连接耗时（毫秒）'
    },
    'ssl': {
        'name': 'ssl',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'TLS 握手耗时（毫秒）'
    },
    'ttfb': {
        'name': 'ttfb',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '首字节时间（毫秒）'
    },
    'response': {
        'name': 'response',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '响应接收耗时（毫秒）'
    },
    'htmlParse': {
        'name': 'htmlParse',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'HTML 解析时间（毫秒）'
    },
    'domContentLoadedDelay': {
        'name': 'domContentLoadedDelay',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'DOMContentLoaded 延迟时间（毫秒）'
    },
    'domContentLoaded': {
        'name': 'domContentLoaded',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'DOMContentLoaded 耗时（毫秒）'
    },
    'resourceLoad': {
        'name': 'resourceLoad',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '页面资源加载耗时（毫秒）'
    },
    'loadDelay': {
        'name': 'loadDelay',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'Load 延迟时间（毫秒）'
    },
    'load': {
        'name': 'load',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'Load 耗时（毫秒）'
    },
    'pageLoad': {
        'name': 'pageLoad',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '页面完全加载耗时（毫秒）'
    },
    'css': {
        'name': 'css',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'CSS 平均加载时间（毫秒）'
    },
    'js': {
        'name': 'js',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'JavaScript 平均加载时间（毫秒）'
    },
    'fpt': {
        'name': 'fpt',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'First Paint 时间（毫秒）'
    },
    'fcpt': {
        'name': 'fcpt',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'First Contentful Paint 时间（毫秒）'
    },
    
    # 小程序特有属性（attributes）
    'duration': {
        'name': 'duration',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '耗时（毫秒）- appLaunch/route/firstRender/downloadPackage'
    },
    'referrerPath': {
        'name': 'referrerPath',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '上一个页面的路径（route日志）'
    },
    'initDataDelay': {
        'name': 'initDataDelay',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '从脚本注入完成，到首次数据从逻辑层发出（毫秒）'
    },
    'initData': {
        'name': 'initData',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '首次数据从逻辑层发出，到接收（毫秒）'
    },
    'viewLayerRender': {
        'name': 'viewLayerRender',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '渲染层从开始渲染，到结束（毫秒）'
    },
    'packageName': {
        'name': 'packageName',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '分包名（downloadPackage日志）'
    },
    'packageSize': {
        'name': 'packageSize',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '分包大小（字节）'
    },
    'network.type': {
        'name': 'network.type',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '网络类型（network日志）'
    },
    'network.signalStrength': {
        'name': 'network.signalStrength',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '信号强度（network日志）'
    },
    'network.hasSystemProxy': {
        'name': 'network.hasSystemProxy',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '是否使用系统代理，0或1（network日志）'
    },
    'network.weakNet': {
        'name': 'network.weakNet',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '是否弱网，0或1（network日志）'
    },
    'network.isConnected': {
        'name': 'network.isConnected',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '是否连上了网，0或1（network日志）'
    },
    
    # Web Vitals 指标（attributes）
    'fcp': {
        'name': 'fcp',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'First Contentful Paint（毫秒）'
    },
    'lcp': {
        'name': 'lcp',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'Largest Contentful Paint（毫秒）'
    },
    'cls': {
        'name': 'cls',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'float',
        'description': 'Cumulative Layout Shift'
    },
    'inp': {
        'name': 'inp',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'Interaction to Next Paint（毫秒）'
    },
    'evaluateScript': {
        'name': 'evaluateScript',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': 'js执行时间（毫秒，仅小程序）'
    },
    
    # 系统信息（attributes，小程序appLaunch日志）
    # system.xxx 字段根据实际系统信息动态生成，这里不预定义
    
    # 用户和设备字段（attributes）
    'user.id': {
        'name': 'user.id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '用户ID（实际字段名：user.id）'
    },
    'user.client_id': {
        'name': 'user.client_id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '客户端ID/设备ID（实际字段名：user.client_id）'
    },
    
    # 地理位置字段（attributes）
    'geo.location.lat': {
        'name': 'geo.location.lat',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'float',
        'description': '地理位置纬度'
    },
    'geo.location.lon': {
        'name': 'geo.location.lon',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'float',
        'description': '地理位置经度'
    },
    'geo.city_name': {
        'name': 'geo.city_name',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '城市名称'
    },
    'geo.country_name': {
        'name': 'geo.country_name',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '国家名称'
    },
    'geo.country_iso_code': {
        'name': 'geo.country_iso_code',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '国家ISO代码'
    },
    'geo.region_name': {
        'name': 'geo.region_name',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '地区名称'
    },
    'geo.timezone': {
        'name': 'geo.timezone',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '时区'
    },
    
    # 来源信息字段（attributes）
    'source.address': {
        'name': 'source.address',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '来源IP地址'
    },
    
    # 通用字段（attributes）
    'body': {
        'name': 'body',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '日志内容（通用）'
    },
    'severity_text': {
        'name': 'severity_text',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '日志严重程度文本'
    },
    'severity_number': {
        'name': 'severity_number',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '日志严重程度数字'
    },
    'trace_id': {
        'name': 'trace_id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '追踪ID'
    },
    'span_id': {
        'name': 'span_id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '跨度ID'
    },
    'timestamp': {
        'name': 'timestamp',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'int64',
        'description': '时间戳（毫秒）'
    },
    
    # 兼容旧字段名（向后兼容）
    'user_id': {
        'name': 'user.id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '用户ID（兼容字段，实际使用user.id）'
    },
    'client_id': {
        'name': 'user.client_id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '客户端ID（兼容字段，实际使用user.client_id）'
    },
    'device_id': {
        'name': 'user.client_id',
        'fieldContext': FIELD_CONTEXT_ATTRIBUTES,
        'fieldDataType': 'string',
        'description': '设备ID（兼容字段，实际使用user.client_id）'
    }
}

# 默认查询字段（按优先级排序）
# 根据平台查询结果，优先包含常用显示字段
DEFAULT_QUERY_FIELDS = [
    'service.name',  # 资源级别：应用名称（平台显示）
    'pathname',  # 属性级别：页面路径（平台显示为Pathname列）
    'message',  # 属性级别：错误信息（平台显示为Message列）
    'stack',  # 属性级别：错误堆栈（平台显示为Stack列）
    'severity_text',  # 属性级别：严重程度文本（平台显示为Severity_text列）
    'user.id',  # 属性级别：用户ID（平台显示为User.id列）
    'severity_number',  # 属性级别：严重程度数字
    'timestamp',  # 属性级别：时间戳（平台显示为Timestamp列）
    'localTime',  # 属性级别：本地时间
    'service.version',  # 资源级别：应用版本
    'service.environment',  # 资源级别：运行环境
    'body',  # 属性级别：日志内容
    'request.pathname',  # 属性级别：请求路径
    'response.status',  # 属性级别：响应状态码
    'response.errno',  # 属性级别：业务错误码
    'trace_id',  # 属性级别：追踪ID
    'span_id'  # 属性级别：跨度ID
]

# 错误日志严重程度值
SEVERITY_ERROR_VALUES = [
    'error', 'Error', 'ERROR',
    '异常', '错误',
    'fatal', 'Fatal', 'FATAL',
    'critical', 'Critical', 'CRITICAL'
]

# 错误日志严重程度数字（OpenTelemetry标准）
SEVERITY_ERROR_NUMBERS = [17, 18, 19, 20, 21, 22]  # ERROR, FATAL, CRITICAL等


def get_field_definition(field_name: str) -> dict:
    """
    获取字段定义
    
    Args:
        field_name: 字段名称
    
    Returns:
        字段定义字典，如果不存在则返回None
    """
    return SIGNOZ_COMMON_FIELDS.get(field_name)


def parse_field_path(field_path: str) -> dict:
    """
    解析字段路径，返回字段定义
    
    Args:
        field_path: 字段路径（如 'service.name', 'body', 'attributes.user_id'）
    
    Returns:
        字段定义字典
    """
    # 如果字段路径包含点，可能是嵌套路径
    if '.' in field_path:
        parts = field_path.split('.')
        
        # 如果是 resource.xxx 或 attributes.xxx 格式
        if parts[0] in ['resource', 'attributes', 'span', 'log']:
            field_context = parts[0]
            field_name = '.'.join(parts[1:])
        else:
            # 尝试从已知字段中查找
            if field_path in SIGNOZ_COMMON_FIELDS:
                return SIGNOZ_COMMON_FIELDS[field_path]
            # 默认假设为属性级别
            field_context = FIELD_CONTEXT_ATTRIBUTES
            field_name = field_path
    else:
        # 简单字段名，尝试从已知字段中查找
        if field_path in SIGNOZ_COMMON_FIELDS:
            return SIGNOZ_COMMON_FIELDS[field_path]
        # 默认假设为属性级别
        field_context = FIELD_CONTEXT_ATTRIBUTES
        field_name = field_path
    
    # 返回解析后的字段定义
    return {
        'name': field_name,
        'fieldContext': field_context,
        'fieldDataType': 'string',  # 默认类型
        'description': f'字段: {field_path}'
    }


def build_field_spec(field_path: str, signal: str = 'logs') -> dict:
    """
    构建字段规范（用于Query Builder）
    
    ⚠️ 注意：SigNoz查询时，attributes、resource这些是不需要传入的
    只需要传入字段名称即可，SigNoz会自动识别字段的上下文
    
    Args:
        field_path: 字段路径
        signal: 信号类型（logs, traces, metrics）
    
    Returns:
        字段规范字典（不包含fieldContext）
    """
    field_def = parse_field_path(field_path)
    
    # 只返回字段名称和数据类型，不包含fieldContext
    return {
        'name': field_def['name'],
        'fieldDataType': field_def.get('fieldDataType', 'string'),
        'signal': signal
        # 注意：不包含fieldContext，SigNoz会自动识别
    }


def is_error_severity(severity_text: Optional[str] = None, severity_number: Optional[int] = None) -> bool:
    """
    判断是否为错误严重程度
    
    Args:
        severity_text: 严重程度文本
        severity_number: 严重程度数字
    
    Returns:
        是否为错误
    """
    if severity_text:
        return severity_text in SEVERITY_ERROR_VALUES
    
    if severity_number is not None:
        return severity_number in SEVERITY_ERROR_NUMBERS
    
    return False
