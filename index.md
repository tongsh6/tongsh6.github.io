---
layout: default
title: 首页
---

<div class="home-intro">
  <p class="home-tagline">记录技术、项目与生活的可复用笔记</p>
</div>

<div class="home-entries">
  <a href="/costruct/" class="home-entry-card costruct-card">
    <div class="entry-icon">⚡</div>
    <div class="entry-content">
      <h2>CoStruct</h2>
      <p>人机协作方法论项目</p>
    </div>
    <span class="entry-arrow">→</span>
  </a>

  <a href="/posts/" class="home-entry-card articles-card">
    <div class="entry-icon">📝</div>
    <div class="entry-content">
      <h2>全部文章</h2>
      <p>浏览 {{ site.posts.size }} 篇技术笔记与实践记录</p>
    </div>
    <span class="entry-arrow">→</span>
  </a>
</div>
