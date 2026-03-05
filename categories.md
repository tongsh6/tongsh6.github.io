---
layout: page
title: 分类
permalink: /categories/
---

下面是本站所有分类与对应文章（纯静态生成，无额外插件）。

{% assign sorted_categories = site.categories | sort %}
{% for cat in sorted_categories %}
## {{ cat[0] }}（{{ cat[1].size }}）

{% for post in cat[1] %}
- {{ post.date | date: "%Y-%m-%d" }} · [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}

{% endfor %}

