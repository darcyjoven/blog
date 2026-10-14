# blog

个人技术博客。**Notion 写 → 自动同步 → GitHub Pages 发布。**

**站点：https://blog.darven.top**

## 发文章

在 Notion `blog` 表里写，填「发布日期」，状态改成「待发布」，等半小时即可上线。

改已发布的文章直接改 Notion，同步会自动检测变更并覆盖发布。

**不要在 GitHub 上直接改正文**——会被下次同步覆盖。

## 技术栈

Hugo 0.167 + Stack 主题 · GitHub Pages · Notion（内容源）· Actions 定时同步 · utterances 评论

## 仓库结构

```
content/post/          文章（由同步脚本生成，不要手改）
static/images/         图片（由同步脚本下载）
scripts/               Notion 同步脚本
themes/Stack/          主题（submodule）
.github/workflows/     sync.yml 定时同步 / deploy.yml 构建部署
hugo.toml              站点配置
```

## 本地开发

```bash
hugo server    # 预览 http://localhost:1313
hugo --minify  # 构建
```

跑同步脚本需要绕过本机代理：

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
  NOTION_DATABASE_ID=<id> python3 scripts/sync.py
```

参数：`--dry-run` 只看不写，`--force` 忽略指纹全量重推。

## 依赖的 Secrets

仓库 Settings → Secrets and variables → Actions：

| Name | 说明 |
| --- | --- |
| `NOTION_API_TOKEN` | Notion 集成 token |
| `NOTION_DATABASE_ID` | blog 表的 data source id |

## 同步机制

每 30 分钟（上海 08:00-19:00，UTC 0:00-11:30）检查一次：

```
查 Notion → 比对内容指纹 → 有变更才转换 → commit → 触发 deploy → 上线 → 回填状态
```

指纹只由内容决定，不含 `lastmod`——否则回填操作会触发无限重推。

## 维护

- 定时任务 60 天无活动会被 GitHub 自动停用，需去 Actions 页面手动 Enable
- 评论存在仓库的 GitHub Issues 里，仓库删除即丢失
- 所有文章公开可读（Pages 免费版要求仓库公开）