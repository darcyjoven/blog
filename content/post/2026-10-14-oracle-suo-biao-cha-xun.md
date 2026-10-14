---
title: 'Oracle锁表查询'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'oracle-suo-biao-cha-xun'
tags: ['oracle', 'sql', '锁']
description: 'sql SELECT l.session_id, l.locked_mode, l.oracle_username, l.os_user_name, o.object_name, s.sid, s.serial , s.logon_time FROM v$locked_object l, dba_objects o, v$session s WHERE l.'
draft: false
---

```sql
SELECT
    l.session_id,
    l.locked_mode,
    l.oracle_username,
    l.os_user_name,
    o.object_name,
    s.sid,
    s.serial#,
    s.logon_time
FROM
    v$locked_object l,
    dba_objects o,
    v$session s
WHERE
    l.object_id = o.object_id
    AND l.session_id = s.sid;

ALTER SYSTEM KILL SESSION 'sid,serial#';
```
