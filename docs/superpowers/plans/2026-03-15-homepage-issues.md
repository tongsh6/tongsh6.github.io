# Homepage Issues Fix Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复首页分析中发现的功能缺陷、样式问题、可访问性不足和构建配置遗漏。

**Architecture:** 站点基于 Jekyll + Minima，通过覆盖 `_layouts/`、`_includes/` 和 `assets/main.scss` 实现定制。本计划只修改现有文件，不引入新的运行时依赖，不做大规模样式体系重构。

**Tech Stack:** Jekyll, Minima theme, SCSS, Liquid, JavaScript (vanilla), Simple Jekyll Search

**Execution Rules:**
- 首次执行构建前，先确认本机可用 `Bundler 4.0.3`（见 `Gemfile.lock` 的 `BUNDLED WITH`）。若缺失该版本，应先安装或明确记录为环境阻塞，不要把环境问题误判为代码问题。
- 每个任务完成后都执行一次 `bundle exec jekyll build`，确保退出码为 0。
- 除非任务明确要求，否则不要顺手做视觉重构或结构性重写。
- 修改 SCSS 时同时考虑深色（默认）和浅色模式。

---

## Chunk 1：首页功能 Bug

### Task 1：修复置顶文章在所有分页页重复显示

**问题：** `_layouts/home.html` 第 31 行使用 `site.posts` 遍历置顶文章，导致置顶文章在分页的每一页（第 2、3、4… 页）都重复显示。注释（第 47 行）说的是"excluding pinned to avoid duplication on page 1"，但实际上只有普通文章做了去重，置顶区域本身没有分页限制。

**Files:**
- Modify: `_layouts/home.html`

- [ ] **Step 1: 将置顶区域限制为仅在第一页显示**

在 `_layouts/home.html` 第 30-45 行的置顶区域外围加上分页页码判断：

```liquid
<!-- Pinned Posts First (only on page 1) -->
{%- if site.paginate == nil or paginator.page == 1 -%}
  {%- for post in site.posts -%}
    {%- if post.pinned -%}
      <li class="pinned-post">
        ...保持原有内容不变...
      </li>
    {%- endif -%}
  {%- endfor -%}
{%- endif -%}
```

说明：
- `site.paginate == nil` 是为了兼容未启用分页的情况（此时 `paginator` 对象不存在）。
- 当前配置 `paginate: 10` 已启用，所以运行时走 `paginator.page == 1` 分支。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: 手工验证**

检查项：
- 首页（`/`）可以看到置顶文章。
- 第二页（`/page2/`）不再显示置顶文章。
- 普通文章列表中不包含被置顶的文章（去重逻辑不受影响）。

- [ ] **Step 4: Commit**

```bash
git add _layouts/home.html
git commit -m "fix(home): only show pinned posts on first page"
```

---

### Task 2：搜索输入框缺少 `<label>` 关联（若执行 Task 9，本任务可跳过）

**问题：** `_layouts/home.html` 第 14 行和 `404.md` 第 17 行的搜索输入框 `<input id="search-input">` 只有 `placeholder` 属性，没有关联的 `<label>` 元素。屏幕阅读器无法正确识别搜索框用途。

**Files:**
- Modify: `_layouts/home.html`
- Modify: `404.md`

- [ ] **Step 1: 为首页搜索框添加视觉隐藏的 label**

在 `_layouts/home.html` 的搜索容器中，`<input>` 之前添加：

```html
<label for="search-input" class="sr-only">搜索文章</label>
```

- [ ] **Step 2: 为 404 页搜索框添加同样的 label**

在 `404.md` 的搜索容器中，`<input>` 之前添加同样的 `<label>`。

- [ ] **Step 3: 在 main.scss 中添加 sr-only 工具类**

在 `assets/main.scss` 末尾添加：

```scss
// Screen reader only utility
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

- [ ] **Step 4: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 5: Commit**

```bash
git add _layouts/home.html 404.md assets/main.scss
git commit -m "fix(a11y): add label for search input"
```

---

## Chunk 2：样式与安全

### Task 3：浅色模式代码高亮 token 颜色未适配

**问题：** `_sass/_syntax-dark.scss` 定义的 Monokai token 颜色（如 `.k { color: #66d9ef }`、`.o { color: #f92672 }`、`.s { color: #e6db74 }`）针对深色背景 `#111111` 设计。浅色模式下 `assets/main.scss` 第 611-616 行将 `pre, code` 的背景改为 `#F4F4F5`、文字改为 `#27272A`，但所有语法 token 颜色仍为深色主题的亮色值。部分 token（如 `#e6db74` 黄色、`#f8f8f2` 白色）在浅色背景上对比度不达标。

**Files:**
- Modify: `assets/main.scss`

- [ ] **Step 1: 在浅色模式区域添加 syntax token 颜色覆盖**

在 `assets/main.scss` 约第 645 行（浅色模式区域末尾）之后添加浅色语法高亮覆盖。选用 GitHub Light 风格配色方案：

```scss
// Light mode syntax highlighting (GitHub Light inspired)
html[data-theme="light"] .highlight {
  color: #24292e;
  background-color: #F4F4F5;

  .c, .cm, .cp, .c1, .cs { color: #6a737d; }  /* Comments */
  .err { color: #cb2431; }                      /* Error */
  .k, .kc, .kd, .kp, .kr, .kt { color: #d73a49; } /* Keywords */
  .l, .m, .mf, .mh, .mi, .mo, .il { color: #005cc5; } /* Literals/Numbers */
  .n, .nb, .ni, .ne, .nl, .nn, .py, .bp, .vc, .vg, .vi { color: #24292e; } /* Names */
  .o, .ow { color: #d73a49; }                   /* Operators */
  .p { color: #24292e; }                         /* Punctuation */
  .s, .sb, .sc, .sd, .s2, .sh, .si, .sx, .sr, .s1, .ss { color: #032f62; } /* Strings */
  .se { color: #005cc5; }                        /* String.Escape */
  .ld { color: #032f62; }                        /* Literal.Date */
  .na { color: #6f42c1; }                        /* Name.Attribute */
  .nc, .nd, .ne, .nf, .nx { color: #6f42c1; }   /* Name.Class/Decorator/Function */
  .no { color: #005cc5; }                        /* Name.Constant */
  .nt { color: #22863a; }                        /* Name.Tag */
  .nv { color: #e36209; }                        /* Name.Variable */
  .ge { font-style: italic; }
  .gs { font-weight: bold; }
  .w { color: #24292e; }                         /* Whitespace */
}
```

说明：
- 使用 GitHub Light 配色方案，所有颜色在 `#F4F4F5` 背景上满足 WCAG AA 对比度要求（4.5:1+）。
- `.highlight` 选择器与 `_syntax-dark.scss` 中的结构一致，浅色模式下覆盖。
- `.ne`（Name.Exception）同时出现在两条规则中，两条规则优先级相同时后者生效（`#6f42c1`），视觉上均可接受。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: 手工验证**

选一篇包含代码块的文章：
- 切换到浅色模式，检查代码块中关键字、字符串、注释等颜色是否清晰可读。
- 切换回深色模式，确认未受影响。

- [ ] **Step 4: Commit**

```bash
git add assets/main.scss
git commit -m "fix(style): add light mode syntax highlighting colors"
```

---

### Task 4：medium-zoom CDN 缺少 SRI integrity

**问题：** `_includes/post_scripts.html` 第 2 行引用 medium-zoom CDN 没有 `integrity` 和 `crossorigin` 属性，而同文件中的其他 CDN 资源（simple-jekyll-search、tocbot）都有 SRI。安全一致性缺失。

**Files:**
- Modify: `_includes/post_scripts.html`

- [ ] **Step 1: 获取 medium-zoom@1.0.8 的 SRI hash**

访问 [SRI Hash Generator](https://www.srihash.org/) 或使用以下命令获取：

```bash
curl -s https://cdn.jsdelivr.net/npm/medium-zoom@1.0.8/dist/medium-zoom.min.js | openssl dgst -sha256 -binary | openssl base64 -A
```

- [ ] **Step 2: 为 medium-zoom script 标签添加 integrity 和 crossorigin**

将 `_includes/post_scripts.html` 第 2 行从：

```html
<script src="https://cdn.jsdelivr.net/npm/medium-zoom@1.0.8/dist/medium-zoom.min.js"></script>
```

改为：

```html
<script src="https://cdn.jsdelivr.net/npm/medium-zoom@1.0.8/dist/medium-zoom.min.js"
        integrity="sha256-<Step 1 获取的 hash>"
        crossorigin="anonymous"></script>
```

- [ ] **Step 3: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 4: 本地验证图片放大功能仍然正常**

打开一篇带图片的文章，点击图片确认 medium-zoom 灯箱效果正常。

- [ ] **Step 5: Commit**

```bash
git add _includes/post_scripts.html
git commit -m "fix(security): add SRI integrity for medium-zoom CDN"
```

---

## Chunk 3：构建配置

### Task 5：完善 `_config.yml` 的 exclude 列表

**问题：** `_config.yml` 的 `exclude` 列表（第 16-20 行）仅排除了 `README.md`、`Gemfile`、`Gemfile.lock`、`vendor`。以下运维文件/目录没有被排除，可能被 Jekyll 编译进 `_site/`，暴露在线上：

| 文件/目录 | 风险 |
|-----------|------|
| `scripts/` | 包含 CSDN 同步脚本（含 Cookie 认证逻辑）和 requirements.txt |
| `new-post.ps1` | PowerShell 脚本 |
| `publish-post.ps1` | PowerShell 脚本 |
| `CI_SETUP.md` | CI 配置文档 |
| `POST_TEMPLATE.md` | 文章模板文档 |
| `docs/` | 计划文件等内部文档 |

**Files:**
- Modify: `_config.yml`

- [ ] **Step 1: 扩充 exclude 列表**

将 `_config.yml` 的 exclude 部分改为：

```yaml
exclude:
  - README.md
  - Gemfile
  - Gemfile.lock
  - vendor
  - scripts/
  - docs/
  - new-post.ps1
  - publish-post.ps1
  - CI_SETUP.md
  - POST_TEMPLATE.md
  - "*.ps1"
```

说明：
- `"*.ps1"` glob 可以覆盖未来新增的 PowerShell 脚本。
- `scripts/` 包含 `csdn_sync.py` 和 `requirements-csdn-sync.txt`，不应出现在线上。
- `docs/` 包含内部计划文件。

- [ ] **Step 2: 验证构建并确认排除生效**

```bash
bundle exec jekyll build
# 确认这些文件不在 _site 中
ls _site/scripts/ 2>/dev/null && echo "FAIL: scripts/ leaked" || echo "OK: scripts/ excluded"
ls _site/docs/ 2>/dev/null && echo "FAIL: docs/ leaked" || echo "OK: docs/ excluded"
ls _site/new-post.ps1 2>/dev/null && echo "FAIL: ps1 leaked" || echo "OK: ps1 excluded"
ls _site/CI_SETUP.md 2>/dev/null && echo "FAIL: CI_SETUP leaked" || echo "OK: CI_SETUP excluded"
```

预期：所有检查项输出 "OK"。

- [ ] **Step 3: Commit**

```bash
git add _config.yml
git commit -m "fix(config): exclude scripts and maintenance files from site build"
```

---

### Task 6：permalink 中 `:categories` 导致的 URL 问题

**问题：** `_config.yml` 第 49 行设置 `permalink: /:categories/:year/:month/:day/:title/`。当文章 `categories` 包含中文时（如 `项目`），生成的 URL 含 UTF-8 编码字符（`/%E9%A1%B9%E7%9B%AE/2026/03/12/...`），不利于 SEO 和可读性。此外，如果后续修改或移除某篇文章的 categories，其 URL 会变化，所有外部链接失效。

**Strategy:** 这是一个影响已发布 URL 的配置变更，需要谨慎处理。不直接修改 permalink 格式（否则所有已有文章 URL 都会变），而是：
1. 为未来文章建立英文 categories 规范。
2. 评估是否需要为已有文章添加 redirect。

**Files:**
- Modify: `_config.yml`（添加注释说明）

- [ ] **Step 1: 在 permalink 配置处添加注释警告**

在 `_config.yml` 第 48-49 行之间添加注释：

```yaml
# WARNING: permalink contains :categories — changing a post's categories will break its URL.
# If categories contain CJK characters, the URL will contain percent-encoded bytes.
# Consider switching to /:year/:month/:day/:title/ in a future migration with proper redirects.
permalink: /:categories/:year/:month/:day/:title/
```

- [ ] **Step 2: Commit**

```bash
git add _config.yml
git commit -m "docs(config): add permalink migration warning"
```

> **后续建议：** 如需迁移 permalink 格式，应：
> 1. 使用 `jekyll-redirect-from` 插件为每篇旧文章生成 301 redirect。
> 2. 在 front matter 中为每篇文章添加 `redirect_from` 指向旧 URL。
> 3. 更新 sitemap 后通知搜索引擎 recrawl。

---

## Chunk 4：首页内容与 UX

### Task 7：首页欢迎语导航冗余（合并原 Task 7 + Task 12）

**问题：**
1. `index.html` 第 17 行 `[CoStruct](...)` 引用了已移出顶栏导航的项目页，导航逻辑不一致（commit `ecdad4c` 已将其移至关于页）。
2. 欢迎语列表中的"关于我"、"分类"、"标签"与顶栏导航（`_config.yml` header_pages）完全重复，增加视觉噪音。

**目标：** 一次性输出最终简洁版本，仅保留顶栏没有的独特入口（RSS 订阅）。

**Files:**
- Modify: `index.html`

- [ ] **Step 1: 精简首页欢迎语，移除所有冗余导航链接**

在 `index.md`（重命名后，见 Task 12）中，将第 14-19 行替换为：

```markdown
欢迎来到我的博客！这里记录技术思考与项目实践。
可通过顶部导航浏览分类与标签，或订阅 [RSS]({{ "/feed.xml" | relative_url }}) 获取更新。
```

说明：
- 顶栏已覆盖"关于我"、"分类"、"标签"，无需重复。
- CoStruct 可通过关于页访问，无需首页入口。
- RSS 订阅为唯一有价值的独特入口，保留。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: Commit**

```bash
git add index.md
git commit -m "fix(home): simplify welcome text, remove redundant nav links"
```

**执行顺序说明：** 本任务依赖 Task 12（重命名 `index.html` → `index.md`），应在 Task 12 之后执行。建议两者合并为一次 commit：先完成 Task 12 的重命名，再在 `index.md` 上进行本任务的内容修改，统一提交。若合并执行，本任务的 Step 3 Commit 跳过，统一在 Task 12 Step 5 提交。

---

### Task 8：首页 H1 渐变效果在浅色模式下失效

**问题：** `assets/main.scss` 第 38-47 行为 `h1, .page-heading` 设置了白→灰渐变文字效果（`linear-gradient(180deg, #FFFFFF 0%, #A1A1AA 100%)`），在深色背景下视觉效果很好。但浅色模式下第 567-572 行将 `h1` 颜色设为 `#09090B`，而 `-webkit-background-clip: text` 和 `-webkit-text-fill-color: transparent` 仍然生效，导致渐变文字（白→灰）在白色背景上几乎不可见。

**Files:**
- Modify: `assets/main.scss`

- [ ] **Step 1: 为浅色模式 h1 重置渐变效果**

在 `assets/main.scss` 浅色模式区域（约第 567-572 行之后）添加：

```scss
html[data-theme="light"] h1,
html[data-theme="light"] .page-heading {
  background: linear-gradient(180deg, #09090B 0%, #52525B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

说明：将渐变从白→灰改为黑→深灰，在白色背景上保持渐变的视觉效果。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: 手工验证**

- 切换到浅色模式，确认首页标题"首页"和文章页标题文字清晰可见。
- 切换回深色模式，确认未受影响。

- [ ] **Step 4: Commit**

```bash
git add assets/main.scss
git commit -m "fix(style): fix h1 gradient visibility in light mode"
```

---

## Chunk 5：代码质量与维护性

### Task 9：搜索初始化代码在 home.html 和 404.md 中重复

**问题：** `_layouts/home.html` 第 91-108 行和 `404.md` 第 21-36 行各有一份 Simple Jekyll Search 的 CDN 引用和初始化代码。配置参数略有不同（home 有 `searchResultTemplate` 含日期、limit: 20；404 只有标题、limit: 10），但 CDN 引用和基础结构完全重复。后续修改搜索配置需要改两处。

**Strategy:** 提取公共 include，但不要把整段 HTML 模板作为 include 参数直接嵌进 JS 字符串。更稳妥的做法是只传 `variant` 和 `limit` 之类的简单参数，在 include 内部分支选择模板，避免 Liquid 参数、HTML 引号和 JS 字符串三层转义互相污染。

**Files:**
- Create: `_includes/search-widget.html`
- Modify: `_layouts/home.html`
- Modify: `404.md`

- [ ] **Step 1: 创建 `_includes/search-widget.html`**

```html
<!-- Search Widget -->
<div class="search-container" {% if include.style %}style="{{ include.style }}"{% endif %}>
  <label for="search-input" class="sr-only">搜索文章</label>
  <input type="text" id="search-input" placeholder="搜索文章标题或内容..." class="search-input">
  <ul id="results-container" class="search-results"></ul>
</div>

{% if include.variant == "home" %}
  {% assign search_result_template = '<li><a href="{url}"><span class="search-result-title">{title}</span><span class="search-result-date">{date}</span></a></li>' %}
{% else %}
  {% assign search_result_template = '<li><a href="{url}">{title}</a></li>' %}
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/simple-jekyll-search@1.10.0/dest/simple-jekyll-search.min.js"
        integrity="sha256-jL0uP6XOIL51TNq/iPNgR1D8AJuMzJCV0sVsLxke2Zk="
        crossorigin="anonymous"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    SimpleJekyllSearch({
      searchInput: document.getElementById('search-input'),
      resultsContainer: document.getElementById('results-container'),
      json: '{{ "/search.json" | relative_url }}',
      searchResultTemplate: {{ search_result_template | jsonify }},
      noResultsText: '<li class="no-results">没有找到相关文章...</li>',
      limit: {{ include.limit | default: 10 }},
      fuzzy: true,
      exclude: []
    })
  });
</script>
```

- [ ] **Step 2: 在 home.html 中替换为 include 调用**

将 `_layouts/home.html` 第 12-108 行的搜索区域替换为：

```liquid
{% include search-widget.html
   style="margin-bottom: 30px;"
  variant="home"
   limit=20 %}
```

- [ ] **Step 3: 在 404.md 中替换为 include 调用**

将 `404.md` 第 16-36 行的搜索区域替换为：

```liquid
{% include search-widget.html style="margin-top: 16px;" %}
```

- [ ] **Step 4: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 5: 手工验证**

检查项：
- 首页搜索框正常，结果显示标题和日期。
- 404 页搜索框正常，结果只显示标题。
- 两处搜索均支持模糊搜索。

- [ ] **Step 6: Commit**

```bash
git add _includes/search-widget.html _layouts/home.html 404.md
git commit -m "refactor(search): extract shared search widget include"
```

注意：此 Task 如果实施，Task 2 中对搜索框添加 label 的改动应合并到这里，避免重复。建议先执行 Task 9，然后跳过 Task 2 中已被覆盖的步骤。

---

## Chunk 6：视觉层级与内容呈现（新增，经验证确认）

> **验证说明：** 以下问题经代码审查验证确认存在。"搜索框样式问题"经验证——border-radius 混用（0/4/6/8/12px）客观存在但影响不大，不单独立 Task。"日期可读性"经验证——深色模式对比度 8.26:1 达 WCAG AAA，浅色模式 4.7:1 刚过 AA，技术上合格但字号偏小，归入 Deferred。"Markdown 未解析"经代码审查确认为**真实 Bug**：`index.html` 扩展名导致 Jekyll 跳过 Markdown 处理器，链接以原始文字输出——修复方案见 Task 12（将 `index.html` 重命名为 `index.md`，启用 Kramdown 渲染）。

### Task 10：h1 标题缺少底部间距，与欢迎语挤压

**问题：** `assets/main.scss` 第 38-47 行 `h1, .page-heading` 设置了 `margin-top: 1em`，但没有 `margin-bottom`。首页"首页"标题与其下方的欢迎语段落之间无显式间距，视觉上拥挤、缺乏层级呼吸感。

**Files:**
- Modify: `assets/main.scss`

- [ ] **Step 1: 为 h1/page-heading 添加 margin-bottom**

在 `assets/main.scss` `h1, .page-heading` 样式块中添加 `margin-bottom`：

```scss
h1, .page-heading {
  // ... 现有属性保持不变 ...
  margin-bottom: 1.2em;  // 新增
}
```

说明：`1.2em` 约等于 `1.2 × font-size`，与标题字号相称，不影响文章页内的 h1（文章 h1 后通常紧跟正文，间距合理）。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: 手工验证**

需检查所有使用 `h1` 的页面，确认间距合理：
- 首页（`/`）：标题"首页"与欢迎语之间有明显留白。
- 文章页：文章标题与正文间距正常，未过度拉开。
- 分类页（`/categories/`）：标题间距正常。
- 标签页（`/tags/`）：标题间距正常。
- 关于页（`/about/`）：标题间距正常。

- [ ] **Step 4: Commit**

```bash
git add assets/main.scss
git commit -m "fix(style): add margin-bottom to h1 for visual breathing room"
```

---

### Task 11：文章列表不显示摘要

**问题：** `_layouts/home.html` 第 40-42、57-59 行已预留 excerpt 显示逻辑（`{%- if site.minima.show_excerpts -%}`），但 `_config.yml` 的 `minima:` 配置块缺少 `show_excerpts: true`，导致所有文章列表只显示日期和标题，缺乏内容预览，难以吸引读者点击。

**Files:**
- Modify: `_config.yml`

- [ ] **Step 1: 在 _config.yml 的 minima 配置中启用 show_excerpts**

在 `_config.yml` 的 `minima:` 块中添加：

```yaml
minima:
  show_excerpts: true   # 新增：在首页文章列表显示摘要
  date_format: "%Y-%m-%d"
  # ... 其余配置保持不变 ...
```

说明：
- `show_excerpts: true` 后，Jekyll 会自动截取每篇文章的第一段（`<!--more-->` 前的内容，或默认 excerpt_separator 前的内容）作为摘要显示。
- 如需自定义摘要截断位置，可在文章 front matter 中添加 `<!--more-->` 标记。
- 如需控制摘要字数，可在 `_config.yml` 中设置 `excerpt_separator: "<!--more-->"` 并在文章中使用该标记。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: 手工验证**

检查首页文章列表，确认每篇文章下方显示摘要文字；置顶文章和普通文章列表均正常显示。

- [ ] **Step 4: Commit**

```bash
git add _config.yml
git commit -m "feat(home): enable post excerpts on homepage"
```

---

### Task 12：首页 Markdown 内容未被渲染（关键 Bug）

**问题：** `index.html` 使用 `.html` 扩展名，Jekyll 对 `.html` 文件仅做 Liquid 模板处理、**不会**经过 Kramdown（Markdown 渲染器）。同时 `_layouts/home.html` 第 10 行 `{{ content }}` 直接输出、没有 `| markdownify` 过滤器。这导致 `index.html` 中的所有 Markdown 语法（`**Tongsh6**`、`[关于我](/about/)`、`- 列表项`）以原始文本显示在页面上，链接不可点击、列表无格式。

**证据链：**
1. 文件路径：`/index.html`（`.html` 扩展名）
2. Jekyll 默认 `markdown_ext: "markdown,mkdown,mkdn,mkd,md"`，不含 `html`
3. `_config.yml` 未自定义 `markdown_ext`
4. `_layouts/home.html` 第 10 行：`{{ content }}`（无 `markdownify` 过滤器）

**影响：** 首页欢迎语完全无法阅读，链接不可点击，这是**用户可见的严重渲染 Bug**。

**Files:**
- Rename: `index.html` → `index.md`

- [ ] **Step 1: 将 index.html 重命名为 index.md**

```bash
git mv index.html index.md
```

说明：
- Jekyll 会将 `index.md` 编译为 `_site/index.html`，站点 URL 路径不变（仍为 `/`）。
- `jekyll-paginate` 同时支持 `index.html` 和 `index.md` 作为分页模板，分页功能不受影响。
- Liquid 表达式（如 `{{ "/feed.xml" | relative_url }}`）在 `.md` 文件中同样生效。
- 重命名后，文件中现有的 Markdown 语法（加粗、链接、列表）将被 Kramdown 正确渲染。

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

构建后确认：
```bash
# 确认 _site/index.html 正常生成
ls _site/index.html
# 确认 Markdown 已渲染为 HTML（加粗文字）
grep '<strong>Tongsh6</strong>' _site/index.html && echo "OK: bold rendered" || echo "FAIL: bold not rendered"
# 确认链接已渲染
grep '<a href=' _site/index.html | grep -v 'post-link\|site-nav' | head -3
```

- [ ] **Step 3: 验证分页功能**

```bash
ls _site/page2/index.html && echo "OK: pagination works" || echo "FAIL: pagination broken"
```

- [ ] **Step 4: 手工验证**

- 首页欢迎语中 `**Tongsh6**` 显示为加粗文字。
- 链接显示为可点击的超链接。
- `/page2/` 等分页页面仍可访问。

- [ ] **Step 5: Commit**

```bash
git add -A  # 记录 git mv 的重命名操作
git commit -m "fix(home): rename index.html to index.md to enable Markdown rendering"
```

**执行顺序说明：** Task 7（精简欢迎语内容）依赖本任务完成重命名。建议合并为一次 commit：先执行本任务的 `git mv`，再在 `index.md` 上进行 Task 7 的内容修改，统一提交。

---

### Task 13：首页 `.wrapper` max-width 过宽导致阅读体验差

**问题：** `assets/main.scss` 第 378 行将 `.wrapper` 的 `max-width` 设为 `1400px`（Minima 默认约 800px），主要是为文章页 `.post-wrapper` 的 flex 布局（正文 + TOC sidebar）服务。但首页不使用 TOC 布局，`1400px` 导致文章列表和欢迎语在宽屏上横跨极大宽度，远超最佳阅读宽度（60-80 字符，约 600-800px）。

此外，`padding: 30px` 在窄屏上固定不变（Minima 原始主题在 `$on-palm` 断点下会将 padding 减半为 15px），可能导致手机上有效内容区域不够宽。

**Files:**
- Modify: `assets/main.scss`

- [ ] **Step 1: 为首页内容区域限制最大宽度**

在 `assets/main.scss` 中为 `.home` 容器添加独立的最大宽度约束：

```scss
// Constrain homepage content width for better readability
.home {
  max-width: 800px;
  margin: 0 auto;
}
```

说明：
- `.wrapper` 保持 `1400px` 不变（文章页 post-wrapper 需要宽容器放置 TOC sidebar）。
- `.home` 是首页专属的 div 容器（`_layouts/home.html` 第 5 行），限制它的宽度不影响其他页面。
- `800px` 接近 Minima 默认值，适合纯文本阅读；`margin: 0 auto` 用于避免首页窄列贴左显示。

- [ ] **Step 2: 为窄屏适配 wrapper padding**

在 `assets/main.scss` 的 `.wrapper` 规则附近添加响应式 padding：

```scss
.wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding-right: 30px;
  padding-left: 30px;

  @include media-query($on-palm) {
    padding-right: 15px;
    padding-left: 15px;
  }
}
```

- [ ] **Step 3: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 4: 手工验证**

- 宽屏（>1024px）：首页内容不超过 800px，文章页正常（宽容器 + TOC）。
- 窄屏（<600px）：padding 缩小为 15px，有效内容区域更宽。

- [ ] **Step 5: Commit**

```bash
git add assets/main.scss
git commit -m "fix(style): constrain homepage width and add responsive padding"
```

---

## Deferred：暂不纳入本次实施

### D1：CSS 变量化主题系统重构

当前浅色模式通过 `html[data-theme="light"]` 前缀逐条覆盖（约 90 行重复选择器），未使用 CSS custom properties。维护成本高但功能正常。

**结论：** 本次不实施。应在单独的"Theme Tokens Refactor"计划中执行。

### D2：代码块中大量 `!important` 声明

`assets/main.scss` 第 234-260 行代码块样式中有大量 `!important`，源于需要覆盖 Minima 默认样式和 Rouge 输出。移除需要重新梳理选择器优先级。

**结论：** 本次不实施。与 D1 一起在样式重构中处理。

### D3：permalink 格式迁移

从 `/:categories/:year/:month/:day/:title/` 迁移到 `/:year/:month/:day/:title/` 需要为所有已发布文章设置 redirect，并通知搜索引擎。Task 6 已添加注释警告。

**结论：** 本次不实施。需单独评估迁移方案。

### D4：Scrollbar 样式缺少 Firefox 支持

当前自定义滚动条样式（第 268-281 行）仅覆盖 WebKit 内核。Firefox 用 `scrollbar-width` 和 `scrollbar-color` 属性。

**结论：** 影响小，本次不实施。

### D5：CDN 无 fallback 策略

核心功能依赖 cdn.jsdelivr.net 和 cdnjs.cloudflare.com，没有本地 fallback。

**结论：** 对于静态博客站点而言风险可接受，本次不实施。

### D6：日期文字偏小

`.post-meta` 使用 `font-size: 0.85rem` + 等宽字体。深色模式对比度 8.26:1（WCAG AAA），浅色模式 4.7:1（刚过 AA）。技术上合格但视觉上偏小偏淡，非 Retina 屏可读性一般。

**结论：** 影响小，与 CSS 变量重构一起处理更合理。

### D7：border-radius 混用（信息密度/风格一致性）

页面中存在 5 种 border-radius 值（0/4/6/8/12px）：文章列表 0px、copy 按钮 4px、pagination/code 6px、搜索框 8px、pinned-post 12px。整体未形成统一的圆角设计规范。

**结论：** 影响低，属于 Design Token 统一的范畴，归入 D1 一并处理。

---

## 最终验证

> **前置条件：** 若本机尚未安装 `Bundler 4.0.3`，先补齐环境再执行以下构建验证；否则应把构建失败标记为环境阻塞，而不是计划执行失败。

- [ ] **完整构建验证**

```bash
bundle exec jekyll build
```
预期：退出码为 0。

- [ ] **本地预览**

```bash
bundle exec jekyll serve
```
访问 `http://127.0.0.1:4000/`，重点检查：

- [ ] 首页搜索功能
- [ ] 置顶文章仅在第一页显示
- [ ] 浅色模式下代码高亮可读
- [ ] 浅色模式下 h1 标题可见
- [ ] 404 页搜索功能
- [ ] 搜索框可被屏幕阅读器识别
- [ ] 图片放大功能正常（medium-zoom SRI 不阻断）
- [ ] 首页文章列表显示摘要
- [ ] h1 标题与欢迎语之间有合理间距
- [ ] 首页欢迎语简洁，无重复导航链接
- [ ] 首页欢迎语中的链接可点击跳转（无裸 Markdown 语法残留）
- [ ] 首页内容在宽屏下不超过 800px 宽度
- [ ] 窄屏下 padding 适当缩小，内容区域利用合理
- [ ] 文章页 TOC sidebar 布局不受影响

- [ ] **按仓库现有流程收尾**

不要在计划中写死新的发布分支命名或合并命令。遵循仓库当前已有的分支与 release 流程执行即可。
