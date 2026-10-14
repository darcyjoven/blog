#!/usr/bin/env python3
"""
Notion page 树-> mdBook 项目

读一个 Notion 根page，递归抓取子页面，按标题里的编号组织成
mdBook 的 src/ 目录 + SUMMARY.md。

核心约定：
- 编号写在页面标题里（`1` / `1.1` / `1.1.1`），脚本只读不猜
- 只有正文非空的页面才输出（不写也没关系，脚本跳过）
- 文件名 = 标题把空格换成连字符，保证全局唯一

用法：
  NOTION_API_TOKEN=xxx NOTION_ROOT_PAGE=<uuid> \\
    python3 scripts/notion_to_mdbook.py

环境变量：
  NOTION_API_TOKEN   必需，Notion 集成 token
  NOTION_ROOT_PAGE   必需，根page ID
  MDBOOK_DIR         可选，mdBook 项目目录（默认 bdl）
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notion_to_md import Converter, image_filename

API = "https://api.notion.com/v1"
VERSION = "2025-09-03"

ROOT = Path(__file__).resolve().parent.parent
MDBOOK = ROOT / (os.environ.get("MDBOOK_DIR") or "bdl")
SRC = MDBOOK / "src"
IMAGES = MDBOOK / "images"

MAX_DEPTH = 3


class Notion:
    def __init__(self, token: str):
        self.token = token
        self.calls = 0

    def req(self, method: str, path: str, data=None, retries=5):
        url = path if path.startswith("http") else f"{API}{path}"
        r = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": VERSION,
                "Content-Type": "application/json",
            },
            method=method,
            data=json.dumps(data).encode() if data else None,
        )
        for a in range(retries):
            try:
                self.calls += 1
                with urllib.request.urlopen(r, timeout=45) as resp:
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(float(e.headers.get("Retry-After", 1.5 * (a + 1))))
                    continue
                try:
                    raise RuntimeError(json.loads(e.read()).get("message"))
                except json.JSONDecodeError:
                    raise RuntimeError(f"API {e.code}")
            except (urllib.error.URLError, TimeoutError) as e:
                if a == retries - 1:
                    raise RuntimeError(f"网络错误（重试 {retries} 次）: {e}")
                time.sleep(1.5 * (a + 1))
        return None

    def blocks(self, block_id: str) -> list:
        """拉取全部块，递归展开子块。"""
        out, cursor = [], None
        while True:
            url = f"/blocks/{block_id}/children?page_size=100"
            if cursor:
                url += f"&start_cursor={cursor}"
            d = self.request("GET", url)
            if not d:
                break
            for b in d.get("results", []):
                if b.get("has_children"):
                    b["children"] = self.blocks(b["id"])
                out.append(b)
            if not d.get("has_more"):
                break
            cursor = d.get("next_cursor")
            time.sleep(0.34)
        return out

    def request(self, method, path, data=None, retries=5):
        return self.req(method, path, data, retries)

    def page_title(self, page_id: str) -> str:
        d = self.req("GET", f"/pages/{page_id}")
        if not d:
            return ""
        for p in d.get("properties", {}).values():
            if p.get("type") == "title":
                return "".join(x.get("plain_text", "") for x in p["title"])
        return ""

    def download(self, url: str) -> bytes | None:
        try:
            r = urllib.request.Request(url, headers={"User-Agent": "notion-sync/1.0"})
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.read()
        except Exception as e:
            print(f"    ⚠ 图片下载失败: {str(e)[:70]}")
            return None


# ---------------------------------------------------------------- 标题解析

NUM_RE = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")


def parse_title(title: str) -> tuple:
    """
    解析标题，返回 (编号, 标题文字, 层级)。

    `1 环境搭建`   -> ('1',    '环境搭建', 1)
    `1.1 初始环境` -> ('1.1',  '初始环境', 2)
    `BDL 开发指南` -> ('',     'BDL 开发指南', 0)  根页面无编号
    """
    t = title.strip()
    m = NUM_RE.match(t)
    if m:
        num, text = m.group(1), m.group(2).strip()
        return num, text, num.count(".") + 1
    return "", t, 0


def slugify(text: str) -> str:
    """
    标题转文件名。

    mdBook 用SUMMARY.md 的链接文字生成文件名，所以规则要和它一致：
    空格换连字符，去掉文件系统非法字符。

    分隔符 / 的处理：换成 -（而不是直接删掉），否则
    `TIPTOP/BDL 开发指南` 会变成 `TIPTOPBDL-开发指南`，读起来粘连。
    """
    s = text
    # 分隔符换成连字符，避免粘连
    s = re.sub(r"[/\\|]", "-", s)
    # 去掉文件系统非法字符
    s = re.sub(r"[:*?\"<>]", "", s)
    # 空格换连字符
    s = s.replace(" ", "-")
    # 压缩连续的连字符
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "untitled"


def has_content(blocks: list) -> bool:
    """
    判断页面是否「有正文」。

    只有 child_page（纯目录）不算内容；
    空段落、空文本列表算作无内容。
    """
    for b in blocks:
        t = b["type"]
        if t == "child_page":
            continue
        if t in ("table_of_contents", "breadcrumb", "column_list"):
            continue
        rt = b.get(t, {}).get("rich_text")
        if rt:
            txt = "".join(x.get("plain_text", "") for x in rt).strip()
            if txt:
                return True
        elif t in ("image", "code", "table", "divider", "equation"):
            return True
    return False


def collect_images(blocks: list, page_id: str) -> dict:
    """递归找出图片块，返回 {block_id: 相对路径}，并下载到 images/。"""
    result = {}

    def walk(items):
        for b in items:
            if b["type"] == "image":
                d = b.get("image", {})
                url = ""
                if d.get("type") == "external":
                    url = d.get("external", {}).get("url", "")
                elif d.get("type") == "file":
                    url = d.get("file", {}).get("url", "")
                if url:
                    fname = image_filename(page_id, len(result), url)
                    path = IMAGES / fname
                    if not path.exists():
                        IMAGES.mkdir(parents=True, exist_ok=True)
                        data = notion.download(url)
                        if data:
                            path.write_bytes(data)
                            print(f"      图片 {fname} ({len(data)//1024} KB)")
                    result[b["id"]] = f"images/{fname}"
            for c in b.get("children", []) or []:
                walk([c])

    walk(blocks)
    return result


# ---------------------------------------------------------------- 抓取树

def fetch_tree(notion: Notion, page_id: str, depth: int = 0) -> list:
    """
    递归抓取页面树。

    返回 [{num, title, level, page_id, blocks, children}]，
    只包含有正文的页面（有子页面的目录页如果自己没正文也保留）。
    """
    if depth > MAX_DEPTH:
        print(f"  ! 超过最大层级 {MAX_DEPTH}，停止")
        return []

    blocks = notion.blocks(page_id)
    children = [b for b in blocks if b["type"] == "child_page"]

    node = {
        "page_id": page_id,
        "blocks": blocks,
        "children": [],
        "title": "",
        "num": "",
        "level": depth,
    }

    for cb in children:
        cid = cb["id"]
        raw_title = cb["child_page"]["title"]
        num, text, level = parse_title(raw_title)
        sub = fetch_tree(notion, cid, depth + 1)
        # 用子页面块的原始标题（去掉子页面的编号前缀）
        if sub:
            sub[0]["title"] = text
            sub[0]["num"] = num
            sub[0]["level"] = level if level else depth + 1
            node["children"].append(sub[0])

    return [node]


# ---------------------------------------------------------------- 生成

def build_placeholder(child: dict, depth: int) -> str:
    """
    目录页/空页面的占位内容。

    mdBook 要求 SUMMARY.md 每一项都是链接，所以这类页面也要生成文件。
    内容写「本章导读 + 子章节列表」，读起来像正常的导航页。

    注意：这里的子章节链接文字**不带编号**，和 SUMMARY.md 保持一致——
    mdBook 会给导航自动加编号，重复显示会很难看。
    但链接目标文件名带编号（保证 URL 稳定）。
    """
    lines = ["*本章内容待补充。*", ""]

    kids = child.get("children") or []
    if kids:
        lines.append("本章包含以下小节：")
        lines.append("")
        for k in kids:
            fn = slugify(f"{k['num']} {k['title']}")
            lines.append(f"- [{k['title']}]({fn}.md)")
    else:
        lines.append("（暂无子章节）")

    return "\n".join(lines) + "\n"


def generate(notion: Notion, root_id: str) -> int:
    print(f"抓取根页面 {root_id} …")
    tree = fetch_tree(notion, root_id)
    if not tree:
        print("没有内容")
        return 0

    root = tree[0]
    root_title = notion.page_title(root_id) or "Guide"

    # 清空旧的 src（保留 images/）
    SRC.mkdir(parents=True, exist_ok=True)
    for f in SRC.glob("*.md"):
        f.unlink()

    # 根页面不放进列表——mdBook 会给列表里的每一项自动编号，
    # 根页面若在列表里就会占掉1.，导致子章节变成 1.1。
    # 写成 draft（列表外的独立链接）就不会被编号。
    summary = [
        "# Summary",
        "",
        f"[{root_title}]({slugify(root_title)}.md)",
        "",
    ]
    written = skipped = 0

    def walk(node, depth):
        nonlocal written, skipped
        indent = "  " * depth

        for child in node["children"]:
            filename = f"{slugify(child['num'] + ' ' + child['title'])}.md"
            content_blocks = [b for b in child["blocks"] if b["type"] != "child_page"]
            has_body = has_content(content_blocks)

            # mdBook 要求 SUMMARY.md 的每一项都是链接（不能是纯文本），
            # 所以目录页也生成一个文件，内容是本章导读 + 子章节链接。
            if has_body:
                images = collect_images(child["blocks"], child["page_id"])
                conv = Converter(child["page_id"], images)
                body = conv.convert(child["blocks"])
                body = re.sub(r"^\s*", "", body)
                kind = "内容页"
            else:
                body = build_placeholder(child, depth)
                kind = "目录页"

            heading = f"{child['num']} {child['title']}".strip()
            (SRC / filename).write_text(
                f"# {heading}\n\n{body}", encoding="utf-8"
            )
            written += 1
            print(f"  写 {filename}  ({kind}, {len(body)} 字)")

            summary.append(f"{indent}- [{child['title']}]({filename})")
            walk(child, depth + 1)

    walk(root, 1)

    # 根页面
    root_file = SRC / f"{slugify(root_title)}.md"
    root_images = collect_images(root["blocks"], root["page_id"])
    root_conv = Converter(root["page_id"], root_images)
    root_body = root_conv.convert(root["blocks"])
    root_file.write_text(f"# {root_title}\n\n{root_body}", encoding="utf-8")
    print(f"  写 {root_file.name}")

    (SRC / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"\n共写入 {written} 篇，跳过 {skipped} 篇（无正文）")
    return written


def main():
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        p = Path(os.path.expanduser("~/.config/notion/api_key"))
        if p.exists():
            token = p.read_text().strip()
    if not token:
        print("✗ 找不到 Notion token")
        return 1

    root_id = os.environ.get("NOTION_ROOT_PAGE")
    if not root_id:
        print("✗ 找不到 NOTION_ROOT_PAGE")
        return 1

    notion = Notion(token)
    generate(notion, root_id)
    print(f"\n下一步：mdbook build {MDBOOK.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())