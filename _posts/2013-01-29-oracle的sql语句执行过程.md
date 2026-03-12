---
layout: post
title: "Oracle的sql语句执行过程"
date: 2013-01-29 19:48:34 +0800
last_modified_at: "2024-07-10 11:31:50 +0800"
categories: [技术]
tags: [oracle, Oracle, ORACLE]
source: "csdn"
csdn_id: "8553858"
source_url: "https://blog.csdn.net/tongsh6/article/details/8553858"
---

--sql语句的执行过程  

1.连接方式  

2.查询语句的执行过程  

    1)语句解析  

        a)检查库缓存，有无执行过相同的sql语句  

            没有，进入b)  

            有，进入2)  

        b)检查语法：关键字  

        c)检查语义：表名，列名  

        d)获得解析锁  

        e)核对访问权限  

        f)确定执行计划（explain plan）  

        g)保存执行计划到缓存区  

    2)语句执行  

        a)检查缓存中有无数据块；  

            没有：进入b)  

            有：进入3)  

        b)查询获取目标数据文件  

    3)返回结果到客户端  

3.DML的执行过程  

    1)语句解析  

        a)检查库缓存，有无执行过相同的sql语句  

            没有，进入b)  

            有，进入2)  

        b)检查语法：关键字  

        c)检查语义：表名，列名  

        d)获得解析锁  

        e)核对访问权限  

        f)确定执行计划（explain plan）  

        g)保存执行计划到缓存区  

    2)语句执行  

        a)检查缓存区有无要修改的数据  

            没有：从数据文件装载到缓存  

        b)在要修改的数据记录上加锁。防止在事务期间其他事务修改这些数据  

        c)把旧数据放到undo segment中，新数据放在数据块对应的缓存中  

    3)返回结果到客户端，返回影响的记录数  

4.事务提交：commit  

    1)redo log buffer.    scn  

    2)LGWR启动，redo log buffer 写入到redo log files  

    3)通知客户端事务已提交  

    4)Oracle Server标示这个事务已完成  

    其他：DBWR把脏数据写入数据文件，示范数据记录上的锁  

5.事务回滚：rollback  

    1)把undo segment中的数据写回  

    2)释放undo segment中被占用的空间
