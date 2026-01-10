# Listen Agent Skills Framework

一个用于管理和安装AI助手技能的CLI工具框架。

## 特性

- 🚀 支持多种AI助手 (Claude, Cursor, Windsurf, Kiro等)
- 📦 统一的技能管理系统
- 🛠️ 简单的CLI命令
- 📝 模板化技能创建
- 🔍 智能AI助手检测

## 安装

```bash
npm install -g listen-agent
```

## 使用方法

### 初始化项目

```bash
# 自动检测AI助手类型
listen-agent init

# 指定AI助手类型
listen-agent init --ai claude
listen-agent init --ai cursor
listen-agent init --ai all

# 强制覆盖现有文件
listen-agent init --force
```

### 创建技能

```bash
# 创建基础技能
listen-agent create my-skill

# 使用高级模板
listen-agent create my-skill --template advanced
```

### 列出技能

```bash
listen-agent list
```

## 支持的AI助手

| AI助手 | 检测文件夹 | 安装路径 | 状态 |
|--------|------------|----------|------|
| Claude Code | `.claude/` | `.claude/skills/` | ✅ |
| Cursor | `.cursor/` | `.cursor/commands/` + `.shared/` | ✅ |
| Windsurf | `.windsurf/` | `.windsurf/workflows/` + `.shared/` | ✅ |
| Kiro | `.kiro/` | `.kiro/steering/` + `.shared/` | ✅ |
| Antigravity | `.agent/` | `.agent/workflows/` + `.shared/` | ✅ |
| GitHub Copilot | `.github/` | `.github/prompts/` + `.shared/` | ✅ |
| Codex | `.codex/` | `.codex/skills/` | ✅ |
| RooCode | `.roo/` | `.roo/commands/` + `.shared/` | ✅ |
| Qoder | `.qoder/` | `.qoder/rules/` + `.shared/` | ✅ |
| Gemini CLI | `.gemini/` | `.gemini/skills/` + `.shared/` | ✅ |

## 项目结构

初始化后的项目结构：

```
your-project/
├── skills/                 # 技能目录
│   └── my-skill/
│       ├── skill.json      # 技能元数据
│       ├── README.md       # 技能说明
│       └── prompt.md       # 技能提示词
├── templates/              # 模板目录
├── listen-agent.config.json # 配置文件
└── .shared/                # 共享资源 (如果适用)
```

## 技能开发

### 技能结构

每个技能包含以下文件：

- `skill.json` - 技能元数据和配置
- `README.md` - 技能文档
- `prompt.md` - AI助手提示词
- `config.json` - 高级配置 (可选)

### 示例技能

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "My awesome agent skill",
  "author": "Your Name",
  "tags": ["productivity", "automation"],
  "aiTypes": ["claude", "cursor", "windsurf"],
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T00:00:00.000Z"
}
```

## 开发

```bash
# 克隆项目
git clone <repository-url>
cd listen-agent

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 本地测试
npm link
listen-agent --help
```

## 许可证

MIT