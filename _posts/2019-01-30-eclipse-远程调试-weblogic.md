---
layout: post
title: "Eclipse 远程调试  weblogic"
date: 2019-01-30 17:13:03 +0800
last_modified_at: "2019-09-30 01:04:33 +0800"
categories: [技术]
tags: [Weblogic]
source: "csdn"
csdn_id: "86706018"
source_url: "https://blog.csdn.net/tongsh6/article/details/86706018"
---

## Eclipse 远程调试 WebLogic

> 该文章记录的是weblogic10.3.6的远程调试配置

### 一、Windows 下的设置

1. 进入域目录下的 `bin` 目录，例如：`base_domain/bin`

2. 找到 `setDomainEnv.sh` 文件。

3. 用文本编辑器打开，查找关键字 `debugFlag`，会看到：

```sh
if [ "${debugFlag}" = "true" ] ; then
```

4. 在这句话上面加上：

```sh
set debugFlag=true
```

5. 重启 WebLogic 服务，就可以在启动窗口看到：

``` 
Listening for transport dt_socket at address: 8453
```

表示可以通过 `8453` 端口进行远程调试。

6. 如果要修改远程调试端口，也是在 `setDomainEnv.sh` 文件中查找 `8453`，把这个数字修改为可用端口即可。

### 二、Linux 下的设置

Linux 下的设置跟 Windows 基本一样，区别在于要把：

```
set debugFlag = true
```

改为：

```sh
debugFlag = true 
export debugFlag
```

就可以了。

至于端口修改，也和 Windows 一样。

### 三、补充说明

Linux 下要对远程调试端口开放防火墙权限。

我用的是 CentOS 7，所以执行：

```sh
firewall-cmd --permanent --zone=public --add-port=8453/tcp 
firewall-cmd --reload
```
