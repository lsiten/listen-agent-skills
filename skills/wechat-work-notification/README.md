# 企业微信通知 Skill

## 描述

企业微信机器人通知技能，支持通过Webhook发送各种类型的消息到企业微信群聊。

## 功能特性

- 📝 文本消息发送
- 📋 Markdown格式消息
- 🖼️ 图片消息发送
- 📰 图文消息发送
- 🏷️ 支持@指定用户
- 🔗 支持链接跳转

## 配置信息

- **Webhook URL**: `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d4da4f73-3667-49a2-b2f3-f79235e984e7`
- **消息类型**: text, markdown, image, news
- **请求方法**: POST
- **内容类型**: application/json

## 使用方法

### 基础文本消息
```bash
curl -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d4da4f73-3667-49a2-b2f3-f79235e984e7" \
-H "Content-Type: application/json" \
-d '{
  "msgtype": "text",
  "text": {
    "content": "Hello World!"
  }
}'
```

### Markdown消息
```bash
curl -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d4da4f73-3667-49a2-b2f3-f79235e984e7" \
-H "Content-Type: application/json" \
-d '{
  "msgtype": "markdown",
  "markdown": {
    "content": "## 标题\n**粗体文本**\n- 列表项1\n- 列表项2"
  }
}'
```

### @指定用户
```bash
curl -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d4da4f73-3667-49a2-b2f3-f79235e984e7" \
-H "Content-Type: application/json" \
-d '{
  "msgtype": "text",
  "text": {
    "content": "请注意查看重要通知",
    "mentioned_list": ["@all"]
  }
}'
```

## 消息类型说明

### 1. 文本消息 (text)
- `content`: 消息内容，最长不超过2048个字节
- `mentioned_list`: @用户列表，可使用userid或手机号
- `mentioned_mobile_list`: @用户手机号列表

### 2. Markdown消息 (markdown)
- `content`: markdown格式内容，最长不超过4096个字节
- 支持标题、粗体、斜体、链接、列表等格式

### 3. 图片消息 (image)
- `base64`: 图片base64编码
- `md5`: 图片MD5值
- 图片大小不超过2M，支持JPG、PNG格式

### 4. 图文消息 (news)
- `articles`: 图文消息数组，最多8条
- 每条包含：title、description、url、picurl

## 示例场景

1. **系统监控告警**: 服务器异常、应用错误通知
2. **构建部署通知**: CI/CD流程状态更新
3. **业务数据报告**: 日报、周报自动推送
4. **任务提醒**: 待办事项、会议提醒
5. **代码审查**: PR状态、代码合并通知
