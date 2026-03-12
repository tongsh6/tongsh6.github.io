from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as html_to_markdown
except ImportError:
    requests = None
    BeautifulSoup = None
    html_to_markdown = None


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/133.0.0.0 Safari/537.36"
)
ARTICLE_URL_RE = re.compile(r"/article/details/(?P<id>\d+)")
DATE_RE = re.compile(
    r"(?P<date>\d{4}[-/]\d{2}[-/]\d{2}"
    r"(?:[ T]\d{2}:\d{2}(?::\d{2})?)?"
    r"(?: ?(?:\+|-)\d{2}:?\d{2})?)"
)


@dataclass
class ArticleRef:
    article_id: str
    title: str
    url: str
    list_date: str | None = None


def ensure_runtime_dependencies() -> None:
    if requests and BeautifulSoup and html_to_markdown:
        return
    print(
        "缺少运行依赖，请先执行：python -m pip install -r scripts/requirements-csdn-sync.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将 CSDN 博客同步到当前 Jekyll 仓库。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover", help="抓取博客文章清单并写入 manifest。")
    add_discover_args(discover)

    sync = subparsers.add_parser("sync", help="根据 manifest 抓取详情并生成 Jekyll 文章。")
    add_sync_args(sync)

    run = subparsers.add_parser("run", help="先 discover，再 sync。")
    add_discover_args(run)
    add_sync_args(run, include_manifest=False, include_network_args=False)

    return parser.parse_args()


def add_discover_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--blog-url", required=True, help="CSDN 博客首页地址")
    parser.add_argument("--manifest", default="data/csdn-manifest.json", help="文章清单输出位置")
    parser.add_argument("--max-pages", type=int, default=50, help="最多抓取多少个列表页")
    parser.add_argument("--pause", type=float, default=0.5, help="请求间隔秒数")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP 超时秒数")
    add_auth_args(parser)


def add_sync_args(
    parser: argparse.ArgumentParser,
    *,
    include_manifest: bool = True,
    include_network_args: bool = True,
) -> None:
    if include_manifest:
        parser.add_argument("--manifest", default="data/csdn-manifest.json", help="discover 生成的文章清单位置")
    parser.add_argument("--repo-root", default=".", help="Jekyll 仓库根目录")
    parser.add_argument("--state", default="data/csdn-sync-state.json", help="同步状态文件")
    if include_network_args:
        parser.add_argument("--pause", type=float, default=0.5, help="请求间隔秒数")
        parser.add_argument("--timeout", type=int, default=30, help="HTTP 超时秒数")
    parser.add_argument("--limit", type=int, default=None, help="仅处理前 N 篇文章，便于试跑")
    parser.add_argument("--no-images", action="store_true", help="不同步正文图片，只保留原始链接")
    parser.add_argument("--overwrite", action="store_true", help="忽略状态文件，强制覆盖已同步文章")
    if include_network_args:
        add_auth_args(parser)


def add_auth_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cookie", default=None, help="直接传入浏览器复制的 Cookie 字符串")
    parser.add_argument("--cookie-file", default=None, help="从文件读取 Cookie 字符串")
    parser.add_argument(
        "--cookie-env",
        default="CSDN_COOKIE",
        help="从环境变量读取 Cookie，默认 CSDN_COOKIE",
    )

def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_cookie_text(raw: str | None) -> str | None:
    if not raw:
        return None
    value = raw.strip()
    if value.lower().startswith('cookie:'):
        value = value.split(':', 1)[1].strip()
    return value or None


def resolve_cookie_text(cookie: str | None, cookie_file: str | None, cookie_env: str | None) -> str | None:
    if cookie:
        return normalize_cookie_text(cookie)
    if cookie_file:
        return normalize_cookie_text(Path(cookie_file).read_text(encoding='utf-8'))
    if cookie_env:
        return normalize_cookie_text(os.environ.get(cookie_env))
    return None


def build_session(timeout: int, *, cookie_text: str | None = None):
    ensure_runtime_dependencies()
    session = requests.Session()
    session.headers.update(
        {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://blog.csdn.net/',
        }
    )
    if cookie_text:
        session.headers['Cookie'] = cookie_text
    session.request_timeout = timeout
    return session

def request_text(session, url: str, *, pause: float) -> str:
    last_error = None
    for attempt in range(1, 4):
        try:
            response = session.get(url, timeout=session.request_timeout)
            response.raise_for_status()
            response.encoding = response.encoding or response.apparent_encoding or "utf-8"
            if pause > 0:
                time.sleep(pause)
            return response.text
        except Exception as exc:
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(max(pause, 0.5) * attempt)
    raise last_error


def request_binary(session, url: str, *, pause: float) -> tuple[bytes, str | None]:
    last_error = None
    for attempt in range(1, 4):
        try:
            response = session.get(url, timeout=session.request_timeout)
            response.raise_for_status()
            if pause > 0:
                time.sleep(pause)
            return response.content, response.headers.get("Content-Type")
        except Exception as exc:
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(max(pause, 0.5) * attempt)
    raise last_error

def normalize_blog_url(url: str) -> str:
    return url.rstrip("/")


def list_page_candidates(blog_url: str, page: int) -> list[str]:
    normalized = normalize_blog_url(blog_url)
    if page == 1:
        return [normalized, f"{normalized}/article/list/1"]
    return [
        f"{normalized}/article/list/{page}",
        f"{normalized}?type=blog&page={page}",
        f"{normalized}/article/list/{page}?spm=1001.2014.3001.5482",
    ]


def extract_article_id(url: str) -> str | None:
    match = ARTICLE_URL_RE.search(urlparse(url).path)
    if not match:
        return None
    return match.group("id")


def normalize_datetime(raw: str | None) -> str | None:
    if not raw:
        return None
    value = raw.strip().replace("/", "-").replace("T", " ")
    if value.endswith("Z"):
        value = value[:-1] + " +0000"
    if re.search(r"[+-]\d{2}:\d{2}$", value):
        value = value[:-3] + value[-2:]
    for fmt in (
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%d %H:%M %z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            parsed = datetime.strptime(value, fmt)
            if parsed.tzinfo is None:
                return parsed.strftime("%Y-%m-%d %H:%M:%S +0800")
            return parsed.strftime("%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            continue
    return None


def find_date_in_text(text: str) -> str | None:
    match = DATE_RE.search(text)
    if not match:
        return None
    return normalize_datetime(match.group("date"))


def find_date_near_node(node) -> str | None:
    current = node
    for _ in range(4):
        if current is None:
            break
        text = " ".join(current.stripped_strings)
        candidate = find_date_in_text(text[:600])
        if candidate:
            return candidate
        current = current.parent
    return None


def normalize_article_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(query="", fragment="")
    return cleaned.geturl()


def clean_list_title(text: str) -> str:
    value = re.sub(r"^(原创|转载)\s+", "", text).strip()
    value = re.sub(r"\s+(原创|转载)\s+博文.*$", "", value)
    value = re.sub(r"\s+(原创|转载).*$", "", value)
    value = re.sub(r"\s+\d+$", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -")


def extract_articles_from_list_page(html: str, base_url: str) -> list[ArticleRef]:
    soup = BeautifulSoup(html, "html.parser")
    discovered: dict[str, ArticleRef] = {}

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href:
            continue
        absolute_url = urljoin(base_url, href)
        article_id = extract_article_id(absolute_url)
        if not article_id:
            continue

        raw_title = " ".join(anchor.stripped_strings).strip() or anchor.get("title", "").strip()
        title = clean_list_title(raw_title)
        if not title or title in {"阅读全文", "查看全文"}:
            continue

        article_ref = ArticleRef(
            article_id=article_id,
            title=title,
            url=normalize_article_url(absolute_url),
            list_date=find_date_near_node(anchor),
        )
        current = discovered.get(article_id)
        if current is None or len(article_ref.title) < len(current.title):
            discovered[article_id] = article_ref

    return list(discovered.values())

def discover_articles(blog_url: str, manifest_path: Path, *, max_pages: int, pause: float, timeout: int, cookie_text: str | None = None) -> list[dict]:
    session = build_session(timeout, cookie_text=cookie_text)
    discovered: dict[str, ArticleRef] = {}
    empty_pages = 0

    for page in range(1, max_pages + 1):
        articles = []
        for candidate in list_page_candidates(blog_url, page):
            try:
                html = request_text(session, candidate, pause=pause)
            except Exception:
                continue
            page_articles = extract_articles_from_list_page(html, candidate)
            if page_articles:
                articles = page_articles
                break

        if not articles:
            empty_pages += 1
            if empty_pages >= 2:
                break
            continue

        empty_pages = 0
        new_count = 0
        for article in articles:
            if article.article_id not in discovered:
                discovered[article.article_id] = article
                new_count += 1

        print(f"[discover] 第 {page} 页抓到 {len(articles)} 条，新增 {new_count} 条")
        if new_count == 0:
            break

    manifest = [
        {
            "article_id": item.article_id,
            "title": item.title,
            "url": item.url,
            "list_date": item.list_date,
        }
        for item in sorted(discovered.values(), key=lambda x: (x.list_date or "", x.article_id))
    ]
    dump_json(manifest_path, manifest)
    print(f"[discover] 已写入 {len(manifest)} 篇文章到 {manifest_path}")
    return manifest


def select_first(soup, selectors: Iterable[str]):
    for selector in selectors:
        node = soup.select_one(selector)
        if node is not None:
            return node
    return None


def get_meta_content(soup, selector: str) -> str | None:
    node = soup.select_one(selector)
    if node is None:
        return None
    return (node.get("content") or "").strip() or None


def extract_title_from_page(soup) -> str | None:
    for selector in ("h1.title-article", "h1", ".article-title-box"):
        node = soup.select_one(selector)
        if node:
            return " ".join(node.stripped_strings).strip()
    return None


def extract_date_from_page(soup, *, updated: bool = False) -> str | None:
    if not updated:
        for selector in ('.blog-postTime[data-time]', '.time.blog-postTime[data-time]'):
            node = soup.select_one(selector)
            if node:
                normalized = normalize_datetime(node.get('data-time'))
                if normalized:
                    return normalized

    up_time = soup.select_one('.up-time')
    if up_time:
        text = ' '.join(up_time.stripped_strings)
        if updated:
            modified_match = re.search(r'已于\s*([0-9\-/: ]+)\s*修改', text)
            if modified_match:
                normalized = normalize_datetime(modified_match.group(1))
                if normalized:
                    return normalized
        else:
            published_match = re.search(r'于\s*([0-9\-/: ]+)\s*首次发布', text)
            if published_match:
                normalized = normalize_datetime(published_match.group(1))
                if normalized:
                    return normalized

    selectors = ['.article-info-box', '.bar-content', '.article-title-box', 'main']
    modified_pattern = re.compile(r'已于\s*([0-9\-/: ]+)\s*修改')
    published_pattern = re.compile(r'于\s*([0-9\-/: ]+)\s*首次发布')

    for selector in selectors:
        node = soup.select_one(selector)
        if not node:
            continue
        text = ' '.join(node.stripped_strings)

        modified_match = modified_pattern.search(text)
        published_match = published_pattern.search(text)
        if updated and modified_match:
            normalized = normalize_datetime(modified_match.group(1))
            if normalized:
                return normalized
        if (not updated) and published_match:
            normalized = normalize_datetime(published_match.group(1))
            if normalized:
                return normalized

        dates = [match.group('date') for match in DATE_RE.finditer(text)]
        if not dates:
            continue
        candidate = dates[0] if updated else dates[-1]
        normalized = normalize_datetime(candidate)
        if normalized:
            return normalized
    return None

def extract_texts(soup, selectors: Iterable[str]) -> list[str]:
    values: list[str] = []
    for selector in selectors:
        for node in soup.select(selector):
            text = " ".join(node.stripped_strings).strip()
            text = text.lstrip("#").strip()
            if text and text not in values:
                values.append(text)
    return values

def pick_category(candidates: list[str]) -> str:
    blacklist = {"首页", "博客", "专栏", "CSDN", "返回首页"}
    filtered = [item for item in candidates if item not in blacklist]
    return filtered[-1] if filtered else "技术"


def strip_nodes(content_node) -> None:
    selectors = [
        ".hljs-button",
        ".toolbar-box",
        ".recommend-box",
        ".recommend-item-box",
        ".blog-extension-box",
        ".copyright-box",
        ".article-copyright",
        ".hide-article-box",
        "script",
        "style",
    ]
    for selector in selectors:
        for node in content_node.select(selector):
            node.decompose()


def sanitize_file_name(name: str) -> str:
    value = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "-", name).strip("-")
    return value or "image.png"


def build_image_name(source_url: str, index: int, used_names: set[str]) -> str:
    parsed = urlparse(source_url)
    base = Path(parsed.path).name or f"image-{index}.png"
    base = sanitize_file_name(base)
    if "." not in base:
        base = f"{Path(base).stem}.png"

    name = base
    counter = 1
    while name in used_names:
        suffix = Path(base).suffix
        stem = Path(base).stem
        name = f"{stem}-{counter}{suffix}"
        counter += 1
    used_names.add(name)
    return name


def ensure_image_suffix(file_name: str, content_type: str | None) -> str:
    if Path(file_name).suffix:
        return file_name
    suffix = mimetypes.guess_extension((content_type or "").split(";")[0].strip()) or ".png"
    return f"{file_name}{suffix}"


def rewrite_images(session, content_node, assets_dir: Path, article_id: str, *, pause: float) -> None:
    article_dir = assets_dir / article_id
    article_dir.mkdir(parents=True, exist_ok=True)
    used_names: set[str] = set()

    for index, image in enumerate(content_node.select("img"), start=1):
        source_url = None
        for key in ("data-src", "data-original", "src"):
            value = image.get(key)
            if value:
                source_url = value.strip()
                break
        if not source_url or source_url.startswith("data:"):
            continue

        source_url = urljoin("https://blog.csdn.net", source_url)
        file_name = build_image_name(source_url, index, used_names)
        file_path = article_dir / file_name

        if not file_path.exists():
            try:
                content, content_type = request_binary(session, source_url, pause=pause)
                file_name = ensure_image_suffix(file_name, content_type)
                file_path = article_dir / file_name
                file_path.write_bytes(content)
            except Exception:
                continue

        relative = file_path.relative_to(assets_dir.parent.parent).as_posix()
        image["src"] = f"/{relative}"
        for attr in ("data-src", "data-original", "srcset", "style"):
            image.attrs.pop(attr, None)


def normalize_markdown(text: str, *, title: str | None = None) -> str:
    value = text.replace("\r\n", "\n")
    value = value.replace("\ufeff", "").replace("\u200b", "").replace("\xa0", " ")
    value = value.replace("![这里写图片描述]", "![]")
    value = re.sub(r"(?m)^\s*@\([^\n]*\)[^\n]*\n?", "", value)
    value = re.sub(r"(?m)^#### 目录\s*\n+(?:[ \t]*[-*][^\n]*\n)+", "", value)
    value = re.sub(r"(?m)^[ \t]+$", "", value)

    # Fix markdownify's incorrect escaping in code blocks and CSDN's double spacing
    def fix_code_block(match):
        code = match.group(0)
        code = code.replace(r"\*", "*").replace(r"\_", "_").replace(r"\[", "[").replace(r"\]", "]")
        lines = code.split("\n")
        empty_count = sum(1 for line in lines if line.strip() == "")
        if len(lines) > 6 and empty_count >= (len(lines) - 2) / 2:
            new_lines = []
            for i, line in enumerate(lines):
                if line.strip() == "" and i > 0 and i < len(lines) - 1:
                    if lines[i-1].strip() != "":
                        continue
                new_lines.append(line)
            code = "\n".join(new_lines)
        return code

    value = re.sub(r"```.*?```", fix_code_block, value, flags=re.DOTALL)

    if title:
        escaped_title = re.escape(title.strip())
        value = re.sub(rf"(?ms)^\s*#+\s*{escaped_title}\s*\n+", "", value, count=1)

    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip() + "\n"


def fetch_article_detail(session, *, article: ArticleRef, assets_dir: Path, pause: float, download_images: bool) -> dict:
    html = request_text(session, article.url, pause=pause)
    soup = BeautifulSoup(html, "html.parser")

    content_node = select_first(
        soup,
        ["#content_views", ".blog-content-box", ".htmledit_views", ".article_content"],
    )
    if content_node is None:
        raise RuntimeError(f"未找到正文容器：{article.url}")

    strip_nodes(content_node)

    title = (
        get_meta_content(soup, "meta[property='og:title']")
        or get_meta_content(soup, "meta[name='title']")
        or extract_title_from_page(soup)
        or article.title
    )
    published_at = (
        get_meta_content(soup, "meta[property='article:published_time']")
        or extract_date_from_page(soup)
        or article.list_date
        or datetime.now().strftime("%Y-%m-%d 00:00:00 +0800")
    )
    updated_at = (
        get_meta_content(soup, "meta[property='article:modified_time']")
        or extract_date_from_page(soup, updated=True)
        or published_at
    )
    tags = extract_texts(soup, [".tags-box a", ".article-tag-box a", ".blog-tags-box a"])
    categories = extract_texts(soup, [".breadcrumb-box a", ".article-categories-box a"])
    category = pick_category(categories)

    if download_images:
        rewrite_images(session, content_node, assets_dir, article.article_id, pause=pause)

    markdown_body = html_to_markdown(str(content_node), heading_style="ATX", bullets="-")
    markdown_body = normalize_markdown(markdown_body, title=title.strip())
    source_hash = hashlib.sha256(markdown_body.encode("utf-8")).hexdigest()

    return {
        "article_id": article.article_id,
        "title": title.strip(),
        "url": article.url,
        "published_at": normalize_datetime(published_at) or published_at,
        "updated_at": normalize_datetime(updated_at) or updated_at,
        "tags": tags,
        "category": category,
        "body": markdown_body,
        "source_hash": source_hash,
    }


def scan_existing_posts(posts_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in posts_dir.glob("*.md"):
        try:
            front_matter = path.read_text(encoding="utf-8").split("---", 2)
        except UnicodeDecodeError:
            continue
        if len(front_matter) < 3:
            continue
        match = re.search(r"(?m)^csdn_id:\s*\"?(?P<id>\d+)\"?\s*$", front_matter[1])
        if match:
            index[match.group("id")] = path
    return index


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^0-9a-z\u4e00-\u9fff-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "post"


def resolve_target_path(posts_dir: Path, detail: dict, existing_path: Path | None) -> Path:
    date_prefix = (detail["published_at"] or datetime.now().strftime("%Y-%m-%d"))[:10]
    slug = slugify(detail["title"])
    return posts_dir / f"{date_prefix}-{slug}.md"

def escape_yaml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def escape_yaml_inline(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    if re.search(r"[\s,:#\[\]\{\}]", escaped):
        return f'"{escaped}"'
    return escaped


def build_post_content(detail: dict) -> str:
    tags = ", ".join(escape_yaml_inline(tag) for tag in detail["tags"])
    return "\n".join(
        [
            "---",
            "layout: post",
            f'title: "{escape_yaml_string(detail["title"])}"',
            f'date: {detail["published_at"]}',
            f'last_modified_at: "{detail["updated_at"]}"',
            f'categories: [{escape_yaml_inline(detail["category"])}]',
            f'tags: [{tags}]',
            'source: "csdn"',
            f'csdn_id: "{detail["article_id"]}"',
            f'source_url: "{detail["url"]}"',
            "---",
            "",
            detail["body"].rstrip(),
            "",
        ]
    )


def sync_articles(
    manifest_path: Path,
    repo_root: Path,
    state_path: Path,
    *,
    timeout: int,
    pause: float,
    limit: int | None,
    download_images: bool,
    overwrite: bool,
    cookie_text: str | None = None,
) -> None:
    session = build_session(timeout, cookie_text=cookie_text)
    manifest = load_json(manifest_path, [])
    if not manifest:
        raise SystemExit(f"未找到可同步文章，请先生成 manifest：{manifest_path}")

    if limit is not None:
        manifest = manifest[:limit]

    posts_dir = repo_root / '_posts'
    assets_dir = repo_root / 'assets' / 'images' / 'csdn'
    posts_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    state = load_json(state_path, {})
    existing_index = scan_existing_posts(posts_dir)
    failures_path = state_path.with_name('csdn-sync-failures.json')
    failures = []

    created = 0
    updated = 0
    skipped = 0

    for item in manifest:
        article_id = str(item['article_id'])
        try:
            detail = fetch_article_detail(
                session,
                article=ArticleRef(
                    article_id=article_id,
                    title=item.get('title', '').strip(),
                    url=item['url'],
                    list_date=item.get('list_date'),
                ),
                assets_dir=assets_dir,
                pause=pause,
                download_images=download_images,
            )
        except Exception as exc:
            failures.append({
                'article_id': article_id,
                'url': item['url'],
                'error': str(exc),
            })
            dump_json(failures_path, failures)
            print(f"[sync] 失败：{article_id} -> {exc}")
            continue

        state_key = detail['article_id']
        source_hash = detail['source_hash']
        previous = state.get(state_key)
        existing_path = existing_index.get(state_key)
        target_path = resolve_target_path(posts_dir, detail, existing_path)

        if (
            not overwrite
            and previous
            and previous.get('source_hash') == source_hash
            and target_path.exists()
        ):
            skipped += 1
            print(f"[sync] 跳过未变更文章：{detail['title']}")
            continue

        target_path.write_text(build_post_content(detail), encoding='utf-8')
        if existing_path and existing_path != target_path and existing_path.exists():
            existing_path.unlink()

        state[state_key] = {
            'title': detail['title'],
            'url': detail['url'],
            'target': str(target_path.relative_to(repo_root)).replace('\\', '/'),
            'source_hash': source_hash,
            'synced_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        existing_index[state_key] = target_path
        dump_json(state_path, state)

        if previous:
            updated += 1
            print(f"[sync] 已更新：{target_path.name}")
        else:
            created += 1
            print(f"[sync] 已新增：{target_path.name}")

    if failures:
        print(f"[sync] 存在 {len(failures)} 篇失败，已记录到 {failures_path}")
    print(f"[sync] 完成。新增 {created}，更新 {updated}，跳过 {skipped}")

def main() -> None:
    args = parse_args()
    cookie_text = resolve_cookie_text(args.cookie, args.cookie_file, args.cookie_env)

    if args.command == "discover":
        discover_articles(
            blog_url=args.blog_url,
            manifest_path=Path(args.manifest),
            max_pages=args.max_pages,
            pause=args.pause,
            timeout=args.timeout,
            cookie_text=cookie_text,
        )
        return

    if args.command == "sync":
        sync_articles(
            manifest_path=Path(args.manifest),
            repo_root=Path(args.repo_root).resolve(),
            state_path=Path(args.state),
            timeout=args.timeout,
            pause=args.pause,
            limit=args.limit,
            download_images=not args.no_images,
            overwrite=args.overwrite,
            cookie_text=cookie_text,
        )
        return

    manifest_path = Path(args.manifest)
    discover_articles(
        blog_url=args.blog_url,
        manifest_path=manifest_path,
        max_pages=args.max_pages,
        pause=args.pause,
        timeout=args.timeout,
        cookie_text=cookie_text,
    )
    sync_articles(
        manifest_path=manifest_path,
        repo_root=Path(args.repo_root).resolve(),
        state_path=Path(args.state),
        timeout=args.timeout,
        pause=args.pause,
        limit=args.limit,
        download_images=not args.no_images,
        overwrite=args.overwrite,
        cookie_text=cookie_text,
    )

if __name__ == '__main__':
    main()















