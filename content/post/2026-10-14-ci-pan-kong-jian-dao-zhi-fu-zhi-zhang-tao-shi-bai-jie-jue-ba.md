---
title: '磁盘空间导致复制账套失败解决办法'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'ci-pan-kong-jian-dao-zhi-fu-zhi-zhang-tao-shi-bai-jie-jue-ba'
tags: ['tiptop', '账套', '运维']
description: 'u1 磁盘空间不足导致复制账套失败 情况适用于以下情况： 复制账套时，报错 EXP-00002: error in writing to export file 最后导出失败 如何判断是否是磁盘空间不足的 2 种方法 1.重新运行一遍 aooi931 建立 sch。 若提示修改 FGLPROFILE,直接 vi $FGLPROFILE 删除掉复制的新账套信息'
draft: false
---

## u1 磁盘空间不足导致复制账套失败

情况适用于以下情况：

复制账套时，报错

`EXP-00002: error in writing to export file`

最后导出失败

## 如何判断是否是磁盘空间不足的 2 种方法

1.重新运行一遍 aooi931 建立 sch。

若提示修改 FGLPROFILE,直接 vi $FGLPROFILE 删除掉复制的新账套信息。一般是最后几行。

再次生成 sch。

运行过程中观察磁盘空间，df -h，如果/u1 磁盘空间一直增长到 100%，即可判断是磁盘空间不足。 2.查看复制的来源账套的最近一次备份，解压之后的 dmp 文件如果大于 u1 剩余可用空间，就可判断磁盘空间不足

## 修改 createsch 脚本

createsch 默认目录

`/u1/topprod//tiptop/ora/bin/createsch`

将 exp 和 imp 语句中的文件位置修改为磁盘空间足够的目录

复制账套只用到第四条命令，可参考文件 createsch 备注为 lixwz

```bash
exp $source/$ans5@$ORACLE_SID owner=${source} file=/u2/topprod/tiptop/tmp/${source}.dmp log=$TOP/tmp/exp_${source}.log

imp system/$ans2@$ORACLE_SID fromuser=$source touser=$1 file=/u2/topprod/tiptop/tmp/${source}.dmp log=$TOP/tmp/imp_$1.log

rm -f /u2/topprod/tiptop/tmp/${source}.dmp
```

上传完文件，注意文件的权限，用 chmod 修改
