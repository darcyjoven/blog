---
title: 'git stash 使用'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'git-stash-shi-yong'
tags: ['git', '版本控制']
description: '- git stash 是储藏的意思 Pasted image 20260518091044.png 654 本地代码落后远程一此commit，但是本地又修改了代码，不希望本地增加一次提交，可以使用git stash。 git stash 是将本地修改的内容暂时保存，当远程同步后，再将暂时保存的内容取出修改。 Pasted image 20260518091'
draft: false
---

- git stash 是储藏的意思
*\[图片：Pasted image 20260518091044.png\]*

本地代码落后远程一此commit，但是本地又修改了代码，不希望本地增加一次提交，可以使用git stash。

git stash 是将本地修改的内容暂时保存，当远程同步后，再将暂时保存的内容取出修改。

![Pasted image 20260518091114.png](/images/2b211076-00.png)

> 这时本地修改的未提交内容，已经保存下来了。

![Pasted image 20260518091131.png](/images/2b211076-01.png)

> 再次查看，本地没有修改内容，可以直接拉去远程合并到本地。

![Pasted image 20260518091144.png](/images/2b211076-02.png)

> 拉取成功

*\[图片：Pasted image 20260518091156.png\]*

> git stash pop 取出最近一次暂存代码

再次查看已经没有差异

![Pasted image 20260518091214.png](/images/2b211076-03.png)
