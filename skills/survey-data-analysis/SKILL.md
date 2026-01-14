---
name: survey-data-analysis
description: 问卷调查报告数据分析技能，支持自动选择分析模型、生成数据分析报告、评估旧方案并给出改进意见，最终生成HTML报告并在浏览器中打开
version: 1.0.0
author: ""
tags: ["data-analysis", "survey", "reporting", "statistics", "visualization"]
---

# 问卷调查报告数据分析 Skill

你是一个专门处理问卷调查报告数据分析的AI助手，具备智能选择分析模型、生成专业数据分析报告、评估旧方案并给出改进建议的能力。

## 任务概述

本技能用于对问卷调查报告数据进行深度分析，根据数据特征自动选择最适合的数据分析模型，生成专业的数据分析报告。如果用户提供了旧的调研方案，会根据数据分析结果对旧方案进行全面评估，给出合理的改进意见。最终生成美观的HTML报告并在浏览器中自动打开。

## 核心能力

- 📊 **智能模型选择** - 根据数据特征自动选择最适合的数据分析模型（描述性统计、相关性分析、回归分析、聚类分析等）
- 📈 **多维度数据分析** - 支持单变量、双变量、多变量分析，包括频数分析、交叉分析、因子分析等
- 📝 **专业报告生成** - 自动生成包含数据概览、分析结果、可视化图表、结论建议的完整分析报告
- 🔍 **方案评估优化** - 基于数据分析结果对旧调研方案进行评估，识别问题并提出改进建议
- 🎨 **可视化展示** - 生成包含多种图表的HTML报告（柱状图、饼图、折线图、热力图等）
- 🌐 **自动打开报告** - 生成报告后自动在浏览器中打开，便于查看和分享

## 系统要求

### 硬件要求
- **处理器**: 现代CPU（推荐多核）
- **内存**: ≥4GB RAM（推荐8GB+）
- **存储**: ≥500MB可用空间

### 软件依赖
- Python 3.8+
- pandas (数据处理)
- numpy (数值计算)
- matplotlib (基础绘图)
- seaborn (高级可视化)
- scipy (统计分析)
- scikit-learn (机器学习分析)
- jinja2 (HTML模板渲染)
- openpyxl (Excel文件处理)
- python-docx (Word文件处理)
- python-pptx (PowerPoint文件处理)
- pdfplumber (PDF文件处理)
- pytesseract (OCR文字识别)
- Pillow (图片处理)

## 执行步骤

### 第一步：环境准备

安装所有必需的Python依赖包：

```bash
cd skills/survey-data-analysis
./scripts/install_dependencies.sh
```

或者手动安装：

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn jinja2 openpyxl python-docx python-pptx pdfplumber pytesseract Pillow
```

**注意**：如果使用图片OCR功能，还需要安装Tesseract OCR引擎：
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- Windows: 下载安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### 第二步：准备数据文件

确保问卷数据文件格式正确：

**支持的格式**：
- CSV文件（推荐）：`.csv`
- Excel文件：`.xlsx`, `.xls`
- JSON文件：`.json`
- 文本文件：`.txt`（支持表格格式的文本数据）
- Markdown文件：`.md`（支持表格格式的Markdown数据）
- Word文件：`.docx`（支持Word表格中的数据）
- PDF文件：`.pdf`（支持PDF中的表格和文本数据）
- 图片文件：`.png`, `.jpg`, `.jpeg`（使用OCR识别图片中的表格数据）

**数据要求**：
- 第一行为列名（变量名）
- 每行为一个样本（受访者）
- 数值型数据应为数字格式
- 分类数据可以是文本或数字编码

**示例数据格式**：
```csv
姓名,年龄,性别,满意度,推荐度,意见
张三,25,男,4,5,很好
李四,30,女,5,4,不错
...
```

### 第三步：执行数据分析

#### 方法1：基础分析（仅数据分析）

```bash
python scripts/analyze_survey.py \
  --data "path/to/survey_data.csv" \
  --output "output/report.html"
```

#### 方法2：完整分析（数据分析 + 方案评估）

如果提供了旧的调研方案文件：

```bash
python scripts/analyze_survey.py \
  --data "path/to/survey_data.csv" \
  --old-plan "path/to/old_research_plan.md" \
  --output "output/report.html"
```

**旧方案支持的格式**：
- Markdown文件：`.md`（推荐）
- Word文件：`.docx`
- PowerPoint文件：`.pptx`
- PDF文件：`.pdf`（支持PDF中的文本内容）
- 图片文件：`.png`, `.jpg`, `.jpeg`（使用OCR识别图片中的文本内容）

#### 方法3：指定分析模型

如果需要强制使用特定分析模型：

```bash
python scripts/analyze_survey.py \
  --data "path/to/survey_data.csv" \
  --model "regression" \
  --output "output/report.html"
```

### 第四步：查看报告

脚本会自动在浏览器中打开生成的HTML报告。如果没有自动打开，可以手动打开 `output/report.html` 文件。

## 参数说明

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| `--data` | string | 是 | - | 问卷数据文件路径（CSV/Excel/JSON/TXT/Markdown/Word/PDF/图片） |
| `--output` | string | 否 | `output/report.html` | 输出HTML报告路径 |
| `--old-plan` | string | 否 | - | 旧调研方案文件路径（Markdown/Word/PowerPoint/PDF/图片格式） |
| `--model` | string | 否 | `auto` | 分析模型类型：`auto`, `descriptive`, `correlation`, `regression`, `cluster`, `factor` |
| `--title` | string | 否 | `问卷数据分析报告` | 报告标题 |
| `--open-browser` | flag | 否 | `true` | 是否自动打开浏览器 |

## 分析模型选择逻辑

系统会根据数据特征自动选择最适合的分析模型：

| 数据特征 | 推荐模型 | 适用场景 |
|---------|---------|---------|
| 单变量描述 | 描述性统计 | 了解数据基本分布和特征 |
| 两个变量关系 | 相关性分析 | 探索变量间的关联程度 |
| 预测关系 | 回归分析 | 建立变量间的预测模型 |
| 分组发现 | 聚类分析 | 发现数据中的潜在分组 |
| 降维分析 | 因子分析 | 提取主要影响因素 |
| 多变量关系 | 多变量分析 | 综合分析多个变量关系 |

**自动选择规则**：
1. 首先进行描述性统计分析（基础）
2. 如果有两个数值变量，进行相关性分析
3. 如果有因变量和自变量，进行回归分析
4. 如果样本量足够（>100），考虑聚类分析
5. 如果变量数量多（>10），考虑因子分析

## 报告内容结构

生成的HTML报告包含以下部分：

1. **执行摘要** - 报告概览和关键发现
2. **数据概览** - 数据基本信息（样本量、变量数、缺失值等）
3. **描述性统计** - 各变量的基本统计信息
4. **可视化分析** - 各类图表展示
5. **深度分析** - 根据选择的模型进行专业分析
6. **方案评估**（如果提供了旧方案）- 对旧方案的评估和改进建议
7. **结论与建议** - 总结性结论和行动建议

## 方案评估功能

当提供了旧的调研方案时，系统会：

1. **提取方案要点** - 从旧方案中提取关键信息
2. **对比分析结果** - 将数据分析结果与方案预期对比
3. **识别问题** - 发现方案中的不足或偏差
4. **提出改进建议** - 基于数据洞察给出具体改进意见

**评估维度**：
- 目标设定是否合理
- 调研方法是否恰当
- 样本选择是否科学
- 问题设计是否有效
- 分析深度是否足够
- 结论是否可靠

## 使用示例

### 示例1：基础问卷分析

```bash
# 分析客户满意度问卷
python scripts/analyze_survey.py \
  --data "data/customer_satisfaction.csv" \
  --title "客户满意度调研报告" \
  --output "reports/satisfaction_report.html"
```

### 示例2：带方案评估的完整分析

```bash
# 分析员工调研数据，并评估旧的调研方案
python scripts/analyze_survey.py \
  --data "data/employee_survey.csv" \
  --old-plan "plans/old_employee_research.md" \
  --title "员工满意度调研分析报告" \
  --output "reports/employee_report.html"
```

### 示例3：指定回归分析模型

```bash
# 使用回归分析模型分析销售数据
python scripts/analyze_survey.py \
  --data "data/sales_survey.csv" \
  --model "regression" \
  --title "销售影响因素分析报告" \
  --output "reports/sales_report.html"
```

## 最佳实践

1. **数据准备**
   - 确保数据格式正确，编码统一
   - 处理缺失值和异常值
   - 检查数据类型是否正确

2. **模型选择**
   - 优先使用自动选择模式
   - 根据研究目的选择合适的模型
   - 考虑样本量和变量数量

3. **结果解读**
   - 结合业务背景理解统计结果
   - 关注显著性和效应量
   - 注意相关性和因果关系的区别

4. **报告使用**
   - 报告可用于决策支持
   - 可以导出为PDF分享
   - 定期更新数据重新分析

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 文件读取失败 | 文件路径错误或格式不支持 | 检查文件路径，确认格式为CSV/Excel/JSON/TXT/Markdown/Word/PDF/图片 |
| OCR识别失败 | Tesseract未安装或图片质量差 | 安装Tesseract OCR引擎，确保图片清晰可读 |
| 依赖包缺失 | 未安装必需的Python包 | 运行 `./scripts/install_dependencies.sh` |
| 内存不足 | 数据量过大 | 分批处理或增加系统内存 |
| 图表显示异常 | 浏览器兼容性问题 | 使用现代浏览器（Chrome/Firefox/Edge） |
| 编码错误 | 文件编码不是UTF-8 | 将文件转换为UTF-8编码 |

### 调试模式

启用详细日志输出：

```bash
python scripts/analyze_survey.py \
  --data "data.csv" \
  --output "report.html" \
  --verbose
```

## 扩展功能

- **批量分析** - 支持同时分析多个问卷文件
- **自定义模板** - 支持自定义HTML报告模板
- **导出功能** - 支持导出为PDF、Word等格式
- **API集成** - 支持通过API调用进行数据分析
- **实时分析** - 支持实时数据流分析

## 技术架构

- **数据处理**: pandas + numpy
- **统计分析**: scipy + scikit-learn
- **可视化**: matplotlib + seaborn
- **报告生成**: jinja2模板引擎
- **文件格式**: 支持CSV、Excel、JSON

## 注意事项

- 确保数据文件路径正确且可访问
- 大数据文件（>100MB）可能需要较长处理时间
- 生成的HTML报告包含交互式图表，需要现代浏览器支持
- 方案评估功能支持Markdown、Word、PowerPoint、PDF、图片格式
- Word和PowerPoint文件需要包含可提取的文本内容
- PDF和图片文件使用OCR技术提取文本，需要安装Tesseract OCR引擎
- 图片文件需要清晰可读，建议分辨率不低于300DPI
- 建议定期备份分析结果和原始数据
