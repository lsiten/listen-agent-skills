# 线上工单分析 Skill - 主要流程

## 整体工作流程

```
用户输入问题描述（支持图文、图、文字、文件等）
    ↓
【阶段0：首次使用检查】
    ├─ AI通读项目，生成项目全局上下文（project_context.json）
    ├─ AI通读项目，生成SigNoz配置信息（signoz_config.json）
    └─ 如果配置不全，脚本扫描补充
    ↓
【阶段1：准备与指令生成】
    ├─ 加载项目全局上下文和SigNoz配置
    ├─ 解析用户输入（提取工单信息：服务名、时间、用户信息、设备信息、接口信息等）
    ├─ AI分析多发送方和多时间（如果是邮件沟通记录）
    ├─ 计算查询时间范围（支持多个时间点）
    ├─ 保存工单上下文
    └─ 生成MCP调用指令（mcp_instructions.json）
    ↓
【等待AI执行MCP查询】
    ├─ AI读取mcp_instructions.json
    ├─ 调用SigNoz MCP工具
    └─ 保存结果到mcp_results.json
    ↓
【阶段2：综合分析】
    ├─ 加载MCP查询结果
    ├─ 检查查询结果是否为空
    │   ├─ 如果为空：生成初步判断文档，提示用户提供更精确信息
    │   └─ 如果不为空：继续分析流程
    ├─ 处理日志数据（深度分析，提取关键错误信息）
    ├─ 分析代码逻辑
    ├─ 检索历史经验
    ├─ 分析普遍性问题（提取特征，生成广泛查询，判断是否普遍性问题）
    ├─ 生成综合解决方案（仅在查询结果不为空时）
    └─ 输出解决方案文档（仅在查询结果不为空时）
```

## 阶段0：首次使用检查

### 主要任务
- **AI通读项目**：从整体项目视角生成配置，不是针对特定工单
- **生成项目上下文**：包含所有服务、架构、技术栈等全局信息
- **生成SigNoz配置**：包含所有API路径映射、字段提取规则、服务名称映射等

### 关键配置信息

**project_context.json** 包含：
- 所有服务的完整列表
- 关键文件和目录结构
- 完整的架构和技术栈信息

**signoz_config.json** 包含：
- `api_pathname_mapping`：API完整pathname映射（通过AI追踪代码生成）
- `field_extraction_rules`：用户输入模式到实际字段名的映射
- `service_name_mapping`：用户输入模式到实际service.name的映射
- `base_url`：API基础URL配置
- `appVersion`、`environment`：应用版本和环境信息
- 所有环境变量的实际值（从打包配置获取）

## 阶段1：准备与指令生成

### 主要任务
1. 加载项目全局上下文和SigNoz配置
2. 解析用户输入，提取工单信息
3. AI分析多发送方和多时间（如果是邮件沟通记录）
4. 计算查询时间范围
5. 生成MCP调用指令

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

- **未来时间**：自动调整为最近24小时
- **窄时间范围**（小于2小时）：自动扩展为+/- 2小时

## SigNoz执行命令生成主要事项

### 1. 查询工具选择优先级

**推荐优先级（从高到低）：**

1. **signoz_execute_builder_query（Query Builder v5）** - 强烈推荐
   - 更灵活，支持复杂过滤条件
   - 字段路径更直观
   - 支持多条件组合查询

2. **list_services** - 必须首先执行
   - 获取服务列表，确认服务名称
   - 实际运行时的服务名可能与代码中的不同

3. **search_logs_by_service** - 备选方案
4. **get_error_logs** - 快速错误查询

### 2. Query Builder v5 格式要求

⚠️ **关键格式要求**：

1. **filter格式**：
   - ✅ 使用 `filter`（单数）和 `expression`（SQL-like字符串）
   - ❌ 不使用 `filters`（复数）和 `items` 数组格式

2. **字段歧义处理**（重要！）：
   - 对于有歧义的字段（如`user.id`），**必须**在`selectFields`中明确指定`fieldContext`和`fieldDataType`
   - **问题**：`user.id`字段在attributes上下文中有3种类型：string、bool、number（int64）
   - **警告示例**：
     ```
     "key `user.id` is ambiguous, found 3 different combinations of field context and data type: 
     [name=user.id,context=attribute,type=string name=user.id,context=attribute,type=bool name=user.id,context=attribute,type=number]"
     ```
   - **解决方案**：
     - 在`selectFields`中明确指定`fieldContext`和`fieldDataType`：
       ```json
       {
         "name": "user.id",
         "fieldContext": "attributes",
         "fieldDataType": "int64",
         "signal": "logs"
       }
       ```
     - 根据实际数据结构，`user.id`是int64（number）类型，必须明确指定
     - 这样filter expression中的`user.id`就能正确解析为int64类型
     - 如果仍然遇到"key is ambiguous"警告，确保查询中使用的字段在selectFields中已明确指定

3. **fieldContext字段**：
   - 一般情况下：查询时不要添加`fieldContext`字段，SigNoz会自动识别
   - 有歧义时：必须明确指定`fieldContext`和`fieldDataType`

4. **formatTableResultForUI**：
   - 必须设置为`true`，以便正确显示结果

5. **having字段**：
   - 必须包含：`"having": {"expression": ""}`

6. **order字段**：
   - key只包含name：`{"key": {"name": "timestamp"}, "direction": "desc"}`

### 3. 查询指令结构

```json
{
  "ticket_id": "ticket_20250120_abc123",
  "time_range": {
    "start": 1737361800000,
    "end": 1737365400000,
    "start_display": "2025-01-20 10:00:00",
    "end_display": "2025-01-20 11:00:00"
  },
  "services": ["user-service"],
  "queries": [
    {
      "priority": 1,
      "tool": "list_services",
      "params": {
        "timeRange": "1h",
        "start": 1737361800000,
        "end": 1737365400000
      },
      "description": "获取服务列表，确认服务名称（必须首先执行）"
    },
    {
      "priority": 2,
      "tool": "signoz_execute_builder_query",
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
                  "filter": {
                    "expression": "service.name IN ('user-service') AND severity_text IN ('error', 'Error', 'ERROR')"
                  },
                  "having": {
                    "expression": ""
                  }
                }
              }
            ]
          },
          "formatOptions": {
            "formatTableResultForUI": true,
            "fillGaps": false
          },
          "variables": {}
        }
      },
      "description": "查询错误日志"
    }
  ]
}
```

### 4. 查询执行注意事项

1. **必须首先执行list_services**：获取服务列表，确认服务名称
2. **服务名过滤**：在Query Builder中添加`service.name`过滤条件
3. **字段类型匹配**：确保字段类型匹配（如`user.id`是int64类型，值也应该是数字）
4. **时间范围验证**：自动调整未来时间和窄时间范围
5. **迭代查询**：支持从查询结果中提取特征信息，进行更精确的查询

### 5. 查询结果为空处理

如果查询结果为空：
- 生成初步判断文档（`preliminary_analysis.md`）
- 分析可能原因（时间范围、服务名称、字段歧义等）
- 提示用户提供更精确的信息
- **不生成完整解决方案**，等待用户提供更精确信息后重新分析

## SigNoz数据结构

### 字段上下文（Field Context）

SigNoz使用OpenTelemetry标准，将字段分为不同的上下文级别：

| 上下文类型 | 说明 | 示例字段 |
|-----------|------|---------|
| **resource** | 资源级别字段，描述服务本身的信息 | `service.name`, `service.version`, `service.environment` |
| **attributes** | 属性级别字段，描述日志的具体内容 | `body`, `severity_text`, `user.id`, `user.client_id` |
| **span** | 跨度级别字段，用于追踪信息 | `span_id`, `parent_span_id` |
| **log** | 日志级别字段，日志特有的元数据 | `log_level`, `log_source` |

### 实际数据结构

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
    "browser.name": "CamScannerWindows",
    "browser.version": "1.0.17",
    "message": "错误信息",
    "name": "Error",
    "stack": "错误堆栈",
    "request.pathname": "/sync/revert_dir_list"
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

### 重要字段说明

#### 资源级别字段（Resource）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `service.name` | string | 应用名称（格式：事业部.小组.项目名） | 服务过滤、分组 |
| `service.version` | string | 应用版本 | 版本追踪 |
| `service.environment` | string | 运行环境 | 环境区分（dev/staging/prod） |

**注意**：
- 实际数据结构中，服务信息存储在 `resources` 对象中（复数），不是 `resource`
- 在Query Builder中使用时，直接使用 `service.name`，不需要 `resources.` 前缀

#### 用户和设备字段（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `user.id` | int64 | 用户ID | 用户过滤、查询 |
| `user.client_id` | string | 客户端ID/设备ID | 设备过滤、查询 |

**重要说明**：
- 字段名是 `user.id`（点分隔），不是 `user_id`
- 字段名是 `user.client_id`（点分隔），不是 `client_id` 或 `device_id`
- `user.id`字段类型是`int64`，值应该是数字，不需要引号
- 这些字段位于`attributes`对象中，但在Query Builder中直接使用`user.id`即可

#### 地理位置字段（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `geo.city_name` | string | 城市名称 | 地理位置过滤 |
| `geo.country_name` | string | 国家名称 | 地理位置过滤 |
| `geo.location.lat` | float | 纬度 | 地理位置查询 |
| `geo.location.lon` | float | 经度 | 地理位置查询 |

#### 请求日志字段（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `request.pathname` | string | 请求路径 | 接口路径查询 |
| `request.host` | string | 请求域名 | 接口域名分析 |
| `request.method` | string | 请求方法 | 方法过滤 |
| `response.status` | int64 | 响应状态码 | 错误过滤（500/404等） |
| `response.errno` | string | 业务错误码 | 业务错误分析 |

#### 错误日志字段（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `message` | string | 错误信息 | 错误内容查询 |
| `name` | string | 错误类型 | 错误分类 |
| `stack` | string | 错误堆栈 | 堆栈分析 |
| `severity_text` | string | 日志严重程度文本 | 错误过滤 |
| `severity_number` | int64 | 日志严重程度数字 | 错误过滤（17=ERROR, 18=FATAL等） |

#### 通用字段（Attributes）

| 字段名 | 数据类型 | 说明 | 使用场景 |
|--------|---------|------|---------|
| `body` | string | 日志内容（通用） | 日志正文查询、全文搜索 |
| `timestamp` | int64 | 时间戳（毫秒） | 时间范围查询、排序 |
| `trace_id` | string | 追踪ID | 追踪关联 |
| `span_id` | string | 跨度ID | 跨度关联 |

### 字段路径格式

在查询和结果解析中，字段可以使用以下格式：

1. **简化格式**（推荐）：
   - `service.name` - 自动识别为resource级别
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

### 查询示例

#### 示例1：查询特定服务的错误日志

```json
{
  "filter": {
    "expression": "service.name IN ('事业部.小组.项目名') AND severity_text IN ('error', 'Error', 'ERROR')"
  },
  "having": {
    "expression": ""
  }
}
```

#### 示例2：查询特定用户的日志

```json
{
  "filter": {
    "expression": "user.id = 4472431079"
  },
  "having": {
    "expression": ""
  }
}
```

**注意**：
- 字段名是 `user.id`（点分隔），不是 `user_id`
- user.id字段类型是int64，值应该是数字，不需要引号
- ⚠️ **重要**：`user.id`字段有歧义，必须在selectFields中明确指定`fieldContext: "attributes"`和`fieldDataType: "int64"`

#### 示例3：查询特定设备的日志

```json
{
  "filter": {
    "expression": "user.client_id = 'B4SMfdd5F0FW83e1a18rfA5J'"
  },
  "having": {
    "expression": ""
  }
}
```

**注意**：
- 字段名是 `user.client_id`（点分隔），不是 `client_id` 或 `device_id`
- ⚠️ **重要**：`user.client_id`字段可能有歧义，建议在selectFields中明确指定`fieldContext: "attributes"`和`fieldDataType: "string"`

#### 示例4：查询特定接口的错误日志

```json
{
  "filter": {
    "expression": "request.pathname = '/api/login' AND response.status IN (500, 502, 503)"
  },
  "having": {
    "expression": ""
  }
}
```

#### 示例5：处理字段歧义

如果遇到"key is ambiguous"警告，需要在selectFields中明确指定fieldContext和fieldDataType：

**警告示例**：
```
"key `user.id` is ambiguous, found 3 different combinations of field context and data type: 
[name=user.id,context=attribute,type=string name=user.id,context=attribute,type=bool name=user.id,context=attribute,type=number]"
```

**解决方案**：在selectFields中明确指定fieldContext和fieldDataType：

```json
{
  "selectFields": [
    {
      "name": "user.id",
      "fieldContext": "attributes",
      "fieldDataType": "int64",
      "signal": "logs"
    }
  ],
  "filter": {
    "expression": "user.id = 4472431079"
  },
  "having": {
    "expression": ""
  }
}
```

**重要**：
- `user.id`字段在attributes上下文中有3种类型：string、bool、number（int64）
- 根据实际数据结构，`user.id`是int64（number）类型
- 必须在selectFields中明确指定`fieldContext: "attributes"`和`fieldDataType: "int64"`
- 这样filter expression中的`user.id`就能正确解析为int64类型

## 阶段2：综合分析

### 主要任务

1. **加载MCP查询结果**
2. **检查查询结果是否为空**
   - 如果为空：生成初步判断文档，提示用户提供更精确信息
   - 如果不为空：继续分析流程
3. **处理日志数据**：深度分析，提取关键错误信息
4. **分析代码逻辑**：基于错误信息定位代码文件
5. **检索历史经验**：从`.production-history/`目录检索相似经验
6. **分析普遍性问题**：
   - 提取关键特征（国家/地区、环境、服务版本、浏览器版本等）
   - 生成广泛查询（不限定用户ID和设备ID）
   - 判断是否是普遍性问题
   - 如果是普遍性问题，特别标注
7. **生成综合解决方案**（仅在查询结果不为空时）
8. **输出解决方案文档**（仅在查询结果不为空时）

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
5. 如果是普遍性问题，在解决方案中特别标注

## 关键信息识别流程

⚠️ **重要**：所有工单查询需要的关键信息，必须通过AI阅读完整项目后，综合配置信息、环境配置、打包配置给出，而不是简单的正则匹配。

### 1. 接口路径识别

**流程**（必须完整执行）：
1. 通读项目代码，查找所有API调用位置
2. 追踪createRequest方法，找到baseUrl的来源
3. 查找config中baseUrl的定义，追踪到环境变量
4. 从打包配置（vite.config.ts）获取环境变量的实际值
5. 解析baseUrl，提取路径部分
6. 组合完整pathname：baseUrl路径部分 + API相对路径
7. 生成api_pathname_mapping配置

### 2. 字段提取规则识别

**流程**：
1. 通读项目代码，查找所有字段的使用方式
2. 了解字段的实际命名规则和嵌套结构
3. 了解用户输入中可能出现的字段名称变体
4. 生成field_extraction_rules配置

### 3. 服务名称映射识别

**流程**：
1. 通读项目代码，查找所有服务的定义和使用
2. 了解服务的实际命名规则
3. 了解用户输入中可能出现的服务名称变体
4. 生成service_name_mapping配置

## 迭代式查询

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
- 如果没有用户ID，可以根据工单中的特征信息（如设备ID）查询到的数据更新设备ID信息
- 查询过程中特征信息会慢慢补充
- 每次查询都会在selectFields中包含这些特征字段，以便提取特征信息
