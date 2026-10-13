---
title: "测试文章：Stack 主题渲染验证"
slug: "stack-render-test"
date: 2026-10-13
lastmod: 2026-10-13T16:30:00Z
tags: ["测试", "Hugo"]
categories: ["测试"]
description: "这是一篇用于验证 Stack 主题渲染效果的临时文章，覆盖代码块、表格、公式、引用、列表等常见元素。上线确认无误后可以删除。"
draft: false
keywords: ["测试", "渲染", "主题", "样式"]
---

> 这是一篇**临时测试文章**，用来验证 Stack 主题的渲染效果。
> 确认没问题后可以删掉。里面覆盖了技术文章里常见的各种元素。

## 二级标题

普通段落中文测试：静态博客的好处是首屏加载快，服务器不用渲染页面。

English mixed with 中文 for testing line breaking behavior in paragraphs.

## 代码高亮

### Python

```python
def convert(notion_blocks_to_markdown):
    """把 Notion blocks 转成 Markdown。"""
    result = []
    for block in notion_blocks:
        block_type = block["type"]
        result.append(render(block_type, block[block_type]))
    return "\n\n".join(result)


class SyncError(Exception):
    """转换失败时抛出。"""

    def __init__(self, page_id: str, reason: str):
        self.page_id = page_id
        super().__init__(f"页面 {page_id} 转换失败：{reason}")
```

### Shell

```bash
# 拉取最新内容并构建
git pull --rebase
hugo --minify --gc
npx pagefind --site public
```

### Go

```go
package main

import "fmt"

type Post struct {
	Title string
	Date  string
}

func main() {
	posts := []Post{{Title: "第一篇", Date: "2026-10-13"}}
	for _, p := range posts {
		fmt.Printf("%s\t%s\n", p.Date, p.Title)
	}
}
```

### YAML（front matter 也会高亮）

```yaml
title: "文章标题"
date: 2026-10-13
tags: ["hugo", "静态博客"]
description: "一句话摘要"
```

## 表格

| 字段 | 类型 | 用途 | 必填 |
| --- | --- | --- | --- |
| 标题 | Title | 文章名，也是 slug 来源 | 是 |
| slug | Text | Hugo URL 路径 | 是 |
| 状态 | Select | 想法 / 草稿 / 待发布 / 已发布 | 是 |
| 摘要 | Text | SEO description | 否 |
| 关键词 | Multi-select | 补偿中文搜索无词根匹配 | 否 |

## 列表

### 无序列表

- 第一项
- 第二项
  - 嵌套的第二层
  - 嵌套的第二层第二项
- 第三项

### 有序列表

1. 打开 Notion
2. 修改文章内容
3. 把状态改成「待发布」
4. 等待 Actions 轮询（10~30 分钟）

### 混合嵌套

1. 在 Notion 写完
   - 标题、正文、代码块
   - 图片、表格
2. 改状态为待发布
   - 记得先填发布日期
3. 等待同步

## 引用

> 「单向同步：Notion → Hugo。Hugo 端的手改会在下次推送时被覆盖。」
>
> —— 同步流程设计

## 行内元素

**加粗**、*斜体*、~~删除线~~、`行内代码`、[链接](https://gohugo.io/)。

## 分隔线

上面一行下面应该有条分隔线：

---

## 数学公式

行内公式：当 $a^2 + b^2 = c^2$ 时，这是勾股定理。

块级公式：

$$
\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
$$

## 很长的一个标题用来测试目录层级和换行行为在最窄宽度下的表现

### 三级标题

#### 四级标题

##### 五级标题（Stack 的 TOC 默认到 4 级）

## 中文混排的边界情况

**测试一**：中英文之间加空格 `Notion 到 Markdown 的转换`，读起来应该更顺。

**测试二**：数字与单位 `2026年10月13日`、`30 分钟`、`10 GB`。

**测试三**：标点混排——问号？感叹号！引号“”、括号（）。

**测试四**：超链接混排：参考 [Notion API 文档](https://developers.notion.com/docs) 和 [Hugo 文档](https://gohugo.io/docs/)。

## 图片

### 站内路径引用（同步脚本下载 Notion 图片后的效果）

Notion 同步时把图片下载到 `static/images/`，构建后就在 `/images/` 下，用站内路径引用：

![站内图片](/images/test-placeholder.png)

### 资源路径引用（主题头像走的是这条路）

Stack 的头像放在 `assets/img/`，构建时输出到 `/img/`：

![资源图片](/img/avatar.png)

> **注意两者的区别**：`assets/` 会被 Hugo 处理（可做图片优化），输出到 `/img/`；`static/` 原样拷贝，输出到 `/`。文章插图应该放 `static/`。

## 结论

如果上面这些元素都渲染正常，说明：

- [x] Stack 主题工作正常
- [x] 中文分词（CJK）正常
- [x] 代码高亮正常
- [x] Pagefind 能索引中文
- [x] YAML front matter 解析正常

确认无误后可以删掉这篇文章，然后进入 Notion 同步链路的开发。
