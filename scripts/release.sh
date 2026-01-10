#!/bin/bash

# Listen Agent Skills 发布脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Listen Agent Skills 发布脚本${NC}"
echo

# 检查是否在main分支
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ 请在main分支上执行发布${NC}"
    echo -e "${YELLOW}当前分支: $CURRENT_BRANCH${NC}"
    exit 1
fi

# 检查工作区是否干净
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 工作区不干净，请先提交所有更改${NC}"
    git status --short
    exit 1
fi

# 获取当前版本
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo -e "${BLUE}📋 当前版本: ${CURRENT_VERSION}${NC}"

# 询问新版本
echo
echo -e "${YELLOW}请选择版本类型:${NC}"
echo "1) patch (修复版本, 如 1.0.0 -> 1.0.1)"
echo "2) minor (功能版本, 如 1.0.0 -> 1.1.0)"  
echo "3) major (重大版本, 如 1.0.0 -> 2.0.0)"
echo "4) 自定义版本"

read -p "请选择 (1-4): " VERSION_TYPE

case $VERSION_TYPE in
    1)
        NEW_VERSION=$(npm version patch --no-git-tag-version)
        ;;
    2)
        NEW_VERSION=$(npm version minor --no-git-tag-version)
        ;;
    3)
        NEW_VERSION=$(npm version major --no-git-tag-version)
        ;;
    4)
        read -p "请输入新版本号 (如 1.2.3): " CUSTOM_VERSION
        NEW_VERSION=$(npm version $CUSTOM_VERSION --no-git-tag-version)
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

# 移除v前缀
NEW_VERSION=${NEW_VERSION#v}

echo
echo -e "${GREEN}📦 新版本: ${NEW_VERSION}${NC}"

# 确认发布
read -p "确认发布版本 ${NEW_VERSION}? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ 发布已取消${NC}"
    # 恢复package.json
    git checkout package.json package-lock.json
    exit 0
fi

echo
echo -e "${BLUE}🔨 构建项目...${NC}"
npm run build

echo -e "${BLUE}🧪 运行测试...${NC}"
npm test

echo -e "${BLUE}📝 提交版本更新...${NC}"
git add package.json package-lock.json
git commit -m "chore: bump version to ${NEW_VERSION}"

echo -e "${BLUE}🏷️  创建标签...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

echo -e "${BLUE}📤 推送到远程仓库...${NC}"
git push origin main
git push origin "v${NEW_VERSION}"

echo
echo -e "${GREEN}✅ 发布完成！${NC}"
echo -e "${BLUE}📋 版本: v${NEW_VERSION}${NC}"
echo -e "${BLUE}🔗 GitHub Actions 将自动发布到 NPM${NC}"
echo -e "${BLUE}🔗 查看发布状态: https://github.com/lsiten/listen-agent-skills/actions${NC}"
echo