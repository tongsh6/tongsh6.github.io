---
layout: post
title: "Mysql order by  case when"
date: 2019-02-14 16:23:32 +0800
last_modified_at: "2025-01-20 22:32:52 +0800"
categories: [技术]
tags: [Mysql, "order by", "case when", 排序, 数据库]
source: "csdn"
csdn_id: "87280332"
source_url: "https://blog.csdn.net/tongsh6/article/details/87280332"
---

MySQL 的 `order by` 支持结合 `case when` 做条件排序，这在“部分数据按一种规则排、其他数据按另一种规则排”的场景里很好用。

## 需求背景

有一类数据需要按分组优先展示：

- 分组数据排在前面
- 分组内数据按操作时间正序排列
- 未分组数据按操作时间倒序排列

## SQL 实现

```sql
order by
    groupFlag desc,
    case when groupFlag > 1 then date end,
    case when groupFlag <= 1 then date end desc
```

## 思路说明

这段排序的关键点是：

1. 先按 `groupFlag desc`，让需要优先展示的分组数据排在前面
2. 对 `groupFlag > 1` 的数据，按 `date` 正序
3. 对其他数据，按 `date` 倒序

也就是说，`case when` 可以让不同条件命中的记录走不同的排序列或排序方向。

## 注意点

- `desc` / `asc` 要写在 `end` 后面
- `case when` 没命中的分支会返回 `null`，因此通常要先配合一个总排序条件把大方向排好
- 如果字段名是关键字或保留字，建议显式加反引号

## 适用场景

- 置顶 + 非置顶混排
- 分组优先展示
- 状态优先级排序
- 特殊记录按一套规则、普通记录按另一套规则
