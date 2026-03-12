---
layout: post
title: "IntelliJ IDEA 2016 自定义JDK路径"
date: 2016-08-11 17:22:42 +0800
last_modified_at: "2026-01-11 09:45:00 +0800"
categories: [技术]
tags: [idea, "intellij idea"]
source: "csdn"
csdn_id: "52184711"
source_url: "https://blog.csdn.net/tongsh6/article/details/52184711"
---

今天首次启动IntelliJ IDEA 2016时报了如下错误：   

cannot start under java 1.7 : java 1.8 or later is required

![](/images/csdn/52184711/20160811172350165.png)

原来IntelliJ IDEA 2016只支持jdk1.8或更高版本，而我本机设置的JAVA\_HOME是jdk1.6，这时有两种解决方法：   

1、下载jdk1.8，修改本机的JAVA\_HMOE为jdk1.8的路径

2、如果不愿意修改本机的JAVA\_HMOE，可以修改\IntelliJ IDEA 2016.1.2\bin\idea.bat文件中的JDK，如下，

```
set JDK=D:\DevTools\Java\64bit\jdk8

```

第一种修改方法双击idea64.exe启动即可   

第二种修改方法是双击idea.bat批处理文件启动IntelliJ IDEA
