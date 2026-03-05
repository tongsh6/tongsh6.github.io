Param(
  [Parameter(Mandatory = $true)]
  [string]$PostFile
)

$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$postsDir = Join-Path $repoRoot "_posts"
if (-not (Test-Path $postsDir)) { throw "未找到目录：$postsDir" }

$postPath = $null
if ([System.IO.Path]::IsPathRooted($PostFile)) {
  $postPath = $PostFile
} else {
  $normalized = $PostFile -replace "/", "\"
  $normalized = $normalized.Trim()
  $normalized = $normalized -replace "^[.\\]+", ""

  # 兼容两种常见写法：
  # 1) 仅文件名：2026-03-05-hello.md
  # 2) 含目录前缀：_posts\2026-03-05-hello.md
  if ($normalized -match "^_posts\\(.+)$") {
    $postPath = Join-Path $postsDir $Matches[1]
  } elseif (Test-Path (Join-Path $repoRoot $normalized)) {
    $postPath = Join-Path $repoRoot $normalized
  } else {
    $postPath = Join-Path $postsDir $normalized
  }
}

if (-not (Test-Path $postPath)) {
  throw "未找到文章文件：$postPath。可用示例：-PostFile ""2026-03-05-hello.md"" 或 -PostFile ""_posts\\2026-03-05-hello.md"""
}

$text = Get-Content -Raw -Path $postPath -Encoding UTF8

if ($text -notmatch "(?ms)^---\s*\n.*?\n---\s*\n") {
  throw "未找到有效的 Front Matter（--- ... ---）：$postPath"
}

$now = Get-Date
$datePrefix = $now.ToString("yyyy-MM-dd")
$timeWithTz = $now.ToString("yyyy-MM-dd HH:mm:ss") + " +0800"

# 1) 将 published: false 改为 true（或补上）
if ($text -match "(?m)^\s*published:\s*false\s*$") {
  $text = [regex]::Replace($text, "(?m)^\s*published:\s*false\s*$", "published: true")
} elseif ($text -notmatch "(?m)^\s*published:\s*true\s*$") {
  $text = [regex]::Replace($text, "(?ms)^---\s*\n", "---`npublished: true`n")
}

# 2) 更新 date 字段（若存在）
if ($text -match "(?m)^\s*date:\s*") {
  $text = [regex]::Replace($text, "(?m)^\s*date:\s*.*$", "date: $timeWithTz")
}

Set-Content -Encoding UTF8 -NoNewline -Path $postPath -Value $text

# 3) 文件名日期前缀同步为今天（保持 GitHub Pages/Jekyll 的约定）
$fileName = [System.IO.Path]::GetFileName($postPath)
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($postPath)
$rest = $baseName
if ($baseName -match "^\d{4}-\d{2}-\d{2}-(.+)$") {
  $rest = $Matches[1]
}

$targetName = "$datePrefix-$rest.md"
$targetPath = Join-Path $postsDir $targetName

if ($targetPath -ne $postPath) {
  if (Test-Path $targetPath) { throw "目标文件已存在：$targetPath" }
  Move-Item -Path $postPath -Destination $targetPath
  Write-Host "已发布并重命名：$targetPath"
} else {
  Write-Host "已发布：$postPath"
}
