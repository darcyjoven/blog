#!/usr/bin/env python3
"""
Notion -> Hugo 同步脚本

流程：
1. 查询 blog 表中状态为「待发布」或「已发布」的条目
2. 对每篇算内容指纹（sha256 of 转换后的 Markdown）
3. 指纹相同则跳过；不同则转换、下载图片、写入 content/post/
4. 回填 Notion：内容指纹、推送时间，状态改为「已发布」

用法：
  python3 scripts/sync.py              # 同步有变更的
  python3 scripts/sync.py --force      # 忽略指纹，全部重推
  python3 scripts/sync.py --dry-run    # 只打印不写入
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notion_to_md import (
    Converter,
    build_front_matter,
    fingerprint_source,
    image_filename,
    make_slug,
)

API = "https://api.notion.com/v1"
VERSION = "2025-09-03"

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "post"
IMAGES = ROOT / "static" / "images"

# 关注的字段名（Notion 里改名会直接导致报错，不静默跳过）
F_TITLE = "标题"
F_SLUG = "slug"
F_STATUS = "状态"
F_DATE = "发布日期"
F_TAGS = "标签"
F_DESC = "摘要"
F_FINGERPRINT = "内容指纹"
F_PUSHED = "推送时间"

STATUS_PENDING = "待发布"
STATUS_PUBLISHED = "已发布"


class NotionClient:
    def __init__(self, token: str):
        self.token = token
        self.calls = 0

    def request(self, method: str, path: str, data=None, retries=5):
        url = path if path.startswith("http") else f"{API}{path}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": VERSION,
                "Content-Type": "application/json",
            },
            method=method,
            data=json.dumps(data).encode() if data else None,
        )
        for attempt in range(retries):
            try:
                self.calls += 1
                with urllib.request.urlopen(req, timeout=45) as resp:
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = float(e.headers.get("Retry-After", 1.5 * (attempt + 1)))
                    time.sleep(wait)
                    continue
                try:
                    body = json.loads(e.read())
                    raise RuntimeError(f"API {e.code}: {body.get('message')}")
                except json.JSONDecodeError:
                    raise RuntimeError(f"API {e.code}")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == retries - 1:
                    raise RuntimeError(f"网络错误（已重试 {retries} 次）: {e}")
                time.sleep(1.5 * (attempt + 1))
        return None

    def blocks(self, block_id: str) -> list:
        """递归拉取全部块（含子块），返回树形结构。"""
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

    def download_image(self, url: str) -> bytes | None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "notion-sync/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception as e:
            print(f"    ⚠ 图片下载失败: {str(e)[:80]}")
            return None


def prop_text(props: dict, name: str) -> str:
    p = props.get(name)
    if not p:
        return ""
    t = p.get("type")
    if t == "title":
        return "".join(x.get("plain_text", "") for x in p["title"])
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in p["rich_text"])
    if t == "select":
        return p["select"]["name"] if p["select"] else ""
    if t == "date":
        return p["date"]["start"] if p["date"] else ""
    return ""


def prop_tags(props: dict, name: str) -> list:
    p = props.get(name) or {}
    if p.get("type") != "multi_select":
        return []
    return [o["name"] for o in p["multi_select"]]


def collect_images(blocks: list) -> list:
    """递归找出所有 image 块，返回 [{block_id, url}]。"""
    out = []
    for b in blocks:
        if b.get("type") == "image":
            d = b.get("image", {})
            url = ""
            if d.get("type") == "external":
                url = d.get("external", {}).get("url", "")
            elif d.get("type") == "file":
                url = d.get("file", {}).get("url", "")
            if url:
                out.append({"block_id": b["id"], "url": url})
        for child in b.get("children", []) or []:
            out.extend(collect_images([child]))
    return out


def render(page: dict, client: NotionClient, dry_run: bool) -> tuple:
    """把一篇 Notion 页面渲染成 (markdown, fingerprint, warnings)。"""
    props = page["properties"]
    page_id = page["id"]

    blocks = client.blocks(page_id)
    images = collect_images(blocks)

    # 先下载图片、建好路径映射，再渲染（保证渲染确定性）
    image_map = {}
    if images:
        print(f"    图片 {len(images)} 张")
        for idx, img in enumerate(images):
            filename = image_filename(page_id, idx, img["url"])
            local_path = f"/images/{filename}"
            abs_path = IMAGES / filename

            if abs_path.exists() and abs_path.stat().st_size > 0:
                image_map[img["block_id"]] = local_path
                continue

            if dry_run:
                image_map[img["block_id"]] = local_path
                continue

            data = client.download_image(img["url"])
            if data:
                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_bytes(data)
                image_map[img["block_id"]] = local_path
                print(f"      ✓ {filename} ({len(data) // 1024} KB)")
            time.sleep(0.2)

    conv = Converter(page_id, image_map)
    body = conv.convert(blocks)

    title = prop_text(props, F_TITLE)
    slug, missing = make_slug(prop_text(props, F_SLUG) or title, page_id)
    if missing:
        print(f"    ⚠ slug 映射表缺字 {''.join(sorted(missing))}，已退回 ID 后缀：{slug}")
    date = prop_text(props, F_DATE) or "2026-01-01"
    tags = prop_tags(props, F_TAGS)

    desc = prop_text(props, F_DESC).strip()
    if not desc:
        # 摘要没填就取正文开头
        plain = " ".join(l for l in body.split("\n") if l and not l.startswith(("#", "-", ">", "|", "```")))
        desc = plain[:150].strip()

    fm_props = {
        "title": title,
        "date": date,
        "tags": tags,
        "description": desc,
    }
    # 指纹只由内容决定，不含 lastmod（否则回填操作会引发无限重推）
    fp_src = fingerprint_source(fm_props, slug, body)
    fingerprint = hashlib.sha256(fp_src.encode()).hexdigest()[:16]

    # lastmod 用 Notion 的最后编辑时间，仅用于页面展示「最后更新」
    lastmod = page.get("last_edited_time", "")
    fm = build_front_matter(fm_props, slug, lastmod)
    full = fm + "\n" + body
    return full, fingerprint, conv.warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="忽略指纹，全部重推")
    ap.add_argument("--dry-run", action="store_true", help="只打印不写入")
    ap.add_argument("--status", default=None, help="只处理指定状态")
    args = ap.parse_args()

    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        p = Path(os.path.expanduser("~/.config/notion/api_key"))
        if p.exists():
            token = p.read_text().strip()
    if not token:
        print("✗ 找不到 Notion token（设 NOTION_API_TOKEN 或 ~/.config/notion/api_key）")
        return 1

    ds_id = os.environ.get("NOTION_DATABASE_ID")
    if not ds_id:
        print("✗ 找不到 NOTION_DATABASE_ID")
        return 1

    client = NotionClient(token)

    # 1. 查目标条目（待发布 + 已发布）
    print("查询 Notion 条目…")
    body = {
        "page_size": 100,
        "filter": {
            "or": [
                {"property": F_STATUS, "select": {"equals": STATUS_PENDING}},
                {"property": F_STATUS, "select": {"equals": STATUS_PUBLISHED}},
            ]
        },
    }

    pages, cursor = [], None
    while True:
        b = dict(body)
        if cursor:
            b["start_cursor"] = cursor
        d = client.request("POST", f"/data_sources/{ds_id}/query", b)
        if not d:
            break
        pages.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")
        time.sleep(0.34)

    print(f"命中 {len(pages)} 条（状态：待发布/已发布）\n")
    if not pages:
        print("没有需要处理的条目。")
        return 0

    changed, skipped, failed = [], [], []

    for page in pages:
        props = page["properties"]
        title = prop_text(props, F_TITLE) or "(无标题)"
        status = prop_text(props, F_STATUS)
        old_fp = prop_text(props, F_FINGERPRINT).strip()

        print(f"[{title}] 状态={status}")

        if not prop_text(props, F_DATE):
            print("    ⚠ 无发布日期，跳过")
            skipped.append(title)
            continue

        try:
            md, fp, warns = render(page, client, args.dry_run)
        except Exception as e:
            print(f"    ✗ 转换失败: {str(e)[:120]}")
            failed.append(title)
            continue

        for w in warns:
            print(f"    ⚠ {w}")

        if fp == old_fp and not args.force:
            print(f"    = 指纹一致，跳过（{fp}）")
            skipped.append(title)
            continue

        reason = "强制重推" if args.force else ("首次发布" if not old_fp else "内容已变更")
        print(f"    ✓ {reason}，指纹 {old_fp or '(空)'} → {fp}")

        if args.dry_run:
            print("    [dry-run] 不写入\n")
            changed.append(title)
            continue

        # 写文件
        slug, _ = make_slug(prop_text(props, F_SLUG) or title, page["id"])
        POSTS.mkdir(parents=True, exist_ok=True)
        date = prop_text(props, F_DATE)
        fname = f"{date}-{slug}.md"
        fpath = POSTS / fname

        # slug 变了就清掉同一篇文章的旧文件
        for old in POSTS.glob(f"*-{slug}.md"):
            if old != fpath:
                print(f"    清理旧文件 {old.name}")
                old.unlink()

        fpath.write_text(md, encoding="utf-8")
        print(f"    写入 {fname} ({len(md.encode())} bytes)")

        # 回填 Notion
        client.request(
            "PATCH",
            f"/pages/{page['id']}",
            {
                "properties": {
                    F_FINGERPRINT: {"rich_text": [{"text": {"content": fp}}]},
                    F_PUSHED: {"date": {"start": time.strftime("%Y-%m-%d")}},
                    F_STATUS: {"select": {"name": STATUS_PUBLISHED}},
                }
            },
        )
        print("    回填 Notion：指纹 / 推送时间 / 状态=已发布\n")
        changed.append(title)
        time.sleep(0.34)

    print("=" * 50)
    print(f"有变更 {len(changed)} | 跳过 {len(skipped)} | 失败 {len(failed)}")
    print(f"API 调用 {client.calls} 次")
    if failed:
        print(f"失败条目：{', '.join(failed)}")
    if changed and not args.dry_run:
        print("\n下一步：git add content/ static/ && git commit && git push")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
