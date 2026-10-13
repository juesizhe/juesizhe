#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · GitHub 同步脚本（基于 REST API，绕过 git 协议端点 github.com:443 不可达问题）

职责：
  1. 逐文件对比本地技能目录 与 远端仓库 juesizhe/juesizhe。
  2. 远端不存在 → 创建；内容一致 → 跳过；内容不同 → 冲突处理。
  3. 冲突处理默认「保留内容更完整（字节更长）的一方」，并把冲突写入报告，
     供人工/自动化核查是否丢失功能（满足「不一致需合并、保留最完好功能」）。
  4. 本地演进版是持续维护的权威源，默认以本地为准；仅当远端明显更长时才保留远端。

安全：
  - Token 从环境变量 GITHUB_TOKEN 读取；若缺失则从本机文件读取（不写进仓库）。
  - 仅同步技能本体；.git / .workbuddy 永不上传。

用法：
  GITHUB_TOKEN=xxx python sync_github.py
  python sync_github.py        # 自动从 ~/.workbuddy/github_token.txt 读取
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone

REPO = "juesizhe/juesizhe"
API = "https://api.github.com"
ROOT = os.path.dirname(os.path.abspath(__file__))          # 技能根目录
BRANCH = "main"
EXCLUDE_DIRS = {".git", ".workbuddy"}
EXCLUDE_FILES = set()                                      # 可在需要时追加
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".workbuddy", "github_token.txt")
LARGE_FILE_GUARD = 950 * 1024                              # >950KB 走警告跳过（极少触发）

REPORT_LINES = []


def log(msg):
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}] {msg}"
    print(line)
    REPORT_LINES.append(line)


def get_token():
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok.strip()
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        log(f"ERROR 无法读取 Token: {e}")
        sys.exit(2)


def api(method, path, data=None):
    url = API + path
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "juesizhe-sync")
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return e.code, body
    except Exception as e:
        return -1, str(e)


def get_remote(path):
    status, data = api("GET", f"/repos/{REPO}/contents/{path}")
    if status == 200:
        return data  # 含 'sha' 与 'content'(base64)
    return None


def put_file(path, raw_bytes, remote_sha, message):
    b64 = base64.b64encode(raw_bytes).decode("ascii")
    data = {"message": message, "content": b64, "branch": BRANCH}
    if remote_sha:
        data["sha"] = remote_sha
    status, resp = api("PUT", f"/repos/{REPO}/contents/{path}", data)
    if status in (200, 201):
        return True, None
    return False, f"HTTP {status}: {resp if isinstance(resp, str) else resp.get('message')}"


def walk_local():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_FILES:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            files.append(rel)
    return sorted(files)


def main():
    global TOKEN
    TOKEN = get_token()
    if not TOKEN:
        log("ERROR: 未找到 GitHub Token")
        sys.exit(2)

    local_files = walk_local()
    log(f"本地待同步文件数: {len(local_files)}  (根目录 {ROOT})")

    created = updated = skipped = conflicts = failed = 0

    for rel in local_files:
        full = os.path.join(ROOT, rel)
        with open(full, "rb") as f:
            local_bytes = f.read()

        # 大文件保护（极少触发；tuiyan_corpus.md 通常在远端已一致而被跳过）
        if len(local_bytes) > LARGE_FILE_GUARD:
            log(f"SKIP(过大) {rel}  {len(local_bytes)//1024}KB —— 需 Git Data API，已跳过")
            skipped += 1
            continue

        remote = get_remote(rel)
        if remote is None:
            ok, err = put_file(rel, local_bytes, None,
                               f"sync: 新增 {rel}")
            if ok:
                log(f"CREATE {rel}")
                created += 1
            else:
                log(f"FAIL   {rel}: {err}")
                failed += 1
            continue

        remote_bytes = base64.b64decode(remote.get("content", ""))
        if remote_bytes == local_bytes:
            skipped += 1
            continue

        # 内容不同 → 冲突
        conflicts += 1
        remote_len = len(remote_bytes)
        local_len = len(local_bytes)
        if local_len >= remote_len:
            chosen = "local"
            chosen_bytes = local_bytes
        else:
            chosen = "remote"
            chosen_bytes = remote_bytes
        log(f"CONFLICT {rel}: 本地 {local_len}B / 远端 {remote_len}B → 保留【{chosen}】(更完整)")
        if chosen == "local":
            ok, err = put_file(rel, local_bytes, remote.get("sha"),
                               f"sync: 以本地为准更新 {rel}")
            if ok:
                updated += 1
            else:
                log(f"FAIL   {rel}: {err}")
                failed += 1
        else:
            # 保留远端：仅记录，不覆盖（避免丢失远端独有内容）；如需采用远端，人工确认后处理
            log(f"NOTE   {rel}: 保留远端版本，未覆盖本地。若确认采用远端，请手动合并。")

    log("=" * 60)
    log(f"完成 → 新增 {created} / 更新 {updated} / 跳过 {skipped} / 冲突 {conflicts} / 失败 {failed}")
    # 报告落盘（不进仓库，写在本地临时）
    report_path = os.path.join(os.path.expanduser("~"), ".workbuddy", "juesizhe_sync_report.txt")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(REPORT_LINES) + "\n")
        log(f"报告已写入: {report_path}")
    except Exception:
        pass
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
