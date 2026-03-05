## 可选：开启 GitHub Actions 的构建检查（推荐）

GitHub Pages 会自动构建站点，但建议额外开一个 CI，避免合并后才发现构建失败。

### 1）创建工作流目录

在仓库根目录创建：

`.github/workflows/`

### 2）放入工作流文件

把仓库根目录的 `WORKFLOW_CI.yml` 移动/复制到：

`.github/workflows/ci.yml`

### 3）提交并推送

推送到 GitHub 后，Actions 页面会出现 `CI` 工作流，并在每次 PR / push 时自动执行 `jekyll build`。

