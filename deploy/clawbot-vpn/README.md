# ClawBot + OpenClaw + SJTU Agent + Student VPN

This stack is for the final architecture:

```text
Personal WeChat
  -> ClawBot
  -> OpenClaw
  -> SJTU Agent MCP Server
  -> sjtu-vpn strongSwan student VPN sidecar
  -> Zhiyuan-1 / SJTU campus services
```

Only `sjtu-agent` shares the VPN network namespace. OpenClaw and the existing
website/Caddy/Portainer stacks stay on the normal Hong Kong server network.

## Portainer

1. Install OpenClaw on the host with the official installer. It runs on port
   `18789` and does not need the SJTU VPN.
2. Create a new stack named `sjtu-agent-vpn`.
3. Use this directory as the compose path: `deploy/clawbot-vpn/docker-compose.yml`.
4. Copy `.env.example` to `.env` in Portainer and fill the real values.
5. Deploy the stack.
6. In host-installed OpenClaw, configure the MCP SSE URL:

```text
http://127.0.0.1:8765/sse
```

If you instead run OpenClaw as a container in the same `sjtu_agent_net`, use:

```text
http://sjtu-vpn:8765/sse
```

The compose file publishes MCP only on `127.0.0.1:8765`, so the campus tools are
not exposed to the public internet.

## Local Debug Tunnel

When QClaw/OpenClaw runs on your laptop:

```bash
ssh -L 8765:127.0.0.1:8765 root@47.83.232.52
```

Then configure OpenClaw/QClaw:

```text
http://127.0.0.1:8765/sse
```

## Custom Campus Search Sites

Custom sites are stored in:

```text
/data/sjtu-agent/campus_sites.json
```

You can add them through MCP with `add_campus_site`, or edit the JSON directly.
Supported kinds are `html` and `rss`.
