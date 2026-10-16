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
  python sync_github.py --force        # 冲突时一律以本地为准（见下方说明）
  python sync_github.py --force-file a.md --force-file b.py  # 只对指定文件强制以本地为准

关于「保留更完整一方」的默认规则：
  冲突时默认保留字节更长的一方，以防覆盖远端他人的改动。
  但该规则会挡住一类正常变更——由脚本重新生成且内容被有意缩短的文件
  （例：prompts/deduce.md 刷新时间戳后重排、cards/Pn.md 标题截断、重构后变短的 workflow）。
  遇到这类情况用 --force / --force-file 显式以本地为准。
"""
import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone

REPO = "juesizhe/juesizhe"
API = "https://api.github.com"
ROOT = os.path.dirname(os.path.abspath(__file__))          # 技能根目录
BRANCH = "main"
EXCLUDE_DIRS = {".git", ".workbuddy", "_site"}
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
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return e.code, body
    except Exception as e:
        return -1, str(e)


def api_retry(method, path, data=None, retries=3):
    """网络抖动时重试；仅当确实拿到 HTTP 响应（非 -1/0）才返回。"""
    last = None
    for i in range(retries):
        status, resp = api(method, path, data)
        if status != -1 and status != 0:
            return status, resp
        last = resp
        time.sleep(2 + i * 2)
    return -1, last


def get_remote(path):
    status, data = api_retry("GET", f"/repos/{REPO}/contents/{path}")
    if status == 200 and isinstance(data, dict):
        return data  # 含 'sha' 与 'content'(base64)
    return None


def put_file(path, raw_bytes, remote_sha, message):
    b64 = base64.b64encode(raw_bytes).decode("ascii")
    data = {"message": message, "content": b64, "branch": BRANCH}
    if remote_sha:
        data["sha"] = remote_sha
    status, resp = api("PUT", f"/repos/{REPO}/contents/{path}", data)
    # 兜底：若 GET 误判为不存在而触发「sha wasn't supplied」，说明远端已有该文件；
    # 此时不强行覆盖（避免丢失远端内容），按「保留远端、跳过」处理为良性结果。
    if status == 422 and remote_sha is None and "sha" in str(resp):
        return True, "SKIP_EXISTING"
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


def parse_args(argv):
    """返回 (force_all: bool, force_files: set[str])。"""
    force_files = set()
    for i, a in enumerate(argv):
        if a == "--force-file" and i + 1 < len(argv):
            p = argv[i + 1].replace("\\", "/")
            if p.startswith("./"):
                p = p[2:]
            force_files.add(p)
    return ("--force" in argv), force_files


def resolve_conflict(rel, local_bytes, remote_bytes, remote, force_all, force_files):
    """
    冲突处置。默认「保留字节更长、更完整的一方」；命中 force 则以本地为准。
    返回 "local" / "remote"，不上传其行为由调用方处理。
    """
    return "local" if (force_all or rel in force_files or len(local_bytes) >= len(remote_bytes)) else "remote"


def main():
    global TOKEN
    FORCE_ALL, FORCE_FILES = parse_args(sys.argv[1:])
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
            if ok and err == "SKIP_EXISTING":
                log(f"SKIP_EXISTING {rel} (远端已存在，保留远端)")
                skipped += 1
            elif ok:
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
        why = "强制(--force)" if (FORCE_ALL or rel in FORCE_FILES) else f"本地 {local_len}B / 远端 {remote_len}B"
        chosen = resolve_conflict(rel, local_bytes, remote_bytes, remote, FORCE_ALL, FORCE_FILES)
        log(f"CONFLICT {rel}: {why} → 保留【{chosen}】")
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
