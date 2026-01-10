# NPM Token 设置指南

本文档详细说明如何为 GitHub Actions 自动发布配置 NPM Token。

## 🔑 创建 NPM Token

### 1. 登录 NPM
```bash
npm login
```

### 2. 创建 Automation Token
**重要**: 新版本的 npm 需要指定 token 名称

```bash
# 创建自动化 token（推荐用于 CI/CD）
npm token create --name="listen-agent-github-actions" --type=automation

# 或者创建只读 token（如果只需要读取权限）
npm token create --name="listen-agent-readonly" --type=readonly

# 查看现有 tokens
npm token list
```

### 3. Token 类型说明
- **automation**: 适用于 CI/CD 环境，可以发布包
- **readonly**: 只读权限，不能发布
- **publish**: 可以发布，但有 IP 限制

### 4. 复制 Token
创建成功后，复制显示的 token（以 `npm_` 开头）。

**⚠️ 重要**: Token 只会显示一次，请立即复制保存！

## 🔧 配置 GitHub Secrets

### 1. 打开 GitHub 仓库设置
1. 进入仓库: https://github.com/lsiten/listen-agent-skills
2. 点击 **Settings** 标签
3. 在左侧菜单中选择 **Secrets and variables** > **Actions**

### 2. 添加 NPM_TOKEN Secret
1. 点击 **New repository secret**
2. Name: `NPM_TOKEN`
3. Secret: 粘贴刚才复制的 NPM token
4. 点击 **Add secret**

## 🧪 测试配置

### 1. 验证 Token 有效性
```bash
# 使用 token 测试（替换 YOUR_TOKEN）
curl -H "Authorization: Bearer YOUR_TOKEN" https://registry.npmjs.org/-/whoami
```

### 2. 测试发布流程
1. 创建测试标签:
   ```bash
   git tag v1.0.2-test
   git push origin v1.0.2-test
   ```

2. 查看 GitHub Actions 执行结果:
   https://github.com/lsiten/listen-agent-skills/actions

3. 如果成功，删除测试标签:
   ```bash
   git tag -d v1.0.2-test
   git push origin :refs/tags/v1.0.2-test
   ```

## 🔍 常见问题

### Q: 创建 token 时提示 "Token name is required"
**A**: 使用新版本 npm 命令:
```bash
npm token create --name="your-token-name" --type=automation
```

### Q: GitHub Actions 发布失败，提示 401 Unauthorized
**A**: 检查以下几点:
1. NPM_TOKEN secret 是否正确设置
2. Token 是否有发布权限（使用 automation 类型）
3. Token 是否已过期

### Q: 如何撤销 Token？
**A**: 
```bash
# 列出所有 tokens
npm token list

# 撤销指定 token（使用 token ID）
npm token revoke <token-id>
```

### Q: 包名冲突怎么办？
**A**: 
1. 检查包名是否已被占用: https://www.npmjs.com/package/listen-agent
2. 如果被占用，修改 package.json 中的 name 字段
3. 考虑使用 scoped package: `@your-username/listen-agent`

## 📋 安全最佳实践

1. **定期轮换 Token**: 建议每 6-12 个月更换一次
2. **最小权限原则**: 只给予必要的权限
3. **监控使用情况**: 定期检查 token 使用日志
4. **及时撤销**: 不再使用的 token 应立即撤销

## 🔗 相关链接

- [NPM Token 官方文档](https://docs.npmjs.com/about-access-tokens)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [NPM 发布指南](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)