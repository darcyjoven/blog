#!/usr/bin/env python3
"""
Notion blocks -> Markdown 转换器

把 Notion 页面的块结构转换成 Markdown，输出带 Hugo front matter 的完整文件。
转换必须是确定性的：同样的 Notion 内容，任何时候转出的 Markdown 必须完全一致
（内容指纹依赖这一点）。
"""

import re

from pinyin_map import to_pinyin

# Notion 代码块语言 -> Chroma/Hugo 语言名
LANG_MAP = {
    "plain text": "text",
    "c++": "cpp",
    "c#": "csharp",
    "f#": "fsharp",
    "java/c/c++/c#": "text",  # 未知组合，退化
    "visual basic": "vb",
    "asm": "asm",
    "bash": "bash",
    "shell": "bash",
    "docker": "dockerfile",
    "elixir": "elixir",
    "erlang": "erlang",
    "go": "go",
    "graphql": "graphql",
    "groovy": "groovy",
    "haskell": "haskell",
    "html": "html",
    "java": "java",
    "javascript": "javascript",
    "json": "json",
    "kotlin": "kotlin",
    "latex": "latex",
    "less": "less",
    "lua": "lua",
    "makefile": "makefile",
    "markdown": "markdown",
    "objective c": "objectivec",
    "ocaml": "ocaml",
    "perl": "perl",
    "php": "php",
    "powershell": "powershell",
    "prolog": "prolog",
    "python": "python",
    "r": "r",
    "ruby": "ruby",
    "rust": "rust",
    "scala": "scala",
    "scheme": "scheme",
    "scss": "scss",
    "sql": "sql",
    "swift": "swift",
    "typescript": "typescript",
    "vb.net": "vbnet",
    "xml": "xml",
    "yaml": "yaml",
    "mermaid": "text",  # Stack 不渲染 mermaid，转无高亮代码块
}


def norm_lang(lang: str) -> str:
    """Notion 语言名转 Chroma 识别名。未知语言一律退化为 text。"""
    if not lang:
        return "text"
    key = lang.strip().lower()
    if key in LANG_MAP:
        return LANG_MAP[key]
    # 未登记的语言：只保留安全的 ASCII 标识符
    safe = re.sub(r"[^a-z0-9_+#.-]", "", key)
    return safe if safe and safe.isascii() else "text"


def rich_text(items, escape=True) -> str:
    """rich_text 数组 -> Markdown 内联文本，保留加粗/斜体/删除线/行内代码/链接。"""
    if not items:
        return ""

    out = []
    for it in items:
        txt = it.get("plain_text") or ""
        if not txt:
            continue

        ann = it.get("annotations") or {}
        # 行内代码优先，其它标注不再叠加（避免 ** `x` ** 这种脏输出）
        if it.get("type") == "equation" or ann.get("code"):
            code = txt.replace("`", "'")
            out.append(f"`{code}`")
            continue

        if escape:
            txt = escape_md(txt)

        if ann.get("bold"):
            txt = f"**{txt}**"
        if ann.get("italic"):
            txt = f"*{txt}*"
        if ann.get("strikethrough"):
            txt = f"~~{txt}~~"

        href = it.get("href") or ann.get("link")
        if href:
            txt = f"[{txt}]({href})"

        out.append(txt)

    return "".join(out)


def escape_md(s: str) -> str:
    """转义会破坏 Markdown 结构的字符。代码块内容不走这里。"""
    # 先保护已存在的行内代码
    parts = re.split(r"(`[^`]+`)", s)
    res = []
    for i, p in enumerate(parts):
        if i % 2 == 1:  # 行内代码原样保留
            res.append(p)
            continue
        p = p.replace("\\", "\\\\")
        for ch in "*_[]<>":
            p = p.replace(ch, "\\" + ch)
        res.append(p)
    return "".join(res)


def make_slug(raw: str, page_id: str) -> tuple:
    """
    生成最终 slug，返回 (slug, 未收录汉字集合)。

    1. 纯 ASCII 输入：直接规范化
    2. 含中文：用内置映射表转拼音
    3. 有未收录汉字：退回「可转的部分 + 页面 ID 后 8 位」

    第 3 步的 ID 后缀是必须的——Notion 批量创建的页面 ID 前几位很接近
    （实测三篇文章的前 8 位完全相同 `3f83853f`），只用前 8 位会撞车。
    用**后** 8 位，碰撞概率可忽略。
    """
    raw = (raw or "").strip()

    def normalize(s: str) -> str:
        s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
        return re.sub(r"-{2,}", "-", s)

    # 纯 ASCII：直接用
    if raw and all(ord(c) < 128 for c in raw):
        s = normalize(raw)
        if s:
            return s[:60], set()

    # 含中文：查内置映射表
    py_str, missing = to_pinyin(raw)
    s = normalize(py_str)
    suffix = page_id.replace("-", "")[-8:]

    if s and not missing:
        return s[:60], missing

    if s:
        return f"{s[:45]}-{suffix}", missing

    # 完全转不出拼音：纯 ID，唯一性有保证
    return suffix, missing


def image_filename(page_id: str, index: int, url: str) -> str:
    """
    图片本地文件名：页面 ID **后** 8 位 + 序号。

    用后 8 位而非前 8 位——Notion 批量创建的页面 ID 前缀高度相似
    （实测三篇文章前 8 位都是 `3f83853f`），前 8 位会撞车。
    """
    ext = "png"
    m = re.search(r"\.(jpg|jpeg|png|gif|webp|svg)(?:\?|$)", url, re.I)
    if m:
        ext = m.group(1).lower()
        if ext == "jpeg":
            ext = "jpg"
    return f"{page_id.replace('-', '')[-8:]}-{index:02d}.{ext}"


class Converter:
    def __init__(self, page_id: str, image_map: dict):
        """
        image_map: {notion_block_id: "/images/xxx.png"}
        预先登记好图片路径，正文渲染时直接查表（避免渲染阶段做网络请求，
        也就保证了转换的确定性）。
        """
        self.page_id = page_id
        self.image_map = image_map
        self.warnings = []

    def convert(self, blocks: list) -> str:
        lines = []
        self.render_blocks(blocks, lines, depth=0, list_ctx=None)
        # 清理多余空行，但保留段落分隔
        out = "\n".join(lines)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip() + "\n"

    def render_blocks(self, blocks, lines, depth=0, list_ctx=None):
        i = 0
        while i < len(blocks):
            b = blocks[i]
            btype = b.get("type")

            # 连续的同类列表项合并渲染，处理有序列表编号
            if btype in ("bulleted_list_item", "numbered_list_item"):
                i = self.render_list(blocks, i, lines, depth)
                continue

            self.render_single(b, lines, depth)
            i += 1

    def render_list(self, blocks, i, lines, depth):
        """渲染连续同类列表项。有序列表的编号在段内从 1 递增。"""
        kind = blocks[i]["type"]
        indent = "  " * depth
        num = 1

        while i < len(blocks) and blocks[i]["type"] == kind:
            b = blocks[i]
            data = b.get(kind, {})
            text = rich_text(data.get("rich_text"))

            marker = f"{num}." if kind == "numbered_list_item" else "-"
            prefix = f"{indent}{marker} "
            # 多行内容对齐到 marker 之后
            body = text.replace("\n", f"\n{' ' * len(prefix)}")
            lines.append(prefix + body)

            # 子块
            if b.get("has_children"):
                lines.append("")
                self.render_blocks(b["children"], lines, depth + 1, kind)
                lines.append("")

            num += 1
            i += 1

        if lines and lines[-1] == "":
            lines.pop()
        return i

    def render_single(self, b, lines, depth):
        btype = b.get("type")
        data = b.get(btype, {})
        indent = "  " * depth

        if btype == "paragraph":
            t = rich_text(data.get("rich_text"))
            if t.strip():
                lines.append(t)
                lines.append("")

        elif btype in ("heading_1", "heading_2", "heading_3"):
            level = int(btype[-1])
            t = rich_text(data.get("rich_text"), escape=False)
            if t.strip():
                lines.append(f"{'#' * level} {t}")
                lines.append("")

        elif btype == "code":
            lang = norm_lang(data.get("language"))
            body = "".join(x.get("plain_text", "") for x in data.get("rich_text", []))
            caption = rich_text(data.get("caption"))
            lines.append(f"```{lang}")
            lines.append(body.rstrip("\n"))
            lines.append("```")
            if caption.strip():
                lines.append(f"*{caption}*")
            lines.append("")

        elif btype == "to_do":
            checked = bool(data.get("checked"))
            mark = "x" if checked else " "
            t = rich_text(data.get("rich_text"))
            prefix = f"{indent}- [{mark}] "
            body = t.replace("\n", f"\n{' ' * len(prefix)}")
            lines.append(prefix + body)
            if b.get("has_children"):
                lines.append("")
                self.render_blocks(b["children"], lines, depth + 1)
                lines.append("")
                if lines and lines[-1] == "":
                    lines.pop()

        elif btype == "quote":
            t = rich_text(data.get("rich_text"))
            if t.strip():
                for ln in t.split("\n"):
                    lines.append(f"> {ln}" if ln else ">")
                lines.append("")

        elif btype == "divider":
            lines.append("---")
            lines.append("")

        elif btype == "image":
            bid = b["id"]
            local = self.image_map.get(bid)
            caption = rich_text(data.get("caption"))
            if local:
                lines.append(f"![{caption}]({local})")
            else:
                lines.append(f"![{caption}](missing)")
                self.warnings.append(f"图片未下载: {bid}")
            lines.append("")

        elif btype == "table":
            self.render_table(b, lines)

        elif btype in ("table_row",):
            pass  # 由 render_table 处理

        else:
            t = rich_text(data.get("rich_text")) if data.get("rich_text") else ""
            if t.strip():
                lines.append(t)
                lines.append("")
            self.warnings.append(f"未处理的块类型: {btype}")

    def render_table(self, b, lines):
        rows = b.get("children", [])
        if not rows:
            return

        matrix = []
        for row in rows:
            cells = row.get("table_row", {}).get("cells", [])
            matrix.append([rich_text(c).replace("|", "\\|").replace("\n", " ") for c in cells])

        if not matrix:
            return

        width = max(len(r) for r in matrix)
        matrix = [r + [""] * (width - len(r)) for r in matrix]

        lines.append("| " + " | ".join(matrix[0]) + " |")
        lines.append("| " + " | ".join(["---"] * width) + " |")
        for r in matrix[1:]:
            lines.append("| " + " | ".join(r) + " |")
        lines.append("")


def _yaml_str(s: str) -> str:
    """
    生成安全的 YAML 标量。

    不能用双引号包裹：值里含 `"` 时，反斜杠转义会和 YAML 自己的
    转义规则打架（实测含 C 代码的 description 会报
    "value is not allowed in this context"）。
    改用单引号——YAML 单引号串里只有 `'` 需要写成 `''`，
    其余字符（含双引号、反斜杠、冒号、#）全部字面保留。
    """
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    s = s.replace("'", "''")
    return f"'{s}'"


def build_front_matter(props: dict, slug: str, lastmod: str) -> str:
    """生成 YAML front matter。字段顺序固定，保证确定性。"""
    title = props.get("title", "")
    date = props.get("date", "")
    tags = props.get("tags", [])
    desc = props.get("description", "")

    lines = ["---"]
    lines.append(f"title: {_yaml_str(title)}")
    lines.append(f"date: {date}")
    lines.append(f"lastmod: {lastmod}")
    lines.append(f"slug: {_yaml_str(slug)}")
    lines.append("tags: [" + ", ".join(_yaml_str(t) for t in tags) + "]")
    lines.append(f"description: {_yaml_str(desc)}")
    lines.append("draft: false")
    lines.append("---")
    return "\n".join(lines) + "\n"


def fingerprint_source(props: dict, slug: str, body: str) -> str:
    """
    构造参与指纹计算的字符串。

    **刻意不含 lastmod。**

    原因：脚本每次推送后回填 Notion 的「内容指纹」和「推送时间」，
    这两个写操作会更新页面的 last_edited_time。如果 lastmod 进入指纹，
    就会形成：
        回填 → last_edited_time 变 → 下次 lastmod 不同 → 指纹不同 → 又推送
    的无限循环。

    所以指纹只由「用户可控的内容」决定：标题、日期、标签、摘要、slug、正文。
    这些不变，指纹就不变。
    """
    parts = [
        "title:" + props.get("title", ""),
        "date:" + props.get("date", ""),
        "tags:" + ",".join(props.get("tags", [])),
        "desc:" + props.get("description", ""),
        "slug:" + slug,
        "---body---",
        body,
    ]
    return "\n".join(parts)
