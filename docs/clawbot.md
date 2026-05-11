# ClawBot / OpenClaw 部署说明

本项目现在推荐的微信路线是：

```text
个人微信
  -> ClawBot
  -> OpenClaw
  -> SJTU Agent MCP Server
  -> 交大 VPN sidecar
  -> 致远一号 / 校园平台
```

也就是说，微信接入和对话编排交给 ClawBot/OpenClaw；SJTU Agent 只提供校园能力。

## 本地调试

先在本机完成配置：

```bash
pip install -e .
sjtu-agent setup
sjtu-agent mcp --http --host 127.0.0.1 --port 8765
```

然后在 OpenClaw/QClaw 里配置 MCP SSE：

```text
http://127.0.0.1:8765/sse
```

可用工具包括：

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

## 香港服务器长期运行

OpenClaw 推荐按官方脚本安装在宿主机上：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

它默认运行 Gateway 网关端口 `18789`，不需要进入 VPN 网络。为了让宿主机上的 OpenClaw 能调用 Docker 里的 SJTU Agent MCP，`deploy/clawbot-vpn/docker-compose.yml` 会把 MCP 端口只映射到本机：

```yaml
ports:
  - "127.0.0.1:8765:8765"
```

所以宿主机 OpenClaw 的 MCP SSE URL 填：

```text
http://127.0.0.1:8765/sse
```

服务器建议使用新增 stack：

```text
deploy/clawbot-vpn/
```

Portainer 里新建 stack：

```text
sjtu-agent-vpn
```

环境变量复制：

```text
deploy/clawbot-vpn/.env.example -> .env
```

如果你使用官方脚本在宿主机安装 OpenClaw，可以不启用 compose 里的 `openclaw` profile；它只是给容器化 OpenClaw 预留的可选入口。

关键变量：

```env
SJTU_VPN_SERVER=stuv4.vpn.sjtu.edu.cn
SJTU_VPN_ID=@stu.vpn.sjtu.edu.cn
SJTU_VPN_USER=你的 jAccount 用户名
SJTU_VPN_PASSWORD=你的 jAccount 密码
ZHIYUAN_API_KEY=你的致远一号 API Key
ZHIYUAN_BASE_URL=https://models.sjtu.edu.cn/api/v1
ZHIYUAN_MODEL=deepseek-chat
```

如果 OpenClaw 不是宿主机安装，而是作为容器加入同一个 Docker 网络，MCP URL 才填：

```text
http://sjtu-vpn:8765/sse
```

如果 OpenClaw 先跑在本地电脑，用 SSH tunnel：

```bash
ssh -L 8765:127.0.0.1:8765 root@47.83.232.52
```

本地 OpenClaw/QClaw 填：

```text
http://127.0.0.1:8765/sse
```

## VPN 网络边界

`deploy/clawbot-vpn/docker-compose.yml` 的关键点：

```text
openclaw      普通 Docker 网络，不走 VPN
sjtu-vpn      strongSwan 学生 VPN
sjtu-agent    network_mode: service:sjtu-vpn
```

所以：

- OpenClaw 访问微信/插件/外部网络：普通香港公网。
- SJTU Agent 访问致远一号和校内服务：交大学生 VPN。
- 原有 `ruilinlu.com`、Caddy、WordPress、MariaDB、FileBrowser、Portainer：不受影响。

## 可扩展校园网站搜索

内置站点：

- `jwc`：教务处通知公告
- `shuiyuan`：水源社区
- `dyweb`：传承·交大课程资料

后续你可以不用改代码，直接通过 MCP 添加新站点：

```text
add_campus_site(
  site_id="seiee_news",
  name="电院新闻",
  url="https://www.seiee.sjtu.edu.cn/",
  kind="html",
  search_url="https://www.seiee.sjtu.edu.cn/search?keyword={query}"
)
```

也可以编辑运行时文件：

```text
/data/sjtu-agent/campus_sites.json
```

示例：

```json
{
  "seiee_news": {
    "id": "seiee_news",
    "name": "电院新闻",
    "kind": "html",
    "url": "https://www.seiee.sjtu.edu.cn/",
    "search_url": "https://www.seiee.sjtu.edu.cn/search?keyword={query}"
  },
  "example_rss": {
    "id": "example_rss",
    "name": "示例 RSS",
    "kind": "rss",
    "url": "https://example.sjtu.edu.cn/rss.xml"
  }
}
```

之后 `search_campus` 不传 `sites` 时会搜索内置站点和所有自定义站点；如果指定站点，只搜索指定 `site_id`。

## 主动提醒

查询式提醒已经通过 MCP 支持：

```text
add_reminder / list_reminders / remove_reminder
```

主动推送取决于你的 OpenClaw 部署是否暴露 webhook。项目新增了通用推送适配器：

```env
OPENCLAW_PUSH_URL=
OPENCLAW_PUSH_TOKEN=
OPENCLAW_PUSH_TO=
```

如果 `OPENCLAW_PUSH_URL` 留空，提醒仍可查询，但不会主动通过 ClawBot 推送。你也可以继续配置 Telegram 作为主动提醒通道。
