import { access, mkdir, cp } from 'node:fs/promises';
import { join, basename } from 'node:path';
import { exec } from 'node:child_process';
import { promisify } from 'node:util';
import type { AIType } from '../types/index.js';
import { AI_FOLDERS } from '../types/index.js';

const execAsync = promisify(exec);

const EXCLUDED_FILES = ['settings.local.json', '.DS_Store'];

export async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

export async function copyFolders(
  sourceDir: string,    // assets/
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
    const sourcePath = join(sourceDir, folder);
    const targetPath = join(targetDir, folder);

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
      return !EXCLUDED_FILES.includes(fileName);
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

export async function createDirectory(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}