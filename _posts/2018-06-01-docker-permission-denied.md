---
layout: post
title: "docker Permission denied"
date: 2018-06-01 15:15:55 +0800
last_modified_at: "2024-01-19 21:57:13 +0800"
categories: [技术]
tags: [docker]
source: "csdn"
csdn_id: "80538121"
source_url: "https://blog.csdn.net/tongsh6/article/details/80538121"
---

以主机用户访问主机的docker容器挂载目录时出现`-bash: cd: logs: Permission denied`，需要主机授予当前登陆用户权限

```
sudo chmod -R 777 /home/xxx

```

[我的博客](https://blog.tongshuanglong.com)
