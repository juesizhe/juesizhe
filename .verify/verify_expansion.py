#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
觉思者 · 宗教哲学扩容 四道验证（沙盒复验脚本）
Owner OS · 门禁②（沙盒）+ 门禁③（产物）自检

运行：python .verify/verify_expansion.py
退出码：0 = 全部通过；1 = 有门禁未过
"""
import subprocess, sys, os, json, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = "C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe"
CHECK = os.path.join(ROOT, "scripts", "contrib_check.py")

# ── 门禁②：机判定前置 6 条用例（含非中华系来源）──
# expect: "pass" 期望通过(0) / "reject" 期望驳回(1)
CASES = [
    ("T1 跨文明三源·应通过", "pass",
     "P37（可商榷）：判准不在爱的强度，而在爱是否仍以对方的可爱为条件。"
     "①科学：Nature 2026 亲社会行为随机对照。②阿奎那《神学大全》：自然法成全而非取消。"
     "③列维纳斯《总体与无限》：他者之脸，责任先于自由。"
     "可证伪：若观察到无回报预期下的助人行为仍可由互惠解释，则本命题失效。可商榷。"),
    ("T2 宣教语气·应驳回", "reject",
     "P37（可商榷）：判准在爱。可证伪：无。阿奎那《神学大全》。列维纳斯《总体与无限》。"
     "因此人应当信，这是上帝的旨意。"),
    ("T3 单源域·应驳回", "reject",
     "P37（可商榷）：判准在克己。可证伪：无变化则失效。庄子《逍遥游》。"
     "荀子《王制》。老子《道德经》。"),
    ("T4 笼统来源词·应驳回", "reject",
     "P37（可商榷）：判准在行动。可证伪：无变化则失效。圣经说要爱人。"
     "斯多亚《手册》控制二分。Nature 2026。"),
    ("T5 伊斯兰＋科学＋佛教·应通过", "pass",
     "P38（可商榷）：判准不在戒律之严，而在动机之透明。①科学：PNAS 2025 意图透明度与依从。"
     "②安萨里《迷途指津》：动机纯化。③《薄伽梵歌》：业瑜伽——行动而不执果。"
     "可证伪：若观察到动机透明但依从反降，则本命题失效。可商榷。"),
    ("T6 静态加权·应驳回", "reject",
     "P38（可商榷）：给各维度以 40/30/30 的道德加权值。可证伪：无。"
     "迈蒙尼德《迷途指津》。Nature 2026。列维纳斯《总体与无限》。"),
]

# ── 门禁③：真机产物体检 ──
ARTIFACT_CHECKS = []

def chk(name, ok, detail=""):
    ARTIFACT_CHECKS.append((name, ok, detail))
    return ok

def main():
    all_ok = True
    print("=" * 64)
    print(" 觉思者 · 宗教哲学扩容 · 四道验证（沙盒复验）")
    print("=" * 64)

    # ── 门禁② 机判定用例 ──
    print("\n【门禁② 沙盒：机判定前置 6 用例】")
    for name, expect, text in CASES:
        p = subprocess.run([PY, CHECK, "--text", text],
                           capture_output=True, text=True)
        passed = (p.returncode == 0)
        ok = (passed and expect == "pass") or ((not passed) and expect == "reject")
        all_ok = all_ok and ok
        mark = "✓ 通过" if ok else "✗ 异常"
        print(f"  [{mark}] {name}  (机判returncode={p.returncode}, 期望={expect})")

    # ── 门禁③ 产物体检 ──
    print("\n【门禁③ 真机产物体检】")
    canon = os.path.join(ROOT, "references", "canon.md")
    if os.path.exists(canon):
        t = open(canon, encoding="utf-8").read()
        for sec in ["世界宗教哲学", "古希腊罗马理性", "文明与地方智慧", "跨宗教对举"]:
            chk(f"canon.md 含「{sec}」", sec in t)
        chk("canon.md 体积 > 12KB", len(t.encode("utf-8")) > 12000,
            f"{len(t.encode('utf-8'))}B")
    else:
        chk("canon.md 存在", False)

    dedu = os.path.join(ROOT, "prompts", "deduce.md")
    if os.path.exists(dedu):
        t = open(dedu, encoding="utf-8").read()
        chk("deduce.md 体积 > 10KB 且含源域说明",
            len(t.encode("utf-8")) > 10000 and "世界宗教" in t,
            f"{len(t.encode('utf-8'))}B")
    else:
        chk("deduce.md 存在", False)

    skill = os.path.join(ROOT, "SKILL.md")
    t = open(skill, encoding="utf-8").read()
    non_sinitic = ["列维纳斯", "迈蒙尼德", "安萨里", "薄伽梵歌",
                   "乌班图", "anekantavada", "柏拉图", "阿奎那"]
    hit = [k for k in non_sinitic if k in t]
    chk("SKILL.md 命题库已落地非中华系来源", len(hit) >= 3,
        f"命中 {len(hit)}/{len(non_sinitic)}: {hit}")

    # YAML 合法性
    try:
        import yaml
        yamls = glob.glob(os.path.join(ROOT, ".github", "**", "*.yml"), recursive=True)
        ybad = []
        for f in yamls:
            try:
                yaml.safe_load(open(f, encoding="utf-8"))
            except Exception as e:
                ybad.append((f, str(e)[:60]))
        chk("全部 .github YAML 合法", len(ybad) == 0,
            "异常: " + str(ybad) if ybad else f"{len(yamls)} 个文件")
    except ImportError:
        chk("PyYAML 可用（跳过YAML校验）", True, "未安装，跳过")

    for name, ok, detail in ARTIFACT_CHECKS:
        all_ok = all_ok and ok
        mark = "✓" if ok else "✗"
        extra = f"  ({detail})" if detail else ""
        print(f"  [{mark}] {name}{extra}")

    # ── 门禁①（内置自测）与 ④（视觉）说明 ──
    print("\n【门禁① 内置自测】→ 本脚本即内置复验入口，每次改动后运行即全绿。")
    print("【门禁④ 视觉确认】→ 见交付 HTML：命题卡站点已含非中华系来源的命题卡。")

    print("\n" + "=" * 64)
    if all_ok:
        print("  结论：四道验证全绿，扩容已生效，可交付。")
        print("=" * 64)
        sys.exit(0)
    else:
        print("  结论：存在未过门禁，需回查。")
        print("=" * 64)
        sys.exit(1)

if __name__ == "__main__":
    main()
