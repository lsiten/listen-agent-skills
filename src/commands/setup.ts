import { join } from 'node:path';
import { writeFile } from 'node:fs/promises';
import chalk from 'chalk';
import { logger } from '../utils/logger.js';
import { createDirectory } from '../utils/files.js';

export async function setupCommand(): Promise<void> {
  logger.title('Listen Agent Skills Framework Setup');

  const cwd = process.cwd();

  try {
    // 创建基础目录结构
    await createDirectory(join(cwd, 'skills'));
    await createDirectory(join(cwd, 'templates'));
    
    // 创建配置文件
    await createConfigFiles(cwd);

    console.log();
    logger.info('Created structure:');
    console.log(`  ${chalk.green('+')} skills/`);
    console.log(`  ${chalk.green('+')} templates/`);
    console.log(`  ${chalk.green('+')} listen-agent.config.json`);

    console.log();
    logger.success('Listen Agent Skills Framework setup complete!');

    // 显示后续步骤
    console.log();
    console.log(chalk.bold('Next steps:'));
    console.log(chalk.dim('  1. Create your first skill: listen-agent create my-skill'));
    console.log(chalk.dim('  2. List available skills: listen-agent list'));
    console.log(chalk.dim('  3. Install skills to AI projects: listen-agent init'));
    console.log();

  } catch (error) {
    logger.error('Setup failed');
    if (error instanceof Error) {
      logger.error(error.message);
    }
    process.exit(1);
  }
}

async function createConfigFiles(cwd: string): Promise<void> {
  const configPath = join(cwd, 'listen-agent.config.json');
  const config = {
    version: '1.0.0',
    skillsDir: 'skills',
    templatesDir: 'templates',
    defaultTemplate: 'basic',
    aiTypes: ['claude', 'cursor', 'windsurf', 'kiro'],
    createdAt: new Date().toISOString()
  };

  await writeFile(configPath, JSON.stringify(config, null, 2));
}