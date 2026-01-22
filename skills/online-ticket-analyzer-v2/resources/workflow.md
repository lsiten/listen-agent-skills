# 线上工单分析 Skill - 工作流程参考

本文档详细说明了线上工单分析技能的工作流程和技术细节，供AI助手在执行任务时参考。

## 文件组织结构

⚠️ **重要**：为了保持原项目整洁，所有生成的文件必须统一放在 `.online-ticket-analyzer` 目录下。

**目录结构**：
```
项目根目录/
└── .online-ticket-analyzer/          # 所有生成的文件统一放在此目录
    ├── project_context.json          # 项目全局上下文（阶段0生成）
    ├── signoz_config.json            # SigNoz配置信息（阶段0生成）
    ├── tickets/                       # 工单分析目录
    │   └── ticket_YYYYMMDD_xxx/      # 每个工单一个子目录
    │       ├── ticket_context.json   # 工单上下文
    │       ├── mcp_instructions.json  # MCP查询指令
    │       ├── mcp_results.json      # MCP查询结果
    │       ├── analysis_summary.json # 本地分析摘要（关键信息）
    │       ├── preliminary_analysis.md # 初步判断文档（查询结果为空时）
    │       └── solution.md           # 综合解决方案文档
    └── .production-history/          # 历史经验库（可选）
        └── ...
```

## 整体工作流程

```
用户输入问题描述（支持图文、图、文字、文件等）
    ↓
【阶段0：首次使用检查】
    ├─ AI通读项目，生成项目全局上下文（.online-ticket-analyzer/project_context.json）
    └─ AI通读项目，生成SigNoz配置信息（.online-ticket-analyzer/signoz_config.json）
    ↓
【阶段1：准备与指令生成】
    ├─ 加载项目全局上下文和SigNoz配置
    ├─ 解析用户输入（提取工单信息：服务名、时间、用户信息、设备信息、接口信息等）
    ├─ AI分析多发送方和多时间（如果是邮件沟通记录）
    ├─ 计算查询时间范围（支持多个时间点）
    ├─ 保存工单上下文（.online-ticket-analyzer/tickets/ticket_xxx/ticket_context.json）
    └─ 生成MCP调用指令（.online-ticket-analyzer/tickets/ticket_xxx/mcp_instructions.json）
    ↓
【等待AI执行MCP查询】
    ├─ AI读取mcp_instructions.json
    ├─ 调用SigNoz MCP工具
    └─ 保存结果到mcp_results.json（.online-ticket-analyzer/tickets/ticket_xxx/mcp_results.json）
    ↓
【阶段2：综合分析】
    ├─ 加载MCP查询结果
    ├─ 检查查询结果是否为空
    │   ├─ 如果为空：生成初步判断文档（.online-ticket-analyzer/tickets/ticket_xxx/preliminary_analysis.md）
    │   └─ 如果不为空：继续分析流程
    ├─ 本地分析SigNoz数据（重要！不要将原始数据全部丢给大模型）
    │   ├─ 统计错误数量、错误类型分布
    │   ├─ 提取关键错误信息（错误消息、堆栈信息、错误模式）
    │   ├─ 统计影响范围（用户数、设备数、地区分布、时间分布）
    │   └─ 生成关键信息摘要（.online-ticket-analyzer/tickets/ticket_xxx/analysis_summary.json）
    ├─ AI分析关键信息（基于本地提取的关键信息进行推理和分析）
    ├─ 分析代码逻辑
    ├─ 检索历史经验
    ├─ 分析普遍性问题（提取特征，生成广泛查询，判断是否普遍性问题）
    ├─ 生成综合解决方案（仅在查询结果不为空时）
    └─ 输出解决方案文档（.online-ticket-analyzer/tickets/ticket_xxx/solution.md，仅在查询结果不为空时）
```

## 阶段0：首次使用检查

### 主要任务
- **AI通读项目**：从整体项目视角生成配置，不是针对特定工单
- **生成项目上下文**：包含所有服务、架构、技术栈等全局信息
- **生成SigNoz配置**：包含所有API路径映射、字段提取规则、服务名称映射等

### 关键配置信息

**`.online-ticket-analyzer/project_context.json`** 包含：
- 所有服务的完整列表
- 关键文件和目录结构
- 完整的架构和技术栈信息

**`.online-ticket-analyzer/signoz_config.json`** 包含：
- `api_pathname_mapping`：API完整pathname映射（通过AI追踪代码生成）
- `field_extraction_rules`：用户输入模式到实际字段名的映射
- `service_name_mapping`：用户输入模式到实际service.name的映射
- `base_url`：API基础URL配置
- `appVersion`、`environment`：应用版本和环境信息
- 所有环境变量的实际值（从打包配置获取）

## 阶段1：准备与指令生成

### 工单信息提取

从用户输入中提取：
- **服务名称**：优先使用AI生成的service_name_mapping
- **时间信息**：支持多个时间点（工单时间、邮件时间、问题时间）
- **用户信息**：用户ID（转换为user.id字段）
- **设备信息**：设备ID（转换为user.client_id字段）
- **接口信息**：接口路径（优先使用AI生成的api_pathname_mapping）
- **地区信息**：国家、城市
- **发送方信息**：多个发送方（如果是邮件沟通记录）

### 时间范围计算优先级

1. 用户明确指定的时间（--start-time, --end-time）
2. 工单上报时间或邮件发送时间（前后2小时）
   - 如果多个时间点，使用最早和最晚时间
3. 问题发生时间（前后2小时）
   - 如果多个时间点，使用最早和最晚时间
4. 默认：最近1小时

### 时间范围自动调整

⚠️ **关键逻辑**：时间范围调整的判断必须基于**计算出的查询时间范围**，而不是工单时间本身。

**调整规则**：
1. **未来时间判断**：
   - 计算查询时间范围：`start = 最早时间 - 2小时`，`end = 最晚时间 + 2小时`
   - 如果 `start > 当前时间`，说明查询时间范围在未来
   - **只有在这种情况下**，才调整为最近24小时（基于当前时间）
   - ⚠️ **错误示例**：工单时间是 2024-12-31（过去时间），但计算出的查询范围是 2024-12-31 02:00 到 2025-01-04 14:00，这个范围是过去时间，**不应该**调整为当前时间

2. **过去时间处理**：
   - 如果计算出的查询时间范围是过去时间（`end < 当前时间`），**直接使用该时间范围**
   - 如果时间在很久以前（超过30天），提示用户确认时间范围，但**仍然使用该时间范围**

3. **窄时间范围**（小于2小时）：自动扩展为+/- 2小时

**正确示例**：
- 工单时间：2024-12-31 11:13:01（timestamp: 1735617181000）
- 计算查询范围：2024-12-31 09:13:01 到 2024-12-31 13:13:01（前后2小时）
- 当前时间：2026-01-22
- 判断：查询范围是过去时间，**直接使用该时间范围**，不调整

**错误示例**（避免）：
- 工单时间：2024-12-31（过去时间）
- 错误判断：认为工单时间是"未来时间"（因为年份是2024，但实际是过去）
- 错误调整：调整为当前时间（2026-01-22）的最近24小时
- 结果：查询时间变成 2026-01-21 到 2026-01-22，完全错误

## SigNoz执行命令生成

### 查询工具选择优先级

1. **signoz_execute_builder_query（Query Builder v5）** - 强烈推荐（使用毫秒时间戳）
2. **signoz_list_services** - 必须首先执行
   - ⚠️ **重要**：需要**纳秒**时间戳，或使用 `timeRange` 参数（推荐）
   - 推荐使用 `timeRange` 参数（如 "1h", "4h", "24h"），避免时间戳单位错误
3. **signoz_search_logs_by_service** - 备选方案（使用毫秒时间戳）
4. **signoz_get_error_logs** - 快速错误查询（使用毫秒时间戳）

### 时间戳单位说明

⚠️ **关键问题**：不同工具使用不同的时间戳单位！

- **纳秒时间戳**（需要乘以 1,000,000）：
  - `signoz_list_services`
  - `signoz_get_service_top_operations`

- **毫秒时间戳**（标准）：
  - `signoz_execute_builder_query`
  - `signoz_get_error_logs`
  - `signoz_search_logs_by_service`
  - 其他大部分工具

**推荐解决方案**：
- 优先使用 `timeRange` 参数（如 "1h", "4h", "24h"），避免时间戳单位错误
- 如果必须使用 `start`/`end` 参数，确保单位正确：
  - `list_services`: 纳秒（毫秒 × 1,000,000）
  - 其他工具: 毫秒

### Query Builder v5 格式要求

⚠️ **关键格式要求**：

1. **filter格式**：
   - ✅ 使用 `filter`（单数）和 `expression`（SQL-like字符串）
   - ❌ 不使用 `filters`（复数）和 `items` 数组格式

2. **字段歧义处理**（重要！）：
   - 对于有歧义的字段，**必须**在`selectFields`中明确指定`fieldContext`和`fieldDataType`
   - **常见歧义字段**：
     - `service.name`：在resource和attribute上下文中都有string类型（通常使用resource上下文）
     - `user.id`：在attributes上下文中有3种类型：string、bool、number（int64）（通常使用int64类型）
   - **警告示例**：
     ```
     "key service.name is ambiguous, found 2 different combinations of field context and data type: 
     [name=service.name,context=resource,type=string name=service.name,context=attribute,type=string]"
     
     "key user.id is ambiguous, found 3 different combinations of field context and data type: 
     [name=user.id,context=attribute,type=number name=user.id,context=attribute,type=string name=user.id,context=attribute,type=bool]"
     ```
   - **解决方案**：
     - 在`selectFields`中明确指定`fieldContext`和`fieldDataType`：
       ```json
       {
         "selectFields": [
           {
             "name": "service.name",
             "fieldContext": "resource",
             "fieldDataType": "string",
             "signal": "logs"
           },
           {
             "name": "user.id",
             "fieldContext": "attributes",
             "fieldDataType": "int64",
             "signal": "logs"
           }
         ]
       }
       ```
     - **重要规则**：
       - `service.name`：使用`fieldContext: "resource"`（资源级别字段）
       - `user.id`：使用`fieldContext: "attributes"`和`fieldDataType: "int64"`（根据实际数据结构）
       - 所有在filter expression中使用的歧义字段，都必须在selectFields中明确指定
       - 如果查询结果中`rows`为`null`，很可能是字段歧义导致的，需要在selectFields中明确指定所有歧义字段

3. **fieldContext字段**：
   - 一般情况下：查询时不要添加`fieldContext`字段，SigNoz会自动识别
   - 有歧义时：必须明确指定`fieldContext`和`fieldDataType`

4. **formatTableResultForUI**：
   - 必须设置为`true`

5. **having字段**：
   - 必须包含：`"having": {"expression": ""}`

## 阶段2：综合分析

### 本地数据分析（重要！）

⚠️ **关键原则**：SigNoz查询到的数据必须先在本地进行分析和处理，提取关键信息后再提供给AI。**不要将原始查询结果直接全部丢给大模型**。

**本地分析流程**：
1. 统计错误数量、错误类型分布
2. 提取关键错误信息（错误消息、堆栈信息、错误模式）
3. 统计影响范围（用户数、设备数、地区分布、时间分布）
4. 提取关键字段值（用户ID、设备ID、IP地址、地理位置、浏览器版本、应用版本等）
5. 识别错误模式和趋势
6. 生成关键信息摘要（只包含关键统计数据和重要发现）
7. 将关键信息摘要提供给AI进行进一步分析

### 普遍性问题分析

**分析流程**：
1. 提取关键特征（国家/地区、环境、服务版本、浏览器版本、错误类型、接口路径）
2. 生成广泛查询（不限定用户ID和设备ID，扩展时间范围到前后24小时）
3. AI执行查询
4. 分析结果，判断普遍性级别：
   - 🔴 严重（critical）：影响超过50个错误或10个用户/设备，且影响超过2个国家或5个城市
   - 🟠 高（high）：影响超过50个错误或10个用户/设备，且影响超过1个国家或3个城市
   - 🟡 中等（medium）：影响超过20个错误或5个用户/设备
   - 🟢 轻微（low）：影响超过10个错误或3个用户/设备
   - ✅ 孤立事件：影响范围有限

## 关键信息识别流程

⚠️ **重要**：所有工单查询需要的关键信息，必须通过AI阅读完整项目后，综合配置信息、环境配置、打包配置给出，而不是简单的正则匹配。

### 接口路径识别流程

1. 通读项目代码，查找所有API调用位置
2. 追踪createRequest方法，找到baseUrl的来源
3. 查找config中baseUrl的定义，追踪到环境变量
4. 从打包配置（vite.config.ts）获取环境变量的实际值
5. 解析baseUrl，提取路径部分
6. 组合完整pathname：baseUrl路径部分 + API相对路径
7. 生成api_pathname_mapping配置

## 迭代式查询

**查询流程**：
1. **首次查询**：基于工单中的基础信息进行查询
2. **特征提取**：从查询结果中提取特征信息
3. **迭代查询**：基于提取的特征信息，生成更精确的查询条件
4. **逐步补充**：如果首次查询没有用户ID，可以根据设备ID等信息进行查询
