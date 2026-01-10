import { writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import chalk from 'chalk';
import { logger } from '../utils/logger.js';
import { createDirectory, exists } from '../utils/files.js';
import type { CreateOptions, SkillMetadata } from '../types/index.js';

export async function createCommand(name: string, options: CreateOptions): Promise<void> {
  logger.title(`Creating Agent Skill: ${name}`);

  const cwd = process.cwd();
  const skillsDir = join(cwd, 'skills');
  const skillPath = join(skillsDir, name);

  // 检查skills目录是否存在
  if (!(await exists(skillsDir))) {
    logger.error('Skills directory not found. Run "listen-agent init" first.');
    return;
  }

  // 检查skill是否已存在
  if (await exists(skillPath)) {
    logger.error(`Skill "${name}" already exists`);
    return;
  }

  try {
    // 创建skill目录
    await createDirectory(skillPath);

    // 创建skill元数据
    const metadata: SkillMetadata = {
      name,
      version: '1.0.0',
      description: `Agent skill: ${name}`,
      author: '',
      tags: [],
      aiTypes: ['claude', 'cursor', 'windsurf', 'kiro'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    await writeFile(
      join(skillPath, 'skill.json'),
      JSON.stringify(metadata, null, 2)
    );

    // 根据模板创建文件
    await createTemplateFiles(skillPath, name, options.template || 'basic');

    logger.success(`Skill "${name}" created successfully!`);
    
    console.log();
    console.log(chalk.bold('Created files:'));
    console.log(`  ${chalk.green('+')} skills/${name}/skill.json`);
    console.log(`  ${chalk.green('+')} skills/${name}/README.md`);
    console.log(`  ${chalk.green('+')} skills/${name}/prompt.md`);
    console.log();
    
    console.log(chalk.bold('Next steps:'));
    console.log(chalk.dim(`  1. Edit skills/${name}/prompt.md to define your skill`));
    console.log(chalk.dim(`  2. Update skills/${name}/skill.json with metadata`));
    console.log(chalk.dim(`  3. Test your skill with your AI assistant`));
    console.log();

  } catch (error) {
    logger.error(`Failed to create skill "${name}"`);
    if (error instanceof Error) {
      logger.error(error.message);
    }
  }
}

async function createTemplateFiles(skillPath: string, name: string, template: string): Promise<void> {
  // 创建README.md
  const readmeContent = `# ${name}

## Description

Agent skill for ${name}.

## Usage

Describe how to use this skill with your AI assistant.

## Configuration

Any configuration options or requirements.

## Examples

Provide examples of how this skill works.
`;

  await writeFile(join(skillPath, 'README.md'), readmeContent);

  // 创建基础prompt.md
  const promptContent = `# ${name} Skill

You are an AI assistant with the ${name} skill.

## Capabilities

- Describe what this skill can do
- List specific functions or features
- Explain any limitations

## Instructions

Provide detailed instructions for how to use this skill effectively.

## Examples

Show examples of input/output or usage patterns.

## Best Practices

- List best practices for using this skill
- Include any tips or recommendations
`;

  await writeFile(join(skillPath, 'prompt.md'), promptContent);

  // 根据模板类型创建额外文件
  if (template === 'advanced') {
    const configContent = `{
  "parameters": {},
  "settings": {},
  "dependencies": []
}`;
    await writeFile(join(skillPath, 'config.json'), configContent);
  }
}