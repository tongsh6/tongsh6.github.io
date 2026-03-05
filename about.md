---
layout: page
title: 关于我
permalink: /about/
---

你好，我是 **Tongsh6**，这里记录技术学习、项目实践和阶段性复盘。

## 我在做什么

- 持续构建个人知识库，沉淀可复用的技术方法
- 关注工程效率、工具链优化和 AI 在实际场景的落地

## 我关注的方向

- 工程效率与自动化
- 后端与系统设计
- AI 应用与产品化实践

## 常用技术栈

- 语言：Java、TypeScript、Python
- 平台/框架：Spring、Node.js、Docker
- 工具：Git、VS Code、Obsidian

## 联系方式（可选）

- GitHub：[https://github.com/tongsh6](https://github.com/tongsh6)
- Zhihu：[https://www.zhihu.com/people/tsloong](https://www.zhihu.com/people/tsloong)
- 邮箱：tongsh6 [at] gmail.com
  <button id="copy-email-btn" type="button" style="margin-left:8px;">点击复制</button>
  <span id="copy-email-msg" style="margin-left:6px;color:#2e7d32;"></span>

## 关于这个博客

- 更新频率：随缘但尽量持续
- 文章偏好：可复用的笔记、可落地的方法、踩坑与复盘
- RSS：[订阅地址](/feed.xml)

<script>
document.addEventListener("DOMContentLoaded", function () {
  var button = document.getElementById("copy-email-btn");
  var message = document.getElementById("copy-email-msg");
  if (!button || !message) return;
  button.addEventListener("click", async function () {
    try {
      await navigator.clipboard.writeText("tongsh6@gmail.com");
      message.textContent = "已复制";
      setTimeout(function () { message.textContent = ""; }, 2000);
    } catch (e) {
      message.textContent = "复制失败，请手动复制";
    }
  });
});
</script>
