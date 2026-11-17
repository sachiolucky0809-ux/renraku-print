#!/usr/bin/env python3
"""index.html（スマホ用PWA）から、オフラインPC用の単体HTMLを生成する。

使い方:  python3 tools/build-pc.py
出力:    pc/renraku-print-pc.html

PC版では次のものを取り除く（ファイル1つだけで動くようにするため）:
  - PWA 関連（manifest, Service Worker, ホーム画面追加バナー）
  - ホーム画面アプリ用の PDF 共有印刷（PCでは通常の印刷画面を使う）
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
OUT = ROOT / "pc" / "renraku-print-pc.html"


def cut(s, start, end, repl="", include_end=True):
    """start から end までを repl に置き換える。見つからなければ停止。"""
    i = s.find(start)
    j = s.find(end, i + len(start)) if i >= 0 else -1
    if i < 0 or j < 0:
        sys.exit(f"build-pc: 置換箇所が見つかりません: {start!r} … {end!r}")
    if include_end:
        j += len(end)
    return s[:i] + repl + s[j:]


def replace_once(s, old, new):
    if s.count(old) != 1:
        sys.exit(f"build-pc: 置換箇所が1か所ではありません: {old!r}")
    return s.replace(old, new)


s = SRC.read_text(encoding="utf-8")

# <head> の PWA 関連
s = cut(s, "<!-- PWA -->", '<link rel="apple-touch-icon" href="./icon-192.svg">\n')
s = replace_once(s, "<title>連絡事項プリント作成</title>",
                 "<title>連絡事項プリント作成（PC版）</title>")

# ホーム画面追加バナー（HTML）
s = cut(s, "<!-- ===== インストールバナー ===== -->", "<!-- 通知 -->",
        "<!-- 通知 -->", include_end=True)

# Service Worker 登録とインストール処理（JS）
s = cut(s, "// --- Service Worker登録 ---", "// --- 初期化 ---", "// --- 初期化 ---")

# 印刷処理: PDF 共有方式を取り除き、通常の印刷のみにする
s = cut(s, "// 印刷:", "document.getElementById('btnPrint').addEventListener('click', printPage);",
        "// 印刷\nfunction printPage() { window.print(); }\n\n"
        "document.getElementById('btnPrint').addEventListener('click', printPage);")
s = replace_once(s, "  preparePdfIfNeeded();\n", "")

# 見出しに PC版 と表示
s = re.sub(r'(<small style="font-weight:400;font-size:11px">)(v\d+)(</small>)',
           r"\1\2 PC版\3", s, count=1)

for word in ("serviceWorker", "manifest", "installBanner", "jspdf", "html2canvas", "./lib/"):
    if word in s:
        sys.exit(f"build-pc: 取り除き漏れがあります: {word}")

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(s, encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)} ({len(s.encode('utf-8')):,} bytes)")
