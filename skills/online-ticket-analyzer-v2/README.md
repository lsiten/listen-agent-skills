# 线上工单分析 Skill

专业的线上工单分析技能，支持多格式输入（图文、图、文字、文件等），通过SigNoz监控系统进行日志查询和错误分析，生成综合解决方案。

## 特性

- 🔍 **多格式输入解析** - 支持图文、图、文字、文件等多种输入格式
- 📊 **SigNoz集成查询** - 通过MCP工具连接SigNoz监控系统
- 🧠 **智能信息提取** - 自动提取服务名、时间、用户信息等关键字段
- ⏰ **智能时间计算** - 自动计算查询时间范围，支持多个时间点
- 🔎 **深度日志分析** - 深度分析日志数据，提取关键错误信息
- 💻 **代码逻辑分析** - 基于错误信息定位代码文件，分析问题根源
- 📚 **历史经验检索** - 从历史经验库中检索相似问题的解决方案
- 🌍 **普遍性问题判断** - 分析问题影响范围，判断是否为普遍性问题
- 📝 **综合解决方案生成** - 生成包含问题分析、根本原因、解决方案的完整文档

## 工作流程

本技能采用三阶段工作流程：

1. **阶段0：首次使用检查**
   - AI通读项目，生成项目全局上下文
   - 生成SigNoz配置信息（API路径映射、字段提取规则、服务名称映射等）

2. **阶段1：准备与指令生成**
   - 解析用户输入，提取工单信息
   - 计算查询时间范围
   - 生成MCP调用指令

3. **阶段2：综合分析**
   - 执行SigNoz查询
   - 深度分析日志数据
   - 分析代码逻辑
   - 检索历史经验
   - 判断普遍性问题
   - 生成综合解决方案

## 使用方法

### 快速开始

直接向AI助手描述你的工单问题，AI会：

1. **理解需求** - 分析工单描述，提取关键信息
2. **生成查询** - 创建SigNoz查询指令
3. **执行查询** - 调用SigNoz MCP工具查询日志
4. **分析结果** - 深度分析日志，定位问题根源
5. **生成方案** - 生成综合解决方案文档

### 输入格式支持

- **文字描述** - 直接描述工单问题
- **图片** - 上传错误截图或日志截图
- **图文混合** - 图片 + 文字描述
- **文件** - 上传邮件记录、日志文件等

### 示例

#### 示例1：基础工单

```
用户反馈登录失败，时间：2025-01-20 10:00:00，用户ID：123456
```

#### 示例2：邮件沟通记录

上传邮件沟通记录（包含多个发送方、多个时间点），AI会自动：
- 分析多个发送方
- 提取多个时间点
- 计算查询时间范围

#### 示例3：错误截图

上传错误截图，AI会：
- 识别图片中的错误信息
- 提取服务名、时间、错误类型等
- 生成查询指令

## 配置

### 首次使用

首次使用时，AI会自动：
1. 通读项目代码
2. 生成项目全局上下文（`project_context.json`）
3. 生成SigNoz配置信息（`signoz_config.json`）

### 配置文件说明

- **project_context.json** - 项目全局上下文，包含所有服务、架构、技术栈信息
- **signoz_config.json** - SigNoz配置，包含API路径映射、字段提取规则、服务名称映射等

## SigNoz集成

本技能通过MCP协议连接SigNoz监控系统，支持：

- **Query Builder v5查询** - 灵活的日志/指标/追踪查询（推荐）
- **服务列表查询** - 获取实际运行的服务名称
- **错误日志查询** - 快速查询错误日志
- **追踪查询** - 查询分布式追踪信息
- **指标查询** - 查询指标数据
- **仪表板管理** - 创建和管理监控仪表板
- **警报管理** - 查看和管理警报规则

### 查询工具优先级

1. **signoz_execute_builder_query** - Query Builder v5（强烈推荐，支持 logs/metrics/traces）
2. **signoz_list_services** - 必须首先执行，确认服务名称
3. **signoz_search_logs_by_service** - 按服务搜索日志
4. **signoz_get_error_logs** - 快速错误查询

### 完整工具列表

**日志查询**：`signoz_execute_builder_query`、`signoz_search_logs_by_service`、`signoz_get_error_logs`、`signoz_list_log_views`、`signoz_get_log_view`、`signoz_get_logs_available_fields`、`signoz_get_logs_field_values`

**追踪查询**：`signoz_search_traces_by_service`、`signoz_get_trace_details`、`signoz_get_trace_error_analysis`、`signoz_get_trace_span_hierarchy`、`signoz_get_trace_available_fields`、`signoz_get_trace_field_values`

**指标查询**：`signoz_list_metric_keys`、`signoz_search_metric_by_text`、`signoz_get_metrics_available_fields`、`signoz_get_metrics_field_values`

**服务相关**：`signoz_list_services`、`signoz_get_service_top_operations`

**仪表板**：`signoz_list_dashboards`、`signoz_get_dashboard`、`signoz_create_dashboard`、`signoz_update_dashboard`

**警报**：`signoz_list_alerts`、`signoz_get_alert`、`signoz_get_alert_history`、`signoz_get_logs_for_alert`

## 数据结构

### SigNoz字段说明

本技能支持OpenTelemetry标准的数据结构：

- **资源级别字段** - `service.name`, `service.version`, `service.environment`
- **属性级别字段** - `user.id`, `user.client_id`, `request.pathname`, `message`, `stack`等
- **嵌套字段** - 使用点分隔符（如`user.id`，不是`user_id`）

### 重要字段

- `user.id` - 用户ID（int64类型）
- `user.client_id` - 设备ID（string类型）
- `request.pathname` - 接口路径
- `severity_text` - 日志严重程度（error, Error, ERROR等）
- `severity_number` - 日志严重程度数字（17=ERROR, 18=FATAL等）

## 普遍性问题分析

本技能支持自动判断问题是否为普遍性问题：

- 🔴 **严重（critical）** - 影响超过50个错误或10个用户/设备，且影响超过2个国家或5个城市
- 🟠 **高（high）** - 影响超过50个错误或10个用户/设备，且影响超过1个国家或3个城市
- 🟡 **中等（medium）** - 影响超过20个错误或5个用户/设备
- 🟢 **轻微（low）** - 影响超过10个错误或3个用户/设备
- ✅ **孤立事件** - 影响范围有限

## 最佳实践

1. **提供详细信息** - 尽可能提供完整的问题描述（时间、用户ID、设备ID、服务名等）
2. **上传相关截图** - 如果有错误截图或日志截图，上传图片有助于分析
3. **包含时间信息** - 明确提供问题发生时间，有助于精确查询
4. **描述问题现象** - 详细描述问题现象，有助于定位问题根源

## 故障排除

### 查询结果为空

如果查询结果为空，AI会：
1. 分析可能原因（时间范围、服务名称、字段歧义、时间戳单位错误等）
2. 执行诊断流程（验证服务名称、检查时间范围、逐步放宽查询条件等）
3. 生成初步判断文档
4. 提示用户提供更精确的信息

**详细内容请参考**：[查询优化指南](./resources/query_optimization_guide.md)

### 常见问题

- **时间范围不正确** - 检查时间格式，确保时间在合理范围内
- **服务名称不匹配** - AI会自动执行`list_services`确认实际服务名
- **字段歧义** - AI会自动处理字段歧义，明确指定字段上下文
- **查询结果 rows 为 null** - 通常是字段歧义导致的，需要修复字段定义（参考查询优化指南）

## 注意事项

- 本技能强调AI的核心能力，SigNoz MCP工具只是数据源
- AI会优先使用自己的知识和推理能力分析问题
- MCP工具仅在需要查询监控数据时使用
- 主要工作应该由AI通过思考和推理来完成

## 许可证

MIT
