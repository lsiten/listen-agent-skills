# Survey Data Analysis Skill

问卷调查报告数据分析技能，支持自动选择分析模型、生成数据分析报告、评估旧方案并给出改进意见。

## 特性

- 智能选择数据分析模型
- 多维度数据分析
- 专业报告生成
- 方案评估优化
- 可视化展示
- 自动打开报告

## 安装

```bash
# 安装依赖
./scripts/install_dependencies.sh
```

## 使用方法

### 快速开始

```bash
# 基础用法
python scripts/analyze_survey.py \
  --data "path/to/survey_data.csv" \
  --output "output/report.html"
```

### 完整分析（包含方案评估）

```bash
python scripts/analyze_survey.py \
  --data "path/to/survey_data.csv" \
  --old-plan "path/to/old_research_plan.md" \
  --output "output/report.html"
```

## 配置

参见 `SKILL.md` 中的详细配置说明。

## 许可证

MIT
