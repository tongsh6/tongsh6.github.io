---
layout: page
title: 标签
permalink: /tags/
---

下面是本站所有标签与对应文章（纯静态生成，无额外插件）。

{% assign sorted_tags = site.tags | sort %}
{% for tag in sorted_tags %}
## {{ tag[0] }}（{{ tag[1].size }}）

{% for post in tag[1] %}
- {{ post.date | date: "%Y-%m-%d" }} · [{{ post.title }}]({{ post.url | relative_url }})
{% endfor %}

{% endfor %}

