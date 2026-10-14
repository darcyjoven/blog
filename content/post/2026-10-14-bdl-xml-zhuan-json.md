---
title: 'BDL XML转JSON'
date: 2026-10-14
lastmod: 2026-10-14T02:12:00.000Z
slug: 'bdl-xml-zhuan-json'
tags: ['bdl', 'json', 'tiptop', 'xml']
description: '通过 base.typeinfo.create(object) 将任意数据转为 JSON。 pascal type demo record str string, dat date, bool boolean, varc varchar(100), inter interval DAY(5) TO MINUTE, datime datetime year t'
draft: false
---

通过`base.typeinfo.create(object)`将任意数据转为 JSON。

```pascal
    type demo record
        str string,
        dat date,
        bool boolean,
        varc   varchar(100),
        inter  interval DAY(5) TO MINUTE,
        datime datetime year to second,
        dec decimal(20,6),
        byt byte,
        txt text
    end record
    type lis dynamic array of demo
    define all record
        all1    string,
        all2    demo,
        all3    lis,
        all4    dynamic array with dimension 2 of demo,
        all5    record
            a   string,
            b   integer,
            c   demo,
            d   lis
        end record,
        all6    dynamic array of    string
    end record
    define list lis
    define node  om.DomNode
    define cnt  integer
```

# Record

```xml
<?xml version='1.0' encoding='UTF-8'?>
<Record>
  <Field type="STRING" value="all1" name="all1"/>
  <Record name="all2">
    <Field type="STRING" value="all2.str" name="str"/>
    <Field type="DATE" value="06/01/02" name="dat"/>
    <Field type="BOOLEAN" value="0" name="bool"/>
    <Field type="VARCHAR(100)" value="all2.varc" name="varc"/>
    <Field type="INTERVAL DAY(5) TO MINUTE" value=" 23423 12:34" name="inter"/>
    <Field type="DATETIME YEAR TO SECOND" value="2026-06-26 14:14:17" name="datime"/>
    <Field type="DECIMAL(20,6)" value="20.123450" name="dec"/>
    <Field name="byt"/>
    <Field name="txt"/>
  </Record>
  <Array length="2" name="all3">
    <Record>
      <Field type="STRING" name="str"/>
      <Field type="DATE" name="dat"/>
      <Field type="BOOLEAN" name="bool"/>
      <Field type="VARCHAR(100)" name="varc"/>
      <Field type="INTERVAL DAY(5) TO MINUTE" name="inter"/>
      <Field type="DATETIME YEAR TO SECOND" name="datime"/>
      <Field type="DECIMAL(20,6)" name="dec"/>
      <Field name="byt"/>
      <Field name="txt"/>
    </Record>
    <Record>
      <Field type="STRING" value="all3[2].str" name="str"/>
      <Field type="DATE" value="06/01/02" name="dat"/>
      <Field type="BOOLEAN" value="0" name="bool"/>
      <Field type="VARCHAR(100)" value="all3[2].varc" name="varc"/>
      <Field type="INTERVAL DAY(5) TO MINUTE" value=" 23423 12:34" name="inter"/>
      <Field type="DATETIME YEAR TO SECOND" value="2026-06-26 14:14:17" name="datime"/>
      <Field type="DECIMAL(20,6)" value="20.123450" name="dec"/>
      <Field name="byt"/>
      <Field name="txt"/>
    </Record>
  </Array>
  <Array length="1" name="all4">
    <Array length="2">
      <Record>
        <Field type="STRING" name="str"/>
        <Field type="DATE" name="dat"/>
        <Field type="BOOLEAN" name="bool"/>
        <Field type="VARCHAR(100)" name="varc"/>
        <Field type="INTERVAL DAY(5) TO MINUTE" name="inter"/>
        <Field type="DATETIME YEAR TO SECOND" name="datime"/>
        <Field type="DECIMAL(20,6)" name="dec"/>
        <Field name="byt"/>
        <Field name="txt"/>
      </Record>
      <Record>
        <Field type="STRING" value="all4[1,2].str" name="str"/>
        <Field type="DATE" value="06/01/02" name="dat"/>
        <Field type="BOOLEAN" value="0" name="bool"/>
        <Field type="VARCHAR(100)" value="all4[1,2].varc" name="varc"/>
        <Field type="INTERVAL DAY(5) TO MINUTE" value=" 23423 12:34" name="inter"/>
        <Field type="DATETIME YEAR TO SECOND" value="2026-06-26 14:14:17" name="datime"/>
        <Field type="DECIMAL(20,6)" value="20.123450" name="dec"/>
        <Field name="byt"/>
        <Field name="txt"/>
      </Record>
    </Array>
  </Array>
  <Record name="all5">
    <Field type="STRING" name="a"/>
    <Field type="INTEGER" value="2" name="b"/>
    <Record name="c">
      <Field type="STRING" value="all5.c.str" name="str"/>
      <Field type="DATE" value="06/01/02" name="dat"/>
      <Field type="BOOLEAN" value="0" name="bool"/>
      <Field type="VARCHAR(100)" value="all5.c.varc" name="varc"/>
      <Field type="INTERVAL DAY(5) TO MINUTE" value=" 23423 12:34" name="inter"/>
      <Field type="DATETIME YEAR TO SECOND" value="2026-06-26 14:14:17" name="datime"/>
      <Field type="DECIMAL(20,6)" value="20.123450" name="dec"/>
      <Field name="byt"/>
      <Field name="txt"/>
    </Record>
    <Array length="2" name="d">
      <Record>
        <Field type="STRING" name="str"/>
        <Field type="DATE" name="dat"/>
        <Field type="BOOLEAN" name="bool"/>
        <Field type="VARCHAR(100)" name="varc"/>
        <Field type="INTERVAL DAY(5) TO MINUTE" name="inter"/>
        <Field type="DATETIME YEAR TO SECOND" name="datime"/>
        <Field type="DECIMAL(20,6)" name="dec"/>
        <Field name="byt"/>
        <Field name="txt"/>
      </Record>
      <Record>
        <Field type="STRING" value="all5.d[2].str" name="str"/>
        <Field type="DATE" value="06/01/02" name="dat"/>
        <Field type="BOOLEAN" value="0" name="bool"/>
        <Field type="VARCHAR(100)" value="all5.d[2].varc" name="varc"/>
        <Field type="INTERVAL DAY(5) TO MINUTE" value=" 23423 12:34" name="inter"/>
        <Field type="DATETIME YEAR TO SECOND" value="2026-06-26 14:14:17" name="datime"/>
        <Field type="DECIMAL(20,6)" value="20.123450" name="dec"/>
        <Field name="byt"/>
        <Field name="txt"/>
      </Record>
    </Array>
  </Record>
  <Array length="2" name="all6">
    <Field type="STRING"/>
    <Field type="STRING" value="string"/>
  </Array>
</Record>
```

# Array

```xml
<?xml version='1.0' encoding='UTF-8'?>
<Array length="2">
  <Record>
    <Field type="STRING" name="str"/>
    <Field type="DATE" name="dat"/>
    <Field type="BOOLEAN" name="bool"/>
    <Field type="VARCHAR(100)" name="varc"/>
    <Field type="INTERVAL DAY(5) TO MINUTE" name="inter"/>
    <Field type="DATETIME YEAR TO SECOND" name="datime"/>
    <Field type="DECIMAL(20,6)" name="dec"/>
    <Field name="byt"/>
    <Field name="txt"/>
  </Record>
  <Record>
    <Field type="STRING" value="list[2].str" name="str"/>
    <Field type="DATE" value="06/01/02" name="dat"/>
    <Field type="BOOLEAN" value="0" name="bool"/>
    <Field type="VARCHAR(100)" value="list[2].varc" name="varc"/>
    <Field type="INTERVAL DAY(5) TO MINUTE" value=" 23423 12:34" name="inter"/>
    <Field type="DATETIME YEAR TO SECOND" value="2026-06-26 10:28:16" name="datime"/>
    <Field type="DECIMAL(20,6)" value="20.123450" name="dec"/>
    <Field name="byt"/>
    <Field name="txt"/>
  </Record>
</Array>
```

# Filed

```xml
<?xml version='1.0' encoding='UTF-8'?>
<Field type="INTEGER" value="0"/>
```
