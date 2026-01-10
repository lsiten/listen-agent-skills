import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import chalk from 'chalk';
import { logger } from '../utils/logger.js';
import { exists } from '../utils/files.js';
import type { SkillMetadata } from '../types/index.js';

export async function listCommand(): Promise<void> {
  logger.title('Installed Agent Skills');

  const cwd = process.cwd();
  const skillsDir = join(cwd, 'skills');

  // 检查skills目录是否存在
  if (!(await exists(skillsDir))) {
    logger.warn('No skills directory found. Run "listen-agent init" first.');
    return;
  }

  try {
    const skillDirs = await readdir(skillsDir, { withFileTypes: true });
    const skills = skillDirs.filter(dirent => dirent.isDirectory());

    if (skills.length === 0) {
      logger.info('No skills found. Create your first skill with "listen-agent create <name>"');
      return;
    }

    console.log();
    for (const skill of skills) {
      const skillPath = join(skillsDir, skill.name);
      const skillMdPath = join(skillPath, 'SKILL.md');

      let metadata: SkillMetadata | null = null;
      
      // 尝试读取SKILL.md
      if (await exists(skillMdPath)) {
        try {
          const skillContent = await readFile(skillMdPath, 'utf-8');
          
          // 解析YAML front matter
          const yamlMatch = skillContent.match(/^---\n([\s\S]*?)\n---/);
          if (yamlMatch) {
            const yamlContent = yamlMatch[1];
            
            // 简单的YAML解析
            metadata = {
              name: skill.name,
              description: '',
              version: '1.0.0',
              author: '',
              tags: [],
              aiTypes: ['all'],
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
                  const tagsMatch = value.match(/\[(.*)\]/);
                  if (tagsMatch) {
                    metadata.tags = tagsMatch[1].split(',').map(t => t.trim().replace(/['"]/g, ''));
                  }
                }
              }
            }
          }
        } catch {
          // 忽略解析错误
        }
      }

      // 显示skill信息
      console.log(chalk.bold.cyan(`📦 ${skill.name}`));
      
      if (metadata) {
        console.log(`   ${chalk.dim('Version:')} ${metadata.version}`);
        console.log(`   ${chalk.dim('Description:')} ${metadata.description}`);
        if (metadata.author) {
          console.log(`   ${chalk.dim('Author:')} ${metadata.author}`);
        }
        if (metadata.tags && metadata.tags.length > 0) {
          console.log(`   ${chalk.dim('Tags:')} ${metadata.tags.join(', ')}`);
        }
        console.log(`   ${chalk.dim('AI Types:')} ${metadata.aiTypes.join(', ')}`);
        console.log(`   ${chalk.dim('Updated:')} ${new Date(metadata.updatedAt).toLocaleDateString()}`);
      } else {
        console.log(`   ${chalk.dim('Agent Skills format - SKILL.md found')}`);
      }
      
      console.log();
    }

    logger.success(`Found ${skills.length} skill${skills.length > 1 ? 's' : ''}`);

  } catch (error) {
    logger.error('Failed to list skills');
    if (error instanceof Error) {
      logger.error(error.message);
    }
  }
}