# Skill Creator

AI Agent技能创建专家，帮助你快速创建符合Agent Skills开放标准的高质量skill包。

## 功能特点

- 🎯 **需求分析** - 深入理解需求，明确skill功能和场景
- 📐 **复杂度评估** - 根据任务特征选择合适的结构模式
- 📝 **标准化生成** - 遵循Agent Skills开放标准
- 🔧 **模板适配** - 提供简单/中等/复杂三种级别模板
- ✅ **质量校验** - 确保生成的skill符合规范

## 快速开始

### 使用方式

1. 告诉AI你想创建什么skill
2. AI会进行需求分析和复杂度评估
3. AI生成完整的skill包

### 示例对话

```
用户：帮我创建一个发送钉钉通知的skill

AI：好的，让我分析一下需求...
- 功能：发送消息到钉钉群
- 复杂度：简单型（单步骤curl调用）
- 生成文件：SKILL.md, README.md

[生成skill文件...]
```

## 目录结构

```
skill-creator/
├── SKILL.md                    # 核心指令文件
├── README.md                   # 本文件
├── templates/                  # Skill模板
│   ├── simple_skill.md        # 简单型模板
│   ├── moderate_skill.md      # 中等型模板
│   └── complex_skill.md       # 复杂型模板
└── resources/                  # 参考资源
    ├── skill_standard.md      # Agent Skills标准
    └── best_practices.md      # 最佳实践指南
```

## Skill复杂度级别

| 级别 | 特征 | 适用场景 | 参考示例 |
|------|------|----------|----------|
| 简单型 | 单一功能，直接调用 | Webhook通知、简单API | wechat-work-notification |
| 中等型 | 多步骤，需脚本 | 数据分析、自动化任务 | survey-data-analysis |
| 复杂型 | 多阶段，有状态管理 | 工单分析、复杂诊断 | online-ticket-analyzer-v2 |

## 生成的Skill结构

### 简单型
```
simple-skill/
├── SKILL.md
└── README.md
```

### 中等型
```
moderate-skill/
├── SKILL.md
├── README.md
└── scripts/
    └── main_script.py
```

### 复杂型
```
complex-skill/
├── SKILL.md
├── README.md
├── scripts/
│   └── ...
└── resources/
    └── ...
```

## 参考资源

- `resources/skill_standard.md` - Agent Skills标准规范
- `resources/best_practices.md` - Skill创建最佳实践
- `templates/` - 各级别Skill模板

## 注意事项

- Skill名称必须使用小写字母、数字和连字符
- SKILL.md是必需文件，必须包含name和description
- 执行步骤应该具体可操作，包含实际命令
- 示例代码应该可以直接复制使用
