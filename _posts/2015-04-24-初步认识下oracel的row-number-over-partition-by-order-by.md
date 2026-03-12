---
layout: post
title: "初步认识下Oracel的ROW_NUMBER()Over(partition by order by )"
date: 2015-04-24 15:02:09 +0800
last_modified_at: "2026-01-13 10:58:43 +0800"
categories: [技术]
tags: []
source: "csdn"
csdn_id: "45246625"
source_url: "https://blog.csdn.net/tongsh6/article/details/45246625"
---

这篇记录两个典型用法：去重，以及分组后取组内第一条记录。

## 删除重复数据

```sql
delete from cwgs.loan_buy_extendopr
where oprno in (
    select oprno
    from (
        select
            d.oprno,
            d.y_contno,
            row_number() over (partition by y_contno order by y_contno) as row_flag
        from cwgs.loan_buy_extendopr d
    ) t
    where t.row_flag > 1
);
```

## 分组并组内排序，取第一条

```sql
select t.userno, t.corpno, t.departno
from (
    select
        r.userno,
        r.corpno,
        r.departno,
        row_number() over (partition by r.departno order by r.userno asc) as rn
    from fmsys.sys_userstation r
    where 1 = 1
) t
where t.rn = 1;
```
