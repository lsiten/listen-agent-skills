#!/usr/bin/env node

import { Command } from 'commander';
import { initCommand } from './commands/init.js';
import { setupCommand } from './commands/setup.js';
import { listCommand } from './commands/list.js';
import { createCommand } from './commands/create.js';
import { AI_TYPES } from './types/index.js';

const program = new Command();

program
  .name('listen-agent')
  .description('CLI to manage and install agent skills for AI coding assistants')
  .version('1.0.0');

// Setup command - 初始化项目结构
program
  .command('setup')
  .description('Setup agent skills framework in current directory')
  .action(async () => {
    await setupCommand();
  });

// Init command - 安装skills到AI助手项目
program
  .command('init')
  .description('Install existing skills to AI assistant projects')
  .option('-a, --ai <type>', `AI assistant type (${AI_TYPES.join(', ')})`)
  .option('-f, --force', 'Overwrite existing files')
  .action(async (options) => {
    if (options.ai && !AI_TYPES.includes(options.ai)) {
      console.error(`Invalid AI type: ${options.ai}`);
      console.error(`Valid types: ${AI_TYPES.join(', ')}`);
      process.exit(1);
    }
    
    await initCommand({
      ai: options.ai,
      force: options.force,
    });
  });

// List command - 列出已安装的skills
program
  .command('list')
  .description('List all available agent skills')
  .action(async () => {
    await listCommand();
  });

// Create command - 创建新的skill
program
  .command('create <name>')
  .description('Create a new agent skill')
  .option('-t, --template <type>', 'Skill template type', 'basic')
  .action(async (name, options) => {
    await createCommand(name, options);
  });

program.parse();