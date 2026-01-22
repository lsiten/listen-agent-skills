---
name: online-ticket-analyzer
description: 线上工单分析技能，通过SigNoz MCP查询日志、分析代码逻辑、检索历史经验，生成综合解决方案，并将经验存储在.production-history目录中
version: 1.0.0
author: ""
tags: ["production", "ticket-analysis", "logging", "signoz", "mcp", "troubleshooting", "observability", "incident-management"]
---

# 线上工单分析 Skill

你是一个专门处理线上工单问题的AI助手，具备通过SigNoz MCP查询日志、分析项目代码逻辑、检索历史经验、生成问题解决方案，并管理问题解决经验库的能力。

## 任务概述

本技能用于分析线上生产环境中的工单问题。用户可以提供文字描述或文字+图片的问题报告，系统会通过SigNoz MCP查询相关服务器日志，分析项目代码逻辑，结合历史解决经验，给出问题原因和解决方案。所有解决过的问题经验会存储在`.production-history`目录中，每个经验保存为单独的Markdown文件，供后续参考和跨项目共享。

## 核心能力

- 🔍 **智能日志查询** - 通过SigNoz MCP工具查询相关服务的日志和错误信息
- 📊 **日志智能分析** - 自动分析日志，提取关键错误信息（不将原始日志发送给大模型）
- 💻 **代码逻辑分析** - 基于错误信息定位并分析相关代码文件
- 📡 **项目上下文生成** - 首次使用通过AI通读项目，生成项目上下文和SigNoz配置信息
- 🧠 **经验库检索** - 从`.production-history`目录中检索相似问题的历史解决经验
- 💡 **解决方案生成** - 综合日志、代码和历史经验，生成问题原因和解决方案
- 📝 **经验存储** - 将解决经验以Markdown格式保存到`.production-history`目录中，每个经验保存为单独文件
- 📁 **工单隔离** - 每个工单拥有独立目录，所有相关文件组织清晰

## 系统要求

### 硬件要求
- **处理器**: 现代CPU（推荐多核）
- **内存**: ≥4GB RAM（推荐8GB+）
- **存储**: ≥100MB可用空间

### 软件依赖
- Python 3.8+
- SigNoz MCP Server已配置（通过`.cursor/mcp.json`或Claude Desktop配置）
- 以下Python包：
  - requests (HTTP请求)
  - Pillow (图片处理)
  - pytesseract (OCR文字识别，可选)
  - markdown (Markdown处理)
  - jinja2 (HTML模板渲染)
  - python-dateutil (时间处理)

## 执行步骤

### 第一步：环境准备

安装所有必需的Python依赖包：

```bash
cd skills/online-ticket-analyzer
./scripts/install_dependencies.sh
```

或者手动安装：

```bash
pip install requests Pillow pytesseract markdown jinja2 python-dateutil
```

**注意**：如果使用图片OCR功能，还需要安装Tesseract OCR引擎：
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- Windows: 下载安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### 第二步：准备问题描述

用户可以提供以下格式的问题描述：

1. **纯文字描述**：直接提供问题的文字描述
2. **文字+图片**：提供文字描述和相关的截图或错误图片
3. **文件**：提供包含问题描述的文件

问题描述应包含：
- 问题现象描述
- 发生时间（可选，支持多种时间格式，详见下方时间查询优先级说明）
- 涉及的服务名称（可选，如果不提供则分析所有服务）
- 错误信息或异常行为
- **用户信息**（可选，但强烈推荐）：
  * 用户ID：`用户ID: 123456` 或 `user_id: 123456`（系统会自动转换为`user.id`字段查询）
  * 用户名：`用户名: 张三` 或 `username: zhangsan`
  * 用户邮箱：自动从描述中提取邮箱地址
- **设备信息**（可选）：
  * 设备ID：`设备ID: device123` 或 `client_id: device123`（系统会自动转换为`user.client_id`字段查询）
- **接口信息**（可选）：
  * 接口路径：`接口: /api/login` 或 `API: /api/login`
  * 功能名称：`登录`、`上传`、`支付`等（系统会自动推断接口）
- **地区信息**（可选）：
  * 国家：`国家: 中国` 或 `country: CN`
  * 城市：`城市: 北京` 或 `city: Beijing`

**时间查询优先级**（按优先级从高到低）：
1. **用户明确指定的时间**：通过 `--start-time` 和 `--end-time` 参数指定的时间区间
2. **工单上报时间或邮件发送时间**：从问题描述中自动提取工单上报时间或邮件发送时间，查询该时间前后30分钟的时间段
3. **问题发生时间**：从问题描述中提取的问题发生时间，查询该时间前后30分钟的时间段
4. **最近1小时**：如果以上都没有，默认查询最近1小时

**支持的时间格式**：
- 完整时间：`2025-01-20 10:00:00` 或 `2025/01/20 10:00:00`
- 仅时间：`10:00:00`（自动假设为今天）
- 关键词：`今天`、`昨天`、`刚才`、`刚刚`、`最近`

**时间提取关键词**：
- 工单时间：`工单时间`、`上报时间`、`创建时间`、`提交时间`、`工单创建`、`工单提交`
- 邮件时间：`邮件时间`、`发送时间`、`收到时间`、`邮件发送`、`邮件收到`
- 问题时间：`发生时间`、`出现时间`、`异常时间`、`问题时间`

### 第三步：执行问题分析

#### 方法1：基础分析（仅分析当前问题）

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --project-path "."
```

#### 方法2：带图片的问题分析

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --image "screenshots/error.png" \
  --project-path "."
```

#### 方法3：指定时间范围和服务

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --service "user-service" \
  --start-time "2025-01-20 10:00:00" \
  --end-time "2025-01-20 11:00:00" \
  --project-path "."
```

#### 方法4：从文件读取问题描述

```bash
python scripts/analyze_ticket.py \
  --file "ticket_description.txt" \
  --project-path "."
```

## 工作流程

### 阶段0：首次使用检查

系统会自动检查项目上下文和SigNoz配置信息：

**⚠️ 重要**：项目上下文和SigNoz配置是从整体项目视角生成的，不是针对特定工单。这些配置是全局的、可复用的，适用于所有工单分析。

1. **检查文件存在性**：
   - `.production-issue-analyzer/project_context.json` - 项目全局上下文（所有工单共享）
   - `.production-issue-analyzer/signoz_config.json` - SigNoz配置信息（所有工单共享）

2. **如果文件不存在**：
   - 通过AI通读整个项目代码，从整体项目视角生成项目上下文：
     * 包含所有服务的完整列表（不仅仅是当前工单涉及的服务）
     * 包含所有关键文件和目录结构
     * 包含完整的架构和技术栈信息
   - 通过AI通读整个项目代码，从整体项目视角生成SigNoz配置信息：
     * 包含所有API baseUrl配置（不仅仅是当前工单需要的）
     * 包含所有环境变量的实际值
     * 包含项目中使用的所有字段
     * 包含所有服务的名称映射

3. **如果文件存在但信息不全**：
   - 通过脚本扫描补充缺失的项目上下文信息
   - 通过脚本扫描补充缺失的SigNoz配置信息

4. **如果信息完整**：
   - 跳过扫描，直接进入阶段1

### 阶段1：准备与指令生成

1. **加载项目全局上下文**：从`.production-issue-analyzer/project_context.json`加载
2. **加载SigNoz配置信息**：从`.production-issue-analyzer/signoz_config.json`加载
3. **解析用户输入**：提取工单信息（服务名、时间、用户信息等）
4. **计算查询时间范围**：根据优先级计算查询时间范围
5. **保存工单上下文**：保存到`.production-issue-analyzer/tickets/{ticket_id}/ticket_context.json`
6. **生成MCP调用指令**：生成到`.production-issue-analyzer/tickets/{ticket_id}/mcp_instructions.json`

### MCP查询执行（AI执行）

脚本生成指令后，等待AI执行：

1. **AI读取指令文件**：`.production-issue-analyzer/tickets/{ticket_id}/mcp_instructions.json`
2. **调用SigNoz MCP工具**：根据指令调用相应的MCP工具
3. **保存查询结果**：保存到`.production-issue-analyzer/tickets/{ticket_id}/mcp_results.json`

### 阶段2：综合分析

1. **加载MCP查询结果**：从`.production-issue-analyzer/tickets/{ticket_id}/mcp_results.json`加载
2. **处理日志数据**：深度分析日志，提取关键错误信息（不发送原始日志给大模型）
3. **提取公共信息**：更新工单上下文
4. **分析代码逻辑**：基于错误信息定位并分析相关代码文件
5. **检索历史经验**：从`.production-history/`目录检索相似问题的历史经验
6. **生成综合解决方案**：综合日志、代码和历史经验，生成问题原因和解决方案
7. **保存工单处理记录**：更新工单上下文
8. **保存经验**：将解决经验保存到`.production-history/experience_{hash}.md`
9. **输出解决方案文档**：生成到`.production-issue-analyzer/tickets/{ticket_id}/solution.md`

## 文件组织

### 分析工作目录

所有分析相关文件保存在`.production-issue-analyzer/`目录下：

```
.production-issue-analyzer/
├── project_context.json          # 项目全局上下文（阶段0生成，全局共享）
├── signoz_config.json            # SigNoz配置信息（阶段0生成，全局共享）
└── tickets/                      # 工单目录
    └── {ticket_id}/              # 每个工单独立目录
        ├── mcp_instructions.json # MCP调用指令（阶段1生成）
        ├── mcp_results.json      # MCP查询结果（AI执行后保存）
        ├── ticket_context.json   # 工单上下文（阶段1保存）
        └── solution.md           # 解决方案文档（阶段2生成）
```

### 经验共享目录

所有经验文件保存在`.production-history/`目录下：

```
.production-history/
└── experience_{hash}.md         # 经验文件（成功/失败案例）
```

每个经验文件包含：
- 问题描述
- 解决方案
- 成功/失败标记
- 相关服务
- 时间戳
- 标签（用于检索）

## SigNoz MCP 工具使用指南

本技能依赖已配置的SigNoz MCP Server。在分析问题时，你需要调用以下MCP工具：

### MCP查询最佳实践（重要！）

基于实际使用经验，以下是MCP查询的最佳实践，可显著提高查询成功率：

#### 1. 查询工具选择优先级

**推荐优先级（从高到低）：**

1. **execute_builder_query（Query Builder v5）** - **强烈推荐**
   - ✅ 优点：更灵活，不需要指定服务名，支持复杂过滤条件
   - ✅ 优点：字段路径更直观，不需要 attributes. 前缀
   - ✅ 优点：支持多条件组合查询
   - ⚠️ 注意：需要构建完整的 Query Builder v5 JSON 结构
   - ⚠️ 重要：查询时不要添加fieldContext字段，SigNoz会自动识别字段上下文
   - ⚠️ 重要：确保formatTableResultForUI设置为true，以便正确显示结果
   - ⚠️ 重要：确保字段类型匹配（如user.id是int64类型，值也应该是数字）

2. **search_logs_by_service** - 备选方案
   - ⚠️ 缺点：需要先获取服务列表（list_services）
   - ⚠️ 缺点：字段路径可能需要 attributes. 前缀（取决于工具实现）
   - ✅ 优点：使用简单，适合快速查询

3. **get_error_logs** - 快速错误查询
   - ✅ 优点：专门用于获取错误日志，使用简单
   - ⚠️ 缺点：功能有限，只能查询错误日志

#### 2. 服务名获取方法（必须！）

**⚠️ 必须首先调用 `list_services` 获取服务列表**，这是查询成功的关键步骤！

```json
{
  "tool": "list_services",
  "params": {
    "timeRange": "1h",
    "start": 1737361800000,
    "end": 1737365400000
  }
}
```

**为什么必须先获取服务列表？**

1. **服务名过滤**：如果不添加 `service.name` 过滤，查询可能返回所有服务的日志，无法精确匹配
2. **服务名格式**：实际运行时的服务名可能与代码中的不同（大小写、前缀等），必须通过 `list_services` 确认
3. **提高查询成功率**：在 Query Builder 中添加 `service.name` 过滤条件，可以精确匹配服务，显著提高查询成功率
4. **多服务支持**：如果有多个服务，可以在 Query Builder 中添加多个 `service.name` 条件，使用OR逻辑组合

#### 3. 迭代式查询（重要！）

⚠️ **重要**：查询过程支持迭代式查询，逐步补充特征信息

**查询流程**：
1. **首次查询**：基于工单中的基础信息（服务名、时间范围、关键词等）进行查询
2. **特征提取**：从查询结果中提取特征信息：
   - 设备信息（`user.client_id`）
   - 用户信息（`user.id`）
   - IP地址（`source.address`）
   - 地理位置（`geo.city_name`, `geo.country_name`等）
   - 浏览器版本（`browser.name`, `browser.version`）
   - 应用版本（`service.version`）
3. **迭代查询**：基于提取的特征信息，生成更精确的查询条件
4. **逐步补充**：如果首次查询没有用户ID，可以根据设备ID等信息进行查询，然后从结果中提取用户ID

**关键特性**：
- ✅ 如果没有用户ID，可以根据工单中的特征信息（如设备ID）查询到的数据更新设备ID信息
- ✅ 查询过程中特征信息会慢慢补充（设备信息、用户信息、IP、地理位置、浏览器版本、应用版本等）
- ✅ 每次查询都会在selectFields中包含这些特征字段，以便提取特征信息

#### 4. 查询指令生成格式

生成的MCP指令文件包含以下结构：

```json
{
  "ticket_id": "ticket_20250120_abc123",
  "time_range": {
    "start": 1737361800000,
    "end": 1737365400000,
    "start_display": "2025-01-20 10:00:00",
    "end_display": "2025-01-20 11:00:00"
  },
  "services": ["user-service", "api-gateway"],
  "queries": [
    {
      "priority": 1,
      "tool": "list_services",
      "params": {
        "timeRange": "1h",
        "start": 1737361800000,
        "end": 1737365400000
      },
      "description": "获取服务列表，确认服务名称"
    },
    {
      "priority": 2,
      "tool": "execute_builder_query",
      "params": {
        "query": {
          "schemaVersion": "v1",
          "start": 1737361800000,
          "end": 1737365400000,
          "requestType": "raw",
          "compositeQuery": {
            "queries": [
              {
                "type": "builder_query",
                "spec": {
                  "name": "A",
                  "signal": "logs",
                  "disabled": false,
                  "limit": 100,
                  "offset": 0,
                  "order": [
                    {
                      "key": {
                        "name": "timestamp"
                      },
                      "direction": "desc"
                    }
                  ],
                  "selectFields": [
                    {
                      "name": "service.name",
                      "fieldDataType": "string",
                      "signal": "logs"
                    },
                    {
                      "name": "body",
                      "fieldDataType": "string",
                      "signal": "logs"
                    }
                  ],
                  "filters": {
                    "items": [
                      {
                        "key": {
                          "name": "service.name",
                          "fieldDataType": "string",
                          "signal": "logs"
                        },
                        "value": ["user-service"],
                        "op": "in"
                      }
                    ],
                    "op": "and"
                  }
                }
              }
            ]
          }
        }
      },
      "description": "查询user-service的日志"
    }
  ],
  "notes": "请按照优先级顺序执行查询，先获取服务列表确认服务名称，再执行具体查询"
}
```

## SigNoz数据结构说明

本技能基于`@ccint/signoz`包的数据结构规范。了解数据结构有助于正确构建查询和解析结果。

### 字段上下文（Field Context）

SigNoz使用OpenTelemetry标准，将字段分为不同的上下文级别：

| 上下文类型 | 说明 | 示例字段 |
|-----------|------|---------|
| **resource** | 资源级别字段，描述服务本身的信息 | `service.name`, `service.namespace`, `service.version` |
| **attributes** | 属性级别字段，描述日志的具体内容 | `body`, `severity_text`, `trace_id`, `user_id` |
| **span** | 跨度级别字段，用于追踪信息 | `span_id`, `parent_span_id` |
| **log** | 日志级别字段，日志特有的元数据 | `log_level`, `log_source` |

### 标准字段定义

本技能基于`@ccint/signoz`包的数据结构规范。该包支持Web应用和微信小程序的日志收集。

#### 资源级别字段（Resource）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `service.name` | string | 应用名称（格式：事业部.小组.项目名） | 服务过滤、分组 |
| `service.version` | string | 应用版本 | 版本追踪 |
| `service.environment` | string | 运行环境 | 环境区分（dev/staging/prod） |

**在Query Builder中的使用**：
```json
{
  "name": "service.name",
  "fieldDataType": "string",
  "signal": "logs",
  "fieldContext": "resource"
}
```

#### 基础属性（Attributes - Web/小程序通用）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `localTime` | string | 本地时间 | 时间查询 |
| `path` | string | 当前页面完整路径 | 页面追踪 |
| `pathname` | string | 当前页面路径（无参数） | 页面分析 |
| `browser.name` | string | 浏览器名称（Web） | 浏览器兼容性分析 |
| `browser.version` | string | 浏览器版本（Web） | 版本问题定位 |
| `browser.user_agent` | string | 用户代理字符串（Web） | 设备识别 |
| `referrer` | string | 来源页面（Web） | 流量来源分析 |
| `pageStack` | int64 | 当前页面的栈索引（小程序） | 小程序页面追踪 |

#### 请求日志属性（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `request.host` | string | 请求域名 | 接口域名分析 |
| `request.pathname` | string | 请求路径 | 接口路径查询 |
| `request.query` | string | 查询参数 | 参数分析 |
| `request.method` | string | 请求方法 | 方法过滤（GET/POST等） |
| `request.body` | string | 请求体 | 请求内容分析 |
| `response.status` | int64 | 响应状态码 | 错误过滤（500/404等） |
| `response.time` | int64 | 响应时间（毫秒） | 性能分析 |
| `response.body` | string | 响应体 | 响应内容分析 |
| `response.headers` | string | 响应头（仅包含配置的错误码字段） | 错误码提取 |
| `response.errno` | string | 业务错误码 | 业务错误分析 |

#### 错误日志属性（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `message` | string | 错误信息 | 错误内容查询 |
| `name` | string | 错误类型 | 错误分类 |
| `filename` | string | 错误文件名（Web） | 文件定位 |
| `lineNo` | int64 | 错误行号（Web） | 代码定位 |
| `colNo` | int64 | 错误列号（Web） | 精确定位 |
| `stack` | string | 错误堆栈（Web） | 堆栈分析 |

#### 性能日志属性（Attributes - Web）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `redirect` | int64 | 重定向耗时（毫秒） | 性能分析 |
| `dns` | int64 | DNS 查询耗时（毫秒） | 网络性能 |
| `tcp` | int64 | TCP 连接耗时（毫秒） | 连接性能 |
| `ssl` | int64 | TLS 握手耗时（毫秒） | 安全连接性能 |
| `ttfb` | int64 | 首字节时间（毫秒） | 服务器响应性能 |
| `response` | int64 | 响应接收耗时（毫秒） | 数据传输性能 |
| `domContentLoaded` | int64 | DOMContentLoaded 耗时（毫秒） | 页面加载性能 |
| `load` | int64 | Load 耗时（毫秒） | 页面完全加载性能 |
| `pageLoad` | int64 | 页面完全加载耗时（毫秒） | 整体性能 |
| `fpt` | int64 | First Paint 时间（毫秒） | 首次渲染性能 |
| `fcpt` | int64 | First Contentful Paint 时间（毫秒） | 内容渲染性能 |
| `css` | int64 | CSS 平均加载时间（毫秒） | 样式加载性能 |
| `js` | int64 | JavaScript 平均加载时间（毫秒） | 脚本加载性能 |

#### 小程序特有属性（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `duration` | int64 | 耗时（毫秒）- appLaunch/route/firstRender/downloadPackage | 性能分析 |
| `referrerPath` | string | 上一个页面的路径（route日志） | 页面跳转分析 |
| `initDataDelay` | int64 | 从脚本注入完成，到首次数据从逻辑层发出（毫秒） | 数据初始化性能 |
| `initData` | int64 | 首次数据从逻辑层发出，到接收（毫秒） | 数据传输性能 |
| `viewLayerRender` | int64 | 渲染层从开始渲染，到结束（毫秒） | 渲染性能 |
| `packageName` | string | 分包名（downloadPackage日志） | 分包分析 |
| `packageSize` | int64 | 分包大小（字节） | 包大小分析 |
| `network.type` | string | 网络类型（network日志） | 网络环境分析 |
| `network.signalStrength` | int64 | 信号强度（network日志） | 网络质量分析 |
| `network.weakNet` | int64 | 是否弱网，0或1（network日志） | 弱网分析 |
| `network.isConnected` | int64 | 是否连上了网，0或1（network日志） | 连接状态分析 |
| `evaluateScript` | int64 | js执行时间（毫秒，仅小程序） | 脚本执行性能 |

#### Web Vitals 指标（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `fcp` | int64 | First Contentful Paint（毫秒） | 首次内容绘制 |
| `lcp` | int64 | Largest Contentful Paint（毫秒） | 最大内容绘制 |
| `cls` | float | Cumulative Layout Shift | 累积布局偏移 |
| `inp` | int64 | Interaction to Next Paint（毫秒） | 交互到下次绘制 |
| `ttfb` | int64 | Time to First Byte（毫秒） | 首字节时间 |

#### 通用字段（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `body` | string | 日志内容（通用） | 日志正文查询、全文搜索 |
| `severity_text` | string | 日志严重程度文本 | 错误过滤（error/Error/ERROR/异常/错误） |
| `severity_number` | int64 | 日志严重程度数字 | 错误过滤（17=ERROR, 18=FATAL等） |
| `timestamp` | int64 | 时间戳（毫秒） | 时间范围查询、排序 |
| `trace_id` | string | 追踪ID | 追踪关联 |
| `span_id` | string | 跨度ID | 跨度关联 |

### 字段路径格式

在查询和结果解析中，字段可以使用以下格式：

1. **简化格式**（推荐）：
   - `service.name` - 自动识别为resource级别（实际在resources对象中）
   - `body` - 自动识别为attributes级别
   - `user.id` - 自动识别为attributes级别（嵌套字段）

2. **完整路径格式**：
   - `resources.service.name` - 明确指定resources级别（注意是复数）
   - `attributes.body` - 明确指定attributes级别
   - `attributes.user.id` - 明确指定attributes下的嵌套字段

3. **嵌套字段**（重要）：
   - `user.id` - 嵌套在attributes.user对象下的id字段（不是user_id）
   - `user.client_id` - 嵌套在attributes.user对象下的client_id字段（不是client_id）
   - `geo.city_name` - 嵌套在attributes.geo对象下的city_name字段
   - `request.pathname` - 嵌套在attributes.request对象下的pathname字段

**注意**：
- 实际数据结构中，服务信息存储在 `resources` 对象中（复数），不是 `resource`
- 用户和设备字段使用点分隔的嵌套格式：`user.id`, `user.client_id`
- 地理位置字段使用 `geo.` 前缀：`geo.city_name`, `geo.country_name`

### 严重程度（Severity）

#### 严重程度文本值

错误级别的严重程度文本值（用于`severity_text`字段）：

- `error`, `Error`, `ERROR`
- `异常`, `错误`
- `fatal`, `Fatal`, `FATAL`
- `critical`, `Critical`, `CRITICAL`

#### 严重程度数字值

OpenTelemetry标准的严重程度数字（用于`severity_number`字段）：

| 值 | 级别 | 说明 |
|----|------|------|
| 17 | ERROR | 错误 |
| 18 | FATAL | 致命错误 |
| 19-22 | CRITICAL | 严重错误 |

**判断错误日志**：
- `severity_text` 在错误值列表中，或
- `severity_number >= 17`

### 查询结果数据结构

MCP查询返回的结果通常具有以下结构：

```json
{
  "queries": [
    {
      "data": [
        {
          "resource": {
            "service": {
              "name": "user-service"
            }
          },
          "attributes": {
            "body": "用户登录失败",
            "severity_text": "error",
            "severity_number": 17,
            "timestamp": 1737361800000,
            "trace_id": "abc123",
            "user_id": "123456"
          }
        }
      ]
    }
  ]
}
```

### 字段提取规则

在解析查询结果时，系统会按以下优先级提取字段值：

1. **直接字段**：`entry['field_name']`
2. **资源级别**：`entry['resource']['service']['name']` 或 `entry['resource']['service.name']`
3. **属性级别**：`entry['attributes']['body']` 或 `entry['attributes']['body']`
4. **嵌套字段**：自动处理点分隔的嵌套路径

### 默认查询字段

系统默认查询以下字段（按优先级排序）：

1. `service.name` - 服务名称（resource）
2. `body` - 日志内容（attributes）
3. `severity_text` - 严重程度文本（attributes）
4. `timestamp` - 时间戳（attributes）
5. `trace_id` - 追踪ID（attributes）
6. `span_id` - 跨度ID（attributes）

### 自定义字段配置

在`.production-issue-analyzer/signoz_config.json`中可以配置项目的自定义字段：

```json
{
  "common_query_fields": [
    "service.name",
    "body",
    "severity_text",
    "user_id",
    "api_path",
    "error_code"
  ],
  "fields": [
    "user_id",
    "request_id",
    "api_path",
    "error_code",
    "client_id"
  ]
}
```

### 字段使用示例

#### 示例1：查询特定服务的错误日志

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "service.name",
          "fieldContext": "resource"
        },
        "value": ["事业部.小组.项目名"],
        "op": "in"
      },
      {
        "key": {
          "name": "severity_text",
          "fieldContext": "attributes"
        },
        "value": ["error", "Error", "ERROR"],
        "op": "in"
      }
    ],
    "op": "and"
  }
}
```

#### 示例2：查询特定用户的日志

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "user.id",
          "fieldContext": "attributes"
        },
        "value": ["4472431079"],
        "op": "in"
      }
    ],
    "op": "and"
  }
}
```

**注意**：字段名是 `user.id`（点分隔），不是 `user_id`。

#### 示例3：查询特定设备的日志

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "user.client_id",
          "fieldContext": "attributes"
        },
        "value": ["B4SMfdd5F0FW83e1a18rfA5J"],
        "op": "in"
      }
    ],
    "op": "and"
  }
}
```

**注意**：字段名是 `user.client_id`（点分隔），不是 `client_id` 或 `device_id`。

#### 示例4：查询特定接口的错误日志

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "request.pathname",
          "fieldContext": "attributes"
        },
        "value": ["/api/login"],
        "op": "in"
      },
      {
        "key": {
          "name": "response.status",
          "fieldContext": "attributes"
        },
        "value": [500, 502, 503],
        "op": "in"
      }
    ],
    "op": "and"
  }
}
```

#### 示例5：查询业务错误码

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "response.errno",
          "fieldContext": "attributes"
        },
        "value": ["E001", "E002"],
        "op": "in"
      }
    ],
    "op": "and"
  }
}
```

#### 示例6：查询特定地理位置的日志

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "geo.city_name",
          "fieldContext": "attributes"
        },
        "value": ["Shanghai"],
        "op": "in"
      }
    ],
    "op": "and"
  }
}
```

#### 示例7：查询性能问题（响应时间过长）

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "response.time",
          "fieldContext": "attributes"
        },
        "value": [3000],
        "op": ">="
      }
    ],
    "op": "and"
  }
}
```

#### 示例8：查询Web Vitals性能指标

```json
{
  "selectFields": [
    {
      "name": "lcp",
      "fieldDataType": "int64",
      "signal": "logs",
      "fieldContext": "attributes"
    },
    {
      "name": "fcp",
      "fieldDataType": "int64",
      "signal": "logs",
      "fieldContext": "attributes"
    },
    {
      "name": "cls",
      "fieldDataType": "float",
      "signal": "logs",
      "fieldContext": "attributes"
    }
  ]
}
```

#### 示例9：查询小程序启动性能

```json
{
  "filters": {
    "items": [
      {
        "key": {
          "name": "duration",
          "fieldContext": "attributes"
        },
        "value": [3000],
        "op": ">="
      }
    ],
    "op": "and"
  }
}
```

### 实际数据结构说明

根据实际上报的数据，SigNoz日志数据结构如下：

```json
{
  "body": "",
  "id": "38CMFx09aoUNJYh8cZa1AgZj3Yi",
  "timestamp": "2026-01-13T10:09:59.986Z",
  "attributes": {
    "user.id": 4472431079,
    "user.client_id": "B4SMfdd5F0FW83e1a18rfA5J",
    "geo.location.lat": 31.2222,
    "geo.location.lon": 121.4581,
    "geo.city_name": "Shanghai",
    "geo.country_name": "China",
    "source.address": "101.226.11.71",
    "message": "错误信息",
    "name": "Error",
    "stack": "错误堆栈"
  },
  "resources": {
    "service.name": "cs.web.camscanner-toc",
    "service.version": "1.0.17",
    "service.environment": "online"
  },
  "severity_text": "error",
  "severity_number": 17
}
```

**重要说明**：
1. **用户ID字段**：实际字段名是 `attributes.user.id`（点分隔），不是 `user_id`
2. **设备ID字段**：实际字段名是 `attributes.user.client_id`（点分隔），不是 `client_id` 或 `device_id`
3. **服务信息**：存储在 `resources` 对象中，不是 `resource`（注意复数形式）
4. **地理位置**：使用 `geo.` 前缀的嵌套字段
5. **字段路径**：使用点分隔的嵌套路径，如 `user.id`, `user.client_id`, `geo.city_name`

### 关键信息识别流程

⚠️ **重要**：所有工单查询需要的关键信息，必须通过AI阅读完整项目后，综合配置信息、环境配置、打包配置给出，而不是简单的正则匹配。

在生成SigNoz配置时，AI必须通读项目代码，了解所有关键信息的实际使用方式和命名规则，生成准确的映射配置。

**关键信息包括**：
1. **接口路径（api_pathname_mapping）**：API的完整pathname映射
2. **字段提取规则（field_extraction_rules）**：用户输入模式到实际字段名的映射
3. **服务名称映射（service_name_mapping）**：用户输入模式到实际service.name的映射
4. **其他关键信息**：所有可能用于工单查询的信息

#### 1. 接口路径识别流程

⚠️ **重要**：pathname识别是必须准确的信息，必须通过AI阅读完整项目后，综合配置信息、环境配置、打包配置给出，而不是简单的正则匹配。

在生成SigNoz配置时，AI必须通读项目代码，追踪API调用，找到baseUrl的来源，然后组合完整pathname。

**流程**（必须完整执行，不能使用简单的正则匹配）：

1. **通读项目代码**：查找所有API调用位置（如`.post('/revert_dir_list', ...)`、`createRequest('SAPI_DOMESTIC').post(...)`等）
2. **追踪createRequest方法**：对于每个API调用，追踪其baseUrl的来源
   - 找到baseUrl从config读取的位置（如`config.api['SAPI_DOMESTIC']`）
   - 查找config中baseUrl的定义，追踪到环境变量（如`import.meta.env.VITE_SAPI_DOMESTIC`）
3. **从打包配置获取环境变量值**：读取打包配置（vite.config.ts），查找loadEnv调用，根据mode和prefix从对应的.env文件中获取实际值
4. **解析baseUrl**：提取baseUrl的路径部分（如`https://cs8.intsig.net/sync` → `/sync`）
5. **组合完整pathname**：baseUrl路径部分 + API相对路径 = 完整pathname（如`/sync/revert_dir_list`）
6. **生成api_pathname_mapping**：在signoz_config.json中生成完整的pathname映射
   ```json
   {
     "api_pathname_mapping": {
       "/revert_dir_list": "/sync/revert_dir_list",
       "/revert_pre_check": "/sync/revert_pre_check",
       "/revert_pre_fix": "/sync/revert_pre_fix"
     }
   }
   ```

**⚠️ 重要**：
- 不能使用简单的正则匹配来识别pathname
- 必须通读项目代码，追踪代码逻辑，找到baseUrl的来源
- 必须综合配置信息、环境配置、打包配置给出准确的pathname
- 在parse_input阶段，优先使用AI生成的api_pathname_mapping，而不是重新匹配

#### 2. 字段提取规则识别流程

⚠️ **重要**：字段提取规则识别是必须准确的信息，必须通过AI阅读完整项目后，了解字段的实际命名规则。

**流程**（必须完整执行，不能使用简单的正则匹配）：

1. **通读项目代码**：查找所有字段的使用方式（如user.id, user.client_id等）
2. **了解字段命名规则**：了解项目中字段的实际命名规则和嵌套结构
3. **了解用户输入变体**：了解用户输入中可能出现的字段名称变体（如"用户ID"、"UserID"、"user_id"等）
4. **生成field_extraction_rules配置**：在signoz_config.json中生成完整的字段提取规则映射
   ```json
   {
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
     }
   }
   ```

**⚠️ 重要**：
- 不能使用简单的正则匹配来识别字段
- 必须通读项目代码，了解字段的实际使用方式
- 必须综合配置信息、环境配置、打包配置给出准确的字段映射
- 在parse_input阶段，优先使用AI生成的field_extraction_rules，而不是重新匹配

#### 3. 服务名称映射识别流程

⚠️ **重要**：服务名称映射识别是必须准确的信息，必须通过AI阅读完整项目后，了解服务的实际命名规则。

**流程**（必须完整执行，不能使用简单的正则匹配）：

1. **通读项目代码**：查找所有服务的定义和使用
2. **了解服务命名规则**：了解项目中服务的实际命名规则（如service.name的值）
3. **了解用户输入变体**：了解用户输入中可能出现的服务名称变体（如"用户服务"、"UserService"等）
4. **生成service_name_mapping配置**：在signoz_config.json中生成完整的服务名称映射
   ```json
   {
     "service_name_mapping": {
       "用户服务": "user-service",
       "UserService": "user-service",
       "用户": "user-service"
     }
   }
   ```

**⚠️ 重要**：
- 不能使用简单的正则匹配来识别服务名称
- 必须通读项目代码，了解服务的实际命名规则
- 必须综合配置信息、环境配置、打包配置给出准确的服务名称映射
- 在parse_input阶段，优先使用AI生成的service_name_mapping，而不是重新匹配

#### 4. 其他关键信息识别

⚠️ **重要**：所有可能用于工单查询的关键信息，都必须通过AI阅读完整项目后，了解其实际使用方式和命名规则。

**流程**：
1. **通读项目代码**：识别所有可能用于工单查询的关键信息
2. **了解实际使用方式**：了解这些信息在代码中的实际使用方式和命名规则
3. **生成映射配置**：生成相应的映射配置，确保从用户输入到实际查询字段的准确转换

**⚠️ 重要**：
- 不能使用简单的正则匹配来识别关键信息
- 必须通读项目代码，了解信息的实际使用方式
- 必须综合配置信息、环境配置、打包配置给出准确的信息映射
- 在parse_input阶段，优先使用AI生成的映射配置，而不是重新匹配

**示例流程**（必须完整执行）：
如果代码中是 `createRequest('SAPI_DOMESTIC').post('/revert_dir_list', ...)`
需要：
1. 识别API相对路径: `/revert_dir_list`
2. 追踪createRequest方法，找到baseUrl从`config.api['SAPI_DOMESTIC']`读取
3. 查找config中SAPI_DOMESTIC的定义，发现来自`import.meta.env.VITE_SAPI_DOMESTIC`
4. 从打包配置（vite.config.ts）中获取VITE_SAPI_DOMESTIC的实际值（打包配置会使用loadEnv加载.env文件，根据mode和prefix获取实际值）
5. 解析baseUrl，提取路径部分（如`https://cs8.intsig.net/sync` → `/sync`）
6. 组合完整pathname: `/sync` + `/revert_dir_list` = `/sync/revert_dir_list`
7. 在api_pathname_mapping中记录: `{"/revert_dir_list": "/sync/revert_dir_list", ...}`

### @ccint/signoz 初始化配置

该包初始化时需要提供以下配置（Options对象）：

| 属性名 | 说明 | 值类型 | 默认值 |
|--------|------|--------|--------|
| `appName` | 应用名称，格式：事业部.小组.项目名 | string | 必填 |
| `appVersion` | 应用版本 | string | 必填 |
| `env` | 运行环境 | string | 必填 |
| `url` | 日志收集服务器地址 | string | 选填，默认根据环境自动选择 |
| `ignoreApis` | 忽略指定的请求日志，匹配完整的url | RegExp[] | 选填 |
| `ajaxIgnorePath` | 忽略指定路径的请求日志，只匹配pathname | RegExp[] | 选填 |
| `headerError` | 响应头中的错误码字段名 | string[] | 选填 |
| `errnoNameArr` | 响应体中的错误码字段名 | string[] | 选填 |

**注意**：`service.name`字段的值就是`appName`配置的值（格式：事业部.小组.项目名）。

### 注意事项

1. **字段上下文必须正确**：resource级别的字段必须使用`fieldContext: "resource"`，attributes级别的字段必须使用`fieldContext: "attributes"`

2. **字段数据类型**：确保`fieldDataType`与实际数据类型匹配（string, int64等）

3. **嵌套字段处理**：对于嵌套字段（如`service.name`），在Query Builder中使用`name: "service.name"`，在结果解析时会自动处理

4. **自定义字段**：如果项目使用了自定义字段，需要在`signoz_config.json`中配置，系统会自动识别和使用

5. **字段路径兼容性**：系统支持多种字段路径格式，但推荐使用简化格式（如`service.name`而不是`resource.service.name`）

6. **查询条件构建**：
   - Query Builder使用`in`操作符进行多值匹配
   - 支持多种操作符进行过滤
   - 服务名使用`in`操作符配合服务列表进行匹配

## 参数说明

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `--description` | string | 否* | - | 问题描述文字（与--file/--image至少一个） |
| `--file` | string | 否* | - | 包含问题描述的文件路径 |
| `--image` | string | 否 | - | 问题相关图片路径（支持OCR识别） |
| `--project-path` | string | 是 | `.` | 项目根目录路径 |
| `--service` | string | 否 | - | 指定服务名称（如果不提供则分析所有服务） |
| `--start-time` | string | 否 | - | 查询开始时间（格式：YYYY-MM-DD HH:MM:SS） |
| `--end-time` | string | 否 | - | 查询结束时间（格式：YYYY-MM-DD HH:MM:SS） |
| `--ticket-id` | string | 否 | - | 工单ID（如果不提供则自动生成） |
| `--verbose` | flag | 否 | false | 显示详细日志 |
| `--skip-phase0` | flag | 否 | false | 跳过阶段0（首次使用检查） |
| `--skip-phase1` | flag | 否 | false | 跳过阶段1（如果已有MCP结果） |
| `--skip-phase2` | flag | 否 | false | 跳过阶段2（仅生成指令） |

*：`--description`、`--file`、`--image` 至少提供一个

## 使用示例

### 示例1：基础工单分析

```bash
python scripts/analyze_ticket.py \
  --description "用户ID 123456反馈登录接口在10:30左右返回500错误" \
  --project-path "."
```

### 示例2：带图片的工单分析

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈支付失败" \
  --image "screenshots/payment_error.png" \
  --project-path "."
```

### 示例3：指定时间范围和服务

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --service "user-service" \
  --start-time "2025-01-20 10:00:00" \
  --end-time "2025-01-20 11:00:00" \
  --project-path "."
```

### 示例4：从文件读取问题描述

```bash
python scripts/analyze_ticket.py \
  --file "tickets/ticket_001.txt" \
  --project-path "."
```

### 示例5：仅生成MCP指令（不执行分析）

```bash
python scripts/analyze_ticket.py \
  --description "用户反馈登录接口返回500错误" \
  --project-path "." \
  --skip-phase2
```

## 最佳实践

1. **问题描述完整性**
   - 提供详细的问题现象描述
   - 包含准确的时间信息（有助于精确查询）
   - 提供用户信息、服务信息等上下文

2. **时间范围选择**
   - 尽量提供准确的问题发生时间
   - 如果时间不确定，使用较宽的时间范围
   - 避免查询过大的时间范围（可能影响性能）

3. **服务名称**
   - 如果不确定服务名称，不指定服务，让系统分析所有服务
   - 如果知道服务名称，指定服务可以提高查询效率

4. **经验积累**
   - 定期查看`.production-history/`目录中的经验文件
   - 相似问题可以参考历史经验
   - 经验文件可以跨项目共享

5. **工单管理**
   - 每个工单有独立目录，便于管理和查找
   - 可以删除不需要的工单目录释放空间
   - 重要工单的解决方案可以备份

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 项目上下文文件不存在 | 首次使用未初始化 | 运行脚本会自动初始化，或手动运行阶段0 |
| SigNoz配置信息不全 | 配置扫描不完整 | 检查项目中的SigNoz初始化代码，手动补充配置 |
| MCP查询失败 | MCP Server未配置或服务名错误 | 检查MCP配置，确认服务名称正确 |
| 时间范围解析失败 | 时间格式不支持 | 使用标准时间格式：YYYY-MM-DD HH:MM:SS |
| 图片OCR识别失败 | Tesseract未安装或图片质量差 | 安装Tesseract OCR引擎，确保图片清晰可读 |
| 经验检索无结果 | 历史经验库为空 | 先解决一些问题，积累经验后再使用检索功能 |

### 调试模式

启用详细日志输出：

```bash
python scripts/analyze_ticket.py \
  --description "问题描述" \
  --project-path "." \
  --verbose
```

## 扩展功能

- **批量分析** - 支持同时分析多个工单
- **报告生成** - 生成指定时间范围内的问题分析报告
- **经验导出** - 导出经验文件用于分享
- **API集成** - 支持通过API调用进行工单分析
- **实时监控** - 支持实时监控和告警

## 技术架构

- **数据处理**: Python标准库 + requests
- **日志分析**: 自定义分析逻辑（不发送原始日志给大模型）
- **代码分析**: 基于错误信息智能定位代码文件
- **经验管理**: 文件系统 + 语义相似度匹配
- **文档生成**: Markdown格式

## 注意事项

- 确保SigNoz MCP Server已正确配置
- 首次使用需要AI通读项目，可能需要较长时间
- 项目上下文和SigNoz配置信息会全局共享，所有工单共用
- 每个工单的所有相关文件都在独立目录下，便于管理
- 经验文件可以跨项目共享，建议定期备份
- 工单目录可以删除，但经验文件建议保留用于后续参考
