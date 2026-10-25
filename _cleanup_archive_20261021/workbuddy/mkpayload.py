#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用载荷构造器：把提示词文本文件包成本机 ollama 载荷 JSON。

用法：
  python .workbuddy/mkpayload.py <prompt.txt> <payload.json> [num_predict]
固定：think=false / num_ctx=8192 / temperature=0.8
"""
import json
import sys

if len(sys.argv) < 3:
    print("usage: mkpayload.py <prompt.txt> <payload.json> [num_predict]")
    sys.exit(2)

prompt = open(sys.argv[1], encoding="utf-8").read()
num_predict = int(sys.argv[3]) if len(sys.argv) > 3 else 4096

payload = {
    "model": "qwen3:14b",
    "prompt": prompt,
    "stream": False,
    "think": False,
    "options": {
        "num_predict": num_predict,
        "temperature": 0.8,
        "num_ctx": 8192,
    },
}
with open(sys.argv[2], "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)
print(f"OK {sys.argv[2]} prompt_chars={len(prompt)} num_predict={num_predict}")
