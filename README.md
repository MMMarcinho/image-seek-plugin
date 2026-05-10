# image-seek-plugin

为 Claude Code 中的非多模态模型提供图片识别能力。

## 工作原理

- 启动一个 MCP Server，暴露 `describe_image` 工具
- 当 Claude Code 使用的模型不支持多模态（如 DeepSeek、Qwen、GLM 等）时，自动启用
- 工具接受文件路径、URL 或 base64 编码的图片，调用视觉 API 生成文字描述
- 当使用 Claude 等多模态模型时，插件自动禁用，避免不必要的调用

```
用户发来图片 → Claude Code 检测到图片 → 调用 describe_image 工具
                                            ↓
                               image-seek MCP Server
                                            ↓
                               OpenAI / Anthropic 视觉 API
                                            ↓
                               返回图片文字描述 → Claude Code 继续处理
```

## 安装

```bash
pip3 install -r image_seek/requirements.txt
bash scripts/setup.sh
```

`setup.sh` 会自动在 `.claude.json` 中注册 MCP Server，并在 `.claude/settings.json` 中授权。

## 配置

有两种配置方式，任选其一即可。

### 方式一：环境变量（推荐）

在 `.claude/settings.json` 的 `env` 中设置：

```json
{
  "env": {
    "IMAGE_SEEK_API_KEY": "sk-你的API密钥",
    "IMAGE_SEEK_PROVIDER": "openai",
    "IMAGE_SEEK_MODEL": "gpt-4o",
    "IMAGE_SEEK_ENDPOINT": "https://api.openai.com/v1"
  }
}
```

如果使用 Anthropic 兼容接口：

```json
{
  "env": {
    "IMAGE_SEEK_API_KEY": "sk-ant-你的API密钥",
    "IMAGE_SEEK_PROVIDER": "anthropic",
    "IMAGE_SEEK_MODEL": "claude-sonnet-4-6",
    "IMAGE_SEEK_ENDPOINT": "https://api.anthropic.com"
  }
}
```

### 方式二：config.yaml

直接编辑插件目录下的 `config.yaml`：

```yaml
provider:
  type: openai
  endpoint: https://api.openai.com/v1
  api_key: ${IMAGE_SEEK_API_KEY}
  model: gpt-4o
```

环境变量优先级高于 config.yaml：如果同时设置了 `IMAGE_SEEK_API_KEY` 环境变量和 config.yaml 中的 `api_key`，环境变量生效。

## 支持的视觉 API

| Provider | 模型示例 | 说明 |
|---|---|---|
| OpenAI 兼容 | GPT-4o, GPT-4V, Qwen-VL | 任何兼容 OpenAI Chat Completions 的接口 |
| Anthropic 兼容 | Claude Sonnet 4, Opus 4 | 任何兼容 Anthropic Messages 的接口 |

## 支持的图片格式

- PNG
- JPEG / JPG
- GIF
- WebP

最大文件：20MB。

## 使用方式

### 自动触发

插件会根据当前模型自动决定是否启用。非多模态模型（如 DeepSeek）看到图片时，Claude Code 会自动调用 `describe_image`。

可在 `config.yaml` 中配置非多模态模型的匹配规则：

```yaml
non_multimodal_models:
  - "deepseek-*"
  - "doubao-*"
  - "qwen-*"
  - "glm-*"
```

### 手动调用

也可以通过 skill 手动调用：

```
/image-seek
```

或直接在对话中调用工具：

- **本地文件**: `describe_image(source="/path/to/image.png")`
- **URL**: `describe_image(source="https://example.com/photo.jpg")`
- **Base64**: `describe_image(source="<base64 编码数据>")`

可以传入 `prompt` 参数指定描述重点：

```
describe_image(source="/path/to/screenshot.png", prompt="识别图中的错误信息")
```

## 项目结构

```
image-seek-plugin/
├── image_seek/           # Python 包（MCP Server）
│   ├── server.py         # MCP 服务主入口
│   ├── config.py         # 配置加载 & 模型匹配
│   └── providers/        # 视觉 API 适配器
│       ├── base.py       # 适配器基类
│       ├── openai.py     # OpenAI 兼容接口
│       └── anthropic.py  # Anthropic 兼容接口
├── hooks/                # Claude Code 生命周期钩子
│   └── session-start.sh  # 会话启动时检查是否启用
├── skills/               # Claude Code skill 文件
│   └── image-seek.md     # /image-seek 手动触发
├── scripts/
│   └── setup.sh          # 一键安装脚本
└── config.yaml           # 插件配置文件
```

## 常见问题

**Q: 为什么插件没有生效？**
A: 检查当前模型是否在 `non_multimodal_models` 列表中。如果模型本身支持多模态，插件会自动禁用。

**Q: API 返回错误？**
A: 检查 API Key 是否正确，endpoint 是否可访问。支持通过 HTTP 代理访问，设置 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量即可。

**Q: 如何切换视觉 API？**
A: 修改 `IMAGE_SEEK_PROVIDER` 环境变量为 `openai` 或 `anthropic`，同时更新对应的 `IMAGE_SEEK_ENDPOINT` 和 `IMAGE_SEEK_MODEL`。
