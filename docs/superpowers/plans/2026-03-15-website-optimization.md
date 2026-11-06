# Website Optimization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复当前博客站点中已经确认的功能缺陷，并完成一组低风险、可验证的 UX 改进。

**Architecture:** 站点基于 Jekyll + Minima，通过覆盖 `_layouts/`、`_includes/` 和 `assets/main.scss` 实现定制。本计划只修改现有文件，不引入新的运行时依赖，不做大规模样式体系重构。

**Tech Stack:** Jekyll, Minima theme, SCSS, Liquid, JavaScript (vanilla), Tocbot, Giscus, Simple Jekyll Search

**Execution Rules:**
- 每个任务完成后都执行一次 `bundle exec jekyll build`，不要使用 `| tail -5` 之类会掩盖退出码的管道命令。
- 除非任务明确要求，否则不要顺手做视觉重构或结构性重写。
- 与主题相关的改动必须同时考虑页面本体和 Giscus 评论区的初始主题一致性。

---

## Chunk 1：关键 Bug 修复

### ~~Task 1：移除 post_scripts.html 中的重复内容渲染~~

> **已废弃：** 此 Bug 已在 PR #25（commit `0581ad1` — "fix(ui): remove duplicated post content rendering in scripts include"）中修复并合并进 main。当前 `_includes/post_scripts.html` 开头不包含 `{{ content }}` 输出。无需执行。

---

### Task 2：修复代码块复制按钮在移动端不可见

**问题：** `assets/main.scss` 中 `.copy-code-btn` 默认 `opacity: 0`，仅在 hover 时显示；移动端无法 hover，按钮始终不可见。

**Files:**
- Modify: `assets/main.scss`

- [ ] **Step 1: 让移动端默认可见，桌面端保持轻量 hover 反馈**

将复制按钮样式调整为：
```scss
.copy-code-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #EDEDED;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 1;
}

@media (hover: hover) {
  .copy-code-btn {
    opacity: 0.4;
  }

  figure.highlight:hover .copy-code-btn,
  pre:hover .copy-code-btn {
    opacity: 1;
  }
}
```

- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: Commit**

```bash
git add assets/main.scss
git commit -m "fix(ui): show copy button on touch devices"
```

---

### Task 3：修复主题切换闪烁，并同步 Giscus 初始主题

**问题：** 主题初始化脚本放在 `_includes/header.html` 末尾，执行时机过晚，页面首屏会出现错误主题闪烁。除此之外，评论区脚本当前把 Giscus 主题写死为 `dark`，即使页面首屏主题正确，评论区初始主题仍可能错误。

**Files:**
- Create: `_includes/custom-head.html`
- Modify: `_includes/header.html`
- Modify: `_includes/post_scripts.html`

- [ ] **Step 1: 创建 `_includes/custom-head.html`，在 head 阶段提前设置主题**

创建 `_includes/custom-head.html`：
```html
<link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
<link rel="dns-prefetch" href="https://cdnjs.cloudflare.com">
<link rel="preconnect" href="https://giscus.app" crossorigin>

<script>
  (function() {
    var theme = 'dark';
    try {
      theme = localStorage.getItem('theme') || 'dark';
    } catch (error) {
      theme = 'dark';
    }
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

说明：该方案依赖 Minima 对 `_includes/custom-head.html` 的 head hook（Minima 2.5.0+ 在 `_includes/head.html` 中包含 `{% include custom-head.html %}`）。

- [ ] **Step 1.5: 验证 custom-head.html hook 生效**

构建站点后检查生成的 HTML 是否包含注入的脚本：
```bash
bundle exec jekyll build
grep -l 'localStorage.getItem' _site/index.html
```
预期：命令输出 `_site/index.html`，表示 hook 生效。

**若验证失败（无输出）：** 说明当前 Minima 版本不支持 `custom-head.html` hook。此时应改为直接覆盖 `_includes/head.html`（从主题 gem 中复制默认版本，再在其中插入主题初始化脚本）。不要在 `header.html` 中叠加第二套初始化逻辑。后续步骤在 hook 验证通过后方可继续。

- [ ] **Step 2: 从 header.html 中移除重复初始化，改为读取 DOM 上已设置的主题**

要求：
- 删除 `</header>` 标签之后、`DOMContentLoaded` 之前的同步主题初始化代码（第 43-44 行的 `const currentTheme = localStorage.getItem('theme') || 'dark'` 及紧跟的 `document.documentElement.setAttribute('data-theme', currentTheme)`）。
- **注意：** 删除这两行后，`DOMContentLoaded` 回调内部原有的 `updateIcon(currentTheme)` 会因 `currentTheme` 未定义而报错。需在回调开头重新获取主题：
  ```javascript
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  ```
- 在 toggle 逻辑中，继续从 `document.documentElement.getAttribute('data-theme')` 读取当前主题。
- 保留现有 toggle 逻辑，并继续在点击时通过 `postMessage` 同步 Giscus iframe。

- [ ] **Step 3: 修复 Giscus 初始主题不是当前主题的问题**

修改 `_includes/post_scripts.html` 中的 Giscus script 标签：
- 不再把 `data-theme` 固定写死为 `dark`。
- 不使用 Liquid 读取运行时主题；Liquid 在构建期执行，无法访问 `document`。
- 统一改为在浏览器端用 JS 动态创建 Giscus script 元素，并在创建时从 `document.documentElement.dataset.theme` 读取当前主题，确保评论区首屏主题与页面一致。

推荐实现约束：
- 保留现有 Giscus 配置项（repo、category、mapping 等）不变。
- 仅把 script 注入方式改为 JS 动态创建。
- 动态创建的 `<script>` 元素应 append 到 `_layouts/post.html` 中已有的 `<div class="giscus">` 容器内（而不是 `document.body` 末尾），以确保评论区渲染位置不变。
- 点击主题切换后的 `postMessage` 同步逻辑继续保留，作为首次加载之后的主题同步机制。

- [ ] **Step 4: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 5: 手工验证主题行为**

检查项：
- 页面首次加载时无明显 FOUC。
- 已保存为浅色主题时，Giscus 首次加载即为浅色。
- 点击主题切换后，页面和 Giscus 都同步切换。

- [ ] **Step 6: Commit**

```bash
git add _includes/custom-head.html _includes/header.html _includes/post_scripts.html
git commit -m "fix(theme): prevent FOUC and sync giscus initial theme"
```

---

### Task 4：完善搜索功能

**问题：** 当前 `search.json` 不包含摘要字段，搜索结果缺少正文命中能力；首页搜索也关闭了 fuzzy 匹配。

**Files:**
- Modify: `search.json`
- Modify: `_layouts/home.html`
- Modify: `assets/main.scss`

- [ ] **Step 1: 为 search.json 增加摘要字段**

将 `search.json` 调整为输出以下字段：
- `title`
- `categories`（原字段名为 `category`，此处改为复数形式以匹配 Jekyll 的 `post.categories` 数组；当前搜索模板不直接引用此字段名，改名不会引起前端异常）
- `tags`
- `url`
- `date`
- `excerpt`

推荐实现：
```liquid
---
layout: null
---
[
  {% for post in site.posts %}
    {
      "title": "{{ post.title | escape }}",
      "categories": "{{ post.categories | join: ', ' }}",
      "tags": "{{ post.tags | join: ', ' }}",
      "url": "{{ site.baseurl }}{{ post.url }}",
      "date": "{{ post.date | date: '%Y-%m-%d' }}",
      "excerpt": "{{ post.excerpt | strip_html | strip_newlines | escape | truncate: 200 }}"
    }{% unless forloop.last %},{% endunless %}
  {% endfor %}
]
```

- [ ] **Step 2: 更新首页搜索配置**

> **依赖：** 本步骤与 Step 3 必须同时完成。Step 2 模板中引用了 `.search-result-date` class，若 Step 3 样式缺失，日期会以无样式裸文本显示。

要求：
- `fuzzy` 改为 `true`。
- 搜索结果模板至少显示标题和日期。
- 如果结果模板中不展示 `excerpt`，则在任务描述中明确说明：摘要字段用于提升命中能力，而不是必须展示在 UI 中。

推荐模板：
```javascript
SimpleJekyllSearch({
  searchInput: document.getElementById('search-input'),
  resultsContainer: document.getElementById('results-container'),
  json: '{{ "/search.json" | relative_url }}',
  searchResultTemplate: '<li><a href="{url}"><span class="search-result-title">{title}</span><span class="search-result-date">{date}</span></a></li>',
  noResultsText: '<li class="no-results">没有找到相关文章...</li>',
  limit: 20,
  fuzzy: true,
  exclude: []
})
```

- [ ] **Step 3: 添加搜索结果日期样式**

在 `assets/main.scss` 中补充 `.search-result-title` 与 `.search-result-date` 样式。

- [ ] **Step 4: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 5: 手工验证搜索**

检查项：
- 标题关键字可命中。
- 正文中出现但标题未出现的词可命中。
- 输入轻微拼写偏差时仍有合理结果。

- [ ] **Step 6: Commit**

```bash
git add search.json _layouts/home.html assets/main.scss
git commit -m "feat(search): add excerpt index and enable fuzzy search"
```

---

## Chunk 2：低风险 UX 增强

### Task 5：文章页显示更新时间

**问题：** 多篇文章 front matter 已包含 `last_modified_at`，但文章头部没有展示更新信息。

**Files:**
- Modify: `_layouts/post.html`
- Modify: `assets/main.scss`

- [ ] **Step 1: 在发布日期后展示更新时间**

调整 `_layouts/post.html` 中的 `.post-meta`，要求：
- 保留发布日期。
- 若存在 `page.last_modified_at`，展示“更新于 YYYY-MM-DD”。
- 保留作者信息。

- [ ] **Step 2: 为更新时间补充样式**

在 `assets/main.scss` 中新增 `.post-updated` 样式，使其视觉层级低于标题、高于正文。

- [ ] **Step 3: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 4: 手工验证**

任选一篇带 `last_modified_at` 的文章，确认：
- 更新时间正常显示。
- 未设置 `last_modified_at` 的文章不受影响。

- [ ] **Step 5: Commit**

```bash
git add _layouts/post.html assets/main.scss
git commit -m "feat(post): display last modified date"
```

---

### Task 6：改善移动端导航的可访问性

**问题：** 当前导航使用 checkbox hack，缺少可感知的菜单状态；仅给 `label` 补 ARIA 属性并不能把它变成真正的可访问交互控件。

**Strategy:** 保持现有布局尽量不变，但把“菜单开关”升级为真正可聚焦的 button，并用最小 CSS 调整保证移动端样式与现有导航行为一致。

**Files:**
- Modify: `_includes/header.html`
- Modify: `assets/main.scss`

- [ ] **Step 1: 为导航区域补充基础语义**

要求：
- `nav.site-nav` 增加 `aria-label="主导航"`。
- 菜单图标的装饰性 SVG 标记为 `aria-hidden="true"`。

- [ ] **Step 2: 让菜单状态可被辅助技术感知**

- 必须把当前 `label[for="nav-trigger"]` 重构为真正的 `button`，不能只给 `label` 补 ARIA 属性。
- `button` 至少包含：
  - `type="button"`
  - `aria-controls`，指向实际展开/收起的菜单容器
  - `aria-expanded="false"` 初始值
  - 可读的 `aria-label`，例如“切换导航菜单”
- **推荐方案：保留 hidden checkbox + button JS toggle。** 具体做法：
  - 保留 `<input type="checkbox" id="nav-trigger" class="nav-trigger" />` 作为 CSS 状态源（`#nav-trigger:checked ~ .trigger` 选择器继续工作）。
  - 将 `<label for="nav-trigger">` 替换为 `<button>`，不再保留 label。
  - button 点击时通过 JS 切换 checkbox 的 `checked` 属性，同时同步 `aria-expanded`。
  - 这样可以最小化 CSS 改动——无需重写 `.trigger` 的展开选择器。
- checkbox 必须保留 `display: none`（或等效隐藏），不能成为额外的可见控件或焦点入口。
- 展开和关闭菜单时，button 上的 `aria-expanded` 必须与视觉状态同步为 `true/false`。

- [ ] **Step 3: 为 button 方案补充最小样式调整**

要求：
- 若将 `label` 改为 `button` 后影响了移动端菜单图标样式，在 `assets/main.scss` 中补最小必要样式。
- 不重写整套导航样式，只修正 button 默认边框、背景、对齐、focus 可见性等问题。
- 若保留 checkbox，应确认它不会成为额外的可见控件，也不会制造双焦点入口。

- [ ] **Step 4: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 5: 手工验证**

检查项：
- 键盘可以聚焦到菜单开关。
- 展开和关闭时，状态变化与视觉表现一致。
- 使用屏幕阅读器或浏览器辅助功能树检查时，菜单开关应被识别为 button，而不是 label。
- 移动端导航链接仍可正常点击。

- [ ] **Step 6: Commit**

```bash
git add _includes/header.html assets/main.scss
git commit -m "feat(a11y): improve mobile navigation accessibility"
```

---

### Task 7：改善 404 页面

**问题：** 当前 404 页面只有返回链接，缺少快速找回内容的入口。

**Files:**
- Modify: `404.md`

- [ ] **Step 1: 在 404 页面加入搜索框**

要求：
- 保留“返回首页 / 查看分类 / 查看标签”入口。
- 新增与首页一致的搜索输入框和结果列表。
- 复用现有 `search.json` 和 Simple Jekyll Search。
- **注意：** `404.md` 使用 `layout: page`，该布局不包含 Simple Jekyll Search 的 JS（仅 `_layouts/home.html` 引入了该脚本）。需要在 `404.md` 底部通过内联 `<script>` 标签引入 CDN 脚本并初始化搜索实例。
- 搜索索引路径不要写死为 `/search.json`，应与首页保持一致，使用 `{{ "/search.json" | relative_url }}`，避免后续 `baseurl` 变化时失效。
  ```html
  <script src="https://cdn.jsdelivr.net/npm/simple-jekyll-search@1.10.0/dest/simple-jekyll-search.min.js"
          integrity="sha256-jL0uP6XOIL51TNq/iPNgR1D8AJuMzJCV0sVsLxke2Zk="
          crossorigin="anonymous"></script>
  <script>
    SimpleJekyllSearch({
      searchInput: document.getElementById('search-input'),
      resultsContainer: document.getElementById('results-container'),
      json: '{{ "/search.json" | relative_url }}',
      searchResultTemplate: '<li><a href="{url}">{title}</a></li>',
      noResultsText: '<li class="no-results">没有找到相关文章...</li>',
      limit: 10,
      fuzzy: true
    })
  </script>
  ```

> **建议：** 同时为 `_layouts/home.html` 中已有的同一 CDN 引用补上相同的 `integrity` 和 `crossorigin` 属性，保持一致性。
- [ ] **Step 2: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 3: 手工验证**

访问 `/404.html`，确认：
- 搜索框可输入。
- 能返回文章列表结果。
- 结果点击后可跳转。

- [ ] **Step 4: Commit**

```bash
git add 404.md
git commit -m "feat(404): add search entry to not found page"
```

---

### Task 8：提取分类/标签公共模板（可选优化，优先级低）

**问题：** `categories.md` 和 `tags.md` 模板结构重复，后续维护容易遗漏其一。

> **注意：** 当前两个文件各 ~15 行，核心模板逻辑仅 ~6 行，独立改动频率极低。提取公共 include 会引入参数传递等额外复杂度，收益有限。若执行时间不足，可跳过此 Task。

**Files:**
- Create: `_includes/post-group-list.html`
- Modify: `categories.md`
- Modify: `tags.md`

- [ ] **Step 1: 创建公共 include**

创建 `_includes/post-group-list.html`，负责：
- 接收 `include.groups`。
- 对分组排序。
- 渲染“组名 + 数量 + 文章列表”。

- [ ] **Step 2: 让分类页与标签页复用该 include**

要求：
- `categories.md` 使用 `site.categories`。
- `tags.md` 使用 `site.tags`。
- 页面文本保持现有中文描述即可。

- [ ] **Step 3: 验证构建并检查生成结果**

```bash
bundle exec jekyll build
ls _site/categories/ _site/tags/
```

- [ ] **Step 4: Commit**

```bash
git add _includes/post-group-list.html categories.md tags.md
git commit -m "refactor: extract shared template for categories and tags"
```

---

### Task 9：将 CoStruct 从主导航迁移到关于页

**问题：** `costruct.md` 目前位于顶栏主导航，会分散博客主线内容。

**Files:**
- Modify: `_config.yml`
- Modify: `about.md`

- [ ] **Step 1: 从 `header_pages` 中移除 `costruct.md`**

保留主导航为：
- `about.md`
- `categories.md`
- `tags.md`

- [ ] **Step 2: 在 about 页面补回项目入口**

在 `about.md` 增加一个“项目”小节，链接到 `/costruct/`。

- [ ] **Step 3: 验证构建**

```bash
bundle exec jekyll build
```

- [ ] **Step 4: 手工验证导航**

检查项：
- 顶栏不再显示 CoStruct。
- about 页面保留 CoStruct 入口。

- [ ] **Step 5: Commit**

```bash
git add _config.yml about.md
git commit -m "refactor(nav): move CoStruct link from header to about page"
```

---

## Deferred：暂不纳入本次实施

### Task 10：CSS 主题变量重构

当前 `assets/main.scss` 的确存在浅色主题重复规则，但这是一次跨整份样式文件的结构性重构，不适合与本轮 bugfix 混合执行。

**结论：** 本次计划不实施。

**原因：**
- 改动面过大，难以与功能修复一同回归。
- 当前计划没有配套的视觉回归策略。
- 与本轮目标相比，优先级低于已确认 bug。

**后续建议：**
- 单独创建一份“Theme Tokens Refactor”计划。
- 先定义变量边界和回归截图范围，再逐步迁移。

### Task 11：移动端 TOC 浮动按钮

移动端目录入口是合理需求，但计划中的 drawer 方案还缺少完整的可访问性设计，例如 focus 管理、Esc 关闭、关闭后焦点返回等。

**结论：** 本次计划不实施。

**原因：**
- 这是新增交互，不是既有 bug 修复。
- 当前方案可访问性未闭环，直接落地风险高。

**后续建议：**
- 单独设计移动端目录交互。
- 明确键盘行为、focus trap、关闭行为和滚动锁定策略后再实现。

---

## 最终验证

- [ ] **完整构建验证**

```bash
bundle exec jekyll build
```
预期：退出码为 0。

- [ ] **本地预览**

```bash
bundle exec jekyll serve
```
访问 `http://127.0.0.1:4000/`，重点检查：首页搜索、文章页正文、复制按钮、主题切换、404 页面、导航菜单。

- [ ] **回归检查清单**

桌面端：
- [ ] 文章正文不再重复渲染。
- [ ] 搜索结果可返回标题，必要时可命中摘要内容。
- [ ] 切换主题后页面和 Giscus 一致。
- [ ] 更新时间显示正常。

移动端：
- [ ] 代码块复制按钮可见并可点击。
- [ ] 汉堡菜单可展开、可关闭、可访问。
- [ ] 404 页面搜索可用。

- [ ] **按仓库现有流程收尾**

不要在计划中写死新的发布分支命名或合并命令。遵循仓库当前已有的分支与 release 流程执行即可。
