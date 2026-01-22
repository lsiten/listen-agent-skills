# 线上工单分析技能

一个智能的线上工单问题分析技能，通过SigNoz MCP查询日志、分析代码逻辑、检索历史经验，生成综合解决方案。

## 快速开始

### 1. 安装依赖

```bash
cd skills/online-ticket-analyzer
./scripts/install_dependencies.sh
```

### 2. 分析工单

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --project-path "."
```

## 功能特性

- 🔍 **智能日志查询** - 通过SigNoz MCP工具自动查询相关日志
- 📊 **日志深度分析** - 自动提取关键错误信息，不发送原始日志
- 💻 **代码逻辑分析** - 基于错误信息智能定位代码文件
- 🧠 **经验库检索** - 从历史经验中检索相似问题的解决方案
- 💡 **综合解决方案** - 综合日志、代码和历史经验生成解决方案
- 📝 **经验积累** - 自动保存解决经验，支持跨项目共享

## 工作流程

### 阶段0：首次使用检查

系统会自动检查并初始化项目上下文和SigNoz配置：

- 如果文件不存在：通过AI通读项目生成
- 如果信息不全：通过脚本扫描补充
- 如果信息完整：跳过初始化

### 阶段1：准备与指令生成

- 加载项目上下文和SigNoz配置
- 解析用户输入，提取工单信息
- 计算查询时间范围
- 生成MCP调用指令

### MCP查询执行

AI根据生成的指令调用SigNoz MCP工具，查询相关日志。

### 阶段2：综合分析

- 处理日志数据，提取关键信息
- 分析代码逻辑
- 检索历史经验
- 生成综合解决方案
- 保存经验和解决方案

## 文件组织

```
.production-issue-analyzer/     # 分析工作目录
├── project_context.json        # 项目全局上下文
├── signoz_config.json          # SigNoz配置信息
└── tickets/                   # 工单目录
    └── {ticket_id}/           # 每个工单独立目录
        ├── mcp_instructions.json
        ├── mcp_results.json
        ├── ticket_context.json
        └── solution.md

.production-history/            # 经验共享目录
└── experience_{hash}.md       # 经验文件
```

## 使用示例

### 基础分析

```bash
python scripts/analyze_ticket.py \
  --description "用户ID 123456反馈登录接口在10:30左右返回500错误" \
  --project-path "."
```

### 带图片分析

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈支付失败" \
  --image "screenshots/payment_error.png" \
  --project-path "."
```

### 指定时间范围

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --start-time "2025-01-20 10:00:00" \
  --end-time "2025-01-20 11:00:00" \
  --project-path "."
```

## 配置要求

- Python 3.8+
- SigNoz MCP Server已配置
- 相关Python依赖包（见install_dependencies.sh）

## 更多信息

详细使用说明请参考 [SKILL.md](./SKILL.md)。
