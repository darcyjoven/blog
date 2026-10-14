---
title: 'Oracle表空间查询与增加'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'oracle-biao-kong-jian-cha-xun-yu-zeng-jia'
tags: ['oracle', 'sql', '表空间']
description: '表空间查询 system/sys 登录sqlplus后运行 @q_tbsFREE sql select from ( select t.tablespace_name,t.owner, t.segment_name, t.segment_type, sum(t.bytes / 1024 / 1024) mb from dba_segments t where'
draft: false
---

## 表空间查询

system/sys 登录sqlplus后运行`@q_tbsFREE`

```sql
select * from (
  select t.tablespace_name,t.owner, t.segment_name, t.segment_type, sum(t.bytes / 1024 / 1024) mb
  from dba_segments t
  where t.segment_type='TABLE'
	AND tablespace_name ='TEMPTABS'
  group by t.tablespace_name,t.OWNER, t.segment_name, t.segment_type
) t
order by t.mb desc;
```

## 查询表空间文件

查询命令`@q_datafile`

```sql
select t.tablespace_name,
       d.file_name,
       d.bytes / 1024 / 1024 as size_mb,
       d.autoextensible,
       d.maxbytes / 1024 / 1024 as max_size_mb
  from dba_tablespaces t
  join dba_data_files d
    on t.tablespace_name = d.tablespace_name
 order by t.tablespace_name, d.file_name;
```

## 增加表空间

`alter tablespace xx add datafile 'xxx.dbf' size 4G;`

## 默认账户密码

- TOPGP
`system/manager`

- T100
`system/tiptop100`
