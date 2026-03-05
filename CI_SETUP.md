## GitHub Actions CI 说明

仓库已启用 CI，工作流文件位置：

`.github/workflows/ci.yml`

该工作流会在每次 `push main/develop` 和 `pull_request` 时执行 `bundle exec jekyll build`，用于提前发现构建问题。

## 常见操作

### 1）查看 CI 状态

进入 GitHub 仓库的 `Actions` 页面，查看 `CI` 工作流执行结果。

### 2）修改 CI 配置

直接编辑：

`.github/workflows/ci.yml`

### 3）临时关闭 CI

可在 `ci.yml` 中注释/删除触发器，或在 GitHub Actions 页面手动禁用工作流。
