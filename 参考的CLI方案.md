我来为你提供最完整详细的init命令梳理，包括每一个执行步骤和代码细节。

# UI/UX Pro Max CLI Init命令完整梳理

## 1. 命令入口与参数解析

### 1.1 CLI程序初始化
```typescript
// cli/src/index.ts
const program = new Command();
program
  .name('uipro')
  .description('CLI to install UI/UX Pro Max skill for AI coding assistants')
  .version('1.5.0');
```

### 1.2 Init命令定义
```typescript
program
  .command('init')
  .description('Install UI/UX Pro Max skill to current project')
  .option('-a, --ai <type>', `AI assistant type (${AI_TYPES.join(', ')})`)
  .option('-f, --force', 'Overwrite existing files')
  .action(async (options) => {
    // 参数验证
    if (options.ai && !AI_TYPES.includes(options.ai)) {
      console.error(`Invalid AI type: ${options.ai}`);
      console.error(`Valid types: ${AI_TYPES.join(', ')}`);
      process.exit(1);
    }
    
    // 调用init命令
    await initCommand({
      ai: options.ai as AIType | undefined,
      force: options.force,
    });
  });
```

### 1.3 支持的命令格式
```bash
# 基本用法
uipro init

# 指定AI类型
uipro init --ai claude
uipro init -a cursor

# 强制覆盖
uipro init --force
uipro init -f

# 组合使用
uipro init --ai windsurf --force
```

## 2. Init命令核心执行流程

### 2.1 初始化阶段
```typescript
// cli/src/commands/init.ts
export async function initCommand(options: InitOptions): Promise<void> {
  // 1. 显示标题
  logger.title('UI/UX Pro Max Installer');
  
  // 2. 获取AI类型
  let aiType = options.ai;
  
  // 3. 确定资源目录路径
  const __dirname = dirname(fileURLToPath(import.meta.url));
  const ASSETS_DIR = join(__dirname, '..', 'assets');
}
```

### 2.2 AI类型确定流程

#### 2.2.1 自动检测逻辑
```typescript
// cli/src/utils/detect.ts
export function detectAIType(cwd: string = process.cwd()): DetectionResult {
  const detected: AIType[] = [];

  // 检测各种AI助手的配置文件夹
  if (existsSync(join(cwd, '.claude'))) detected.push('claude');
  if (existsSync(join(cwd, '.cursor'))) detected.push('cursor');
  if (existsSync(join(cwd, '.windsurf'))) detected.push('windsurf');
  if (existsSync(join(cwd, '.agent'))) detected.push('antigravity');
  if (existsSync(join(cwd, '.github'))) detected.push('copilot');
  if (existsSync(join(cwd, '.kiro'))) detected.push('kiro');
  if (existsSync(join(cwd, '.codex'))) detected.push('codex');
  if (existsSync(join(cwd, '.roo'))) detected.push('roocode');
  if (existsSync(join(cwd, '.qoder'))) detected.push('qoder');
  if (existsSync(join(cwd, '.gemini'))) detected.push('gemini');

  // 智能建议逻辑
  let suggested: AIType | null = null;
  if (detected.length === 1) {
    suggested = detected[0];        // 单个AI：直接建议
  } else if (detected.length > 1) {
    suggested = 'all';              // 多个AI：建议安装全部
  }
  // detected.length === 0：无建议，用户自选

  return { detected, suggested };
}
```

#### 2.2.2 交互式选择
```typescript
if (!aiType) {
  const { detected, suggested } = detectAIType();

  // 显示检测结果
  if (detected.length > 0) {
    logger.info(`Detected: ${detected.map(t => chalk.cyan(t)).join(', ')}`);
  }

  // 交互式选择菜单
  const response = await prompts({
    type: 'select',
    name: 'aiType',
    message: 'Select AI assistant to install for:',
    choices: AI_TYPES.map(type => ({
      title: getAITypeDescription(type),  // 友好的描述文本
      value: type,                        // 实际值
    })),
    initial: suggested ? AI_TYPES.indexOf(suggested) : 0,  // 默认选项
  });

  // 处理用户取消
  if (!response.aiType) {
    logger.warn('Installation cancelled');
    return;
  }

  aiType = response.aiType as AIType;
}
```

#### 2.2.3 AI类型描述映射
```typescript
export function getAITypeDescription(aiType: AIType): string {
  switch (aiType) {
    case 'claude':      return 'Claude Code (.claude/skills/)';
    case 'cursor':      return 'Cursor (.cursor/commands/ + .shared/)';
    case 'windsurf':    return 'Windsurf (.windsurf/workflows/ + .shared/)';
    case 'antigravity': return 'Antigravity (.agent/workflows/ + .shared/)';
    case 'copilot':     return 'GitHub Copilot (.github/prompts/ + .shared/)';
    case 'kiro':        return 'Kiro (.kiro/steering/ + .shared/)';
    case 'codex':       return 'Codex (.codex/skills/)';
    case 'roocode':     return 'RooCode (.roo/commands/ + .shared/)';
    case 'qoder':       return 'Qoder (.qoder/rules/ + .shared/)';
    case 'gemini':      return 'Gemini CLI (.gemini/skills/ + .shared/)';
    case 'all':         return 'All AI assistants';
  }
}
```

### 2.3 文件复制执行阶段

#### 2.3.1 启动复制流程
```typescript
logger.info(`Installing for: ${chalk.cyan(getAITypeDescription(aiType))}`);

const spinner = ora('Installing files...').start();

try {
  const cwd = process.cwd();
  const copiedFolders = await copyFolders(ASSETS_DIR, cwd, aiType);
  
  spinner.succeed('Installation complete!');
  // ... 成功处理
} catch (error) {
  spinner.fail('Installation failed');
  // ... 错误处理
}
```

#### 2.3.2 文件夹映射配置
```typescript
// cli/src/types/index.ts
export const AI_FOLDERS: Record<Exclude<AIType, 'all'>, string[]> = {
  claude:      ['.claude'],
  cursor:      ['.cursor', '.shared'],
  windsurf:    ['.windsurf', '.shared'],
  antigravity: ['.agent', '.shared'],
  copilot:     ['.github', '.shared'],
  kiro:        ['.kiro', '.shared'],
  codex:       ['.codex'],
  roocode:     ['.roo', '.shared'],
  qoder:       ['.qoder', '.shared'],
  gemini:      ['.gemini', '.shared'],
};
```

#### 2.3.3 核心复制逻辑
```typescript
// cli/src/utils/extract.ts
export async function copyFolders(
  sourceDir: string,    // cli/assets/
  targetDir: string,    // 当前工作目录
  aiType: AIType
): Promise<string[]> {
  const copiedFolders: string[] = [];

  // 1. 确定要复制的文件夹列表
  const foldersToCopy = aiType === 'all'
    ? ['.claude', '.cursor', '.windsurf', '.agent', '.github', '.kiro', '.roo', '.codex', '.gemini', '.shared']
    : AI_FOLDERS[aiType];

  // 2. 去重处理（.shared可能重复）
  const uniqueFolders = [...new Set(foldersToCopy)];

  // 3. 逐个复制文件夹
  for (const folder of uniqueFolders) {
    const sourcePath = join(sourceDir, folder);    // cli/assets/.cursor
    const targetPath = join(targetDir, folder);    // ./cursor

    // 3.1 检查源文件夹是否存在
    const sourceExists = await exists(sourcePath);
    if (!sourceExists) {
      continue;  // 跳过不存在的文件夹
    }

    // 3.2 创建目标目录
    await mkdir(targetPath, { recursive: true });

    // 3.3 定义文件过滤器
    const filterFn = (src: string): boolean => {
      const fileName = basename(src);
      return !EXCLUDED_FILES.includes(fileName);  // 排除 settings.local.json
    };

    // 3.4 执行复制（多重容错）
    try {
      // 优先使用Node.js原生API
      await cp(sourcePath, targetPath, { recursive: true, filter: filterFn });
      copiedFolders.push(folder);
    } catch {
      // 降级到系统命令
      try {
        if (process.platform === 'win32') {
          await execAsync(`xcopy "${sourcePath}" "${targetPath}" /E /I /Y`);
        } else {
          await execAsync(`cp -r "${sourcePath}/." "${targetPath}"`);
        }
        copiedFolders.push(folder);
      } catch {
        // 静默跳过失败的文件夹
      }
    }
  }

  return copiedFolders;
}
```

#### 2.3.4 文件存在性检查
```typescript
async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}
```

#### 2.3.5 排除文件配置
```typescript
const EXCLUDED_FILES = ['settings.local.json'];
```

### 2.4 结果反馈阶段

#### 2.4.1 成功反馈
```typescript
spinner.succeed('Installation complete!');

// 显示安装摘要
console.log();
logger.info('Installed folders:');
copiedFolders.forEach(folder => {
  console.log(`  ${chalk.green('+')} ${folder}`);
});

console.log();
logger.success('UI/UX Pro Max installed successfully!');

// 显示后续步骤
console.log();
console.log(chalk.bold('Next steps:'));
console.log(chalk.dim('  1. Restart your AI coding assistant'));
console.log(chalk.dim('  2. Try: "Build a landing page for a SaaS product"'));
console.log();
```

#### 2.4.2 错误处理
```typescript
} catch (error) {
  spinner.fail('Installation failed');
  if (error instanceof Error) {
    logger.error(error.message);
  }
  process.exit(1);
}
```

## 3. 支持的AI助手完整列表

### 3.1 AI类型定义
```typescript
export type AIType = 'claude' | 'cursor' | 'windsurf' | 'antigravity' | 'copilot' | 'kiro' | 'roocode' | 'codex' | 'qoder' | 'gemini' | 'all';

export const AI_TYPES: AIType[] = ['claude', 'cursor', 'windsurf', 'antigravity', 'copilot', 'roocode', 'kiro', 'codex', 'qoder', 'gemini', 'all'];
```

### 3.2 每种AI的完整配置

| AI助手 | 检测文件夹 | 安装文件夹 | 配置文件路径 | 激活方式 |
|--------|------------|------------|--------------|----------|
| **Claude Code** | `.claude/` | `.claude/` | `.claude/skills/ui-ux-pro-max/` | 自动激活 |
| **Cursor** | `.cursor/` | `.cursor/` + `.shared/` | `.cursor/commands/ui-ux-pro-max.md` | `/ui-ux-pro-max` |
| **Windsurf** | `.windsurf/` | `.windsurf/` + `.shared/` | `.windsurf/workflows/ui-ux-pro-max.md` | `/ui-ux-pro-max` |
| **Antigravity** | `.agent/` | `.agent/` + `.shared/` | `.agent/workflows/ui-ux-pro-max.md` | `/ui-ux-pro-max` |
| **GitHub Copilot** | `.github/` | `.github/` + `.shared/` | `.github/prompts/ui-ux-pro-max.prompt.md` | `/ui-ux-pro-max` |
| **Kiro** | `.kiro/` | `.kiro/` + `.shared/` | `.kiro/steering/ui-ux-pro-max.md` | 手动包含 |
| **Codex** | `.codex/` | `.codex/` | `.codex/skills/ui-ux-pro-max/` | `$ui-ux-pro-max` |
| **RooCode** | `.roo/` | `.roo/` + `.shared/` | `.roo/commands/ui-ux-pro-max.md` | `/ui-ux-pro-max` |
| **Qoder** | `.qoder/` | `.qoder/` + `.shared/` | `.qoder/rules/ui-ux-pro-max.md` | `/ui-ux-pro-max` |
| **Gemini CLI** | `.gemini/` | `.gemini/` + `.shared/` | `.gemini/skills/ui-ux-pro-max/` | 自动激活 |

### 3.3 共享资源结构
```
.shared/ui-ux-pro-max/
├── data/                    # 设计数据库
│   ├── charts.csv          # 24种图表类型
│   ├── colors.csv          # 95个调色板
│   ├── landing.csv         # 着陆页最佳实践
│   ├── products.csv        # 产品类型分类
│   ├── prompts.csv         # 提示词模板
│   ├── styles.csv          # 57种UI风格
│   ├── typography.csv      # 56个字体配对
│   ├── ux-guidelines.csv   # 98条UX指南
│   └── stacks/             # 10个技术栈配置
└── scripts/                # Python搜索引擎
    ├── core.py            # 核心搜索逻辑
    └── search.py          # 命令行接口
```

## 4. 日志系统

### 4.1 日志工具定义
```typescript
// cli/src/utils/logger.ts
export const logger = {
  info: (msg: string) => console.log(chalk.blue('info'), msg),
  success: (msg: string) => console.log(chalk.green('success'), msg),
  warn: (msg: string) => console.log(chalk.yellow('warn'), msg),
  error: (msg: string) => console.log(chalk.red('error'), msg),
  title: (msg: string) => console.log(chalk.bold.cyan(`\n${msg}\n`)),
  dim: (msg: string) => console.log(chalk.dim(msg)),
};
```

### 4.2 完整执行日志示例
```bash
$ uipro init

UI/UX Pro Max Installer

info Detected: cursor, kiro
? Select AI assistant to install for: › 
❯ Claude Code (.claude/skills/)
  Cursor (.cursor/commands/ + .shared/)
  Windsurf (.windsurf/workflows/ + .shared/)
  Antigravity (.agent/workflows/ + .shared/)
  GitHub Copilot (.github/prompts/ + .shared/)
  Kiro (.kiro/steering/ + .shared/)
  Codex (.codex/skills/)
  RooCode (.roo/commands/ + .shared/)
  Qoder (.qoder/rules/ + .shared/)
  Gemini CLI (.gemini/skills/ + .shared/)
  All AI assistants

info Installing for: All AI assistants
⠋ Installing files...
✔ Installation complete!

info Installed folders:
  + .claude
  + .cursor
  + .windsurf
  + .agent
  + .github
  + .kiro
  + .roo
  + .codex
  + .gemini
  + .shared

success UI/UX Pro Max installed successfully!

Next steps:
  1. Restart your AI coding assistant
  2. Try: "Build a landing page for a SaaS product"
```

## 5. 错误处理与容错机制

### 5.1 参数验证
```typescript
if (options.ai && !AI_TYPES.includes(options.ai)) {
  console.error(`Invalid AI type: ${options.ai}`);
  console.error(`Valid types: ${AI_TYPES.join(', ')}`);
  process.exit(1);
}
```

### 5.2 用户取消处理
```typescript
if (!response.aiType) {
  logger.warn('Installation cancelled');
  return;
}
```

### 5.3 文件复制容错
```typescript
try {
  // 优先使用Node.js原生API
  await cp(sourcePath, targetPath, { recursive: true, filter: filterFn });
  copiedFolders.push(folder);
} catch {
  // 降级到系统命令
  try {
    if (process.platform === 'win32') {
      await execAsync(`xcopy "${sourcePath}" "${targetPath}" /E /I /Y`);
    } else {
      await execAsync(`cp -r "${sourcePath}/." "${targetPath}"`);
    }
    copiedFolders.push(folder);
  } catch {
    // 静默跳过失败的文件夹，不中断整个流程
  }
}
```

### 5.4 全局错误处理
```typescript
try {
  // 主要逻辑
} catch (error) {
  spinner.fail('Installation failed');
  if (error instanceof Error) {
    logger.error(error.message);
  }
  process.exit(1);
}
```

## 6. 跨平台兼容性

### 6.1 路径处理
```typescript
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ASSETS_DIR = join(__dirname, '..', 'assets');
```

### 6.2 文件复制兼容
```typescript
// Windows使用xcopy
if (process.platform === 'win32') {
  await execAsync(`xcopy "${sourcePath}" "${targetPath}" /E /I /Y`);
} else {
  // Unix系统使用cp
  await execAsync(`cp -r "${sourcePath}/." "${targetPath}"`);
}
```

### 6.3 文件存在性检查
```typescript
import { access } from 'node:fs/promises';
import { existsSync } from 'node:fs';

// 异步检查
async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

// 同步检查（用于AI检测）
if (existsSync(join(cwd, '.claude'))) {
  detected.push('claude');
}
```