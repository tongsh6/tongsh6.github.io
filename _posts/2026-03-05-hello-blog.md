---
layout: post
title: "博客开张：写什么，以及怎么写"
date: 2026-03-05 12:00:00 +0800
categories: [随笔]
tags: [博客, Jekyll, GitHub Pages]
---

这是我的开站说明，也用来确认博客的文章发布流程是否正常。

你可以把下面这些内容替换成更真实的自我介绍（或者删掉重写）。

## 我是谁

- 我是：Tongsh6（你可以在这里补一句更具体的身份/经历）
- 目前在做：\[你正在做的事/方向\]
- 关注：\[工程效率/后端/前端/AI 应用/产品体验……\]

## 这个博客会写什么

- 技术：可复用的学习笔记、踩坑记录、工具/框架实践
- 项目：阶段性总结、复盘、设计取舍
- 生活：随缘更新，但希望保持真实与长期主义

## 如何快速写一篇（推荐流程）

1）新建草稿（PowerShell，在仓库根目录运行）：

```powershell
.\new-post.ps1 -Title "标题" -Category "技术" -Tags Jekyll,GitHubPages -Draft
```

2）开始写正文（打开 `_posts/` 下新生成的文件）

3）发布草稿（把 `published: false` 变成 `true`，并同步日期）：

```powershell
.\publish-post.ps1 -PostFile "YYYY-MM-DD-xxx.md"
```

4）提交并推送到 `main`，GitHub Pages 会自动构建并上线：

```powershell
git add .
git commit -m "发布：xxx"
git push
```

## 浏览方式

- 分类页：`/categories/`
- 标签页：`/tags/`
- RSS：`/feed.xml`
