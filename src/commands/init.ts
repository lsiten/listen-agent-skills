import { dirname, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readdir, readFile, writeFile, cp } from 'node:fs/promises';
import prompts from 'prompts';
import ora from 'ora';
import chalk from 'chalk';
import { logger } from '../utils/logger.js';
import { detectAIType, getAITypeDescription } from '../utils/detect.js';
import { exists, createDirectory } from '../utils/files.js';
import type { InitOptions, AIType, SkillMetadata } from '../types/index.js';
import { AI_TYPES, AI_FOLDERS } from '../types/index.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

interface SkillInstallResult {
  name: string;
  targetPath: string;
}

async function getAvailableSkills(skillsDir: string): Promise<SkillMetadata[]> {
  const skills: SkillMetadata[] = [];
  
  try {
    const skillDirs = await readdir(skillsDir, { withFileTypes: true });
    
    for (const dirent of skillDirs) {
      if (!dirent.isDirectory()) continue;
      
      const skillPath = join(skillsDir, dirent.name);
      const skillMdPath = join(skillPath, 'SKILL.md');
      
      if (await exists(skillMdPath)) {
        try {
          const skillContent = await readFile(skillMdPath, 'utf-8');
          
          // 解析YAML front matter
          const yamlMatch = skillContent.match(/^---\n([\s\S]*?)\n---/);
          if (yamlMatch) {
            const yamlContent = yamlMatch[1];
            
            // 简单的YAML解析（仅支持基本的key: value格式）
            const metadata: SkillMetadata = {
              name: dirent.name,
              description: '',
              version: '1.0.0',
              author: '',
              tags: [],
              aiTypes: ['all'], // 默认支持所有AI类型
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString()
            };
            
            const lines = yamlContent.split('\n');
            for (const line of lines) {
              const match = line.match(/^(\w+):\s*(.+)$/);
              if (match) {
                const [, key, value] = match;
                if (key === 'name') metadata.name = value.replace(/['"]/g, '');
                if (key === 'description') metadata.description = value.replace(/['"]/g, '');
                if (key === 'version') metadata.version = value.replace(/['"]/g, '');
                if (key === 'author') metadata.author = value.replace(/['"]/g, '');
                if (key === 'tags') {
                  // 解析数组格式 ["tag1", "tag2"]
                  const tagsMatch = value.match(/\[(.*)\]/);
                  if (tagsMatch) {
                    metadata.tags = tagsMatch[1].split(',').map(t => t.trim().replace(/['"]/g, ''));
                  }
                }
              }
            }
            
            skills.push(metadata);
          }
        } catch {
          // 跳过无效的SKILL.md
        }
      }
    }
  } catch {
    // 目录不存在或读取失败
  }
  
  return skills;
}

async function installSkillsToAI(
  cwd: string,
  skillsSourceDir: string,
  skills: SkillMetadata[],
  aiType: AIType,
  force?: boolean
): Promise<SkillInstallResult[]> {
  const installed: SkillInstallResult[] = [];
  
  // 确定要安装的AI类型
  const aiTypes = aiType === 'all' 
    ? Object.keys(AI_FOLDERS) as Exclude<AIType, 'all'>[]
    : [aiType as Exclude<AIType, 'all'>];
  
  for (const currentAiType of aiTypes) {
    const folders = AI_FOLDERS[currentAiType];
    
    for (const folder of folders) {
      const targetDir = join(cwd, folder);
      
      // 创建目标目录
      await createDirectory(targetDir);
      
      // 为每个skill安装到对应目录
      for (const skill of skills) {
        const skillSourceDir = join(skillsSourceDir, skill.name);
        const result = await installSkillToFolder(
          skillSourceDir,
          targetDir,
          skill,
          currentAiType,
          force
        );
        
        if (result) {
          installed.push(result);
        }
      }
    }
  }
  
  return installed;
}

/**
 * 复制 scripts 目录到目标位置
 * @param sourceScriptsDir 源 scripts 目录路径
 * @param targetScriptsDir 目标 scripts 目录路径
 */
async function copyScriptsDirectory(
  sourceScriptsDir: string,
  targetScriptsDir: string
): Promise<void> {
  if (!(await exists(sourceScriptsDir))) {
    return; // 如果源目录不存在，直接返回
  }

  // 创建目标目录
  await createDirectory(targetScriptsDir);

  // 定义文件过滤器，排除不必要的文件
  const EXCLUDED_SCRIPTS_FILES = ['__pycache__', '.DS_Store', '.git', '.gitignore'];
  const filterFn = (src: string): boolean => {
    const fileName = basename(src);
    return !EXCLUDED_SCRIPTS_FILES.includes(fileName);
  };

  // 复制 scripts 目录
  try {
    await cp(sourceScriptsDir, targetScriptsDir, { recursive: true, filter: filterFn });
  } catch (error) {
    // 如果复制失败，记录错误但不中断安装流程
    logger.warn(`Failed to copy scripts directory: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * 复制 skill 目录下的所有资源文件（除了 SKILL.md 和 scripts）
 * @param skillSourceDir 源 skill 目录路径
 * @param targetPath 目标路径（skill 的安装目录）
 */
async function copySkillResources(
  skillSourceDir: string,
  targetPath: string
): Promise<void> {
  try {
    const entries = await readdir(skillSourceDir, { withFileTypes: true });
    
    // 定义需要排除的文件和目录
    const EXCLUDED_ITEMS = ['SKILL.md', 'scripts', '.DS_Store', '.git', '.gitignore', '__pycache__'];
    
    for (const entry of entries) {
      const itemName = entry.name;
      
      // 跳过排除的项目
      if (EXCLUDED_ITEMS.includes(itemName)) {
        continue;
      }
      
      const sourcePath = join(skillSourceDir, itemName);
      const targetItemPath = join(targetPath, itemName);
      
      // 如果是目录，递归复制
      if (entry.isDirectory()) {
        // 定义目录过滤器，排除不必要的文件
        const EXCLUDED_FILES = ['__pycache__', '.DS_Store', '.git', '.gitignore'];
        const filterFn = (src: string): boolean => {
          const fileName = basename(src);
          return !EXCLUDED_FILES.includes(fileName);
        };
        
        try {
          await createDirectory(targetItemPath);
          await cp(sourcePath, targetItemPath, { recursive: true, filter: filterFn });
        } catch (error) {
          logger.warn(`Failed to copy directory ${itemName}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      } else {
        // 如果是文件，直接复制
        try {
          const content = await readFile(sourcePath);
          await writeFile(targetItemPath, content);
        } catch (error) {
          logger.warn(`Failed to copy file ${itemName}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }
    }
  } catch (error) {
    // 如果读取目录失败，记录错误但不中断安装流程
    logger.warn(`Failed to copy skill resources: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

async function installSkillToFolder(
  skillSourceDir: string,
  targetDir: string,
  skill: SkillMetadata,
  aiType: Exclude<AIType, 'all'>,
  force?: boolean
): Promise<SkillInstallResult | null> {
  const skillMdPath = join(skillSourceDir, 'SKILL.md');
  
  if (!(await exists(skillMdPath))) {
    return null;
  }
  
  let targetPath: string;
  let targetFileName: string;
  
  // 根据AI类型确定目标路径和文件名
  switch (aiType) {
    case 'claude':
      targetPath = join(targetDir, 'skills', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, 'skill.md');
      break;
      
    case 'cursor':
      // 调整目录结构：创建 skill 名称的目录，将文件放在其中
      targetPath = join(targetDir, 'commands', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'windsurf':
      // 创建子目录结构以支持 scripts
      targetPath = join(targetDir, 'workflows', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'kiro':
      // 创建子目录结构以支持 scripts
      targetPath = join(targetDir, 'steering', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'antigravity':
      // 创建子目录结构以支持 scripts
      targetPath = join(targetDir, 'workflows', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'copilot':
      // 创建子目录结构以支持 scripts
      targetPath = join(targetDir, 'prompts', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.prompt.md`);
      break;
      
    case 'codex':
      targetPath = join(targetDir, 'skills', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, 'skill.md');
      break;
      
    case 'roocode':
      // 创建子目录结构以支持 scripts
      targetPath = join(targetDir, 'commands', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'qoder':
      // 创建子目录结构以支持 scripts
      targetPath = join(targetDir, 'rules', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'gemini':
      targetPath = join(targetDir, 'skills', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, 'skill.md');
      break;
      
    default:
      return null;
  }
  
  // 检查目标文件是否已存在（只有在非强制模式下才跳过）
  if (!force && await exists(targetFileName)) {
    return null; // 跳过已存在的文件
  }
  
  // 读取SKILL.md内容
  const skillContent = await readFile(skillMdPath, 'utf-8');
  
  // 提取Markdown内容（去掉YAML front matter）
  const markdownContent = skillContent.replace(/^---\n[\s\S]*?\n---\n/, '');
  
  // 写入目标文件
  await writeFile(targetFileName, markdownContent);
  
  // 复制 scripts 目录（如果存在）
  const sourceScriptsDir = join(skillSourceDir, 'scripts');
  let targetScriptsDir: string;
  
  // 根据 AI 类型确定 scripts 目录的目标位置
  switch (aiType) {
    case 'claude':
    case 'codex':
    case 'gemini':
      // 这些类型已经有 skill 名称的目录，scripts 放在其中
      targetScriptsDir = join(targetPath, 'scripts');
      break;
      
    case 'cursor':
      // cursor 现在也有 skill 名称的目录
      targetScriptsDir = join(targetPath, 'scripts');
      break;
      
    case 'windsurf':
    case 'antigravity':
    case 'kiro':
    case 'copilot':
    case 'roocode':
    case 'qoder':
      // 这些类型现在都有子目录结构，scripts 放在其中
      targetScriptsDir = join(targetPath, 'scripts');
      break;
      
    default:
      // 其他类型不复制 scripts
      return {
        name: skill.name,
        targetPath: targetFileName.replace(process.cwd() + '/', '')
      };
  }
  
  // 复制 scripts 目录
  await copyScriptsDirectory(sourceScriptsDir, targetScriptsDir);
  
  // 复制其他资源文件（README.md、配置文件、模板文件等）
  await copySkillResources(skillSourceDir, targetPath);
  
  return {
    name: skill.name,
    targetPath: targetFileName.replace(process.cwd() + '/', '')
  };
}

export async function initCommand(options: InitOptions): Promise<void> {
  // 1. 显示标题
  logger.title('Listen Agent Skills Installer');

  const cwd = process.cwd();

  // 2. 查找 skills 来源
  let skillsSourceDir: string | null = null;
  
  // 优先级1: 检查当前目录是否有 skills 目录（开发模式）
  const localSkillsDir = join(cwd, 'skills');
  if (await exists(localSkillsDir)) {
    skillsSourceDir = localSkillsDir;
    logger.info('Found local skills directory');
  }
  
  // 优先级2: 检查全局安装的 listen-agent 包中的 skills
  if (!skillsSourceDir) {
    try {
      // 尝试找到全局安装的 listen-agent 包
      const globalSkillsDir = join(__dirname, '..', '..', 'skills');
      if (await exists(globalSkillsDir)) {
        skillsSourceDir = globalSkillsDir;
        logger.info('Using skills from global listen-agent installation');
      }
    } catch {
      // 忽略错误
    }
  }
  
  // 优先级3: 提示用户指定 skills 目录
  if (!skillsSourceDir) {
    logger.error('No skills found.');
    logger.info('Options:');
    logger.info('1. Run this command in a listen-agent skills project directory');
    logger.info('2. Install listen-agent globally: npm install -g listen-agent');
    logger.info('3. Clone skills repository: git clone https://github.com/lsiten/listen-agent-skills.git');
    return;
  }

  // 3. 获取AI类型
  let aiType = options.ai;

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
      message: 'Select AI assistant to install skills for:',
      choices: AI_TYPES.map(type => ({
        title: getAITypeDescription(type),
        value: type,
      })),
      initial: suggested ? AI_TYPES.indexOf(suggested) : 0,
    });

    // 处理用户取消
    if (!response.aiType) {
      logger.warn('Installation cancelled');
      return;
    }

    aiType = response.aiType as AIType;
  }

  logger.info(`Installing skills for: ${chalk.cyan(getAITypeDescription(aiType))}`);
  logger.info(`Skills source: ${skillsSourceDir}`);

  // 获取所有可用的skills
  const allSkills = await getAvailableSkills(skillsSourceDir);
  
  if (allSkills.length === 0) {
    logger.error('No skills found to install');
    logger.info('Make sure the skills directory contains valid SKILL.md files');
    return;
  }

  // 4. 技能选择交互
  let selectedSkills = allSkills;

  // 如果通过命令行指定了特定技能
  if (options.skills && options.skills.length > 0) {
    const requestedSkills = options.skills;
    selectedSkills = allSkills.filter(skill => 
      requestedSkills.includes(skill.name)
    );

    // 检查是否有未找到的技能
    const foundSkillNames = selectedSkills.map(s => s.name);
    const notFoundSkills = requestedSkills.filter(name => 
      !foundSkillNames.includes(name)
    );

    if (notFoundSkills.length > 0) {
      logger.warn(`Skills not found: ${notFoundSkills.join(', ')}`);
    }

    if (selectedSkills.length === 0) {
      logger.error('None of the specified skills were found');
      logger.info('Available skills:');
      allSkills.forEach(skill => {
        console.log(`  ${chalk.cyan('•')} ${skill.name}`);
      });
      return;
    }

    logger.info(`Installing specified skills: ${selectedSkills.map(s => s.name).join(', ')}`);
  }
  // 交互式选择技能（仅在非强制模式且未指定特定技能时）
  else if (!options.force) {
    logger.info(`Found ${allSkills.length} available skill${allSkills.length > 1 ? 's' : ''}:`);
    allSkills.forEach(skill => {
      console.log(`  ${chalk.cyan('•')} ${skill.name} - ${skill.description}`);
    });

    console.log();
    const skillResponse = await prompts({
      type: 'multiselect',
      name: 'skills',
      message: 'Select skills to install (use space to select, enter to confirm):',
      choices: allSkills.map(skill => ({
        title: `${skill.name} - ${skill.description}`,
        value: skill,
        selected: true, // 默认全选
      })),
      min: 1,
      hint: '- Space to select. Return to submit'
    });

    // 处理用户取消
    if (!skillResponse.skills || skillResponse.skills.length === 0) {
      logger.warn('No skills selected, installation cancelled');
      return;
    }

    selectedSkills = skillResponse.skills;
  }

  logger.info(`Installing ${selectedSkills.length} skill${selectedSkills.length > 1 ? 's' : ''}...`);

  const spinner = ora('Installing skills...').start();

  try {
    // 安装选中的skills到对应的AI助手目录
    const installedSkills = await installSkillsToAI(cwd, skillsSourceDir, selectedSkills, aiType, options.force);

    spinner.succeed('Skills installation complete!');

    // 显示安装摘要
    console.log();
    logger.info('Installed skills:');
    installedSkills.forEach(skill => {
      console.log(`  ${chalk.green('+')} ${skill.name} → ${skill.targetPath}`);
    });

    console.log();
    logger.success(`${installedSkills.length} skill${installedSkills.length > 1 ? 's' : ''} installed successfully!`);

    // 显示后续步骤
    console.log();
    console.log(chalk.bold('Next steps:'));
    console.log(chalk.dim('  1. Restart your AI coding assistant'));
    console.log(chalk.dim('  2. Skills are now available in your AI assistant'));
    console.log();

  } catch (error) {
    spinner.fail('Installation failed');
    if (error instanceof Error) {
      logger.error(error.message);
    }
    process.exit(1);
  }
}

