import { existsSync } from 'node:fs';
import { join } from 'node:path';
import type { AIType, DetectionResult } from '../types/index.js';

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