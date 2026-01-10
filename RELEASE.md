# 发布指南

本文档说明如何发布新版本的 Listen Agent Skills。

## 🚀 自动发布流程

### 方法1：使用发布脚本（推荐）

```bash
# 运行发布脚本
./scripts/release.sh
```

脚本会：
1. 检查当前分支和工作区状态
2. 询问版本类型（patch/minor/major/自定义）
3. 更新package.json版本
4. 构建和测试项目
5. 创建git标签
6. 推送到GitHub
7. 触发GitHub Actions自动发布到NPM

### 方法2：手动打标签

```bash
# 更新版本号
npm version patch  # 或 minor, major

# 推送标签
git push origin main
git push origin --tags
```

### 方法3：GitHub手动发布

1. 访问 GitHub Actions 页面
2. 选择 "Manual Release" 工作流
3. 点击 "Run workflow"
4. 输入版本号和是否为预发布版本
5. 点击运行

## 📋 发布检查清单

发布前请确保：

- [ ] 所有功能已完成并测试
- [ ] 代码已合并到main分支
- [ ] 工作区干净（无未提交的更改）
- [ ] 更新了CHANGELOG.md（如果有）
- [ ] 更新了README.md中的版本信息
- [ ] 所有CI检查通过

## 🔧 GitHub Actions配置

### 必需的Secrets

在GitHub仓库设置中添加以下secrets：

1. **NPM_TOKEN**
   ```bash
   # 获取NPM token
   npm login
   npm token create --read-only=false
   ```
   
2. **GITHUB_TOKEN** (自动提供，无需手动设置)

### 工作流说明

#### 1. CI工作流 (`.github/workflows/ci.yml`)
- 触发：推送到main/develop分支或PR
- 功能：代码检查、构建、测试
- 支持Node.js 16, 18, 20版本

#### 2. 发布工作流 (`.github/workflows/release.yml`)
- 触发：推送以`v`开头的标签
- 功能：构建、测试、发布到NPM、创建GitHub Release

#### 3. 手动发布工作流 (`.github/workflows/manual-release.yml`)
- 触发：手动触发
- 功能：创建标签、发布到NPM、创建GitHub Release
- 支持预发布版本

## 📦 NPM包配置

### package.json关键字段

```json
{
  "name": "listen-agent",
  "files": [
    "dist/",
    "templates/",
    "skills/",
    "README.md",
    "LICENSE"
  ],
  "bin": {
    "listen-agent": "./dist/index.js"
  },
  "engines": {
    "node": ">=16.0.0"
  }
}
```

### 发布内容

NPM包将包含：
- `dist/` - 编译后的JavaScript代码
- `templates/` - Agent Skills模板
- `skills/` - 示例skills
- `README.md` - 文档
- `LICENSE` - 许可证

## 🔍 版本策略

遵循[语义化版本](https://semver.org/)：

- **MAJOR** (1.0.0 -> 2.0.0): 不兼容的API更改
- **MINOR** (1.0.0 -> 1.1.0): 向后兼容的功能添加
- **PATCH** (1.0.0 -> 1.0.1): 向后兼容的错误修复

### 版本示例

- `1.0.0` - 首个稳定版本
- `1.0.1` - 修复bug
- `1.1.0` - 添加新功能
- `2.0.0` - 重大更改，可能不向后兼容

## 🚨 故障排除

### 常见问题

1. **NPM发布失败**
   - 检查NPM_TOKEN是否正确
   - 确认包名未被占用
   - 检查版本号是否已存在

2. **GitHub Actions失败**
   - 查看Actions日志
   - 检查Node.js版本兼容性
   - 确认所有依赖正确安装

3. **标签推送失败**
   - 检查Git权限
   - 确认标签格式正确（v1.0.0）
   - 检查是否有冲突的标签

### 回滚发布

如果需要回滚：

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0

# 从NPM撤回包（24小时内）
npm unpublish listen-agent@1.0.0
```

## 📞 支持

如有问题，请：
1. 查看GitHub Actions日志
2. 检查本文档的故障排除部分
3. 在GitHub仓库创建Issue