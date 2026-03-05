# tongsh6.github.io（个人博客）

这是一个基于 **GitHub Pages + Jekyll** 的个人博客站点仓库。

## 站点结构

- `_config.yml`：站点配置（标题、主题、导航、插件等）
- `index.md`：首页（使用 `layout: home` 展示文章列表）
- `about.md`：关于页
- `_posts/`：博客文章目录（文件名必须是 `YYYY-MM-DD-xxx.md`）
- `categories.md`：分类页（自动聚合）
- `tags.md`：标签页（自动聚合）
- `new-post.ps1`：快速新建文章（支持草稿）
- `publish-post.ps1`：快速发布草稿（将 `published: false` 改为 `true` 并同步日期）
- `CI_SETUP.md`：可选，开启 GitHub Actions 构建检查

## 写一篇新文章

### 方式 A：命令一键创建（推荐，最省事）

在仓库根目录运行（PowerShell）：

```powershell
.\new-post.ps1 -Title "我的第一篇文章" -Category "技术" -Tags Jekyll,GitHubPages -Draft
```

这会在 `_posts/` 下创建一个带 `published: false` 的草稿文件（站点不会展示它）。

写完后发布：

```powershell
.\publish-post.ps1 -PostFile "YYYY-MM-DD-xxx.md"
```

发布完成后提交并推送到 `main`，GitHub Pages 会自动上线。

说明：脚本同时兼容 `"_posts\\YYYY-MM-DD-xxx.md"` 这种带目录前缀的写法。

### 方式 B：手动创建（不依赖脚本）

1. 在 `_posts/` 下创建文件，例如：`2026-03-06-my-note.md`
2. 写入类似下面的头部信息（Front Matter）：

```yaml
---
layout: post
title: "文章标题"
date: 2026-03-06 10:00:00 +0800
categories: [技术]
tags: [Jekyll, GitHub Pages]
---
```

3. 在头部下面写正文（Markdown）

## 发布流程（简单快捷）

1. 新建草稿：`.\new-post.ps1 -Draft ...`
2. 本地预览（可选）：`bundle exec jekyll serve`
3. 发布草稿：`.\publish-post.ps1 ...`
4. 提交并推送：`git add .` → `git commit -m "xxx"` → `git push`

## 需要你改的地方（建议）

打开 `_config.yml`，把这些内容替换成你的真实信息：

- `title`、`description`
- `author.name`
- `minima.social_links`（可加你的掘金/知乎/微博等链接）

## 发布

把改动推送到 GitHub 仓库的默认分支（通常是 `main`）。GitHub Pages 会自动构建并更新网站。

## 本地预览（可选）

如果你希望在本地先预览再发布，需要先安装 Ruby（建议 3.x）和 Bundler。

安装完成后，在仓库根目录执行：

```bash
bundle install
bundle exec jekyll serve
```

然后访问 `http://127.0.0.1:4000/`。

## 可选：开启 CI（构建检查）

见 `CI_SETUP.md`。
