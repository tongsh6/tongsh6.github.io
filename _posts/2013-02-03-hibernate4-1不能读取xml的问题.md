---
layout: post
title: "Hibernate4.1不能读取XML的问题"
date: 2013-02-03 23:41:05 +0800
last_modified_at: "2017-11-15 16:45:27 +0800"
categories: [技术]
tags: [Hibernate]
source: "csdn"
csdn_id: "8567713"
source_url: "https://blog.csdn.net/tongsh6/article/details/8567713"
---

[引用](http://bbs.csdn.net/topics/390309722?page=1)

在hibernate 4.1下用myeclipse 生成的xx.hbm.xml文件中的头部,在最后面多了一个空格  

```
< !DOCTYPE hibernate-mapping PUBLIC "-//Hibernate/Hibernate Mapping DTD 3.0//EN"
"http://www.hibernate.org/dtd/hibernate-mapping-3.0.dtd ">
```

把这个空格去除：  

```
< !DOCTYPE hibernate-mapping PUBLIC "-//Hibernate/Hibernate Mapping DTD 3.0//EN"
"http://www.hibernate.org/dtd/hibernate-mapping-3.0.dtd">
```

即能解决此问题
```
Caused by: org.dom4j.DocumentException:
http://www.jboss.org/dtd/hibernate/hibernate-mapping-3.0.dtd%20 Nested exception:
http://www.jboss.org/dtd/hibernate/hibernate-mapping-3.0.dtd%20 
at org.dom4j.io.SAXReader.read(SAXReader.java:484) 
at org.hibernate.internal.util.xml.MappingReader.readMappingDocument(MappingReader.java:78)

```
