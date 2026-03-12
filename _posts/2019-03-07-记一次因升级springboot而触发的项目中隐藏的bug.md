---
layout: post
title: "记一次因升级springboot而触发的项目中隐藏的bug"
date: 2019-03-07 18:57:02 +0800
last_modified_at: "2023-01-21 01:20:34 +0800"
categories: [技术]
tags: [spring, springboot, 升级, 空格, 路径]
source: "csdn"
csdn_id: "88317102"
source_url: "https://blog.csdn.net/tongsh6/article/details/88317102"
---

这次问题出在升级后请求路径匹配规则发生了变化：

> `springboot-1.3.5` 对应 `spring-core-4.2.6.RELEASE`  
> `springboot-1.5.7` 对应 `spring-core-4.3.11.RELEASE`

## 问题描述

项目中有一个请求路径映射的末尾带了一个空格，导致从 `springboot-1.3.5` 升级到 `1.5.7` 后直接变成 `404`。

示例代码：

```java
@RequestMapping(value = "/query ", method = RequestMethod.GET)
public void query() {
    return null;
}
```

`query` 后面多了一个空格。在旧版本中项目运行正常，但升级后该路径就失效了。

## 问题分析

经过排查，最终定位到 `spring-core` 中 `AntPathMatcher` 的实现差异。

问题关键出在 `tokenizePattern` / `tokenizePath`：

```java
/**
 * Tokenize the given path pattern into parts, based on this matcher's settings.
 * <p>Performs caching based on {@link #setCachePatterns}, delegating to
 * {@link #tokenizePath(String)} for the actual tokenization algorithm.
 * @param pattern the pattern to tokenize
 * @return the tokenized pattern parts
 */
protected String[] tokenizePattern(String pattern) {
    String[] tokenized = null;
    Boolean cachePatterns = this.cachePatterns;
    if (cachePatterns == null || cachePatterns.booleanValue()) {
        tokenized = this.tokenizedPatternCache.get(pattern);
    }
    if (tokenized == null) {
        tokenized = tokenizePath(pattern);
        if (cachePatterns == null && this.tokenizedPatternCache.size() >= CACHE_TURNOFF_THRESHOLD) {
            deactivatePatternCache();
            return tokenized;
        }
        if (cachePatterns == null || cachePatterns.booleanValue()) {
            this.tokenizedPatternCache.put(pattern, tokenized);
        }
    }
    return tokenized;
}

protected String[] tokenizePath(String path) {
    return StringUtils.tokenizeToStringArray(path, this.pathSeparator, this.trimTokens, true);
}
```

`tokenizePath` 中传入了一个属性 `trimTokens`。这个属性在 `spring-core-4.2.6.RELEASE` 中默认是 `true`。  
![](/images/csdn/88317102/b963634464301d11c6874a4cfab5d300.png)

而在 `spring-core-4.3.11.RELEASE` 中默认变成了 `false`。  
![](/images/csdn/88317102/1736ae17e0d86aaae81c4eb299c4a53a.png)

这就导致 `org.springframework.util.StringUtils#tokenizeToStringArray` 在处理路径时，对空格的裁剪行为不同。  
![](/images/csdn/88317102/c184e3c7bd70edae1031751723dc57f6.png)

## 结论

这个问题本质上不是 Spring Boot 升级“随机出 bug”，而是旧代码里原本就隐藏了一个路径尾部空格的问题。旧版本因为默认裁剪空格而“侥幸可用”，升级后行为更严格，问题才被暴露出来。

[博客](http://blog.tongshuanglong.com/)
