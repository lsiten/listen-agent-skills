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
    print("\n请执行以下操作：")
    print("1. 让AI查找项目中的SigNoz初始化代码")
    print("2. 分析SigNoz配置，提取以下信息：")
    print("   - init_code_location: SigNoz初始化代码位置")
    print("   - fields: 项目字段列表")
    print("   - common_query_fields: 公共查询字段")
    print("   - service_names: 服务名称映射")
    print("\n生成后，将结果保存到 .production-issue-analyzer/signoz_config.json")
    print("\n示例格式：")
    print("""
{
  "init_code_location": "src/utils/signoz.py",
  "fields": [
    "user_id",
    "request_id",
    "api_path",
    "error_code"
  ],
  "common_query_fields": [
    "service.name",
    "body",
    "severity_text"
  ],
  "service_names": {
    "user-service": "user-service",
    "api-gateway": "api-gateway"
  }
}
    """)
    
    # 返回None，表示需要AI生成
    return None


def scan_project_context(project_path: str, existing_context: Dict[str, Any], missing_fields: list) -> Dict[str, Any]:
    """
    通过脚本扫描补充项目上下文缺失信息
    
    Args:
        project_path: 项目根目录路径
        existing_context: 现有的上下文数据
        missing_fields: 缺失的字段列表
    
    Returns:
        补充后的上下文数据
    """
    print(f"\n📊 扫描项目，补充缺失字段: {', '.join(missing_fields)}")
    
    project_root = Path(project_path).resolve()
    updated_context = existing_context.copy()
    
    # 扫描服务列表
    if 'services' in missing_fields:
        services = scan_services(project_root)
        updated_context['services'] = services
        print(f"  ✅ 发现 {len(services)} 个服务: {', '.join(services[:5])}...")
    
    # 扫描关键文件
    if 'key_files' in missing_fields:
        key_files = scan_key_files(project_root)
        updated_context['key_files'] = key_files
        print(f"  ✅ 发现 {len(key_files)} 个关键文件")
    
    # 扫描架构信息
    if 'architecture' in missing_fields:
        architecture = scan_architecture(project_root)
        updated_context['architecture'] = architecture
        print(f"  ✅ 架构信息: {architecture}")
    
    # 扫描技术栈
    if 'tech_stack' in missing_fields:
        tech_stack = scan_tech_stack(project_root)
        updated_context['tech_stack'] = tech_stack
        print(f"  ✅ 技术栈: {', '.join(tech_stack)}")
    
    return updated_context


def scan_signoz_config(project_path: str, existing_config: Dict[str, Any], missing_fields: list) -> Dict[str, Any]:
    """
    通过脚本扫描补充SigNoz配置缺失信息
    
    Args:
        project_path: 项目根目录路径
        existing_config: 现有的配置数据
        missing_fields: 缺失的字段列表
    
    Returns:
        补充后的配置数据
    """
    print(f"\n📊 扫描SigNoz配置，补充缺失字段: {', '.join(missing_fields)}")
    
    project_root = Path(project_path).resolve()
    updated_config = existing_config.copy()
    
    # 扫描SigNoz初始化代码位置
    if 'init_code_location' in missing_fields:
        init_location = scan_signoz_init_code(project_root)
        updated_config['init_code_location'] = init_location
        if init_location:
            print(f"  ✅ SigNoz初始化代码位置: {init_location}")
        else:
            print(f"  ⚠️  未找到SigNoz初始化代码")
    
    # 扫描字段
    if 'fields' in missing_fields:
        fields = scan_signoz_fields(project_root, updated_config.get('init_code_location'))
        updated_config['fields'] = fields
        print(f"  ✅ 发现 {len(fields)} 个字段")
    
    # 扫描公共查询字段
    if 'common_query_fields' in missing_fields:
        common_fields = scan_common_query_fields(project_root)
        updated_config['common_query_fields'] = common_fields
        print(f"  ✅ 公共查询字段: {', '.join(common_fields)}")
    
    # 扫描服务名称
    if 'service_names' in missing_fields:
        service_names = scan_service_names(project_root)
        updated_config['service_names'] = service_names
        print(f"  ✅ 服务名称映射: {len(service_names)} 个服务")
    
    return updated_config


def scan_services(project_root: Path) -> list:
    """扫描服务列表"""
    services = []
    
    # 查找常见的服务配置文件
    service_patterns = [
        '**/docker-compose.yml',
        '**/docker-compose.yaml',
        '**/k8s/**/*.yaml',
        '**/k8s/**/*.yml',
        '**/services/**/*.py',
        '**/services/**/*.js',
        '**/services/**/*.ts'
    ]
    
    for pattern in service_patterns:
        for file_path in project_root.glob(pattern):
            # 简单的服务名提取逻辑（可以根据实际情况优化）
            if 'service' in file_path.name.lower():
                service_name = file_path.stem
                if service_name not in services:
                    services.append(service_name)
    
    return services if services else ['unknown-service']


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
    # 查找包含signoz的文件
    signoz_patterns = [
        '**/*signoz*.py',
        '**/*signoz*.js',
        '**/*signoz*.ts',
        '**/utils/*.py',
        '**/utils/*.js',
        '**/utils/*.ts',
        '**/config/*.py',
        '**/config/*.js',
        '**/config/*.ts'
    ]
    
    for pattern in signoz_patterns:
        for file_path in project_root.rglob(pattern):
            try:
                content = file_path.read_text(encoding='utf-8')
                if 'signoz' in content.lower() or 'Signoz' in content:
                    rel_path = str(file_path.relative_to(project_root))
                    return rel_path
            except Exception:
                continue
    
    return None


def scan_signoz_fields(project_root: Path, init_code_location: Optional[str]) -> list:
    """扫描SigNoz字段"""
    fields = []
    
    if init_code_location:
        init_file = project_root / init_code_location
        if init_file.exists():
            try:
                content = init_file.read_text(encoding='utf-8')
                # 简单的字段提取逻辑（可以根据实际情况优化）
                import re
                # 查找常见的字段定义模式
                field_patterns = [
                    r'["\'](\w+)["\']\s*[:=]',
                    r'field\s*[:=]\s*["\'](\w+)["\']',
                    r'attribute\s*[:=]\s*["\'](\w+)["\']'
                ]
                for pattern in field_patterns:
                    matches = re.findall(pattern, content)
                    fields.extend(matches)
            except Exception:
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
    
    # 从docker-compose文件提取服务名
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
    
    return service_names if service_names else {'default': 'default-service'}


def init_phase_0(project_path: str, skip_if_complete: bool = True) -> Tuple[bool, bool]:
    """
    阶段0主函数：检查并初始化项目上下文和SigNoz配置
    
    Args:
        project_path: 项目根目录路径
        skip_if_complete: 如果信息完整是否跳过（默认True）
    
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
        print("\n📝 项目上下文文件不存在，需要通过AI生成")
        generate_project_context_with_ai(project_path)
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
    
    # 检查SigNoz配置
    config_exists, config_data, config_missing = check_signoz_config(project_path)
    
    if not config_exists:
        print("\n📝 SigNoz配置文件不存在，需要通过AI生成")
        generate_signoz_config_with_ai(project_path)
        config_complete = False
    elif config_missing:
        print(f"\n⚠️  SigNoz配置信息不全，缺失字段: {', '.join(config_missing)}")
        if config_data:
            # 通过脚本扫描补充
            updated_config = scan_signoz_config(project_path, config_data, config_missing)
            config_file = analyzer_dir / SIGNOZ_CONFIG_FILE
            if save_json_file(config_file, updated_config):
                print(f"✅ SigNoz配置已更新: {config_file}")
            config_complete = len(config_missing) == 0
        else:
            config_complete = False
    else:
        print("✅ SigNoz配置信息完整")
        config_complete = True
    
    print("\n" + "="*60)
    
    return context_complete, config_complete
