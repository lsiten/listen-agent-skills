import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readdir, readFile, writeFile } from 'node:fs/promises';
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
        const skillSourceDir = join(cwd, 'skills', skill.name);
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
      targetPath = join(targetDir, 'commands');
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'windsurf':
      targetPath = join(targetDir, 'workflows');
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'kiro':
      targetPath = join(targetDir, 'steering');
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'antigravity':
      targetPath = join(targetDir, 'workflows');
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'copilot':
      targetPath = join(targetDir, 'prompts');
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.prompt.md`);
      break;
      
    case 'codex':
      targetPath = join(targetDir, 'skills', skill.name);
      await createDirectory(targetPath);
      targetFileName = join(targetPath, 'skill.md');
      break;
      
    case 'roocode':
      targetPath = join(targetDir, 'commands');
      await createDirectory(targetPath);
      targetFileName = join(targetPath, `${skill.name}.md`);
      break;
      
    case 'qoder':
      targetPath = join(targetDir, 'rules');
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
  
  // 检查目标文件是否已存在
  if (!force && await exists(targetFileName)) {
    return null; // 跳过已存在的文件
  }
  
  // 读取SKILL.md内容
  const skillContent = await readFile(skillMdPath, 'utf-8');
  
  // 提取Markdown内容（去掉YAML front matter）
  const markdownContent = skillContent.replace(/^---\n[\s\S]*?\n---\n/, '');
  
  // 写入目标文件
  await writeFile(targetFileName, markdownContent);
  
  return {
    name: skill.name,
    targetPath: targetFileName.replace(process.cwd() + '/', '')
  };
}

export async function initCommand(options: InitOptions): Promise<void> {
  // 1. 显示标题
  logger.title('Listen Agent Skills Installer');

  const cwd = process.cwd();
  const skillsDir = join(cwd, 'skills');

  // 检查skills目录是否存在
  if (!(await exists(skillsDir))) {
    logger.error('No skills directory found in current project.');
    logger.info('This command installs existing skills to AI assistant projects.');
    logger.info('Make sure you are in a listen-agent skills project directory.');
    return;
  }

  // 2. 获取AI类型
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

  const spinner = ora('Installing skills...').start();

  try {
    // 获取所有skills
    const skills = await getAvailableSkills(skillsDir);
    
    if (skills.length === 0) {
      spinner.fail('No skills found to install');
      logger.info('Create skills first using: listen-agent create <skill-name>');
      return;
    }

    // 安装skills到对应的AI助手目录
    const installedSkills = await installSkillsToAI(cwd, skills, aiType, options.force);

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

