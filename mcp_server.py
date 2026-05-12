#!/usr/bin/env python3
"""
SJTU Agent MCP Server

This server is the recommended integration point for ClawBot/OpenClaw. WeChat
transport and conversation orchestration stay in ClawBot/OpenClaw; this process
only exposes stable SJTU campus tools through MCP.

Typical local run:
  sjtu-agent mcp --http --host 127.0.0.1 --port 8765

Typical Docker run:
  sjtu-agent mcp --http --host 0.0.0.0 --port 8765
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP

from sjtu_agent.agent.tools import run_tool

try:
    import ddl_checker as dc
except Exception as exc:  # pragma: no cover - setup errors surface through tools
    dc = None
    _DDL_IMPORT_ERROR = exc
else:
    _DDL_IMPORT_ERROR = None


mcp = FastMCP("sjtu-agent")


def _run_in_worker(func, *args: Any, **kwargs: Any) -> Any:
    """Run sync tools outside FastMCP's asyncio loop."""

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(func, *args, **kwargs).result()


def _json_result(tool_name: str, args: dict[str, Any] | None = None) -> str:
    """Run a built-in SJTU Agent tool and return compact JSON text."""

    return _run_in_worker(run_tool, tool_name, args or {})


def _dc_result(func_name: str, *args: Any, **kwargs: Any) -> str:
    """Run a ddl_checker helper and return JSON text."""

    if dc is None:
        return json.dumps({"error": f"ddl_checker import failed: {_DDL_IMPORT_ERROR}"}, ensure_ascii=False)
    try:
        result = getattr(dc, func_name)(*args, **kwargs)
    except Exception as exc:
        result = {"error": str(exc)}
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def check_setup() -> str:
    """Check whether SJTU credentials, Canvas token, and LLM config are present."""

    return _json_result("check_setup")


@mcp.tool()
def save_credentials(
    jaccount_username: str = "",
    jaccount_password: str = "",
    canvas_token: str = "",
    mooc_username: str = "",
    mooc_password: str = "",
) -> str:
    """Save SJTU Agent credentials and Canvas token to the configured data dir."""

    return _json_result(
        "save_credentials",
        {
            "jaccount_username": jaccount_username,
            "jaccount_password": jaccount_password,
            "canvas_token": canvas_token,
            "mooc_username": mooc_username,
            "mooc_password": mooc_password,
        },
    )


@mcp.tool()
def setup_canvas(
    open_browser: bool = False,
    auto_create: bool = False,
    token_purpose: str = "SJTU Agent",
) -> str:
    """Guide Canvas token setup or validate an existing Canvas token."""

    return _json_result(
        "setup_canvas",
        {
            "open_browser": open_browser,
            "auto_create": auto_create,
            "token_purpose": token_purpose,
        },
    )


@mcp.tool()
def login_platform(platform: str) -> str:
    """Refresh cookies for a supported platform after credentials are configured."""

    return _json_result("login_platform", {"platform": platform})


@mcp.tool()
def get_ddls(
    skip_canvas: bool = False,
    skip_aihaoke: bool = False,
    skip_icourse: bool = False,
) -> str:
    """Get unfinished Canvas / AI haoke / iCourse DDLs sorted by due time."""

    return _json_result(
        "get_ddls",
        {
            "skip_canvas": skip_canvas,
            "skip_aihaoke": skip_aihaoke,
            "skip_icourse": skip_icourse,
        },
    )


@mcp.tool()
def get_next_lab() -> str:
    """Get the next physics lab arrangement."""

    return _json_result("get_next_lab")


@mcp.tool()
def get_all(
    skip_canvas: bool = False,
    skip_aihaoke: bool = False,
    skip_icourse: bool = False,
    skip_phycai: bool = False,
) -> str:
    """Get DDLs and the next physics lab in one call."""

    return _json_result(
        "get_all",
        {
            "skip_canvas": skip_canvas,
            "skip_aihaoke": skip_aihaoke,
            "skip_icourse": skip_icourse,
            "skip_phycai": skip_phycai,
        },
    )


@mcp.tool()
def get_canvas_overview(
    course_filter: str = "",
    include_announcements: bool = True,
    include_assignment_descriptions: bool = True,
    include_html: bool = False,
    max_courses: int = 30,
    max_announcements_per_course: int = 20,
) -> str:
    """Get complete Canvas courses, assignments, submissions, announcements, and URLs."""

    return _json_result(
        "get_canvas_overview",
        {
            "course_filter": course_filter,
            "include_announcements": include_announcements,
            "include_assignment_descriptions": include_assignment_descriptions,
            "include_html": include_html,
            "max_courses": max_courses,
            "max_announcements_per_course": max_announcements_per_course,
        },
    )


@mcp.tool()
def get_schedule(
    query_type: str = "day",
    date: str = "",
    week_offset: int = 0,
    set_semester_start: str = "",
    refresh: bool = False,
) -> str:
    """Query today's, tomorrow's, a specific day's, or a week's class schedule."""

    return _json_result(
        "get_schedule",
        {
            "query_type": query_type,
            "date": date,
            "week_offset": week_offset,
            "set_semester_start": set_semester_start,
            "refresh": refresh,
        },
    )


@mcp.tool()
def query_grades(year: str = "", semester: str = "") -> str:
    """Query grades and GPA from i.sjtu.edu.cn."""

    return _json_result("query_grades", {"year": year, "semester": semester})


@mcp.tool()
def add_reminder(title: str, start: str, end: str = "", note: str = "") -> str:
    """Add a local reminder. Use 'YYYY-MM-DD HH:MM' for start/end when possible."""

    return _json_result("add_reminder", {"title": title, "start": start, "end": end, "note": note})


@mcp.tool()
def list_reminders() -> str:
    """List active and expired local reminders."""

    return _json_result("list_reminders")


@mcp.tool()
def remove_reminder(reminder_id: int) -> str:
    """Remove a reminder by id."""

    return _json_result("remove_reminder", {"reminder_id": reminder_id})


@mcp.tool()
def search_campus(query: str, sites: list[str] | None = None, max_results: int = 6) -> str:
    """Search built-in and user-configured SJTU/campus-related sites."""

    args: dict[str, Any] = {"query": query, "max_results": max_results}
    if sites:
        args["sites"] = sites
    return _json_result("search_campus", args)


@mcp.tool()
def list_campus_sites() -> str:
    """List built-in and custom campus search sites."""

    return _dc_result("list_campus_sites")


@mcp.tool()
def add_campus_site(
    site_id: str,
    name: str,
    url: str,
    kind: str = "html",
    search_url: str = "",
) -> str:
    """Add a custom searchable campus site.

    kind supports:
      - html: fetch search_url or url and collect matching links
      - rss: parse RSS/Atom feed items

    search_url may contain {query} for URL-encoded query text and {query_raw}
    for raw text. Example: https://example.sjtu.edu.cn/search?q={query}
    """

    return _dc_result(
        "add_campus_site",
        site_id=site_id,
        name=name,
        url=url,
        kind=kind,
        search_url=search_url,
    )


@mcp.tool()
def remove_campus_site(site_id: str) -> str:
    """Remove a custom campus site by id."""

    return _dc_result("remove_campus_site", site_id=site_id)


@mcp.tool()
def download_assignments(
    skip_canvas: bool = False,
    skip_aihaoke: bool = False,
    course_filter: str = "",
    assignment_filter: str = "",
    due_within_days: int = 7,
    output_dir: str = "./assignments",
) -> str:
    """Download recent assignment descriptions and attachments."""

    return _json_result(
        "download_assignments",
        {
            "skip_canvas": skip_canvas,
            "skip_aihaoke": skip_aihaoke,
            "course_filter": course_filter,
            "assignment_filter": assignment_filter,
            "due_within_days": due_within_days,
            "output_dir": output_dir,
        },
    )


@mcp.tool()
def list_assignment_files(course_filter: str = "", assignments_dir: str = "./assignments") -> str:
    """List downloaded assignment files."""

    return _json_result(
        "list_assignment_files",
        {"course_filter": course_filter, "assignments_dir": assignments_dir},
    )


@mcp.tool()
def read_assignment_file(file_path: str, max_chars: int = 8000, start_page: int = 1) -> str:
    """Read text from a downloaded assignment PDF or HTML file."""

    return _json_result(
        "read_assignment_file",
        {"file_path": file_path, "max_chars": max_chars, "start_page": start_page},
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the SJTU Agent MCP server.")
    parser.add_argument("--http", action="store_true", help="serve MCP over HTTP/SSE")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP/SSE listen host")
    parser.add_argument("--port", type=int, default=8765, help="HTTP/SSE listen port")
    args = parser.parse_args(argv)

    if args.http:
        print(f"Starting SJTU Agent MCP over HTTP/SSE at http://{args.host}:{args.port}/sse")
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
