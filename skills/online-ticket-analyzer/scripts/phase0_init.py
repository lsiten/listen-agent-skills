#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段0：首次使用检查与初始化模块
检查项目上下文和SigNoz配置信息，如果不存在或不完整则初始化
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from utils import (
    get_analyzer_dir,
    load_json_file,
    save_json_file,
    validate_json_structure
)

# 项目上下文必需字段
PROJECT_CONTEXT_REQUIRED_FIELDS = [
    'services',
    'key_files',
    'architecture',
    'tech_stack'
]

# SigNoz配置必需字段
SIGNOZ_CONFIG_REQUIRED_FIELDS = [
    'init_code_location',
    'base_url',  # API基础URL，用于组合完整接口路径
    'app_version',  # 应用版本（从环境变量获取的实际值）
    'environment',  # 环境名称（从环境变量获取的实际值，如online, production等）
    'signoz_env_vars',  # SigNoz相关环境变量（包含实际值）
    'fields',
    'common_query_fields',
    'service_names'
]

# 项目上下文文件路径
PROJECT_CONTEXT_FILE = 'project_context.json'
# SigNoz配置文件路径
SIGNOZ_CONFIG_FILE = 'signoz_config.json'


def check_project_context(project_path: str) -> Tuple[bool, Optional[Dict[str, Any]], list]:
    """
    检查项目上下文文件是否存在且完整
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        (是否存在, 上下文数据, 缺失字段列表)
    """
    analyzer_dir = get_analyzer_dir(project_path)
    context_file = analyzer_dir / PROJECT_CONTEXT_FILE
    
    if not context_file.exists():
        return False, None, PROJECT_CONTEXT_REQUIRED_FIELDS
    
    context_data = load_json_file(context_file)
    if context_data is None:
        return False, None, PROJECT_CONTEXT_REQUIRED_FIELDS
    
    is_complete, missing_fields = validate_json_structure(
        context_data,
        PROJECT_CONTEXT_REQUIRED_FIELDS
    )
    
    return True, context_data, missing_fields


def check_signoz_config(project_path: str) -> Tuple[bool, Optional[Dict[str, Any]], list]:
    """
    检查SigNoz配置文件是否存在且完整
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        (是否存在, 配置数据, 缺失字段列表)
    """
    analyzer_dir = get_analyzer_dir(project_path)
    config_file = analyzer_dir / SIGNOZ_CONFIG_FILE
    
    if not config_file.exists():
        return False, None, SIGNOZ_CONFIG_REQUIRED_FIELDS
    
    config_data = load_json_file(config_file)
    if config_data is None:
        return False, None, SIGNOZ_CONFIG_REQUIRED_FIELDS
    
    is_complete, missing_fields = validate_json_structure(
        config_data,
        SIGNOZ_CONFIG_REQUIRED_FIELDS
    )
    
    return True, config_data, missing_fields


def generate_project_context_with_ai(project_path: str) -> Optional[Dict[str, Any]]:
    """
    通过AI通读项目生成项目上下文
    
    注意：此函数会提示AI执行，实际生成需要AI配合
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        项目上下文数据，如果生成失败则返回None
    """
    print("\n" + "="*60)
    print("📋 阶段0：首次使用检查 - 生成项目上下文")
    print("="*60)
    print("\n⚠️  项目上下文文件不存在，需要通过AI通读项目生成。")
    print("\n请执行以下操作：")
    print("1. 让AI通读项目代码，了解项目结构、服务列表、关键文件等信息")
    print("2. 生成项目上下文JSON，包含以下字段：")
    print("   - services: 服务列表")
    print("   - key_files: 关键文件路径")
    print("   - architecture: 架构信息")
    print("   - tech_stack: 技术栈信息")
    print("\n生成后，将结果保存到 .production-issue-analyzer/project_context.json")
    print("\n示例格式：")
    print("""
{
  "services": ["user-service", "api-gateway", "payment-service"],
  "key_files": [
    "src/main.py",
    "src/config.py",
    "src/routes/api.py"
  ],
  "architecture": "微服务架构，使用Docker容器化部署",
  "tech_stack": ["Python", "Flask", "PostgreSQL", "Redis"]
}
    """)
    
    # 返回None，表示需要AI生成
    return None


def generate_signoz_config_with_ai(project_path: str) -> Optional[Dict[str, Any]]:
    """
    通过AI通读项目生成SigNoz配置信息
    
    注意：此函数会提示AI执行，实际生成需要AI配合
    
    Args:
        project_path: 项目根目录路径
    
    Returns:
        SigNoz配置数据，如果生成失败则返回None
    """
    print("\n" + "="*60)
    print("📋 阶段0：首次使用检查 - 生成SigNoz配置")
    print("="*60)
    print("\n⚠️  SigNoz配置文件不存在，需要通过AI通读项目生成。")
    print("\n⚠️  重要：SigNoz配置是从整体项目视角生成的，不是针对特定工单")
    print("   这个配置是全局的、可复用的，适用于所有工单分析")
    print("\n请执行以下操作：")
    print("1. 让AI通读整个项目代码，从整体项目视角查找以下信息：")
    print("   a. SigNoz初始化代码位置（通常在 src/libs/signoz.ts 等位置）")
    print("   b. 从打包配置（vite.config.ts, webpack.config.js等）中获取环境变量：")
    print("      ⚠️ 重要：环境变量的值应该从打包配置中获取，而不是直接从.env文件读取")
    print("      - 读取打包配置文件，查找loadEnv调用（Vite）或DefinePlugin配置（Webpack）")
    print("      - 根据打包配置的mode和prefix参数，从对应的.env文件中获取实际值")
    print("      - 或者从打包配置的define配置中获取实际值")
    print("      - base_url: API基础URL（从VITE_BASE_URL, REACT_APP_BASE_URL, BASE_URL等）")
    print("      - 所有API baseUrl配置（如VITE_SAPI_DOMESTIC, VITE_SAPI_FOREIGN, VITE_UAPI等）")
    print("      - appVersion: 从APP_VERSION或VITE_APP_VERSION获取实际值")
    print("      - env: 从VITE_ENV或NODE_ENV获取实际值（如online, production等）")
    print("      - 所有SigNoz相关环境变量（如SIGNOZ_ENDPOINT等）")
    print("   c. 从打包配置文件（vite.config.ts/js, webpack.config.js等）中提取：")
    print("      - base_url: 从base或publicPath配置中提取")
    print("      - 所有环境变量引用（如import.meta.env.XXX）")
    print("   d. 从SigNoz初始化代码中提取：")
    print("      - appName: 服务名称（这就是service.name的值）")
    print("      - appVersion: 如果使用import.meta.env.APP_VERSION，需要读取.env文件获取实际值")
    print("      - env: 如果使用import.meta.env.VITE_ENV，需要读取.env文件获取实际值")
    print("      - 所有其他配置项")
    print("   e. ⚠️ 所有工单查询关键信息识别配置（从整体项目视角，必须由AI通读代码完成）：")
    print("      ⚠️ 重要：所有工单查询需要的关键信息，必须通过AI阅读完整项目后，")
    print("      综合配置信息、环境配置、打包配置给出，而不是简单的正则匹配")
    print("      ")
    print("      必须完成的工作包括：")
    print("      1) ⚠️ 接口路径识别（api_pathname_mapping）：")
    print("         - 通读项目代码，查找所有API调用位置（如createRequest, axios等）")
    print("         - 对于每个API调用，追踪其baseUrl的来源：")
    print("           * 追踪createRequest等方法，找到baseUrl从config读取的位置")
    print("           * 查找config中baseUrl的定义，追踪到环境变量（如import.meta.env.XXX）")
    print("           * 从打包配置（vite.config.ts）中获取环境变量的实际值")
    print("           * 解析baseUrl，提取路径部分（如https://cs8.intsig.net/sync → /sync）")
    print("         - 组合完整pathname：baseUrl路径部分 + API相对路径")
    print("         - 生成api_pathname_mapping配置，包含所有API的完整pathname映射")
    print("      ")
    print("      2) ⚠️ 字段提取规则识别（field_extraction_rules）：")
    print("         - 通读项目代码，查找所有字段的使用方式")
    print("         - 了解项目中字段的实际命名规则（如user.id, user.client_id等）")
    print("         - 了解用户输入中可能出现的字段名称变体（如\"用户ID\"、\"UserID\"、\"user_id\"等）")
    print("         - 生成field_extraction_rules配置，映射用户输入模式到实际字段名")
    print("      ")
    print("      3) ⚠️ 服务名称映射识别（service_name_mapping）：")
    print("         - 通读项目代码，查找所有服务的定义和使用")
    print("         - 了解项目中服务的实际命名规则（如service.name的值）")
    print("         - 了解用户输入中可能出现的服务名称变体（如\"用户服务\"、\"UserService\"等）")
    print("         - 生成service_name_mapping配置，映射用户输入模式到实际service.name")
    print("      ")
    print("      4) ⚠️ 其他关键信息识别：")
    print("         - 通读项目代码，识别所有可能用于工单查询的关键信息")
    print("         - 了解这些信息在代码中的实际使用方式和命名规则")
    print("         - 生成相应的映射配置，确保从用户输入到实际查询字段的准确转换")
    print("      ")
    print("      示例流程（必须完整执行）：")
    print("      如果代码中是 createRequest('SAPI_DOMESTIC').post('/revert_dir_list', ...)")
    print("      需要：1) 识别API相对路径: /revert_dir_list")
    print("           2) 追踪createRequest方法，找到baseUrl从config.api['SAPI_DOMESTIC']读取")
    print("           3) 查找config中SAPI_DOMESTIC的定义，发现来自import.meta.env.VITE_SAPI_DOMESTIC")
    print("           4) 从打包配置（vite.config.ts）中获取VITE_SAPI_DOMESTIC的实际值")
    print("              （打包配置会使用loadEnv加载.env文件，根据mode和prefix获取实际值）")
    print("           5) 解析baseUrl，提取路径部分（如https://cs8.intsig.net/sync → /sync）")
    print("           6) 组合完整pathname: /sync + /revert_dir_list = /sync/revert_dir_list")
    print("           7) 在api_pathname_mapping中记录: {\"/revert_dir_list\": \"/sync/revert_dir_list\", ...}")
    print("\n⚠️  重要：环境变量的值必须从打包配置中获取，而不是直接从.env文件读取")
    print("   打包配置（如vite.config.ts）会使用loadEnv等方法加载.env文件，并在构建时处理环境变量")
    print("   例如：如果代码中是 import.meta.env.VITE_SAPI_DOMESTIC，需要：")
    print("   1) 读取vite.config.ts，查找loadEnv调用")
    print("   2) 根据loadEnv的mode和prefix参数，从对应的.env文件中获取实际值")
    print("   3) 或者从vite.config.ts的define配置中获取实际值")
    print("\n⚠️  重要：要从整体项目视角生成，包含所有可能用到的配置，不仅仅是当前工单需要的")
    print("   - 包含所有API类型的baseUrl配置")
    print("   - 包含所有环境变量的实际值")
    print("   - 包含项目中使用的所有字段")
    print("   - 包含所有服务的名称映射")
    print("   - 包含完整的api_pathname_mapping（所有API的完整pathname映射）")
    print("\n⚠️  重要：要从整体项目视角生成，包含所有可能用到的配置，不仅仅是当前工单需要的")
    print("\n2. 分析SigNoz配置，从整体项目视角提取以下信息：")
    print("   - init_code_location: SigNoz初始化代码位置")
    print("   - base_url: API基础URL（从环境变量或打包配置中获取的实际值）")
    print("   - app_version: 应用版本（从环境变量获取的实际值）")
    print("   - environment: 环境名称（从环境变量获取的实际值，如online, production等）")
    print("   - api_baseurls: 所有API baseUrl配置（字典格式，包含项目中所有API类型的baseUrl）")
    print("     例如：{\"SAPI_DOMESTIC\": \"https://cs8.intsig.net/sync\", \"SAPI_FOREIGN\": \"...\", \"UAPI\": \"...\", ...}")
    print("     注意：包含所有可能用到的API baseUrl，不仅仅是当前工单需要的")
    print("   - api_pathname_mapping: ⚠️ 所有API的完整pathname映射（必须由AI通读代码生成）")
    print("     格式：{\"相对路径\": \"完整pathname\", ...}")
    print("     例如：{\"/revert_dir_list\": \"/sync/revert_dir_list\", \"/revert_pre_check\": \"/sync/revert_pre_check\", ...}")
    print("     注意：这是必须准确的信息，必须通过AI阅读完整项目后，综合配置信息、环境配置、打包配置给出")
    print("     不能使用简单的正则匹配，必须追踪代码逻辑，找到baseUrl的来源，然后组合完整pathname")
    print("   - field_extraction_rules: ⚠️ 字段提取规则映射（必须由AI通读代码生成）")
    print("     格式：{\"字段类型\": {\"用户输入模式\": \"实际字段名\", ...}, ...}")
    print("     例如：{\"user_id\": {\"用户ID\": \"user.id\", \"UserID\": \"user.id\", \"user_id\": \"user.id\"}, ...}")
    print("     注意：这是必须准确的信息，必须通过AI阅读完整项目后，了解项目中使用的字段命名规则")
    print("     不能使用简单的正则匹配，必须通读代码，了解字段的实际使用方式")
    print("   - service_name_mapping: ⚠️ 服务名称映射规则（必须由AI通读代码生成）")
    print("     格式：{\"用户输入模式\": \"实际service.name\", ...}")
    print("     例如：{\"用户服务\": \"user-service\", \"UserService\": \"user-service\", ...}")
    print("     注意：这是必须准确的信息，必须通过AI阅读完整项目后，了解项目中使用的服务名称")
    print("     不能使用简单的正则匹配，必须通读代码，了解服务的实际命名规则")
    print("   - signoz_env_vars: 所有SigNoz相关环境变量（字典格式，包含实际值）")
    print("   - fields: 项目中使用的所有字段列表（不仅仅是当前工单涉及的字段）")
    print("   - common_query_fields: 公共查询字段（适用于所有工单的常用字段）")
    print("   - service_names: 所有服务名称映射（从appName提取，包含所有可能的服务）")
    print("\n生成后，将结果保存到 .production-issue-analyzer/signoz_config.json")
    print("\n示例格式：")
    print("""
{
  "init_code_location": "src/libs/signoz.ts",
  "base_url": "https://api.example.com",
  "app_version": "1.0.17",
  "environment": "online",
  "api_baseurls": {
    "SAPI_DOMESTIC": "https://cs8.intsig.net/sync",
    "SAPI_FOREIGN": "https://cs8.intsig.net/sync",
    "VITE_SAPI_DOMESTIC": "https://cs8.intsig.net/sync",
    "VITE_SAPI_FOREIGN": "https://cs8.intsig.net/sync",
    "VITE_UAPI": "https://cs8.intsig.net/uapi",
    "VITE_OAPI": "https://cs8.intsig.net/oapi"
  },
  "api_pathname_mapping": {
    "/revert_dir_list": "/sync/revert_dir_list",
    "/revert_pre_check": "/sync/revert_pre_check",
    "/revert_pre_fix": "/sync/revert_pre_fix"
  },
  "field_extraction_rules": {
    "user_id": {
      "用户ID": "user.id",
      "UserID": "user.id",
      "user_id": "user.id",
      "userId": "user.id"
    },
    "client_id": {
      "设备ID": "user.client_id",
      "DeviceID": "user.client_id",
      "client_id": "user.client_id",
      "clientId": "user.client_id",
      "设备号": "user.client_id"
    }
  },
  "service_name_mapping": {
    "用户服务": "user-service",
    "UserService": "user-service",
    "用户": "user-service"
  },
  "signoz_env_vars": {
    "VITE_SIGNOZ_ENDPOINT": "https://signoz.example.com",
    "APP_VERSION": "1.0.17",
    "VITE_ENV": "online"
  },
  "fields": [
    "user.id",
    "user.client_id",
    "request.pathname",
    "geo.city_name"
  ],
  "common_query_fields": [
    "service.name",
    "body",
    "severity_text",
    "request.pathname"
  ],
  "service_names": {
    "cs.web.camscanner-toc": "cs.web.camscanner-toc"
  }
}
    """)
    
    # 返回None，表示需要AI生成
    return None


def scan_project_context(project_path: str, existing_context: Dict[str, Any], missing_fields: list) -> Dict[str, Any]:
    """
    通过脚本扫描补充项目上下文缺失信息
    
    注意：从整体项目视角扫描，包含所有可能用到的信息，不仅仅是当前工单需要的
    
    Args:
        project_path: 项目根目录路径
        existing_context: 现有的上下文数据
        missing_fields: 缺失的字段列表
    
    Returns:
        补充后的上下文数据
    """
    print(f"\n📊 扫描项目，补充缺失字段: {', '.join(missing_fields)}")
    print("   注意：从整体项目视角扫描，包含所有可能用到的信息")
    
    project_root = Path(project_path).resolve()
    updated_context = existing_context.copy()
    
    # 扫描服务列表（包含所有服务，不仅仅是当前工单涉及的）
    if 'services' in missing_fields:
        services = scan_services(project_root)
        updated_context['services'] = services
        print(f"  ✅ 发现 {len(services)} 个服务: {', '.join(services[:5])}{'...' if len(services) > 5 else ''}（包含所有服务）")
    
    # 扫描关键文件（包含所有关键文件）
    if 'key_files' in missing_fields:
        key_files = scan_key_files(project_root)
        updated_context['key_files'] = key_files
        print(f"  ✅ 发现 {len(key_files)} 个关键文件（包含所有关键文件）")
    
    # 扫描架构信息（整体项目架构）
    if 'architecture' in missing_fields:
        architecture = scan_architecture(project_root)
        updated_context['architecture'] = architecture
        print(f"  ✅ 架构信息: {architecture}（整体项目架构）")
    
    # 扫描技术栈（完整技术栈）
    if 'tech_stack' in missing_fields:
        tech_stack = scan_tech_stack(project_root)
        updated_context['tech_stack'] = tech_stack
        print(f"  ✅ 技术栈: {', '.join(tech_stack)}（完整技术栈）")
    
    return updated_context


def scan_signoz_config(project_path: str, existing_config: Dict[str, Any], missing_fields: list) -> Dict[str, Any]:
    """
    通过脚本扫描补充SigNoz配置缺失信息
    
    注意：此函数用于补充AI生成后仍缺失的字段，不是主要的数据来源
    AI应该先通读代码生成完整配置，脚本扫描只作为补充
    
    Args:
        project_path: 项目根目录路径
        existing_config: 现有的配置数据（AI生成后的）
        missing_fields: 缺失的字段列表
    
    Returns:
        补充后的配置数据
    """
    print(f"\n📊 扫描SigNoz配置，补充缺失字段: {', '.join(missing_fields)}")
    print("   注意：脚本扫描仅作为补充，主要配置应由AI通读代码生成")
    
    project_root = Path(project_path).resolve()
    updated_config = existing_config.copy()
    
    # 扫描环境变量和打包配置（仅当AI未生成时作为补充）
    if 'base_url' in missing_fields or 'signoz_env_vars' in missing_fields or 'app_version' in missing_fields or 'environment' in missing_fields:
        env_vars = scan_environment_variables(project_root)
        build_config = scan_build_config(project_root)
        
        # 扫描代码中环境变量的使用情况
        init_location = existing_config.get('init_code_location')
        signoz_init_file = None
        if init_location:
            signoz_init_file = project_root / init_location
        env_usage = scan_code_for_env_usage(project_root, signoz_init_file)
        
        # 提取baseurl和SigNoz相关配置
        if 'base_url' in missing_fields and 'base_url' not in updated_config:
            # 优先从环境变量获取
            base_url = env_vars.get('VITE_BASE_URL') or env_vars.get('REACT_APP_BASE_URL') or env_vars.get('BASE_URL') or env_vars.get('API_BASE_URL')
            if not base_url:
                # 从打包配置获取
                base_url = build_config.get('base_url') or build_config.get('public_path')
            if base_url:
                updated_config['base_url'] = base_url
                print(f"  ✅ 发现base_url: {base_url}")
        
        # 提取API baseUrl配置（用于接口路径识别）
        # 注意：从整体项目视角提取所有API baseUrl，不仅仅是当前工单需要的
        if 'api_baseurls' in missing_fields and 'api_baseurls' not in updated_config:
            api_baseurls = {}
            # 从环境变量中提取所有API相关的baseUrl（包含所有可能用到的）
            for key, value in env_vars.items():
                if any(prefix in key.upper() for prefix in ['SAPI', 'UAPI', 'OAPI', 'WSAPI', 'DAPI', 'PAPI', 'TAPI', 'API_']):
                    api_baseurls[key] = value
            # 从代码使用情况中提取
            for key, usage_info in env_usage.items():
                if any(prefix in key.upper() for prefix in ['SAPI', 'UAPI', 'OAPI', 'WSAPI', 'DAPI', 'PAPI', 'TAPI', 'API_']):
                    actual_value = usage_info.get('actual_value')
                    if actual_value:
                        api_baseurls[key] = actual_value
            if api_baseurls:
                updated_config['api_baseurls'] = api_baseurls
                print(f"  ✅ 发现API baseUrl配置: {len(api_baseurls)} 个（包含所有API类型）")
        
        # 提取appVersion（从环境变量获取实际值）
        if 'app_version' in missing_fields and 'app_version' not in updated_config:
            # 从环境变量使用情况中获取
            if 'APP_VERSION' in env_usage:
                app_version = env_usage['APP_VERSION'].get('actual_value')
            else:
                # 直接从环境变量文件获取
                app_version = env_vars.get('APP_VERSION') or env_vars.get('VITE_APP_VERSION')
            if app_version:
                updated_config['app_version'] = app_version
                print(f"  ✅ 发现app_version: {app_version}")
        
        # 提取environment（从环境变量获取实际值）
        if 'environment' in missing_fields and 'environment' not in updated_config:
            # 从环境变量使用情况中获取
            if 'VITE_ENV' in env_usage:
                environment = env_usage['VITE_ENV'].get('actual_value')
            elif 'ENV' in env_usage:
                environment = env_usage['ENV'].get('actual_value')
            else:
                # 直接从环境变量文件获取
                environment = env_vars.get('VITE_ENV') or env_vars.get('NODE_ENV') or env_vars.get('ENV')
            if environment:
                updated_config['environment'] = environment
                print(f"  ✅ 发现environment: {environment}")
        
        # 提取SigNoz相关环境变量
        if 'signoz_env_vars' in missing_fields and 'signoz_env_vars' not in updated_config:
            signoz_env_vars = {}
            # 从环境变量文件中提取
            for key, value in env_vars.items():
                if 'signoz' in key.lower() or 'SIGNOZ' in key:
                    signoz_env_vars[key] = value
            # 从代码使用情况中提取
            for key, usage_info in env_usage.items():
                if 'signoz' in key.lower() or 'SIGNOZ' in key:
                    signoz_env_vars[key] = usage_info.get('actual_value', '')
            if signoz_env_vars:
                updated_config['signoz_env_vars'] = signoz_env_vars
                print(f"  ✅ 发现SigNoz环境变量: {', '.join(signoz_env_vars.keys())}")
    
    # 扫描SigNoz初始化代码位置（仅当AI未生成时作为补充）
    if 'init_code_location' in missing_fields:
        init_location = scan_signoz_init_code(project_root)
        if init_location:
            updated_config['init_code_location'] = init_location
            print(f"  ✅ SigNoz初始化代码位置: {init_location}")
        else:
            print(f"  ⚠️  未找到SigNoz初始化代码")
    
    # 扫描字段（仅当AI未生成时作为补充）
    # 注意：从整体项目视角提取所有字段，不仅仅是当前工单涉及的
    if 'fields' in missing_fields:
        fields = scan_signoz_fields(project_root, updated_config.get('init_code_location'))
        if fields:
            updated_config['fields'] = fields
            print(f"  ✅ 发现 {len(fields)} 个字段（包含项目中使用的所有字段）")
    
    # 扫描公共查询字段（仅当AI未生成时作为补充）
    # 注意：公共查询字段适用于所有工单
    if 'common_query_fields' in missing_fields:
        common_fields = scan_common_query_fields(project_root)
        if common_fields:
            updated_config['common_query_fields'] = common_fields
            print(f"  ✅ 公共查询字段: {', '.join(common_fields)}（适用于所有工单）")
    
    # 扫描服务名称（仅当AI未生成时作为补充）
    # 注意：从整体项目视角提取所有服务，不仅仅是当前工单涉及的
    if 'service_names' in missing_fields:
        service_names = scan_service_names(project_root)
        if service_names:
            updated_config['service_names'] = service_names
            print(f"  ✅ 服务名称映射: {len(service_names)} 个服务（包含所有可能的服务）")
    
    return updated_config


def scan_services(project_root: Path) -> list:
    """扫描服务列表"""
    services = []
    
    # 优先从SigNoz配置中提取服务名
    signoz_init_code = scan_signoz_init_code(project_root)
    if signoz_init_code:
        init_file = project_root / signoz_init_code
        if init_file.exists():
            try:
                content = init_file.read_text(encoding='utf-8')
                import re
                # 查找appName配置（这就是service.name的值）
                app_name_match = re.search(r'appName\s*[:=]\s*["\']([^"\']+)["\']', content)
                if app_name_match:
                    app_name = app_name_match.group(1)
                    services.append(app_name)
                    return services
            except Exception:
                pass
    
    # 如果没找到，从docker-compose文件提取服务名
    docker_compose_files = [
        project_root / 'docker-compose.yml',
        project_root / 'docker-compose.yaml'
    ]
    
    for compose_file in docker_compose_files:
        if compose_file.exists():
            try:
                import yaml
                with open(compose_file, 'r', encoding='utf-8') as f:
                    compose_data = yaml.safe_load(f)
                    if 'services' in compose_data:
                        for service_name in compose_data['services'].keys():
                            if service_name not in services:
                                services.append(service_name)
            except Exception:
                pass
    
    # 如果还没找到，尝试从package.json获取
    if not services:
        package_json = project_root / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    package_name = package_data.get('name', '')
                    if package_name:
                        services.append(package_name)
            except Exception:
                pass
    
    return services if services else []


def scan_key_files(project_root: Path) -> list:
    """扫描关键文件"""
    key_files = []
    
    # 查找常见的关键文件
    key_file_patterns = [
        'main.py',
        'app.py',
        'index.js',
        'server.js',
        'package.json',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml'
    ]
    
    for pattern in key_file_patterns:
        for file_path in project_root.rglob(pattern):
            rel_path = str(file_path.relative_to(project_root))
            if rel_path not in key_files:
                key_files.append(rel_path)
    
    return key_files[:20]  # 限制数量


def scan_architecture(project_root: Path) -> str:
    """扫描架构信息"""
    # 检查是否有docker-compose文件
    if (project_root / 'docker-compose.yml').exists() or (project_root / 'docker-compose.yaml').exists():
        return "容器化部署架构"
    
    # 检查是否有k8s配置
    if (project_root / 'k8s').exists():
        return "Kubernetes部署架构"
    
    # 检查是否有微服务目录结构
    if (project_root / 'services').exists():
        return "微服务架构"
    
    return "单体应用架构"


def scan_tech_stack(project_root: Path) -> list:
    """扫描技术栈"""
    tech_stack = []
    
    # 检查Python
    if (project_root / 'requirements.txt').exists() or (project_root / 'pyproject.toml').exists():
        tech_stack.append('Python')
    
    # 检查Node.js
    if (project_root / 'package.json').exists():
        tech_stack.append('Node.js')
    
    # 检查Java
    if (project_root / 'pom.xml').exists() or (project_root / 'build.gradle').exists():
        tech_stack.append('Java')
    
    # 检查Go
    if (project_root / 'go.mod').exists():
        tech_stack.append('Go')
    
    return tech_stack if tech_stack else ['Unknown']


def scan_signoz_init_code(project_root: Path) -> Optional[str]:
    """扫描SigNoz初始化代码位置"""
    # 优先查找常见位置的signoz初始化文件
    priority_paths = [
        'src/libs/signoz.ts',
        'src/libs/signoz.js',
        'src/config/signoz.ts',
        'src/config/signoz.js',
        'src/utils/signoz.ts',
        'src/utils/signoz.js',
        'libs/signoz.ts',
        'libs/signoz.js',
        'config/signoz.ts',
        'config/signoz.js',
        'utils/signoz.ts',
        'utils/signoz.js'
    ]
    
    # 先检查优先路径
    for priority_path in priority_paths:
        file_path = project_root / priority_path
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                # 检查是否包含signoz初始化代码（import signoz 或 from '@ccint/signoz'）
                if 'signoz' in content.lower() and ('import' in content or 'from' in content):
                    return priority_path
            except Exception:
                continue
    
    # 如果优先路径没找到，再全局搜索
    signoz_patterns = [
        '**/*signoz*.ts',
        '**/*signoz*.js',
        '**/libs/*signoz*.ts',
        '**/libs/*signoz*.js',
        '**/config/*signoz*.ts',
        '**/config/*signoz*.js'
    ]
    
    for pattern in signoz_patterns:
        for file_path in project_root.rglob(pattern):
            try:
                content = file_path.read_text(encoding='utf-8')
                # 检查是否包含signoz初始化代码
                if 'signoz' in content.lower() and ('import' in content or 'from' in content or '@ccint/signoz' in content):
                    rel_path = str(file_path.relative_to(project_root))
                    return rel_path
            except Exception:
                continue
    
    return None


def scan_environment_variables(project_root: Path) -> Dict[str, str]:
    """
    扫描环境变量配置文件
    
    扫描所有环境变量文件，提取环境变量的实际值
    包括：.env, .env.local, .env.development, .env.production等
    """
    env_vars = {}
    
    # 查找环境变量文件（按优先级排序）
    env_files = [
        '.env.production',  # 生产环境优先
        '.env.staging',
        '.env.development',
        '.env.local',
        '.env.test',
        '.env'
    ]
    
    for env_file_name in env_files:
        env_file = project_root / env_file_name
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # 跳过注释和空行
                        if not line or line.startswith('#'):
                            continue
                        # 解析 KEY=VALUE 格式
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            # 如果key已存在，不覆盖（优先使用高优先级文件的值）
                            if key not in env_vars:
                                env_vars[key] = value
            except Exception:
                continue
    
    return env_vars


def scan_code_for_env_usage(project_root: Path, signoz_init_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    扫描代码中环境变量的使用情况
    
    查找代码中使用的环境变量（如import.meta.env.VITE_XXX, process.env.XXX等）
    并尝试从打包配置中获取实际值（优先），如果打包配置中没有，才从环境变量文件获取（后备）
    
    ⚠️ 重要：环境变量的值应该从打包配置中获取，而不是直接从.env文件读取
    """
    env_usage = {}
    # 优先从打包配置中获取环境变量
    build_config = scan_build_config(project_root)
    env_vars_from_build = build_config.get('env_vars', {})
    # 如果打包配置中没有，才从.env文件读取（作为后备）
    env_vars = scan_environment_variables(project_root)
    # 合并：优先使用打包配置中的值
    for key, value in env_vars_from_build.items():
        env_vars[key] = value
    
    # 如果提供了signoz初始化文件，优先扫描该文件
    files_to_scan = []
    if signoz_init_file and signoz_init_file.exists():
        files_to_scan.append(signoz_init_file)
    else:
        # 否则扫描常见的signoz初始化文件位置
        signoz_patterns = [
            '**/signoz*.ts',
            '**/signoz*.js',
            '**/libs/signoz*.ts',
            '**/libs/signoz*.js'
        ]
        for pattern in signoz_patterns:
            for file_path in project_root.rglob(pattern):
                if file_path.is_file():
                    files_to_scan.append(file_path)
                    break
    
    import re
    
    for file_path in files_to_scan[:5]:  # 限制扫描文件数量
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 查找 import.meta.env.XXX 模式
            import_meta_pattern = r'import\.meta\.env\.([A-Z_][A-Z0-9_]*)'
            matches = re.findall(import_meta_pattern, content)
            for env_key in matches:
                # 尝试从环境变量文件中获取值
                # Vite环境变量需要VITE_前缀
                vite_key = f'VITE_{env_key}' if not env_key.startswith('VITE_') else env_key
                actual_value = env_vars.get(vite_key) or env_vars.get(env_key)
                if actual_value:
                    env_usage[env_key] = {
                        'source': 'import.meta.env',
                        'env_key': vite_key,
                        'actual_value': actual_value,
                        'file': str(file_path.relative_to(project_root))
                    }
            
            # 查找 process.env.XXX 模式
            process_env_pattern = r'process\.env\.([A-Z_][A-Z0-9_]*)'
            matches = re.findall(process_env_pattern, content)
            for env_key in matches:
                actual_value = env_vars.get(env_key)
                if actual_value:
                    env_usage[env_key] = {
                        'source': 'process.env',
                        'env_key': env_key,
                        'actual_value': actual_value,
                        'file': str(file_path.relative_to(project_root))
                    }
        except Exception:
            continue
    
    return env_usage


def trace_api_pathname_from_code(project_root: Path, api_call_text: str) -> Optional[Dict[str, Any]]:
    """
    从代码调用位置追踪pathname和baseurl
    
    流程：
    1. 从代码调用位置识别pathname（如 .post('/revert_dir_list', ...)）
    2. 追踪createRequest等方法，找到baseUrl的来源
    3. 从config中查找baseUrl配置
    4. 识别环境变量引用（如import.meta.env.XXX）
    5. 从环境配置文件中读取实际值
    6. 结合baseurl和pathname生成完整路径
    
    Args:
        project_root: 项目根目录
        api_call_text: 包含API调用的代码文本
    
    Returns:
        包含pathname, baseurl, full_path等信息的字典
    """
    import re
    from urllib.parse import urlparse
    
    result = {
        'pathname': None,
        'baseurl': None,
        'full_path': None,
        'trace_steps': []
    }
    
    # 步骤1：从代码调用位置识别pathname
    # 匹配模式：.post('/path', ...) 或 .get('/path', ...) 等
    api_call_patterns = [
        r'\.(?:post|get|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        r'\.(?:post|get|put|delete|patch)\s*\(\s*`([^`]+)`',
        r'\.(?:post|get|put|delete|patch)\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*["\']([^"\']+)["\']',  # createRequest(api).post(pathname)
    ]
    
    pathname = None
    api_type = None
    
    for pattern in api_call_patterns:
        match = re.search(pattern, api_call_text)
        if match:
            # 如果是第三个模式，可能有api类型和pathname
            if len(match.groups()) > 1:
                api_type = match.group(1)
                pathname = match.group(2)
            else:
                pathname = match.group(1)
            
            if pathname and pathname.startswith('/'):
                result['pathname'] = pathname
                result['trace_steps'].append(f"步骤1: 从代码调用位置识别pathname: {pathname}")
                break
    
    if not pathname:
        return None
    
    # 步骤2：查找createRequest方法（如果存在）
    # 查找createRequest的定义
    create_request_pattern = r'createRequest\s*=\s*\([^)]+\)\s*=>'
    if re.search(create_request_pattern, api_call_text):
        result['trace_steps'].append("步骤2: 发现createRequest方法调用")
    
    # 步骤3：查找config中的baseUrl配置
    # 这里需要AI通读代码来查找，脚本只能提供辅助
    # 查找常见的config模式
    config_patterns = [
        r'config\.api\[[^\]]+\]',
        r'config\.api\.([A-Z_][A-Z0-9_]*)',
        r'get\s+([A-Z_][A-Z0-9_]*)\s*\([^)]*\)\s*\{[^}]*import\.meta\.env\.([A-Z_][A-Z0-9_]*)',
    ]
    
    env_var_ref = None
    for pattern in config_patterns:
        match = re.search(pattern, api_call_text)
        if match:
            if len(match.groups()) >= 2:
                env_var_ref = match.group(2)
            elif len(match.groups()) == 1:
                # 可能需要进一步查找
                pass
            break
    
    # 步骤4-5：从环境变量文件读取实际值
    if env_var_ref:
        result['trace_steps'].append(f"步骤3-4: 发现环境变量引用: {env_var_ref}")
        env_vars = scan_environment_variables(project_root)
        
        # 尝试多种可能的key名称
        possible_keys = [
            env_var_ref,
            f'VITE_{env_var_ref}',
            env_var_ref.replace('VITE_', ''),
        ]
        
        for key in possible_keys:
            if key in env_vars:
                baseurl = env_vars[key]
                result['baseurl'] = baseurl
                result['trace_steps'].append(f"步骤5: 从环境变量文件读取baseurl: {baseurl}")
                break
    
    # 步骤6：组合完整路径
    if pathname and result.get('baseurl'):
        baseurl = result['baseurl']
        # 解析baseurl，提取路径部分
        try:
            parsed = urlparse(baseurl)
            base_path = parsed.path  # 如 /sync
            # 组合完整路径
            if base_path and base_path != '/':
                # baseurl包含路径前缀
                full_path = base_path.rstrip('/') + pathname
            else:
                # baseurl只是域名，pathname就是完整路径
                full_path = pathname
            result['full_path'] = full_path
            result['trace_steps'].append(f"步骤6: 组合完整路径: {full_path}")
        except Exception:
            result['full_path'] = pathname
    
    return result if result.get('pathname') else None


def scan_build_config(project_root: Path) -> Dict[str, Any]:
    """
    扫描打包配置文件（vite.config, webpack.config等）
    
    重要：环境变量的值应该从打包配置中获取，而不是直接从.env文件读取
    打包配置会使用loadEnv等方法加载.env文件，并在构建时处理环境变量
    """
    build_config = {}
    env_vars_from_build = {}  # 从打包配置中获取的环境变量
    
    # 查找vite.config文件
    vite_config_files = [
        'vite.config.ts',
        'vite.config.js',
        'vite.config.mjs',
        'vite.config.cjs'
    ]
    
    for config_file_name in vite_config_files:
        config_file = project_root / config_file_name
        if config_file.exists():
            try:
                content = config_file.read_text(encoding='utf-8')
                import re
                
                # 查找base URL配置
                base_match = re.search(r'base\s*[:=]\s*["\']([^"\']+)["\']', content)
                if base_match:
                    build_config['base_url'] = base_match.group(1)
                
                # 查找loadEnv调用（Vite加载环境变量的方式）
                # loadEnv(mode, process.cwd(), '') 或 loadEnv(mode, root, prefix)
                load_env_patterns = [
                    r'loadEnv\s*\(\s*["\']?(\w+)["\']?\s*,\s*[^,]+,\s*["\']?([^"\']*)["\']?\s*\)',  # loadEnv(mode, root, prefix)
                    r'loadEnv\s*\(\s*["\']?(\w+)["\']?\s*,\s*[^,]+\)',  # loadEnv(mode, root)
                ]
                
                for pattern in load_env_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        for match in matches:
                            if isinstance(match, tuple):
                                mode = match[0] if match[0] else 'production'
                                prefix = match[1] if len(match) > 1 and match[1] else 'VITE_'
                            else:
                                mode = match if match else 'production'
                                prefix = 'VITE_'
                            
                            # 根据mode和prefix加载环境变量
                            # Vite的loadEnv会按优先级加载：.env.[mode].local > .env.[mode] > .env.local > .env
                            env_files_priority = [
                                f'.env.{mode}.local',
                                f'.env.{mode}',
                                '.env.local',
                                '.env'
                            ]
                            
                            # 从环境文件中读取，但只读取符合prefix的变量
                            for env_file_name in env_files_priority:
                                env_file = project_root / env_file_name
                                if env_file.exists():
                                    try:
                                        with open(env_file, 'r', encoding='utf-8') as f:
                                            for line in f:
                                                line = line.strip()
                                                if not line or line.startswith('#'):
                                                    continue
                                                if '=' in line:
                                                    key, value = line.split('=', 1)
                                                    key = key.strip()
                                                    value = value.strip().strip('"').strip("'")
                                                    # 只加载符合prefix的变量（Vite默认只暴露VITE_前缀的变量）
                                                    if key.startswith(prefix):
                                                        # 如果key已存在，不覆盖（优先使用高优先级文件的值）
                                                        if key not in env_vars_from_build:
                                                            env_vars_from_build[key] = value
                                    except Exception:
                                        continue
                            
                            build_config['load_env_mode'] = mode
                            build_config['load_env_prefix'] = prefix
                            break
                
                # 查找define配置（可能直接定义环境变量）
                # define: { 'import.meta.env.XXX': JSON.stringify('value') }
                define_pattern = r'define\s*:\s*\{([^}]+)\}'
                define_match = re.search(define_pattern, content, re.DOTALL)
                if define_match:
                    define_content = define_match.group(1)
                    # 查找 import.meta.env.XXX: JSON.stringify('value')
                    env_define_pattern = r'["\']import\.meta\.env\.([A-Z_][A-Z0-9_]*)["\']\s*:\s*JSON\.stringify\(["\']([^"\']+)["\']\)'
                    env_defines = re.findall(env_define_pattern, define_content)
                    for env_key, env_value in env_defines:
                        vite_key = f'VITE_{env_key}' if not env_key.startswith('VITE_') else env_key
                        if vite_key not in env_vars_from_build:
                            env_vars_from_build[vite_key] = env_value
                
                # 查找envPrefix配置（环境变量前缀）
                env_prefix_match = re.search(r'envPrefix\s*[:=]\s*["\']([^"\']+)["\']', content)
                if env_prefix_match:
                    build_config['env_prefix'] = env_prefix_match.group(1)
                
                # 查找环境变量引用
                env_refs = re.findall(r'process\.env\.(\w+)|import\.meta\.env\.(\w+)', content)
                for match in env_refs:
                    env_key = match[0] or match[1]
                    if env_key:
                        build_config.setdefault('env_refs', []).append(env_key)
            except Exception:
                continue
    
    # 如果从打包配置中获取到了环境变量，使用它们
    if env_vars_from_build:
        build_config['env_vars'] = env_vars_from_build
    
    # 查找webpack.config文件
    webpack_config_files = [
        'webpack.config.js',
        'webpack.config.ts',
        'webpack.prod.js',
        'webpack.dev.js'
    ]
    
    for config_file_name in webpack_config_files:
        config_file = project_root / config_file_name
        if config_file.exists():
            try:
                content = config_file.read_text(encoding='utf-8')
                import re
                # 查找publicPath配置
                public_path_match = re.search(r'publicPath\s*[:=]\s*["\']([^"\']+)["\']', content)
                if public_path_match:
                    build_config['public_path'] = public_path_match.group(1)
                
                # Webpack可能使用DefinePlugin定义环境变量
                # new webpack.DefinePlugin({ 'process.env.XXX': JSON.stringify('value') })
                define_plugin_pattern = r'DefinePlugin\s*\(\s*\{([^}]+)\}\)'
                define_plugin_match = re.search(define_plugin_pattern, content, re.DOTALL)
                if define_plugin_match:
                    plugin_content = define_plugin_match.group(1)
                    # 查找 process.env.XXX: JSON.stringify('value')
                    env_define_pattern = r'["\']process\.env\.([A-Z_][A-Z0-9_]*)["\']\s*:\s*JSON\.stringify\(["\']([^"\']+)["\']\)'
                    env_defines = re.findall(env_define_pattern, plugin_content)
                    for env_key, env_value in env_defines:
                        if env_key not in env_vars_from_build:
                            env_vars_from_build[env_key] = env_value
            except Exception:
                continue
    
    # 如果从打包配置中获取到了环境变量，更新build_config
    if env_vars_from_build:
        build_config['env_vars'] = env_vars_from_build
    
    return build_config


def scan_signoz_fields(project_root: Path, init_code_location: Optional[str]) -> list:
    """扫描SigNoz字段"""
    fields = []
    
    if init_code_location:
        init_file = project_root / init_code_location
        if init_file.exists():
            try:
                content = init_file.read_text(encoding='utf-8')
                import re
                
                # 从@ccint/signoz初始化代码中提取字段
                # 查找signoz({...})中的配置项
                signoz_config_match = re.search(r'signoz\s*\(\s*\{([^}]+)\}', content, re.DOTALL)
                if signoz_config_match:
                    config_content = signoz_config_match.group(1)
                    # 提取配置项名称（如appName, appVersion, env等）
                    config_patterns = [
                        r'(\w+)\s*[:=]',  # 配置项名称
                        r'["\'](\w+)["\']\s*[:=]'  # 字符串配置项
                    ]
                    for pattern in config_patterns:
                        matches = re.findall(pattern, config_content)
                        fields.extend(matches)
                
                # 查找logError, logInfo等函数调用，可能包含字段信息
                log_function_patterns = [
                    r'log(Error|Info|Warn|Debug)\s*\([^)]*["\']([^"\']+)["\']',
                    r'log(Error|Info|Warn|Debug)\s*\(\s*\{[^}]*(\w+)\s*[:=]'
                ]
                for pattern in log_function_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple):
                            fields.extend(match)
                        else:
                            fields.append(match)
            except Exception as e:
                # 如果解析失败，返回空列表
                pass
    
    # 去重并返回
    return list(set(fields))[:20]  # 限制数量


def scan_common_query_fields(project_root: Path) -> list:
    """扫描公共查询字段"""
    # 使用signoz_schema模块的默认字段
    try:
        from signoz_schema import DEFAULT_QUERY_FIELDS
        return DEFAULT_QUERY_FIELDS
    except ImportError:
        # 如果模块不存在，返回基本字段
        return [
            'service.name',
            'body',
            'severity_text',
            'timestamp',
            'trace_id',
            'span_id'
        ]


def scan_service_names(project_root: Path) -> Dict[str, str]:
    """扫描服务名称映射"""
    service_names = {}
    
    # 优先从SigNoz初始化代码中提取appName
    signoz_init_code = scan_signoz_init_code(project_root)
    if signoz_init_code:
        init_file = project_root / signoz_init_code
        if init_file.exists():
            try:
                content = init_file.read_text(encoding='utf-8')
                import re
                # 查找appName配置
                app_name_match = re.search(r'appName\s*[:=]\s*["\']([^"\']+)["\']', content)
                if app_name_match:
                    app_name = app_name_match.group(1)
                    # appName就是service.name的值
                    service_names[app_name] = app_name
                    return service_names
            except Exception:
                pass
    
    # 如果没找到，从docker-compose文件提取服务名
    docker_compose_files = [
        project_root / 'docker-compose.yml',
        project_root / 'docker-compose.yaml'
    ]
    
    for compose_file in docker_compose_files:
        if compose_file.exists():
            try:
                import yaml
                with open(compose_file, 'r', encoding='utf-8') as f:
                    compose_data = yaml.safe_load(f)
                    if 'services' in compose_data:
                        for service_name in compose_data['services'].keys():
                            service_names[service_name] = service_name
            except Exception:
                pass
    
    # 如果都没找到，尝试从package.json获取项目名
    package_json = project_root / 'package.json'
    if package_json.exists() and not service_names:
        try:
            import json
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                package_name = package_data.get('name', '')
                if package_name:
                    # 尝试推断服务名（可能需要根据实际项目调整）
                    service_names[package_name] = package_name
        except Exception:
            pass
    
    return service_names if service_names else {}


def init_phase_0(project_path: str, skip_if_complete: bool = False) -> Tuple[bool, bool]:
    """
    阶段0主函数：检查并初始化项目上下文和SigNoz配置
    
    工作流程：
    1. 如果文件不存在（首次使用）：
       - 优先：通过AI通读项目代码生成完整配置
       - 补充：AI生成后如果仍有缺失，用脚本扫描补充
    2. 如果文件存在但不完整：
       - 优先：用脚本扫描补充缺失字段
       - 补充：如果脚本无法补充完整，再提示AI生成
    
    Args:
        project_path: 项目根目录路径
        skip_if_complete: 如果信息完整是否跳过（默认False）
    
    Returns:
        (项目上下文是否完整, SigNoz配置是否完整)
    """
    print("\n" + "="*60)
    print("📋 阶段0：首次使用检查")
    print("="*60)
    
    analyzer_dir = get_analyzer_dir(project_path)
    
    # 检查项目上下文
    context_exists, context_data, context_missing = check_project_context(project_path)
    
    if not context_exists:
        print("\n📝 项目上下文文件不存在（首次使用）")
        print("   需要通过AI通读项目代码生成项目上下文")
        print("\n⚠️  重要：项目上下文是从整体项目视角生成的，不是针对特定工单")
        print("   这个配置是全局的、可复用的，适用于所有工单分析")
        print("\n" + "="*60)
        print("🤖 请执行以下操作：")
        print("="*60)
        print("1. 让AI通读整个项目代码，从整体项目视角了解：")
        print("   - 项目整体架构和设计")
        print("   - 所有服务的完整列表（不仅仅是当前工单涉及的服务）")
        print("   - 所有关键文件和目录结构")
        print("   - 完整的技术栈信息")
        print("   - 项目的部署方式和运行环境")
        print("   - 项目的业务领域和主要功能模块")
        print("2. 分析项目结构、服务、技术栈等信息")
        print("3. 生成完整的项目上下文配置（包含所有可能用到的信息）")
        print("\n生成后，将结果保存到:", analyzer_dir / PROJECT_CONTEXT_FILE)
        print("\n示例格式：")
        print("""
{
  "services": ["service1", "service2"],
  "key_files": ["src/main.py", "config/app.yaml"],
  "architecture": "微服务架构",
  "tech_stack": ["Python", "Flask", "PostgreSQL"]
}
        """)
        generate_project_context_with_ai(project_path)
        # 等待AI生成后，检查是否已创建
        context_exists, context_data, context_missing = check_project_context(project_path)
        if context_exists:
            if context_missing:
                print(f"\n⚠️  AI生成的项目上下文信息不全，缺失字段: {', '.join(context_missing)}")
                print("   正在通过脚本扫描补充缺失信息...")
                # 用脚本扫描补充缺失字段
                updated_context = scan_project_context(project_path, context_data, context_missing)
                context_file = analyzer_dir / PROJECT_CONTEXT_FILE
                if save_json_file(context_file, updated_context):
                    print(f"✅ 项目上下文已补充: {context_file}")
                # 再次检查
                _, _, still_missing = check_project_context(project_path)
                context_complete = len(still_missing) == 0
            else:
                print("✅ 项目上下文信息完整")
                context_complete = True
        else:
            print("⚠️  项目上下文文件仍未生成，请确保AI已完成生成")
            context_complete = False
    elif context_missing:
        print(f"\n⚠️  项目上下文信息不全，缺失字段: {', '.join(context_missing)}")
        if context_data:
            # 通过脚本扫描补充
            updated_context = scan_project_context(project_path, context_data, context_missing)
            context_file = analyzer_dir / PROJECT_CONTEXT_FILE
            if save_json_file(context_file, updated_context):
                print(f"✅ 项目上下文已更新: {context_file}")
            context_complete = len(context_missing) == 0
        else:
            context_complete = False
    else:
        print("✅ 项目上下文信息完整")
        context_complete = True
        # 如果信息完整且skip_if_complete为True，可以跳过后续检查
        if skip_if_complete and context_complete:
            # 快速检查SigNoz配置
            config_exists, _, config_missing = check_signoz_config(project_path)
            if config_exists and len(config_missing) == 0:
                print("✅ SigNoz配置信息完整")
                return context_complete, True
    
    # 检查SigNoz配置
    config_exists, config_data, config_missing = check_signoz_config(project_path)
    
    if not config_exists:
        print("\n📝 SigNoz配置文件不存在（首次使用）")
        print("   需要通过AI通读项目代码生成SigNoz配置")
        print("\n⚠️  重要：SigNoz配置是从整体项目视角生成的，不是针对特定工单")
        print("   这个配置是全局的、可复用的，适用于所有工单分析")
        print("\n" + "="*60)
        print("🤖 请执行以下操作：")
        print("="*60)
        print("1. 让AI通读整个项目代码，从整体项目视角查找以下信息：")
        print("   a. SigNoz初始化代码位置（通常在 src/libs/signoz.ts 等位置）")
        print("   b. 从环境变量文件（.env, .env.local, .env.production等）中提取：")
        print("      - base_url: API基础URL（从VITE_BASE_URL, REACT_APP_BASE_URL, BASE_URL等）")
        print("      - SigNoz相关环境变量（如SIGNOZ_ENDPOINT等）")
        print("   c. 从打包配置文件（vite.config.ts/js, webpack.config.js等）中提取：")
        print("      - base_url: 从base或publicPath配置中提取")
        print("   d. 从SigNoz初始化代码中提取：")
        print("      - appName: 服务名称（这就是service.name的值）")
        print("      - 其他配置项（appVersion, env等）")
        print("2. 分析SigNoz配置，提取以下信息：")
        print("   - init_code_location: SigNoz初始化代码位置")
        print("   - base_url: API基础URL（用于组合完整接口路径）")
        print("   - signoz_env_vars: SigNoz相关环境变量（字典格式）")
        print("   - fields: 项目使用的字段列表")
        print("   - common_query_fields: 公共查询字段")
        print("   - service_names: 服务名称映射（从appName提取）")
        print("\n生成后，将结果保存到:", analyzer_dir / SIGNOZ_CONFIG_FILE)
        print("\n示例格式：")
        print("""
{
  "init_code_location": "src/libs/signoz.ts",
  "base_url": "https://api.example.com",
  "signoz_env_vars": {
    "VITE_SIGNOZ_ENDPOINT": "https://signoz.example.com"
  },
  "fields": ["user.id", "user.client_id", "request.pathname"],
  "common_query_fields": ["service.name", "body", "severity_text"],
  "service_names": {
    "cs.web.camscanner-toc": "cs.web.camscanner-toc"
  }
}
        """)
        generate_signoz_config_with_ai(project_path)
        # 等待AI生成后，检查是否已创建
        config_exists, config_data, config_missing = check_signoz_config(project_path)
        if config_exists:
            if config_missing:
                print(f"\n⚠️  AI生成的SigNoz配置信息不全，缺失字段: {', '.join(config_missing)}")
                print("   正在通过脚本扫描补充缺失信息...")
                # 用脚本扫描补充缺失字段（仅作为补充，不是主要数据来源）
                updated_config = scan_signoz_config(project_path, config_data, config_missing)
                config_file = analyzer_dir / SIGNOZ_CONFIG_FILE
                if save_json_file(config_file, updated_config):
                    print(f"✅ SigNoz配置已补充: {config_file}")
                # 再次检查
                _, _, still_missing = check_signoz_config(project_path)
                config_complete = len(still_missing) == 0
                if still_missing:
                    print(f"⚠️  仍有缺失字段: {', '.join(still_missing)}")
                    print("   请确保AI已通读代码并生成完整配置")
            else:
                print("✅ SigNoz配置信息完整")
                config_complete = True
        else:
            print("⚠️  SigNoz配置文件仍未生成，请确保AI已完成生成")
            config_complete = False
    elif config_missing:
        print(f"\n⚠️  SigNoz配置信息不全，缺失字段: {', '.join(config_missing)}")
        if config_data:
            # 通过脚本扫描补充
            updated_config = scan_signoz_config(project_path, config_data, config_missing)
            config_file = analyzer_dir / SIGNOZ_CONFIG_FILE
            if save_json_file(config_file, updated_config):
                print(f"✅ SigNoz配置已更新: {config_file}")
            # 再次检查是否完整
            _, _, still_missing = check_signoz_config(project_path)
            config_complete = len(still_missing) == 0
            if still_missing:
                print(f"⚠️  仍有缺失字段: {', '.join(still_missing)}")
                print("   需要通过AI通读项目补充完整信息")
                generate_signoz_config_with_ai(project_path)
        else:
            config_complete = False
    else:
        print("✅ SigNoz配置信息完整")
        config_complete = True
    
    print("\n" + "="*60)
    
    return context_complete, config_complete
