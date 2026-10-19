#!/usr/bin/env python3
"""Check the mini program catalog, copy list, and page structure."""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MINI = ROOT / "miniprogram"

spec = importlib.util.spec_from_file_location("build", ROOT / "scripts" / "build_miniprogram_catalog.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def load_js_module(path):
    text = path.read_text(encoding="utf-8")
    prefix = "module.exports = "
    if not text.startswith(prefix):
        raise AssertionError(path.name + " is not a module.exports JSON module")
    return json.loads(text[len(prefix):])


def check_balanced(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    tokens = re.findall(r"<(/?)([A-Za-z][\w-]*)([^>]*)>", text)
    stack = []
    for closing, name, attrs in tokens:
        name = name.lower()
        if closing:
            if not stack or stack[-1] != name:
                raise AssertionError("%s has a mismatched </%s>" % (path, name))
            stack.pop()
            continue
        if attrs.rstrip().endswith("/"):
            continue
        stack.append(name)
    if stack:
        raise AssertionError("%s has unclosed tags: %s" % (path, ", ".join(stack)))


def main():
    fresh = build.build_catalog(build.merge_categories(build.parse_readme(build.README.read_text(encoding="utf-8"))))
    disk = load_js_module(MINI / "data" / "catalog.js")
    if disk != fresh:
        raise AssertionError("catalog.js is stale. Run python3 scripts/build_miniprogram_catalog.py")

    copy = load_js_module(MINI / "copy.js")
    expected_copy = {key: text for key, _page, _where, text in build.COPY}
    if copy != expected_copy:
        raise AssertionError("copy.js does not match the copy source")

    listing = (MINI / "文案清单.md").read_text(encoding="utf-8")
    for text in expected_copy.values():
        if text not in listing:
            raise AssertionError("文案清单缺少: " + text)
    for category in disk["categories"]:
        if category["summary"] and category["summary"] not in listing:
            raise AssertionError("文案清单缺少分类简介: " + category["name"])
        if "](" in category["summary"] or "[" in category["summary"]:
            raise AssertionError("分类简介仍有 Markdown: " + category["name"])
        if not category["items"]:
            raise AssertionError("空分类: " + category["name"])
        for item in category["items"]:
            if not item["name"] or not item["desc"]:
                raise AssertionError("条目缺少名称或简介: " + category["name"])

    ids = []
    for category in disk["categories"]:
        ids.append(category["id"])
        ids.extend(item["id"] for item in category["items"])
    if len(ids) != len(set(ids)):
        raise AssertionError("存在重复 id")

    grouped = []
    for group in disk["groups"]:
        grouped.extend(group["categoryIds"])
    if sorted(grouped) != sorted(category["id"] for category in disk["categories"]):
        raise AssertionError("分类没有刚好落入一个场景")

    by_source = {category["sourceName"]: category for category in disk["categories"]}
    if by_source["Video"]["name"] != "视频":
        raise AssertionError("Video 应显示为视频")
    html = by_source["HTML 处理"]
    scrapy = [item for item in html["items"] if item["name"] == "Scrapy"]
    if not scrapy or scrapy[0]["section"] != "爬取网络站点的库":
        raise AssertionError("Scrapy 应归在爬取网络站点的库")
    for source_name in ("环境管理", "Web 框架", "机器学习"):
        if source_name not in by_source:
            raise AssertionError("缺少分类 " + source_name)

    app = json.loads((MINI / "app.json").read_text(encoding="utf-8"))
    tab_text = [item["text"] for item in app["tabBar"]["list"]]
    if tab_text != [copy["tabHome"], copy["tabCatalog"], copy["tabAbout"]]:
        raise AssertionError("底部标签和文案不一致")
    if app["window"]["navigationBarTitleText"] != copy["appName"]:
        raise AssertionError("导航标题和文案不一致")

    page_titles = {
        "pages/home/home.json": "appName",
        "pages/catalog/catalog.json": "catalogTitle",
        "pages/about/about.json": "aboutTitle",
        "pages/search/search.json": "searchTitle",
        "pages/detail/detail.json": "detailNav",
        "pages/category/category.json": "categoryNav",
    }
    for relative, key in page_titles.items():
        page = json.loads((MINI / relative).read_text(encoding="utf-8"))
        if page["navigationBarTitleText"] != copy[key]:
            raise AssertionError("%s 标题不是 %s" % (relative, copy[key]))
        stem = relative[:-5]
        for suffix in (".js", ".wxml", ".wxss"):
            if not (MINI / (stem + suffix)).exists():
                raise AssertionError("缺少页面文件 " + stem + suffix)

    used = set()
    for path in MINI.rglob("*"):
        if path.suffix not in {".js", ".wxml", ".wxss"}:
            continue
        if path.name == "copy.js" or "data" in path.parts:
            continue
        source = path.read_text(encoding="utf-8").replace("copy.js", "")
        used.update(re.findall(r"copy\.([A-Za-z][A-Za-z0-9_]*)", source))
    missing = sorted(set(copy) - used)
    unknown = sorted(used - set(copy))
    if missing or unknown:
        raise AssertionError("文案键不匹配 missing=%s unknown=%s" % (missing, unknown))

    for path in MINI.rglob("*.wxml"):
        check_balanced(path)
    for path in MINI.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    root_config = json.loads((ROOT / "project.config.json").read_text(encoding="utf-8"))
    if root_config.get("miniprogramRoot") != "miniprogram/":
        raise AssertionError("仓库根目录的小程序根路径不正确")

    for name in (
        "tab-home.png",
        "tab-home-active.png",
        "tab-catalog.png",
        "tab-catalog-active.png",
        "tab-about.png",
        "tab-about-active.png",
    ):
        header = (MINI / "assets" / name).read_bytes()[:8]
        if header != b"\x89PNG\r\n\x1a\n":
            raise AssertionError("图标不是 PNG: " + name)

    for path in MINI.rglob("*.js"):
        completed = subprocess.run(["node", "--check", str(path)], cwd=ROOT, check=False)
        if completed.returncode != 0:
            raise AssertionError("JavaScript 语法检查失败: " + str(path))
    node = r"""
const store = require('./miniprogram/utils/store.js')
const copy = require('./miniprogram/copy.js')
function assert(ok, message) { if (!ok) { console.error(message); process.exit(1) } }
const view = store.homeView()
const categoryCount = view.groups.reduce((sum, group) => sum + group.categories.length, 0)
assert(view.hot.length === 8, 'hot')
assert(view.statsText.indexOf(String(categoryCount)) > 0, 'category count shown')
assert(view.statsText.indexOf('个分类') > 0, 'stats text')
const scrapy = store.search('爬虫').find(item => item.name === 'Scrapy')
assert(scrapy && scrapy.section === '爬取网络站点的库', 'scrapy search')
const django = store.search('Django').find(item => item.name === 'Django')
assert(django && django.categoryName === 'Web 框架', 'django')
assert(store.relatedItems(django).every(item => item.id !== django.id), 'related excludes self')
assert(store.relatedItems(django).length > 0, 'related')
assert(store.search('不可能存在的关键词zzz').length === 0, 'empty search')
const pyenv = store.search('pyenv').find(item => item.name === 'pyenv')
assert(pyenv && pyenv.categoryName === '环境管理', 'pyenv')
assert(store.search('Video').some(item => item.categoryName === '视频'), 'video alias')
const category = store.getCategory(django.categoryId)
assert(store.sectionsOf(category).indexOf('全部') === -1, 'all is not a stored section')
assert(store.filterItems(category, '').length === category.items.length, 'filter all')
const filled = store.fill(copy.searchHit, { count: 3 })
assert(filled === '找到 3 条', filled)
console.log(JSON.stringify({
  categories: categoryCount,
  statsText: view.statsText,
  scrapy: scrapy.desc,
  django: django.desc,
  searchCrawl: store.search('爬虫').length
}))
"""
    completed = subprocess.run(["node", "-e", node], cwd=ROOT, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise AssertionError("目录检索检查失败")
    print(completed.stdout.strip())
    print("ok", disk["stats"]["categories"], "categories", disk["stats"]["items"], "items", len(copy), "copy strings")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print("FAIL", error)
        sys.exit(1)
