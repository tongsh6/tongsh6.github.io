Param(
  [Parameter(Mandatory = $true)]
  [string]$Title,

  [string]$Category = "技术",

  [string[]]$Tags = @(),

  # 草稿模式：文章会放在 _posts 中，但设置 published: false（不会出现在站点里）
  [switch]$Draft
)

$ErrorActionPreference = "Stop"

function To-Slug([string]$text) {
  $slug = $text.Trim().ToLowerInvariant()
  $slug = $slug -replace "\s+", "-"
  $slug = $slug -replace "[^a-z0-9\u4e00-\u9fa5\-]", ""
  $slug = $slug -replace "-{2,}", "-"
  $slug = $slug.Trim("-")
  if ([string]::IsNullOrWhiteSpace($slug)) { $slug = "post" }
  return $slug
}

$repoRoot = $PSScriptRoot
$postsDir = Join-Path $repoRoot "_posts"
if (-not (Test-Path $postsDir)) { throw "未找到目录：$postsDir" }

$now = Get-Date
$datePrefix = $now.ToString("yyyy-MM-dd")
$timeWithTz = $now.ToString("yyyy-MM-dd HH:mm:ss") + " +0800"
$slug = To-Slug $Title

$filePath = Join-Path $postsDir "$datePrefix-$slug.md"
if (Test-Path $filePath) {
  throw "文件已存在：$filePath"
}

$normalizedTags = $Tags | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
$tagsYaml = if ($normalizedTags.Count -gt 0) { "[{0}]" -f ($normalizedTags -join ", ") } else { "[]" }

$draftLine = if ($Draft) { "published: false`n" } else { "" }

$content = @"
---
layout: post
title: ""$Title""
date: $timeWithTz
categories: [$Category]
tags: $tagsYaml
$draftLine---

在这里开始写正文……

"@

Set-Content -Encoding UTF8 -NoNewline -Path $filePath -Value $content
Write-Host "已创建：$filePath"
if ($Draft) { Write-Host "提示：该文章为草稿（published: false），发布时运行 publish-post.ps1" }

