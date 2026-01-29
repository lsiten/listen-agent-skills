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
    │       ├── ticket_info.json      # 工单基本信息（阶段1生成）
    │       ├── ticket_context.json   # 工单上下文（阶段1生成，可选）
    │       ├── mcp_instructions.json  # MCP查询指令（阶段1生成）
    │       ├── mcp_results.json      # MCP查询结果（执行查询后生成，必须）
    │       ├── analysis_summary.json # 本地分析摘要（阶段2生成，关键信息）
    │       ├── preliminary_analysis.md # 初步判断文档（查询结果为空时生成）
    │       └── solution.md           # 综合解决方案文档（查询结果不为空时生成）
    └── .production-history/          # 历史经验库（可选）
        └── ...
```

## 整体工作流程

```
用户输入问题描述（支持图文、图、文字、文件等）
    ↓
【阶段0：首次使用检查】
    ├─ 检查 .online-ticket-analyzer/project_context.json 是否存在
    ├─ 检查 .online-ticket-analyzer/signoz_config.json 是否存在
    ├─ 如果不存在：AI通读项目，生成配置文件
    └─ 如果都存在：进入阶段1
    ↓
【阶段1：日志查询循环】⚠️ 这是一个循环过程！
    │
    ├─ 🔄 【循环开始】
    │
    ├─ 📥 【信息收集】从三个来源整理查询条件（优先级从高到低）：
    │   ├─ 1️⃣ 工单信息（优先）：从工单内容中提取（服务名、时间、错误信息、截图等）
    │   ├─ 2️⃣ 代码分析信息（优先）：从代码/配置中分析得到（接口路径映射、服务名映射、错误码等）
    │   └─ 3️⃣ 用户补充信息（最后）：仅在穷尽自动方法后才询问用户
    │
    ├─ 🔍 【查询条件评估】
    │   ├─ 条件充足 → 执行查询
    │   └─ 条件不足 → 先尝试查询，从结果中提取信息；穷尽自动方法后才询问用户
    │
    ├─ 🚀 【执行查询】
    │   ├─ 更新 ticket_info.json（记录迭代次数和状态）
    │   ├─ 更新 mcp_instructions.json
    │   ├─ 执行 SigNoz MCP 查询
    │   └─ 保存结果到 mcp_results.json
    │
    ├─ 📊 【结果评估】
    │   ├─ ✅ 查询到相关日志 → 退出循环，进入阶段2
    │   ├─ 🔍 有结果但缺少用户信息 → 从结果中提取用户ID/设备ID，进行更精确查询
    │   ├─ ❌ 无结果或不相关：
    │   │   ├─ 🔄 自动调整策略（必须穷尽以下方法）：
    │   │   │   ├─ 放宽查询条件
    │   │   │   ├─ 扩展时间范围（±2h → ±4h → ±24h）
    │   │   │   ├─ 切换时间优先级
    │   │   │   └─ 尝试其他关键词/接口路径
    │   │   └─ 🚨 只有穷尽自动方法后 → 才向用户请求更多信息
    │   └─ 🔄 用户提供新信息 → 回到信息收集，继续循环
    │
    ├─ 🚪 【循环退出条件】
    │   ├─ ✅ 查询到能够定位问题的相关日志
    │   ├─ ⏭️ 用户明确要求跳过日志查询
    │   └─ ❌ 用户确认无法提供更多信息，且所有策略已尝试
    │
    └─ 🔄 【循环结束】
    ↓
【阶段2：综合分析】⚠️ 只有阶段1退出后才能进入！
    ├─ 加载MCP查询结果
    ├─ 检查查询结果是否为空
    │   ├─ 如果为空（用户跳过）：生成初步判断文档（preliminary_analysis.md）
    │   └─ 如果不为空：继续分析流程
    ├─ 本地分析SigNoz数据（重要！不要将原始数据全部丢给大模型）
    │   ├─ 统计错误数量、错误类型分布
    │   ├─ 提取关键错误信息（错误消息、堆栈信息、错误模式）
    │   ├─ 统计影响范围（用户数、设备数、地区分布、时间分布）
    │   └─ 生成关键信息摘要（analysis_summary.json）
    ├─ AI分析关键信息（基于本地提取的关键信息进行推理和分析）
    ├─ 分析代码逻辑
    ├─ 检索历史经验
    ├─ 分析普遍性问题（提取特征，生成广泛查询，判断是否普遍性问题）
    ├─ 生成综合解决方案
    └─ 输出解决方案文档（solution.md 或 preliminary_analysis.md）
```

## 阶段0：首次使用检查

### 主要任务
- **AI通读项目**：从整体项目视角生成配置，不是针对特定工单
- **生成项目上下文**：包含所有服务、架构、技术栈等全局信息
- **生成SigNoz配置**：包含所有API路径映射、字段提取规则、服务名称映射等

### 关键配置信息

⚠️ **重要**：以下信息文件每次生成的格式可能不同，但必须字段必须包含，尽量要的字段尽量包含，其他补充字段可随意。

**`.online-ticket-analyzer/project_context.json`** 字段规范：

**必须字段**（必须包含）：
- `services`：所有服务的完整列表（数组）
- `architecture`：项目架构信息（对象或字符串）
- `tech_stack`：技术栈信息（对象或数组）

**尽量要的字段**（尽量包含）：
- `key_files`：关键文件列表（数组）
- `directory_structure`：目录结构信息（对象或字符串）
- `project_name`：项目名称（字符串）
- `description`：项目描述（字符串）

**其他补充字段**（可随意）：
- 可以根据项目实际情况添加其他字段，如：`dependencies`、`build_config`、`deployment_info`等

**`.online-ticket-analyzer/signoz_config.json`** 字段规范：

**必须字段**（必须包含）：
- `api_pathname_mapping`：API完整pathname映射（对象），格式：`{"用户输入模式": "实际pathname"}`
- `service_name_mapping`：用户输入模式到实际service.name的映射（对象），格式：`{"用户输入模式": "实际service.name"}`
- `base_url`：API基础URL配置（对象或字符串）

**尽量要的字段**（尽量包含）：
- `field_extraction_rules`：用户输入模式到实际字段名的映射（对象）
- `appVersion`：应用版本信息（字符串）
- `environment`：环境信息（字符串，如：dev/staging/prod）
- `env_vars`：环境变量的实际值（对象），从打包配置获取

**其他补充字段**（可随意）：
- 可以根据项目实际情况添加其他字段，如：`log_levels`、`error_patterns`、`custom_fields`等

## 阶段1：日志查询循环

⚠️ **核心理念**：阶段1是一个**循环过程**，主要目的是查询到相关日志。

🔴 **重要原则**：尽量从工单和代码中自动提取/推断信息，只有在穷尽自动方法后才询问用户！

### 信息收集（三个来源）

⚠️ **关键原则**：查询条件必须从三个来源综合整理，而不是仅依赖单一来源。

🔴 **信息收集优先级策略（重要！）**：
1. **首先**：尽量从**工单信息**和**代码分析**中提取必要的查询条件
2. **其次**：如果工单和代码中确实无法获取某些关键信息，再向用户询问
3. **原则**：减少对用户的打扰，尽可能自动从已有信息中推断

#### 1️⃣ 来源一：工单信息（优先级：高）

从工单内容中直接提取的信息：
- **时间信息**：问题发生时间、邮件发送时间
- **用户信息**：用户ID、账号、邮箱
- **设备信息**：设备ID、客户端ID
- **错误信息**：错误截图、错误描述
- **功能描述**：涉及的功能、页面
- **操作描述**：用户操作步骤

⚠️ **重要**：工单中可能包含隐藏信息，需要仔细分析：
- 截图中可能包含用户ID、设备ID、时间戳等
- 邮件转发链中可能包含原始报错时间
- 用户描述中可能隐含功能/接口信息

#### 2️⃣ 来源二：代码分析信息（优先级：高）

从代码中分析得到的辅助信息：
- **接口路径映射**：从 signoz_config.json 的 api_pathname_mapping 获取
- **服务名映射**：从 signoz_config.json 的 service_name_mapping 获取
- **字段映射**：从 signoz_config.json 的 field_extraction_rules 获取
- **代码逻辑分析**：读取相关代码文件，理解功能实现
- **错误码映射**：从代码中分析错误码定义

⚠️ **重要**：代码分析可以补充大量信息：
- 通过功能描述反推可能涉及的接口路径
- 通过错误描述反推可能的错误类型和日志关键词
- 通过业务逻辑分析可能的出错点

#### 3️⃣ 来源三：用户补充信息（优先级：低 - 仅在必要时询问）

用户在对话过程中提供的额外信息：
- 用户回答问题时提供的更精确信息
- 用户补充的用户ID、设备ID
- 用户提供的更精确的时间范围
- 用户确认的功能/接口信息
- 用户提供的其他定位信息（IP、地理位置等）

🚨 **何时向用户询问信息**：
- ❌ **不要**：在还没尝试从工单和代码中提取信息时就询问用户
- ❌ **不要**：在还没尝试使用已有信息进行查询时就询问用户
- ✅ **可以**：在工单和代码中确实无法获取，且查询无结果时询问用户
- ✅ **可以**：在自动调整策略都尝试过后仍无结果时询问用户

⚠️ **重要**：每次用户提供新信息后，必须将新信息整合到现有查询条件中，然后重新进入查询循环。

### 查询条件评估

#### 必须条件（缺一不可）
- **服务名称**：必须知道查询哪个服务
- **时间范围**：必须有查询时间范围

#### 推荐条件（强烈建议，但可尝试无条件查询）
- **用户标识**：user.id 或 user.client_id（先尝试从工单/代码推断，或从查询结果中提取）
- **接口路径**：相关功能的API路径

#### 🔴 条件不足时的处理策略（重要！）

🚨 **核心原则**：先尝试查询，再考虑询问用户！

**处理流程**：
1. 【自动推断】从工单和代码中尽可能提取/推断信息
2. 【尝试查询】即使信息不完整，也先尝试查询，从结果中提取更多信息
3. 【自动调整】如果查询无结果，尝试放宽条件、扩展时间、切换时间优先级等
4. 【最后手段】只有在上述方法都失败后，才询问用户

❌ **禁止行为**：
- 一开始就询问用户提供用户ID/设备ID
- 未尝试查询就要求用户补充信息
- 查询一次无结果就立即询问用户

### 结果评估与循环

查询执行后，评估结果：

#### ✅ 查询到相关日志
- 日志数量 > 0
- 日志内容与问题相关
- → **退出循环，进入阶段2**

#### ❌ 无结果或结果不相关

执行以下**自动调整策略**（按顺序尝试）：
1. **检查字段歧义** - 如果 rows 为 null，检查 warnings
2. **验证服务名称** - 使用 signoz_list_services 确认
3. **放宽查询条件** - 移除部分过滤条件
4. **扩展时间范围** - 从 ±2小时 扩展到 ±4小时、±24小时
5. **切换时间优先级** - 尝试其他时间点

如果自动调整后仍无结果：
- **向用户请求更多信息**
- 明确说明已尝试的策略和结果
- 询问用户是否有其他信息可以提供

### 循环退出条件

满足以下任一条件时退出循环：
- ✅ 查询到能够定位问题的相关日志
- ⏭️ 用户明确要求跳过日志查询
- ❌ 用户确认无法提供更多信息，且所有查询策略都已尝试

### ticket_info.json 字段规范

⚠️ **重要**：必须生成`.online-ticket-analyzer/tickets/ticket_xxx/ticket_info.json`文件。

**必须字段**（必须包含）：
- `ticket_id`：工单ID（字符串），格式：`ticket_YYYYMMDD_xxx`
- `problem`：问题描述（字符串）
- `query_loop_status`：查询循环状态（对象），包含：
  - `current_iteration`：当前迭代次数
  - `status`：状态（`in_progress` / `completed` / `skipped`）
  - `exit_reason`：退出原因（如果已退出）

**尽量要的字段**（尽量包含）：
- `sources`：信息来源汇总（对象），包含：
  - `ticket_info`：从工单提取的信息
  - `user_provided`：用户补充的信息
  - `code_analysis`：从代码分析的信息
- `user_id`：用户ID
- `client_id`：设备ID
- `service`：服务名称
- `times`：时间信息数组
- `keywords`：关键词数组

**其他补充字段**（可随意）：
- 可以根据工单实际情况添加其他字段

### 时间范围计算优先级

⚠️ **重要约束**：最长查询时间范围为3天。

**时间优先级（从高到低）**：

1. **明确说明的发生时间前后2小时**（最高优先级）
   - 如果工单中明确说明了问题发生时间，优先使用该时间
   - 计算范围：`start = 明确说明的发生时间 - 2小时`，`end = 明确说明的发生时间 + 2小时`
   - ⚠️ **重要**：必须基于工单中的实际时间戳计算，不能使用当前时间

2. **邮件中最早发送时间前后2小时**（次优先级）
   - 如果工单中没有明确说明发生时间，使用邮件中最早发送的时间
   - 如果工单中有多个邮件沟通时间点，使用邮件中最早发送的时间
   - 计算范围：`start = 邮件中最早发送时间 - 2小时`，`end = 邮件中最早发送时间 + 2小时`
   - ⚠️ **重要**：必须基于工单中的实际时间戳计算，不能使用当前时间

3. **最近1天时间**（第三优先级）
   - 如果前两个优先级都查询无结果，使用最近1天时间
   - 计算范围：`start = 当前时间 - 24小时`，`end = 当前时间`

4. **工单中其他提到的时间点当天**（最低优先级）
   - 如果前三个优先级都无结果，依次查询工单中其他提到的时间点当天
   - 计算范围：每个时间点的当天（00:00:00 到 23:59:59）

**查询策略**：

1. **时间区间内的完整查询**：
   - 每个时间区间内需要**完整地**根据工单信息查询相关的所有逻辑
   - 查询顺序（根据工单场景逐步扩展）：
     - **第一步**：如果功能涉及到接口查询，先查该用户接口相关数据
     - **第二步**：如果没有结果，查询该用户报错相关数据
     - **第三步**：如果还是没有，查询该用户对应时间段所有日志
     - **第四步**：根据不同场景，可能还需要查询其他相关数据（如设备信息、地理位置等）
   - ⚠️ **重要**：不同场景查询的内容可能有差异，需要根据工单信息灵活调整
   - ⚠️ **重要**：一般不会从`body`中去匹配关键词
     - 优先使用结构化字段进行过滤（如`message`、`severity_text`、`request.pathname`等）
     - 只有在确实需要搜索日志内容时，才使用`body LIKE '%关键词%'`或`message LIKE '%关键词%'`
     - 避免过度使用`body LIKE`查询，因为性能较差

2. **时间切换条件**：
   - ⚠️ **关键逻辑**：时间切换**不是**某个查询为空就切换
   - 而是：当前时间区间内**所有查询都执行完毕**，且**所有查询结果都无法定位到问题**（无数据或数据不相关），才切换到下一个时间优先级
   - **提前终止**：如果当前时间区间内**任意一个查询**查到符合要求的数据（**有数据并且相关数据能够定位到问题**），则**不再查询**后续时间优先级
   - ⚠️ **重要判断**：仅仅有数据还不够，必须判断数据是否**相关**和**能够定位到问题**

3. **超时重试机制**：
   - 如果查询超时，自动优化时间区间长度（缩短为原来的一半），继续自动重试对应的查询
   - 最多重试3次，如果仍然超时，记录错误并继续当前时间区间内的下一个查询

### 时间范围自动调整

⚠️ **关键逻辑**：时间范围调整的判断必须基于**计算出的查询时间范围**，而不是工单时间本身。

**调整规则**：
1. **未来时间判断**：
   - 如果 `start > 当前时间`，说明查询时间范围在未来
   - **只有在这种情况下**，才调整为最近24小时（基于当前时间）
   - ⚠️ **错误示例**：工单时间是 2024-12-31（过去时间），但计算出的查询范围是 2024-12-31 02:00 到 2025-01-04 14:00，这个范围是过去时间，**不应该**调整为当前时间

2. **过去时间处理**：
   - 如果计算出的查询时间范围是过去时间（`end < 当前时间`），**直接使用该时间范围**
   - 如果时间在很久以前（超过30天），提示用户确认时间范围，但**仍然使用该时间范围**

3. **时间范围限制**：
   - ⚠️ **最长3天**：任何查询时间范围不能超过3天
   - 如果计算出的时间范围超过3天，自动截断为3天（保留最接近当前时间的3天）

4. **窄时间范围**（小于2小时）：自动扩展为+/- 2小时

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

## 查询诊断和优化

### 查询诊断流程

当查询结果为空（`rows` 为 `null` 或 `[]`）时，按以下流程进行诊断：

1. **检查字段歧义**（如果 `rows` 为 `null`）：
   - 检查查询结果中的 `warnings` 字段
   - 如果有字段歧义警告，必须修复：
     - 在 `filter.expression` 中使用完整前缀（`resource.service.name`、`attribute.user.id`）
     - 在 `selectFields` 中明确指定 `fieldContext` 和 `fieldDataType`
   - 修复后重新执行查询

2. **验证服务名称**：
   - 执行 `signoz_list_services` 确认服务名称是否正确
   - 使用 `timeRange` 参数（推荐）或确保时间戳单位正确（纳秒）
   - 如果服务名称不匹配，更新查询条件

3. **检查时间范围**：
   - 验证时间范围是否合理（不是未来时间、不过窄、不过长）
   - 检查时间戳单位是否正确（纳秒 vs 毫秒）
   - 如果时间范围有问题，自动调整后重新查询

4. **逐步放宽查询条件**：
   - 先查询服务 + 时间范围（不限定用户/设备）
   - 如果有数据，再逐步添加过滤条件（用户ID → 错误级别 → 接口路径）
   - 如果放宽条件后仍无结果，继续下一步

5. **扩展时间范围**：
   - 如果当前时间范围无数据，尝试扩展时间范围
   - 从 ±2 小时扩展到 ±4 小时或 ±24 小时
   - 如果扩展后仍无结果，继续下一步

6. **切换到其他时间优先级**：
   - 如果当前时间优先级无数据，切换到下一个时间优先级
   - 按优先级依次尝试：明确说明的发生时间 → 邮件最早时间 → 最近1天 → 其他时间点

7. **检查字段值**：
   - 使用 `signoz_get_logs_field_values` 检查字段的实际值
   - 确认字段值是否存在和正确

### 查询优化策略

详细内容请参考：[查询优化指南](./query_optimization_guide.md)

**核心策略**：
1. **渐进式查询**：从宽泛到精确，逐步缩小范围
2. **多时间优先级查询**：按时间优先级依次查询，找到数据后提前终止
3. **迭代式查询**：根据查询结果动态调整查询策略
4. **容错查询**：查询失败时自动尝试替代方案

## SigNoz执行命令生成

### 查询工具选择优先级

**推荐优先级（从高到低）：**

1. **signoz_execute_builder_query（Query Builder v5）** - 强烈推荐（使用毫秒时间戳）
   - 支持日志（logs）、指标（metrics）、追踪（traces）三种数据源
   - 更灵活，支持复杂过滤条件

2. **signoz_list_services** - 必须首先执行
   - ⚠️ **重要**：需要**纳秒**时间戳，或使用 `timeRange` 参数（推荐）
   - 推荐使用 `timeRange` 参数（如 "1h", "4h", "24h"），避免时间戳单位错误

3. **signoz_search_logs_by_service** - 按服务搜索日志（使用毫秒时间戳）
4. **signoz_get_error_logs** - 快速错误查询（使用毫秒时间戳）

### SigNoz MCP 工具完整列表

**日志查询工具**：
- `signoz_execute_builder_query` - Query Builder v5 查询（推荐，支持 logs/metrics/traces）
- `signoz_search_logs_by_service` - 按服务搜索日志
- `signoz_get_error_logs` - 获取错误日志（ERROR/FATAL）
- `signoz_list_log_views` - 列出保存的日志视图
- `signoz_get_log_view` - 获取日志视图详情
- `signoz_get_logs_available_fields` - 获取日志可用字段列表
- `signoz_get_logs_field_values` - 获取日志字段值（用于过滤选项）

**追踪查询工具**：
- `signoz_search_traces_by_service` - 按服务搜索追踪
- `signoz_get_trace_details` - 获取追踪详情（包含所有 spans）
- `signoz_get_trace_error_analysis` - 分析追踪中的错误模式
- `signoz_get_trace_span_hierarchy` - 获取追踪跨度层次结构
- `signoz_get_trace_available_fields` - 获取追踪可用字段列表
- `signoz_get_trace_field_values` - 获取追踪字段值

**指标查询工具**：
- `signoz_list_metric_keys` - 列出可用指标键
- `signoz_search_metric_by_text` - 按文本搜索指标
- `signoz_get_metrics_available_fields` - 获取指标可用字段列表
- `signoz_get_metrics_field_values` - 获取指标字段值

**服务相关工具**：
- `signoz_list_services` - 列出所有服务（必须首先执行，使用纳秒时间戳或 timeRange）
- `signoz_get_service_top_operations` - 获取服务的顶部操作（使用纳秒时间戳或 timeRange）

**仪表板工具**：
- `signoz_list_dashboards` - 列出所有仪表板
- `signoz_get_dashboard` - 获取仪表板详情
- `signoz_create_dashboard` - 创建新仪表板
- `signoz_update_dashboard` - 更新现有仪表板

**警报工具**：
- `signoz_list_alerts` - 列出所有警报规则
- `signoz_get_alert` - 获取警报规则详情
- `signoz_get_alert_history` - 获取警报历史记录
- `signoz_get_logs_for_alert` - 获取与警报相关的日志

### 时间戳单位说明

⚠️ **关键问题**：不同工具使用不同的时间戳单位！

- **纳秒时间戳**（需要乘以 1,000,000）：
  - `signoz_list_services` - 列出服务
  - `signoz_get_service_top_operations` - 获取服务顶部操作

- **毫秒时间戳**（标准，大部分工具使用）：
  - **日志查询**：`signoz_execute_builder_query`、`signoz_search_logs_by_service`、`signoz_get_error_logs`、`signoz_list_log_views`、`signoz_get_log_view`、`signoz_get_logs_available_fields`、`signoz_get_logs_field_values`
  - **追踪查询**：`signoz_search_traces_by_service`、`signoz_get_trace_details`、`signoz_get_trace_error_analysis`、`signoz_get_trace_span_hierarchy`、`signoz_get_trace_available_fields`、`signoz_get_trace_field_values`
  - **指标查询**：`signoz_list_metric_keys`、`signoz_search_metric_by_text`、`signoz_get_metrics_available_fields`、`signoz_get_metrics_field_values`
  - **警报**：`signoz_list_alerts`、`signoz_get_alert`、`signoz_get_alert_history`、`signoz_get_logs_for_alert`
  - **仪表板**：`signoz_list_dashboards`、`signoz_get_dashboard`、`signoz_create_dashboard`、`signoz_update_dashboard`

**推荐解决方案**：
- 优先使用 `timeRange` 参数（如 "1h", "4h", "24h"），避免时间戳单位错误
- 如果必须使用 `start`/`end` 参数，确保单位正确：
  - `signoz_list_services` 和 `signoz_get_service_top_operations`: 纳秒（毫秒 × 1,000,000）
  - 其他所有工具: 毫秒

### Query Builder v5 格式要求

⚠️ **关键格式要求**：

**🚨 快速参考：字段歧义处理（遇到警告时必看）**

如果查询结果中`rows`为`null`且出现以下警告，需要**同时**在`filter.expression`和`selectFields`中明确指定：

| 警告信息 | 解决方案 |
|---------|---------|
| `service.name is ambiguous, found 2 different combinations` | **方法1（推荐）**：在`filter.expression`中使用完整前缀：`resource.service.name IN ('cs.web.camscanner-toc')`<br>**方法2**：在`selectFields`中添加：`{"name": "service.name", "fieldContext": "resource", "fieldDataType": "string", "signal": "logs"}`<br>⚠️ **最佳实践**：两种方法同时使用 |
| `user.id is ambiguous, found 3 different combinations` | **方法1（推荐）**：在`filter.expression`中使用完整前缀：`attribute.user.id = 1734170267`<br>**方法2**：在`selectFields`中添加：`{"name": "user.id", "fieldContext": "attributes", "fieldDataType": "int64", "signal": "logs"}`<br>⚠️ **最佳实践**：两种方法同时使用 |

**重要规则**：
1. ⚠️ **关键**：在`filter.expression`中使用的歧义字段，**必须使用完整前缀**（`resource.`或`attribute.`）来明确指定上下文
2. 同时在`selectFields`中为所有歧义字段明确指定`fieldContext`和`fieldDataType`
3. 如果查询结果中`rows`为`null`且出现字段歧义警告，这是导致查询失败的主要原因，必须立即修复
4. **修复优先级**：
   - **优先**：在`filter.expression`中使用完整前缀（如`resource.service.name`、`attribute.user.id`）
   - **同时**：在`selectFields`中明确指定`fieldContext`和`fieldDataType`

1. **filter格式**：
   - ✅ 使用 `filter`（单数）和 `expression`（SQL-like字符串）
   - ❌ 不使用 `filters`（复数）和 `items` 数组格式

2. **字段歧义处理**（重要！）：
   - 对于有歧义的字段，**必须同时**在`filter.expression`中使用完整前缀，**并在**`selectFields`中明确指定`fieldContext`和`fieldDataType`
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
   - **完整解决方案**（必须同时使用两种方法）：
     - **方法1（推荐，必须）**：在`filter.expression`中使用完整前缀：
       ```json
       {
         "filter": {
           "expression": "resource.service.name IN ('cs.web.camscanner-toc') AND attribute.user.id = 1734170267"
         }
       }
       ```
     - **方法2（同时使用）**：在`selectFields`中明确指定`fieldContext`和`fieldDataType`：
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
       - ⚠️ **关键**：在`filter.expression`中使用的歧义字段，**必须使用完整前缀**（`resource.service.name`、`attribute.user.id`）
       - `service.name`：在filter中使用`resource.service.name`，在selectFields中使用`fieldContext: "resource"`
       - `user.id`：在filter中使用`attribute.user.id`，在selectFields中使用`fieldContext: "attributes"`和`fieldDataType: "int64"`
       - 如果查询结果中`rows`为`null`，很可能是字段歧义导致的，必须同时修复filter expression（使用完整前缀）和selectFields（明确指定fieldContext和fieldDataType）

3. **fieldContext字段**：
   - 一般情况下：查询时不要添加`fieldContext`字段，SigNoz会自动识别
   - 有歧义时：必须明确指定`fieldContext`和`fieldDataType`

4. **formatTableResultForUI**：
   - 必须设置为`true`

5. **having字段**：
   - 必须包含：`"having": {"expression": ""}`

### SigNoz Query Builder v5 支持的查询操作

**数据源类型（signal）**：
- `logs` - 日志数据：支持日志查询、过滤、聚合
- `metrics` - 指标数据：支持指标查询、时间序列聚合、空间聚合
- `traces` - 追踪数据：支持分布式追踪查询、span分析

**过滤操作（filter.expression）**：

支持SQL-like表达式，包括：

1. **比较操作符**：
   - `=` - 等于
   - `!=` 或 `<>` - 不等于
   - `>` - 大于
   - `>=` - 大于等于
   - `<` - 小于
   - `<=` - 小于等于
   - `IN` - 在列表中（如 `resource.service.name IN ('service1', 'service2')`）
   - `NOT IN` - 不在列表中
   - `LIKE` - 模式匹配（如 `message LIKE '%error%'`）
   - `NOT LIKE` - 不匹配模式
   - `IS NULL` - 为空
   - `IS NOT NULL` - 不为空

2. **逻辑操作符**：
   - `AND` - 逻辑与
   - `OR` - 逻辑或
   - `NOT` - 逻辑非
   - 支持括号分组：`(condition1 OR condition2) AND condition3`

3. **字段路径格式**：
   - **资源字段**：`resource.service.name`、`resource.service.version`、`resource.service.environment`
   - **属性字段**：`attribute.user.id`、`attribute.request.pathname`、`attribute.response.status`
   - **简化格式**（无歧义时）：`service.name`、`user.id`、`request.pathname`
   - ⚠️ **重要**：有歧义的字段必须使用完整前缀（`resource.`或`attribute.`）

4. **值类型**：
   - **字符串**：使用单引号 `'value'`
   - **数字**：直接使用数字，不需要引号
   - **布尔值**：`true` 或 `false`
   - **数组**：`IN ('value1', 'value2', 'value3')`

**聚合操作（aggregations）**：

1. **时间聚合（timeAggregation）**：
   - `avg` - 平均值
   - `sum` - 求和
   - `min` - 最小值
   - `max` - 最大值
   - `count` - 计数
   - `p50`、`p95`、`p99` - 百分位数

2. **空间聚合（spaceAggregation）**：
   - `avg` - 平均值
   - `sum` - 求和
   - `min` - 最小值
   - `max` - 最大值
   - `latest` - 最新值

3. **序列聚合（seriesAggregation）**（用于groupBy时）：
   - `avg` - 平均值
   - `sum` - 求和
   - `min` - 最小值
   - `max` - 最大值

4. **聚合操作符（aggregateOperator）**：
   - `count` - 计数
   - `count_distinct` - 去重计数
   - `sum` - 求和
   - `avg` - 平均值
   - `min` - 最小值
   - `max` - 最大值
   - `p50`、`p95`、`p99` - 百分位数
   - `rate` - 速率
   - `rate_sum` - 速率求和
   - `rate_avg` - 速率平均值
   - `rate_max` - 速率最大值

**分组操作（groupBy）**：
- 支持按一个或多个字段分组
- 字段格式：`{"key": "field.name", "name": "field.name", "dataType": "string", "type": "tag"}`
- 示例：按服务名分组、按用户ID分组、按接口路径分组

**排序操作（orderBy）**：
- 支持按字段升序（`asc`）或降序（`desc`）排序
- 格式：`{"columnName": "timestamp", "order": "desc"}`
- 支持多字段排序

**分页操作**：
- `limit` - 限制返回记录数（默认100，最大建议1000）
- `offset` - 跳过记录数（用于分页）
- `pageSize` - 页面大小

**字段选择（selectFields）**：
- 指定要返回的字段
- 支持资源字段、属性字段
- 必须指定字段的数据类型和上下文（如有歧义）

**Having子句（having）**：
- 用于对聚合结果进行过滤
- 格式：`{"expression": "count > 10"}`

**函数支持（functions）**：
- 支持在查询中使用函数
- 格式：`{"name": "function_name", "args": [arg1, arg2], "namedArgs": {}}`

**时间范围（start/end）**：
- 使用毫秒时间戳
- 或使用 `timeRange` 参数（推荐）：`"1h"`, `"4h"`, `"24h"`, `"7d"` 等

**查询类型（type）**：
- `builder_query` - Query Builder查询（推荐）
- `clickhouse_sql` - ClickHouse SQL查询（高级用法）
- `promql` - PromQL查询（用于指标）

**查询组合（compositeQuery）**：
- 支持多个查询组合（queries数组）
- 支持查询公式（queryFormulas）
- 支持查询之间的运算和组合

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

⚠️ **核心原则**：创建SigNoz查询并不一定一次生成完整的，而是可以根据查询的数据或其他信息补充后继续生成新的查询思路。相关流程符合日志查询定位的流程，最终目标是**定位到问题原因**。

**迭代式查询流程**：

1. **初始查询**：基于工单中的基础信息（服务名、时间范围、关键词等）进行查询
   - 不要求一次性生成所有查询
   - 先执行基础查询，获取初步数据

2. **结果分析**：分析查询结果，提取关键信息：
   - 错误信息：错误类型、错误消息、错误堆栈
   - 接口信息：接口路径、请求方法、响应状态码
   - 特征信息：设备信息（`user.client_id`）、用户信息（`user.id`）、IP地址（`source.address`）
   - 环境信息：地理位置（`geo.city_name`, `geo.country_name`）、浏览器版本（`browser.name`, `browser.version`）、应用版本（`service.version`）
   - 时间模式：错误发生的时间分布、频率等

3. **判断是否定位到问题**：
   - 如果当前查询结果能够定位到问题原因，停止查询，进入分析阶段
   - 如果当前查询结果无法定位到问题原因，继续下一步

4. **生成补充查询**：基于分析结果，生成新的查询思路：
   - 如果发现特定错误类型，查询该错误类型的所有日志
   - 如果发现特定接口有问题，查询该接口的详细日志
   - 如果发现特定设备或地理位置模式，查询特定设备或地理位置的日志
   - 如果发现时间模式，查询特定时间段的日志
   - 如果发现关键词模式，查询包含该关键词的所有日志

5. **迭代深入**：继续执行补充查询，分析新结果，进一步细化查询条件
   - 重复步骤2-4，逐步深入
   - 每次迭代都基于前一次查询的结果
   - 直到定位到问题原因或确定无法定位

**关键特性**：
- **动态查询生成**：查询不是一次性生成的，而是根据查询结果动态调整
- **逐步深入定位**：从宽泛查询逐步细化到精确查询，最终定位到问题原因
- **特征信息补充**：查询过程中特征信息会慢慢补充，用于生成更精确的查询
  - 如果首次查询没有用户ID，可以根据设备ID等信息进行查询，然后从结果中提取用户ID
  - 如果首次查询没有设备ID，可以根据用户ID等信息进行查询，然后从结果中提取设备ID
  - 如果工单中没有提供用户信息或设备信息，先尝试通过工单中其他信息（接口路径、错误信息、关键词、时间范围等）+ 代码相关逻辑生成相关查询，从查询结果中提取用户ID或设备ID
- **灵活调整策略**：如果某个查询方向无法定位问题，可以调整查询策略，尝试其他方向
- **最终目标**：不是简单地获取数据，而是**定位到问题原因**
