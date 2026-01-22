import { writeFile, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import chalk from 'chalk';
import { logger } from '../utils/logger.js';
import { createDirectory, exists } from '../utils/files.js';
import type { CreateOptions } from '../types/index.js';

export async function createCommand(name: string, options: CreateOptions): Promise<void> {
  logger.title(`Creating Agent Skill: ${name}`);

  const cwd = process.cwd();
  const skillsDir = join(cwd, 'skills');
  const skillPath = join(skillsDir, name);

  // 检查skills目录是否存在
  if (!(await exists(skillsDir))) {
    logger.error('Skills directory not found. Run "listen-agent setup" first.');
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

    // 根据模板创建文件
    await createFromTemplate(skillPath, name, options.template || 'basic');

    logger.success(`Skill "${name}" created successfully!`);
    
    console.log();
    console.log(chalk.bold('Created files:'));
    console.log(`  ${chalk.green('+')} skills/${name}/SKILL.md`);
    console.log(`  ${chalk.green('+')} skills/${name}/README.md`);
    
    if (options.template === 'advanced') {
      console.log(`  ${chalk.green('+')} skills/${name}/scripts/`);
    }
    
    console.log();
    
    console.log(chalk.bold('Next steps:'));
    console.log(chalk.dim(`  1. Edit skills/${name}/SKILL.md to define your skill`));
    console.log(chalk.dim(`  2. Update the metadata and instructions`));
    console.log(chalk.dim(`  3. Test your skill with your AI assistant`));
    console.log();

  } catch (error) {
    logger.error(`Failed to create skill "${name}"`);
    if (error instanceof Error) {
      logger.error(error.message);
    }
  }
}

async function createFromTemplate(skillPath: string, name: string, template: string): Promise<void> {
  const cwd = process.cwd();
  const templateDir = join(cwd, 'templates', template);
  
  // 检查模板是否存在
  if (!(await exists(templateDir))) {
    throw new Error(`Template "${template}" not found`);
  }

  // 模板变量
  const variables = {
    name,
    description: `Agent skill for ${name}`,
    author: '',
    tags: '[]',
    task_overview: `completing ${name} related tasks`,
    domain: name,
    capabilities: 'comprehensive analysis and problem-solving',
    features: 'advanced functionality',
    capability_1_description: '理解任务需求，分析问题本质，识别关键信息',
    capability_2_description: '基于已有知识和上下文进行逻辑推理，做出合理决策',
    capability_3_description: '制定执行计划，按步骤完成任务',
    capability_4_description: '独立分析和解决复杂问题',
    capability_5_description: '评估结果，优化方案，提供最佳解决方案',
    processor_requirement: 'Modern CPU',
    memory_requirement: '≥8GB RAM',
    storage_requirement: '≥10GB available space',
    dependency_1: 'Python 3.8+',
    dependency_2: 'Node.js 16+',
    dependency_3: 'Required libraries',
    config_param: 'default',
    input_param: 'input_path',
    output_param: 'output_path',
    config_file: 'config.json',
    result_path: 'results/',
    param_1: 'input_path',
    default_1: './input',
    param_1_desc: 'Input file or directory path',
    param_2: 'batch_size',
    default_2: '10',
    param_2_desc: 'Processing batch size',
    param_3: 'verbose',
    default_3: 'false',
    param_3_desc: 'Enable verbose output',
    performance_tip_1: 'Use appropriate batch sizes',
    performance_tip_2: 'Enable parallel processing when possible',
    security_tip_1: 'Validate all input parameters',
    security_tip_2: 'Use secure file permissions',
    error_handling_tip_1: 'Always check return codes',
    error_handling_tip_2: 'Implement proper logging',
    error_1: 'Command not found',
    cause_1: 'Missing dependencies',
    solution_1: 'Run install_dependencies.sh',
    error_2: 'Permission denied',
    cause_2: 'Insufficient file permissions',
    solution_2: 'Check file and directory permissions',
    error_3: 'Out of memory',
    cause_3: 'Large dataset processing',
    solution_3: 'Reduce batch size or increase system memory',
    plugin_description: 'Extensible plugin architecture',
    api_description: 'RESTful API integration',
    batch_description: 'Batch processing capabilities',
    monitoring_description: 'Real-time monitoring and reporting',
    framework: 'Custom framework',
    data_processing: 'Stream processing',
    storage_solution: 'File-based storage',
    communication_protocol: 'HTTP/REST',
    feature_1: 'Feature 1 description',
    feature_2: 'Feature 2 description',
    feature_3: 'Feature 3 description'
  };

  // 复制并处理SKILL.md
  const skillTemplate = await readFile(join(templateDir, 'SKILL.md'), 'utf-8');
  const skillContent = replaceVariables(skillTemplate, variables);
  await writeFile(join(skillPath, 'SKILL.md'), skillContent);

  // 复制并处理README.md
  const readmeTemplate = await readFile(join(templateDir, 'README.md'), 'utf-8');
  const readmeContent = replaceVariables(readmeTemplate, variables);
  await writeFile(join(skillPath, 'README.md'), readmeContent);

  // 如果是高级模板，复制scripts目录
  if (template === 'advanced') {
    const scriptsDir = join(templateDir, 'scripts');
    const targetScriptsDir = join(skillPath, 'scripts');
    
    if (await exists(scriptsDir)) {
      await createDirectory(targetScriptsDir);
      
      // 复制脚本文件
      const { readdir } = await import('node:fs/promises');
      const scriptFiles = await readdir(scriptsDir);
      
      for (const file of scriptFiles) {
        const scriptTemplate = await readFile(join(scriptsDir, file), 'utf-8');
        const scriptContent = replaceVariables(scriptTemplate, variables);
        await writeFile(join(targetScriptsDir, file), scriptContent);
      }
      
      // 设置脚本执行权限
      const { chmod } = await import('node:fs/promises');
      for (const file of scriptFiles) {
        if (file.endsWith('.sh')) {
          await chmod(join(targetScriptsDir, file), 0o755);
        }
      }
    }
  }
}

function replaceVariables(content: string, variables: Record<string, string>): string {
  let result = content;
  
  for (const [key, value] of Object.entries(variables)) {
    const regex = new RegExp(`{{${key}}}`, 'g');
    result = result.replace(regex, value);
  }
  
  return result;
}