---
layout: post
title: "关于在java6中使用XFire时碰到的一个问题Could not initialize Service"
date: 2016-07-31 11:59:40 +0800
last_modified_at: "2026-01-09 16:37:49 +0800"
categories: [技术]
tags: [webservice]
source: "csdn"
csdn_id: "52077710"
source_url: "https://blog.csdn.net/tongsh6/article/details/52077710"
---

在一个采用了XFire作为WebService框架Web项目中，添加由JDK1.6 wsimport命令生成的一个WebService客户端调用，在客户端调用时出现了如下问题

```
log4j:WARN No appenders could be found for logger (org.codehaus.xfire.jaxws.Provider).
log4j:WARN Please initialize the log4j system properly.
Exception in thread "main" java.lang.IllegalStateException: Could not initialize Service.
	at org.codehaus.xfire.jaxws.ServiceDelegate.<init>(ServiceDelegate.java:77)
	at org.codehaus.xfire.jaxws.Provider.createServiceDelegate(Provider.java:32)
	at javax.xml.ws.Service.<init>(Service.java:56)
	at com.xxx.xxx..XXXService.<init>(XXXService.java:48)
	at com.xxx.xxx..main(Test.java:8)
Caused by: java.lang.NoSuchMethodException: com.xxx.xxx.getPortClassMap()
	at java.lang.Class.getMethod(Class.java:1607)
	at org.codehaus.xfire.jaxws.ServiceDelegate.<init>(ServiceDelegate.java:60)
	... 4 more
```

根据错误信息来看，是由于getPortClassMap()方法未找到，导致Could not initialize Service；但是我的客户端是用jdk自带的wsimport生成的，为什么在方法执行过程中会调用XFire相关的代码呢？

再仔细看错误提示，javax.xml.ws.Service.<init>(Service.java:56)，原来是这里出了问题，

```
    protected Service(java.net.URL wsdlDocumentLocation, QName serviceName) {
        delegate = Provider.provider().createServiceDelegate(wsdlDocumentLocation,
                serviceName,
                this.getClass());
    }
```

在这个地方调用Provider的方法，而Provider在jdk6中是一个抽象类，jdk6有该类的子类com.sun.xml.internal.ws.spi.ProviderImpl，  
 XFire也有一个该类的子类org.codehaus.xfire.jaxws.Provider，并且在xfire-all-1.2.6.jar包中/META-INF/services/javax.xml.ws.spi.Provider的文件里，

指定了由org.codehaus.xfire.jaxws.Provider去执行。

那么现在该问题解决方式就是把javax.xml.ws.spi.Provider文件中的  

```
org.codehaus.xfire.jaxws.Provider
```
改为

```
com.sun.xml.internal.ws.spi.ProviderImpl
```

就可以了。

这样java6的wsimport生成的客户端就不会再条用XFire相关的代码了。

本文章只记录了该问题的现象和解决方法。

关于本文章记录的解决方法的原理介绍可参考：

<http://blog.csdn.net/fenglibing/article/details/7083071>  

<http://blog.csdn.net/conquer0715/article/details/50728458>
