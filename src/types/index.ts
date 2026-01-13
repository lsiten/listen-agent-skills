export type AIType = 
  | 'claude' 
  | 'cursor' 
  | 'windsurf' 
  | 'antigravity' 
  | 'copilot' 
  | 'kiro' 
  | 'roocode' 
  | 'codex' 
  | 'qoder' 
  | 'gemini' 
  | 'all';

export const AI_TYPES: AIType[] = [
  'claude', 
  'cursor', 
  'windsurf', 
  'antigravity', 
  'copilot', 
  'roocode', 
  'kiro', 
  'codex', 
  'qoder', 
  'gemini', 
  'all'
];

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

export interface InitOptions {
  ai?: AIType;
  force?: boolean;
  skills?: string[]; // 指定要安装的技能名称列表
}

export interface CreateOptions {
  template?: string;
}

export interface DetectionResult {
  detected: AIType[];
  suggested: AIType | null;
}

export interface SkillMetadata {
  name: string;
  version: string;
  description: string;
  author?: string;
  tags?: string[];
  aiTypes: AIType[];
  createdAt: string;
  updatedAt: string;
}