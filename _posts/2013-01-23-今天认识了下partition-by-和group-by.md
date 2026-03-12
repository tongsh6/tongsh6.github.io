---
layout: post
title: "今天认识了下partition by 和group by"
date: 2013-01-23 19:18:27 +0800
last_modified_at: "2024-12-27 10:57:39 +0800"
categories: [技术]
tags: [oracle, Oracle, ORACLE, Partition, PARTITION, partition]
source: "csdn"
csdn_id: "8535415"
source_url: "https://blog.csdn.net/tongsh6/article/details/8535415"
---

今天学习Oracle  sql语句时碰到了这样的题目：

**查询各科成绩前三名的记录:(不考虑成绩并列情况)**

略看题目，以为能弄出来，下手写时才发现不是那样的

经过一番查阅后，才知道，还有partition by这个分区函数，这个函数貌似和group by 差不多，但仔细分析，partition却能做到group by不能做到的功能，比如说这题：

答案这样的：select \* from  (select sno,cno,score ,row\_number() over (partition by cno order by score desc)rn from sc) where  rn<4;

原来，partition 能按照指定的列把查询结果集给分成不同的区

暂时只理解到这里，以后在重新理理吧！
