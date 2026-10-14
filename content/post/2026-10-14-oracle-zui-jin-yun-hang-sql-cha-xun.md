---
title: 'Oracle最近运行SQL查询'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'oracle-zui-jin-yun-hang-sql-cha-xun'
tags: ['oracle', 'sql', '性能']
description: '最近运行平均时间较长SQL查询 sql select from (select sa.SQL_TEXT, sa.SQL_FULLTEXT, sa.EXECUTIONS "执行次数", round(sa.ELAPSED_TIME / 1000000, 2) "总执行时间", round(sa.ELAPSED_TIME / 1000000 / sa.EXECUT'
draft: false
---

## 最近运行平均时间较长SQL查询

```sql
select *
  from (select sa.SQL_TEXT,
               sa.SQL_FULLTEXT,
               sa.EXECUTIONS "执行次数",
               round(sa.ELAPSED_TIME / 1000000, 2) "总执行时间",
               round(sa.ELAPSED_TIME / 1000000 / sa.EXECUTIONS, 2) "平均执行时间",
               sa.COMMAND_TYPE,
               sa.PARSING_USER_ID "用户ID",
               u.username "用户名",
               sa.HASH_VALUE
          from v$sqlarea sa
          left join all_users u
            on sa.PARSING_USER_ID = u.user_id
         where sa.EXECUTIONS > 0
         order by (sa.ELAPSED_TIME / sa.EXECUTIONS) desc)
 where rownum <= 50;
```

## 最近运行SQL查询

```sql
SELECT * from V$SQL WHERE sql_id IS NOT NULL;
```
