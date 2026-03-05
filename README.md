# tongsh6.github.io（个人博客）

这是一个基于 **GitHub Pages + Jekyll** 的个人博客站点仓库。

## 站点结构

- `_config.yml`：站点配置（标题、主题、导航、插件等）
- `index.md`：首页（使用 `layout: home` 展示文章列表）
- `about.md`：关于页
- `_posts/`：博客文章目录（文件名必须是 `YYYY-MM-DD-xxx.md`）
- `categories.md`：分类页（自动聚合）
- `tags.md`：标签页（自动聚合）
- `CI_SETUP.md`：CI 说明

## Git Flow 分支模型

采用标准 Git Flow：

- `main`：线上已发布版本（GitHub Pages 从这里发布）
- `develop`：日常集成分支
- `feature/*`：新增文章/更新文章/删除文章
- `release/*`：发布准备分支（从 `develop` 合到 `main`）
- `hotfix/*`：线上紧急修复（从 `main` 开）

建议分支命名：

- 新增文章：`feature/post-2026-03-06-xxx`
- 更新文章：`feature/update-xxx`
- 删除文章：`feature/delete-xxx`

## 博客发布（新增文章）

1. 从 `develop` 开功能分支

```bash
git checkout develop
git pull origin develop
git checkout -b feature/post-2026-03-06-my-note
```

2. 在 `_posts/` 新建文章并写 Front Matter：

```yaml
---
layout: post
title: "文章标题"
date: 2026-03-06 10:00:00 +0800
categories: [技术]
tags: [Jekyll, GitHub Pages]
---
```

3. 提交并发起 PR 到 `develop`

```bash
git add .
git commit -m "feat(post): 新增 xxx"
git push -u origin feature/post-2026-03-06-my-note
```

4. 合并到 `develop` 后，按发布窗口从 `develop` 切 `release/*`，再合并到 `main`

```bash
git checkout develop
git pull origin develop
git checkout -b release/2026-03-06
git push -u origin release/2026-03-06
```

`release/*` 通过 PR 合并到 `main` 后即发布上线（GitHub Pages 自动构建）。

## 博客更新（修改文章）

1. 从 `develop` 拉分支：`feature/update-xxx`
2. 修改目标文章（例如 `_posts/2026-03-05-hello-blog.md`）
3. 提交并 PR 到 `develop`
4. 通过 `release/*` 合并到 `main`

提交示例：

```bash
git commit -m "fix(post): 更新 xxx 内容"
```

## 博客删除（下线文章）

1. 从 `develop` 拉分支：`feature/delete-xxx`
2. 删除目标文章文件
3. 提交并 PR 到 `develop`
4. 通过 `release/*` 合并到 `main`

提交示例：

```bash
git commit -m "chore(post): 删除 xxx"
```

## 需要你改的地方（建议）

打开 `_config.yml`，把这些内容替换成你的真实信息：

- `title`、`description`
- `author.name`
- `minima.social_links`（可加你的掘金/知乎/微博等链接）

## 本地预览（可选）

如果你希望在本地先预览再发布，需要先安装 Ruby（建议 3.x）和 Bundler。

安装完成后，在仓库根目录执行：

```bash
bundle install
bundle exec jekyll serve
```

然后访问 `http://127.0.0.1:4000/`。

## CI（构建检查）

见 `CI_SETUP.md`。
