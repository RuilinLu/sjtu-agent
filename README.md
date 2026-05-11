# SJTU Agent

面向上海交通大学学生的校园助手。当前推荐架构是：

```text
个人微信 + ClawBot
  -> OpenClaw
  -> SJTU Agent MCP Server
  -> 交大学生 VPN sidecar
  -> 致远一号 / Canvas / DDL / 课表 / 成绩 / 校园搜索
```

SJTU Agent 不再把微信接入层作为主任务；微信和对话编排交给 ClawBot/OpenClaw，本项目专注提供稳定的校园工具能力。

## 安装

macOS / Linux:

```bash
git clone https://github.com/RuilinLu/sjtu-agent.git
cd sjtu-agent
bash install.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/RuilinLu/sjtu-agent.git
cd sjtu-agent
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

手动安装：

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
sjtu-agent setup
```

## 致远一号 API

致远一号 API 按上海交通大学官方文档配置，OpenAI-compatible base URL 为：

```text
https://models.sjtu.edu.cn/api/v1
```

在 `.env` 中配置：

```env
ZHIYUAN_API_KEY=你的致远一号 API Key
ZHIYUAN_BASE_URL=https://models.sjtu.edu.cn/api/v1
ZHIYUAN_MODEL=deepseek-chat
```

申请方式：登录 `https://my.sjtu.edu.cn/`，搜索并提交「“致远一号”AI模型API申请（测试）」。校外或香港服务器访问致远一号通常需要交大 VPN。

常用模型：

| 调用名 | 说明 |
| --- | --- |
| `deepseek-chat` | 默认聊天模型 |
| `deepseek-reasoner` | 推理模型 |
| `minimax` / `minimax-m2.5` | MiniMax |
| `qwen3coder` | Qwen Coder |
| `qwen3vl` | Qwen VL |

## ClawBot / OpenClaw 接入

本项目推荐：

```text
个人微信 -> ClawBot -> OpenClaw -> sjtu-agent MCP
```

本地调试：

```bash
sjtu-agent setup
sjtu-agent mcp --http --host 127.0.0.1 --port 8765
```

OpenClaw/QClaw MCP SSE URL:

```text
http://127.0.0.1:8765/sse
```

服务器 Docker 部署见：

```text
docs/clawbot.md
deploy/clawbot-vpn/
```

香港服务器长期运行时，OpenClaw 不走 VPN；只有 `sjtu-agent` 容器共享 `sjtu-vpn` 网络访问致远一号和校内服务。

## MCP 工具

`sjtu-agent mcp` 当前暴露：

- `check_setup`
- `get_ddls`
- `get_next_lab`
- `get_all`
- `get_schedule`
- `query_grades`
- `add_reminder`
- `list_reminders`
- `remove_reminder`
- `search_campus`
- `list_campus_sites`
- `add_campus_site`
- `remove_campus_site`
- `download_assignments`
- `list_assignment_files`
- `read_assignment_file`

Docker 内监听：

```bash
sjtu-agent mcp --http --host 0.0.0.0 --port 8765
```

不要把 MCP 端口裸露到公网。生产部署应只允许 OpenClaw 所在 Docker 网络访问，或通过 SSH tunnel/认证反向代理访问。

## 可扩展校园搜索

内置站点：

- `jwc`：教务处通知公告
- `shuiyuan`：水源社区
- `dyweb`：传承·交大课程资料

新增网站不需要改代码，可以通过 MCP 调用：

```text
add_campus_site(site_id, name, url, kind="html", search_url="")
```

运行时配置文件：

```text
campus_sites.json
```

在服务器部署中路径通常为：

```text
/data/sjtu-agent/campus_sites.json
```

## 微信接入路线

推荐：

```text
个人微信 + ClawBot + OpenClaw + SJTU Agent MCP
```

备用：

```text
wechat_bot.py / sjtu-agent wechat-bot
```

备用方案使用 ilink 扫码长轮询，仅建议个人测试或 OpenClaw 暂不支持主动 push 时临时使用，不作为主路线。

企业微信/微信客服/公众号适合以后做组织级服务；当前个人使用不需要。

## 常用命令

```bash
sjtu-agent setup
sjtu-agent doctor
sjtu-agent chat
sjtu-agent ddl --canvas-only
sjtu-agent daily-report --test
sjtu-agent remind-check --list
sjtu-agent mcp --http --host 127.0.0.1 --port 8765
```

## 运行时数据

默认运行时目录：

- macOS: `~/Library/Application Support/sjtu-agent`
- Linux: `${XDG_DATA_HOME:-~/.local/share}/sjtu-agent`
- Windows: `%APPDATA%/sjtu-agent`

Docker 推荐：

```env
SJTU_AGENT_HOME=/data/sjtu-agent
```

敏感信息只放 `.env`、`config.json`、`agent_config.json` 或运行时目录，不要提交到 GitHub。
