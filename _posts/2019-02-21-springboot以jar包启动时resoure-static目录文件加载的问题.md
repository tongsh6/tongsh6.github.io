---
layout: post
title: "springboot以jar包启动时resoure/static目录文件加载的问题"
date: 2019-02-21 11:20:55 +0800
last_modified_at: "2023-08-03 14:57:31 +0800"
categories: [技术]
tags: [springboot, jar, static]
source: "csdn"
csdn_id: "87857608"
source_url: "https://blog.csdn.net/tongsh6/article/details/87857608"
---

Spring Boot 项目中，`resource/static` 目录下的文件如果需要在后台 Java 代码里读取，不能简单按 IDE 里的文件系统路径处理；更稳妥的方式是使用 Spring 提供的资源加载工具，例如 `ClassPathResource`。

## 问题重现

在 IDE 中直接启动项目时，某些写法不会报错；但打包成 Jar 后，通过 `java -jar xxx.jar` 启动，就可能出现“文件找不到”。

根因在于：

- IDE 运行时，资源文件通常以普通目录的形式存在
- Jar 启动后，资源会被打进 `BOOT-INF/classes/`，不再是可直接按磁盘路径访问的普通文件

## 问题分析

打包后的 Jar 中，资源文件路径和开发态看到的不一样。  
也就是说，下面这种思路在 IDE 中可能能跑，但放进 Jar 后就不稳定：

- 通过绝对路径 / 相对路径直接找文件
- 依赖 `File`、`getPath()` 等文件系统语义来读取 classpath 资源

这也是为什么“本地启动正常，Jar 启动报错”。

## 推荐做法

使用 Spring 的 `ClassPathResource` 来读取资源。

```java
import java.io.InputStream;

import org.springframework.core.io.ClassPathResource;

ClassPathResource resource = new ClassPathResource("static/test.txt");
try (InputStream inputStream = resource.getInputStream()) {
    // 在这里读取资源内容
}
```

这样做的好处是：

- 在 IDE 中启动可以正常读取
- 打包成 Jar 后也可以正常读取
- 不依赖物理文件路径，兼容 Spring Boot 的打包结构

## 结论

如果资源文件位于 `resources/static` 或其他 classpath 目录下，后台代码读取时优先用“类路径资源”的思路，不要把它当成普通磁盘文件处理。

[博客](http://blog.tongshuanglong.com/)
