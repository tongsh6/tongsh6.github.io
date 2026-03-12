---
layout: post
title: "通过ClassPathXmlApplicationContext源码解读Spring启动过程"
date: 2018-08-27 16:01:28 +0800
last_modified_at: "2022-03-23 08:57:30 +0800"
categories: [技术]
tags: []
source: "csdn"
csdn_id: "82114364"
source_url: "https://blog.csdn.net/tongsh6/article/details/82114364"
---

> 注：本次分析基于 `spring-context-5.1.0.RC1.jar`

## 类关系

![](/images/csdn/82114364/e0c7d90f3ebfe3228d0705d4b839a649.png)

## 入口函数

通过 `ClassPathXmlApplicationContext` 构造方法，最终会触发父类 `AbstractApplicationContext` 的 `refresh()` 方法。

```java
/**
 * Create a new ClassPathXmlApplicationContext, loading the definitions
 * from the given XML file and automatically refreshing the context.
 * @param configLocation resource location
 * @throws BeansException if context creation failed
 */
public ClassPathXmlApplicationContext(String configLocation) throws BeansException {
    this(new String[] {configLocation}, true, null);
}
```

```java
/**
 * Create a new ClassPathXmlApplicationContext with the given parent,
 * loading the definitions from the given XML files.
 * @param configLocations array of resource locations
 * @param refresh whether to automatically refresh the context,
 * loading all bean definitions and creating all singletons.
 * Alternatively, call refresh manually after further configuring the context.
 * @param parent the parent context
 * @throws BeansException if context creation failed
 * @see #refresh()
 */
public ClassPathXmlApplicationContext(
        String[] configLocations, boolean refresh, @Nullable ApplicationContext parent)
        throws BeansException {
    super(parent);
    setConfigLocations(configLocations);
    if (refresh) {
        refresh();
    }
}
```

```java
@Override
public void refresh() throws BeansException, IllegalStateException {
    synchronized (this.startupShutdownMonitor) {
        prepareRefresh();
        ConfigurableListableBeanFactory beanFactory = obtainFreshBeanFactory();
        prepareBeanFactory(beanFactory);

        try {
            postProcessBeanFactory(beanFactory);
            invokeBeanFactoryPostProcessors(beanFactory);
            registerBeanPostProcessors(beanFactory);
            initMessageSource();
            initApplicationEventMulticaster();
            onRefresh();
            registerListeners();
            finishBeanFactoryInitialization(beanFactory);
            finishRefresh();
        }
        catch (BeansException ex) {
            destroyBeans();
            cancelRefresh(ex);
            throw ex;
        }
        finally {
            resetCommonCaches();
        }
    }
}
```

## 解读 refresh 方法

`refresh()` 的第一行先对 `startupShutdownMonitor` 加锁，保证线程同步，然后依次执行 Spring 容器启动的一系列关键步骤。

### `prepareRefresh()`

主要有两段逻辑，涉及重要的环境类 `Environment / AbstractEnvironment`：

1. `initPropertySources()` 是一个 `protected` 的空方法，留给子类扩展。
2. `getEnvironment().validateRequiredProperties()` 用于创建并校验 Spring 环境参数组件。

> 通过 `System.getProperties()` 获取 JVM 参数，通过 `System.getenv()` 获取系统与环境变量信息；最终这些参数会放入 `AbstractEnvironment` 的 `propertySources` 中。

```java
protected void prepareRefresh() {
    this.startupDate = System.currentTimeMillis();
    this.closed.set(false);
    this.active.set(true);

    initPropertySources();
    getEnvironment().validateRequiredProperties();
    this.earlyApplicationEvents = new LinkedHashSet<>();
}
```

![](/images/csdn/82114364/a3ea56958afeff60a3efa7f7e8290f59.png)

### `obtainFreshBeanFactory()`

解析项目配置中的 `application.xml`、其他 XML 文件中的 `import`、`bean`、`resource`、`profile` 等定义，得到一个可用的 `BeanFactory`。

### `prepareBeanFactory(beanFactory)`

对 `beanFactory` 做初始化处理。

### `postProcessBeanFactory(beanFactory)`

Spring 提供的扩展点，可以通过继承 `ClassPathXmlApplicationContext` 重写该方法。

### `invokeBeanFactoryPostProcessors(beanFactory)`

执行 `BeanFactoryPostProcessor`。

### `registerBeanPostProcessors(beanFactory)`

注册 `BeanPostProcessor`。

### `initMessageSource()`

初始化消息源。

### `initApplicationEventMulticaster()`

初始化事件广播器。

### `onRefresh()`

留给具体上下文子类做扩展。

### `registerListeners()`

注册监听器。

### `finishBeanFactoryInitialization(beanFactory)`

初始化剩余的非懒加载单例 Bean。

### `finishRefresh()`

完成刷新流程并发布对应事件。

### `destroyBeans()`

异常场景下销毁已经创建的 Bean。

### `cancelRefresh(ex)`

取消刷新并重置状态。

### `resetCommonCaches()`

清理 Spring Core 的通用缓存。
