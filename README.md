# tongsh6.github.io（个人博客）

这是一个基于 **GitHub Pages + Jekyll** 的个人博客站点仓库。

## 站点结构

- `_config.yml`：站点配置（标题、主题、导航、插件等）
- `index.md`：首页（使用 `layout: home` 展示文章列表）
- `about.md`：关于页
- `_posts/`：博客文章目录（文件名必须是 `YYYY-MM-DD-xxx.md`）
- `scripts/`：辅助脚本（新增文章、发布文章、CSDN 同步）
- `data/`：同步过程中的清单与状态文件目录（运行时生成）
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
- `author`
- `minima.social_links`（可加你的掘金/知乎/微博等链接）

## 本地预览（可选）

如果你希望在本地先预览再发布，需要先安装 Ruby（建议 3.x）和 Bundler。

安装完成后，在仓库根目录执行：

```bash
bundle install
bundle exec jekyll serve
```

然后访问 `http://127.0.0.1:4000/`。

## CSDN 内容同步（跨平台）

新增了一个跨平台的 Python 脚本：

`scripts/csdn_sync.py`

适用于 Windows、macOS、Linux，只要本机有 Python 3.11+ 即可。

### 1）安装同步依赖

```bash
python -m pip install -r scripts/requirements-csdn-sync.txt
```

### 2）先抓文章清单

```bash
python scripts/csdn_sync.py discover --blog-url https://blog.csdn.net/tongsh6
```

默认会生成：

- `data/csdn-manifest.json`：文章清单

### 3）先试跑少量文章

```bash
python scripts/csdn_sync.py sync --manifest data/csdn-manifest.json --repo-root . --limit 5
```

脚本会：

- 抓取文章详情页
- 转成 Jekyll 文章写入 `_posts/`
- 为每篇文章写入 `csdn_id`、`source_url`
- 默认下载正文图片到 `assets/images/csdn/<article_id>/`
- 生成 `data/csdn-sync-state.json` 作为增量同步状态

### 4）全量执行

```bash
python scripts/csdn_sync.py run --blog-url https://blog.csdn.net/tongsh6 --repo-root .
```

### 5）常用参数

- `--limit 5`：只同步前 5 篇，便于验证
- `--no-images`：不同步图片
- `--overwrite`：忽略状态文件，强制覆盖已同步文章
- `--pause 1.0`：降低抓取频率，减少被限流概率
- `--cookie-file data/csdn-cookie.txt`：从文件读取登录态 Cookie
- `--cookie-env CSDN_COOKIE`：从环境变量读取登录态 Cookie

### 6）遇到 WAF/521 时的登录态抓取

如果公开页抓取被 CSDN WAF 拦截，可以改成带登录态执行。

方式一：环境变量

```bash
# Windows PowerShell
$env:CSDN_COOKIE='你的完整 Cookie 字符串'
python scripts/csdn_sync.py sync --manifest data/csdn-sync-failures.json --repo-root .
```

方式二：文件

```bash
python scripts/csdn_sync.py sync --manifest data/csdn-sync-failures.json --repo-root . --cookie-file data/csdn-cookie.txt
```

`data/csdn-cookie.txt` 中直接放浏览器开发者工具里复制出来的整段 `Cookie` 即可，带不带 `Cookie:` 前缀都可以。

### 7）只重跑失败文章

脚本如果遇到无法访问的详情页，会把失败项写入：

- `data/csdn-sync-failures.json`

后续可直接把这个文件当作输入再次执行：

```bash
python scripts/csdn_sync.py sync --manifest data/csdn-sync-failures.json --repo-root . --cookie-file data/csdn-cookie.txt
```

### 8）建议执行顺序

1. 先跑 `discover`
2. 再跑 `sync --limit 5`
3. 抽样检查 Markdown、代码块、图片、日期
4. 如果有 `521`，补 Cookie 后重跑 `data/csdn-sync-failures.json`
5. 确认无误后再跑全量 `run`

## CI（构建检查）

见 `CI_SETUP.md`。
