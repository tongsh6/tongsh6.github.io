---
layout: post
title: "java 命令行启动指定classpath"
date: 2018-05-10 15:32:14 +0800
last_modified_at: "2025-06-12 15:11:14 +0800"
categories: [技术]
tags: [Java, Classpath]
source: "csdn"
csdn_id: "80268642"
source_url: "https://blog.csdn.net/tongsh6/article/details/80268642"
---

```
java -classpath ".;./lib/*" xxx.xxx.xxx.MainClass

```

“.;./lib/\*”  
 window环境以分号“;” 做分割  
 Linux以冒号“：”做分割  
 “.” 指当前目录

该命令适用于，jar包中的MANIFEST.MF未指定MainClass

[我的博客](https://blog.tongshuanglong.com)
