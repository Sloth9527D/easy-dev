#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将 Markdown 文件转换为自包含的 HTML 文件。

供 `/summary` 命令在用户选择 HTML 输出时调用，把已生成的 .md 总结渲染成
带内嵌样式、可直接用浏览器打开的单文件 .html。

用法：
    python md_to_html.py <输入.md> [输出.html]

约定：
- 不指定输出路径时，输出到与输入同目录、同名的 .html。
- 依赖第三方库 `markdown` 做正规渲染；若未安装则尝试用 pip 自动安装，
  安装失败时回退到一个零依赖的极简转换器（覆盖标题/段落/列表/代码块/行内代码/
  粗斜体/链接），保证命令在任何环境下都能产出可读的 HTML。
- 样式内嵌在 <style> 中，输出为单文件，无外部资源依赖。
"""

import html as html_lib
import re
import subprocess
import sys
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei",
                 Helvetica, Arial, sans-serif;
    line-height: 1.7; max-width: 820px; margin: 2.5rem auto; padding: 0 1.2rem;
    color: #24292f; background: #ffffff;
  }}
  h1, h2, h3, h4 {{ line-height: 1.3; margin-top: 1.6em; }}
  h1 {{ border-bottom: 1px solid #d0d7de; padding-bottom: .3em; }}
  h2 {{ border-bottom: 1px solid #d8dee4; padding-bottom: .25em; }}
  code {{
    background: rgba(175,184,193,.2); padding: .15em .4em; border-radius: 6px;
    font-family: "Cascadia Code", Consolas, "Courier New", monospace; font-size: .9em;
  }}
  pre {{
    background: #f6f8fa; padding: 1rem; border-radius: 8px; overflow: auto;
  }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{
    margin: 0; padding: 0 1em; color: #57606a; border-left: .25em solid #d0d7de;
  }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #d0d7de; padding: .5em .8em; }}
  th {{ background: #f6f8fa; }}
  a {{ color: #0969da; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #c9d1d9; background: #0d1117; }}
    h1, h2 {{ border-color: #30363d; }}
    pre {{ background: #161b22; }}
    th {{ background: #161b22; }}
    th, td {{ border-color: #30363d; }}
    blockquote {{ color: #8b949e; border-color: #30363d; }}
    a {{ color: #58a6ff; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def _render_with_markdown(text):
    """用第三方 markdown 库渲染；失败返回 None。"""
    try:
        import markdown  # type: ignore
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", "markdown"],
                check=True,
            )
            import markdown  # type: ignore
        except Exception:
            return None
    return markdown.markdown(
        text, extensions=["fenced_code", "tables", "toc", "sane_lists"]
    )


def _render_fallback(text):
    """零依赖的极简 Markdown 渲染，覆盖最常见语法。"""
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    list_open = False

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    def inline(s):
        s = html_lib.escape(s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        return s

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            close_list()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html_lib.escape(lines[i]))
                i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            i += 1
            continue
        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            close_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if re.match(r"\s*[-*+]\s+", line):
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append("<li>" + inline(re.sub(r"^\s*[-*+]\s+", "", line)) + "</li>")
            i += 1
            continue
        if line.strip() == "":
            close_list()
            i += 1
            continue
        close_list()
        out.append("<p>" + inline(line) + "</p>")
        i += 1

    close_list()
    return "\n".join(out)


def convert(md_path, html_path=None):
    src = Path(md_path)
    if not src.is_file():
        raise FileNotFoundError(f"找不到输入文件：{src}")
    # utf-8-sig 容错：兼容带 BOM 的 Markdown（避免 BOM 破坏首行标题匹配）
    text = src.read_text(encoding="utf-8-sig")

    body = _render_with_markdown(text)
    if body is None:
        body = _render_fallback(text)

    # 标题取第一个一级标题，否则用文件名
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else src.stem

    out = Path(html_path) if html_path else src.with_suffix(".html")
    out.write_text(
        HTML_TEMPLATE.format(title=html_lib.escape(title), body=body),
        encoding="utf-8",
    )
    return out


def main(argv):
    if len(argv) < 1:
        print("用法：python md_to_html.py <输入.md> [输出.html]", file=sys.stderr)
        return 2
    try:
        out = convert(argv[0], argv[1] if len(argv) > 1 else None)
    except Exception as exc:  # noqa: BLE001
        print(f"转换失败：{exc}", file=sys.stderr)
        return 1
    print(f"已生成 HTML：{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
