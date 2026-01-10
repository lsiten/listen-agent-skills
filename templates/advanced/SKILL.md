---
name: {{name}}
description: {{description}}
version: 1.0.0
author: {{author}}
tags: {{tags}}
---

# {{name}} Skill

你是一个专门处理{{domain}}的AI助手，具备{{capabilities}}能力。

## 任务概述

本技能用于{{task_overview}}，支持{{features}}等功能。

## 核心能力

- 🚀 **能力1** - {{capability_1_description}}
- 🧠 **能力2** - {{capability_2_description}}
- 📊 **能力3** - {{capability_3_description}}
- 💾 **能力4** - {{capability_4_description}}
- 🔄 **能力5** - {{capability_5_description}}

## 系统要求

### 硬件要求
- **处理器**: {{processor_requirement}}
- **内存**: {{memory_requirement}}
- **存储**: {{storage_requirement}}

### 软件依赖
- {{dependency_1}}
- {{dependency_2}}
- {{dependency_3}}

## 执行步骤

### 第一步：环境准备

```bash
# 环境安装脚本
./scripts/install_dependencies.sh
```

### 第二步：配置设置

```bash
# 配置命令
./scripts/setup_config.sh --param {{config_param}}
```

### 第三步：执行任务

#### 方法1：交互式执行

```bash
./scripts/interactive_run.sh
```

#### 方法2：命令行执行

```bash
./scripts/run_task.sh \
  --input "{{input_param}}" \
  --output "{{output_param}}" \
  --config "{{config_file}}"
```

### 第四步：结果处理

```bash
# 处理结果
./scripts/process_results.sh --input {{result_path}}
```

## 配置选项

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `{{param_1}}` | string | "{{default_1}}" | {{param_1_desc}} |
| `{{param_2}}` | number | {{default_2}} | {{param_2_desc}} |
| `{{param_3}}` | boolean | {{default_3}} | {{param_3_desc}} |

## 使用示例

### 基础示例

```bash
# 基础用法
{{name}} --input "example.txt" --output "result.txt"
```

### 高级示例

```bash
# 高级用法
{{name}} \
  --input "data/" \
  --output "results/" \
  --config "advanced.json" \
  --parallel 4 \
  --verbose
```

## 最佳实践

1. **性能优化**
   - {{performance_tip_1}}
   - {{performance_tip_2}}

2. **安全考虑**
   - {{security_tip_1}}
   - {{security_tip_2}}

3. **错误处理**
   - {{error_handling_tip_1}}
   - {{error_handling_tip_2}}

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| {{error_1}} | {{cause_1}} | {{solution_1}} |
| {{error_2}} | {{cause_2}} | {{solution_2}} |
| {{error_3}} | {{cause_3}} | {{solution_3}} |

### 调试模式

```bash
# 启用调试模式
{{name}} --debug --verbose --log-level debug
```

## 扩展功能

- **插件系统**: {{plugin_description}}
- **API集成**: {{api_description}}
- **批量处理**: {{batch_description}}
- **监控报告**: {{monitoring_description}}

## 技术架构

- **核心框架**: {{framework}}
- **数据处理**: {{data_processing}}
- **存储方案**: {{storage_solution}}
- **通信协议**: {{communication_protocol}}