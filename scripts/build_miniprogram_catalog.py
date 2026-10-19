#!/usr/bin/env python3
"""Build the WeChat mini program catalog and copy list from README.md."""

import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
OUT = ROOT / "miniprogram"
DATA = OUT / "data"
ASSETS = OUT / "assets"

LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ITEM = re.compile(r"^(\s*)\*\s+(.*)$")
HEADING = re.compile(r"^###\s+(.+?)\s*$")

DISPLAY_NAMES = {
    "Video": "视频",
}

# Scene groups follow the README order inside each group.
GROUPS = [
    ("foundation", "工程基础", "版本、依赖、打包和构建", [
        "环境管理", "包管理", "包仓库", "分发", "构建工具", "配置",
        "兼容性", "重构", "高性能", "微软的 Windows 平台",
    ]),
    ("web", "网站与接口", "Web 框架、API、内容和站点", [
        "Web 框架", "RESTful API", "WebSocket", "模板引擎", "CMS",
        "电子商务", "静态站点生成器", "Serverless 框架", "GraphQL",
        "企业级应用集成", "权限", "验证",
    ]),
    ("data", "数据与存储", "数据库、缓存、校验和序列化", [
        "数据库", "数据库驱动", "ORM", "缓存", "搜索", "序列化",
        "数据验证", "表单",
    ]),
    ("text", "文本与语言", "文本、文档、网页和自然语言", [
        "文本处理", "特殊文本格式处理", "自然语言处理", "文档",
        "HTML 处理", "网页内容提取", "URL 处理", "国际化",
    ]),
    ("science", "科学与智能", "计算、可视化、学习和视觉", [
        "科学计算和数据分析", "数据可视化", "机器学习", "深度学习",
        "计算机视觉", "推荐系统", "OCR",
    ]),
    ("network", "网络与系统", "协议、并发、服务器和硬件", [
        "HTTP", "网络", "并发和并行", "进程", "分布式计算",
        "WSGI 服务器", "ASGI 服务器", "RPC 服务器", "地理位置",
        "网络可视化和 SDN", "硬件", "密码学", "外来函数接口",
    ]),
    ("workflow", "效率工具", "命令行、测试、调试和编辑器", [
        "交互式解析器", "命令行工具", "下载器", "测试", "调试工具",
        "代码分析和 Lint 工具", "日志", "任务调度", "DevOps 工具",
        "编辑器插件和 IDE", "算法和设计模式", "函数式编程", "文件", "日期和时间",
    ]),
    ("media", "界面与媒体", "图像、声音、界面和消息", [
        "图像处理", "音频", "Video", "图形用户界面", "游戏开发",
        "电子邮件", "队列", "管理面板", "动态消息", "Web 资源管理",
        "反垃圾技术", "标记", "第三方 API", "机器人", "聊天工具",
        "内置类的增强版实现", "渗透测试", "杂项",
    ]),
]

HOT = [
    "Web 框架",
    "机器学习",
    "数据可视化",
    "自然语言处理",
    "命令行工具",
    "测试",
    "数据库",
    "图像处理",
]

# Fixed interface copy. Resource blurbs stay verbatim from README.md.
COPY = [
    ("appName", "品牌", "小程序名称", "Python 资源库"),
    ("slogan", "首页", "主标题", "人生苦短，我用 Python"),
    ("tagline", "首页", "副标题", "按场景查找库、框架和工具"),
    ("sourceNote", "首页", "页脚", "简介沿用《Python 资源大全中文版》原文"),
    ("searchEntry", "首页", "搜索入口", "搜索库名或关键词"),
    ("hotTitle", "首页", "推荐区标题", "常用分类"),
    ("groupTitle", "首页", "分组区标题", "按场景浏览"),
    ("statsLine", "首页", "统计", "共 {categories} 个分类，{items} 条资源"),
    ("categoryCount", "首页", "分类数量", "{count} 条"),
    ("catalogTitle", "分类", "页面标题", "全部分类"),
    ("catalogLead", "分类", "页首说明", "点开分类，查看里面的库和一句简介"),
    ("categoryNav", "分类详情", "默认标题", "分类"),
    ("filterAll", "分类详情", "筛选", "全部"),
    ("emptyCategory", "分类详情", "空列表", "这个分类还没有条目"),
    ("itemCount", "分类详情", "数量", "{count} 条资源"),
    ("searchTitle", "搜索", "页面标题", "搜索"),
    ("searchPlaceholder", "搜索", "输入框", "输入名称，或简介里的词"),
    ("searchIdle", "搜索", "未输入", "可以试这些词：Django、爬虫、可视化、测试"),
    ("searchEmpty", "搜索", "无结果", "没有找到相关资源，换个关键词试试"),
    ("searchHit", "搜索", "结果数量", "找到 {count} 条"),
    ("searchLimitNote", "搜索", "结果过多", "先显示前 {count} 条，可以把词写得更具体"),
    ("searchClear", "搜索", "清空", "清空"),
    ("detailNav", "详情", "默认标题", "资源详情"),
    ("detailIntro", "详情", "简介标题", "它做什么"),
    ("detailCategory", "详情", "分类标签", "所属分类"),
    ("detailSection", "详情", "细分标签", "细分"),
    ("detailLink", "详情", "链接标题", "项目链接"),
    ("copyLink", "详情", "按钮", "复制链接"),
    ("copyDesc", "详情", "按钮", "复制简介"),
    ("copied", "详情", "复制链接后的提示", "链接已复制，可到浏览器打开"),
    ("copiedDesc", "详情", "复制简介后的提示", "简介已复制"),
    ("noLink", "详情", "无链接", "这条暂时没有外链，只能看简介"),
    ("openHint", "详情", "链接说明", "小程序内不打开外站。复制链接后，用手机浏览器访问"),
    ("relatedTitle", "详情", "相关列表", "同分类的其他资源"),
    ("aboutTitle", "关于", "页面标题", "关于"),
    ("aboutHeadline", "关于", "主标题", "一份给开发者的 Python 资源清单"),
    ("aboutP1", "关于", "正文", "这里按场景收录 Web、数据、文本、机器学习、工具链等方向的 Python 库。每条保留原文里的那一句中文说明。"),
    ("aboutP2", "关于", "正文", "清单由「开源前哨」和「Python开发者」维护，对应开源项目 awesome-python-cn。"),
    ("aboutP3", "关于", "正文", "本小程序只做检索和阅读。项目主页需要复制链接，再在浏览器中打开。"),
    ("aboutPrivacy", "关于", "隐私说明", "不收集账号，搜索词也不会上传。"),
    ("aboutCredit", "关于", "署名", "维护：开源前哨 · Python开发者"),
    ("aboutRepo", "关于", "仓库", "仓库：awesome-python-cn"),
    ("shareHome", "分享", "首页", "Python 资源库：按场景找库和工具"),
    ("shareCategory", "分享", "分类", "{name} · Python 资源库"),
    ("shareDetail", "分享", "详情", "{name}：{desc}"),
    ("tabHome", "导航", "底部标签", "首页"),
    ("tabCatalog", "导航", "底部标签", "分类"),
    ("tabAbout", "导航", "底部标签", "关于"),
    ("loadFail", "反馈", "找不到页面数据", "这条内容不存在，返回上一页再试"),
    ("summaryFallback", "反馈", "分类缺少简介时", "这个分类下的 Python 资源"),
]


def plain(text):
    text = LINK.sub(lambda found: found.group(1), text)
    return re.sub(r"\s+", " ", text).strip()


def parse_item(text):
    links = list(LINK.finditer(text))
    if not links:
        if "：" in text:
            name, desc = text.split("：", 1)
            return {"name": name.strip(), "url": "", "desc": desc.strip(), "link_text": ""}
        return None
    match = links[0]
    before = text[: match.start()].strip(" ：:\t")
    after = LINK.sub(lambda found: found.group(1), text[match.end() :]).strip()
    after = after.lstrip("：:").strip()
    link_text = match.group(1).strip()
    name = before or link_text
    desc = after
    if before and link_text and link_text not in desc:
        desc = (link_text + " " + desc).strip()
    return {
        "name": name.strip(),
        "url": match.group(2).strip(),
        "desc": desc.strip(),
        "link_text": link_text,
    }


def parse_readme(text):
    lines = text.splitlines()
    start = 0
    for index, line in enumerate(lines):
        if line.strip() == "## 资源列表":
            start = index + 1
            break
    categories = []
    current = None
    pending_section = ""
    group_stack = [(-1, "")]

    def close_category():
        nonlocal current
        current = None

    for raw in lines[start:]:
        line = raw.rstrip()
        if line.startswith("## "):
            break
        heading = HEADING.match(line)
        if heading:
            current = {
                "source_name": heading.group(1).strip(),
                "summary": "",
                "items": [],
            }
            categories.append(current)
            pending_section = ""
            group_stack = [(-1, "")]
            continue
        if current is None:
            continue
        matched = ITEM.match(line)
        if not matched:
            prose = line.strip()
            if not prose:
                continue
            if current["items"]:
                pending_section = prose
                group_stack = [(-1, "")]
            elif current["summary"]:
                current["summary"] = (current["summary"] + " " + prose).strip()
            else:
                current["summary"] = prose
            continue
        indent = len(matched.group(1).replace("\t", "    "))
        parsed = parse_item(matched.group(2).strip())
        while group_stack and indent <= group_stack[-1][0]:
            group_stack.pop()
        if not group_stack:
            group_stack = [(-1, "")]
        if parsed is None:
            group_stack.append((indent, matched.group(2).strip()))
            continue
        section = group_stack[-1][1] or pending_section
        parent = None
        for previous in current["items"][::-1]:
            if previous["indent"] < indent:
                parent = previous
                break
        desc = parsed["desc"]
        if not desc and parent:
            desc = parent["name"] + " 相关系列"
        elif desc in {"系列", "系列。"}:
            desc = (parent["name"] + " 相关系列") if parent else "相关系列"
        elif not desc:
            desc = "见项目主页"
        current["items"].append({
            "indent": indent,
            "name": parsed["name"],
            "url": parsed["url"],
            "desc": plain(desc),
            "section": plain(section),
        })
    close_category()
    return categories


def merge_categories(categories):
    order = []
    by_name = {}
    for category in categories:
        name = category["source_name"]
        if name in by_name:
            existing = by_name[name]
            if not existing["summary"]:
                existing["summary"] = category["summary"]
            existing["items"].extend(category["items"])
            continue
        by_name[name] = category
        order.append(category)
    for category in order:
        index = {}
        unique = []
        for item in category["items"]:
            key = (item["name"], item["url"])
            if key in index:
                previous = unique[index[key]]
                if len(item["desc"]) > len(previous["desc"]):
                    unique[index[key]] = item
                continue
            index[key] = len(unique)
            unique.append(item)
        category["items"] = unique
    return order


def build_catalog(categories):
    group_meta = {item[0]: {"id": item[0], "name": item[1], "desc": item[2], "categoryIds": []} for item in GROUPS}
    group_of = {}
    for group_id, _name, _desc, members in GROUPS:
        for member in members:
            if member in group_of:
                raise SystemExit("分类重复分组: " + member)
            group_of[member] = group_id
    built = []
    missing_group = []
    for index, category in enumerate(categories):
        source_name = category["source_name"]
        group_id = group_of.get(source_name)
        if not group_id:
            missing_group.append(source_name)
            continue
        cat_id = "c%d" % index
        items = []
        for item_index, item in enumerate(category["items"]):
            items.append({
                "id": "%s-i%d" % (cat_id, item_index),
                "name": item["name"],
                "url": item["url"],
                "desc": item["desc"],
                "section": item["section"],
            })
        built.append({
            "id": cat_id,
            "name": DISPLAY_NAMES.get(source_name, source_name),
            "sourceName": source_name,
            "summary": plain(category["summary"]),
            "items": items,
        })
        group_meta[group_id]["categoryIds"].append(cat_id)
    if missing_group:
        raise SystemExit("这些分类还没有分到场景里: " + "、".join(missing_group))
    present = {category["sourceName"] for category in built}
    unknown_members = []
    for _group_id, _name, _desc, members in GROUPS:
        for member in members:
            if member not in present:
                unknown_members.append(member)
    if unknown_members:
        raise SystemExit("分组里有 README 不存在的分类: " + "、".join(unknown_members))
    name_to_id = {category["sourceName"]: category["id"] for category in built}
    hot_ids = []
    for name in HOT:
        if name not in name_to_id:
            raise SystemExit("常用分类不存在: " + name)
        hot_ids.append(name_to_id[name])
    item_total = sum(len(category["items"]) for category in built)
    return {
        "stats": {"categories": len(built), "items": item_total},
        "hotIds": hot_ids,
        "groups": list(group_meta.values()),
        "categories": built,
    }


def write_js(path, payload):
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    text = text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    path.write_text("module.exports = " + text + "\n", encoding="utf-8")


def write_copy():
    payload = {key: value for key, _page, _where, value in COPY}
    write_js(OUT / "copy.js", payload)


def markdown_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_copy_markdown(catalog):
    by_page = []
    current = None
    for key, page, where, text in COPY:
        if current != page:
            current = page
            by_page.append((page, []))
        by_page[-1][1].append((where, text, key))
    lines = [
        "# Python 资源库 · 微信小程序文案",
        "",
        "小程序名称是「Python 资源库」。下面列出界面里的固定文案。分类简介和每条资源的说明直接使用 README 原文，生成时不改写。",
        "",
        "用微信开发者工具导入仓库根目录（已配置 `miniprogramRoot`），或直接导入 `miniprogram` 目录。没有 AppID 时选择测试号。",
        "",
        "目录更新命令：`python3 scripts/build_miniprogram_catalog.py`",
        "",
        "## 固定文案",
        "",
    ]
    for page, rows in by_page:
        lines.append("### " + page)
        lines.append("")
        lines.append("| 出现位置 | 文案 |")
        lines.append("| --- | --- |")
        for where, text, _key in rows:
            lines.append("| %s | %s |" % (markdown_cell(where), markdown_cell(text)))
        lines.append("")
    lines.append("## 场景分组")
    lines.append("")
    lines.append("| 分组 | 分组说明 | 分类 |")
    lines.append("| --- | --- | --- |")
    by_id = {category["id"]: category for category in catalog["categories"]}
    for group in catalog["groups"]:
        names = "、".join(by_id[cat_id]["name"] for cat_id in group["categoryIds"])
        lines.append("| %s | %s | %s |" % (markdown_cell(group["name"]), markdown_cell(group["desc"]), markdown_cell(names)))
    lines.append("")
    lines.append("## 分类简介")
    lines.append("")
    lines.append("这些句子来自 README 各分类标题下的原文。")
    lines.append("")
    lines.append("| 分类 | 条目 | 简介 |")
    lines.append("| --- | --- | --- |")
    for category in catalog["categories"]:
        lines.append("| %s | %d | %s |" % (
            markdown_cell(category["name"]),
            len(category["items"]),
            markdown_cell(category["summary"]),
        ))
    lines.append("")
    (OUT / "文案清单.md").write_text("\n".join(lines), encoding="utf-8")


def blank(size):
    return [bytearray(size * 4) for _ in range(size)]


def paint(rows, x, y, color):
    size = len(rows)
    if x < 0 or y < 0 or x >= size or y >= size:
        return
    start = x * 4
    rows[y][start : start + 4] = bytes(color)


def write_png(path, rows):
    height = len(rows)
    width = len(rows[0]) // 4

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def icon_home(color):
    rows = blank(81)
    for y in range(16, 40):
        span = int((y - 16) * 22 / 23)
        for x in range(40 - span, 41 + span):
            paint(rows, x, y, color)
    for y in range(38, 66):
        for x in range(22, 59):
            paint(rows, x, y, color)
    for y in range(50, 66):
        for x in range(35, 46):
            paint(rows, x, y, (0, 0, 0, 0))
    return rows


def icon_catalog(color):
    rows = blank(81)
    for top in (22, 36, 50):
        for y in range(top, top + 8):
            for x in range(18, 64):
                paint(rows, x, y, color)
    return rows


def icon_about(color):
    rows = blank(81)
    for y in range(81):
        for x in range(81):
            distance = (x - 40) ** 2 + (y - 40) ** 2
            if 24 ** 2 <= distance <= 30 ** 2:
                paint(rows, x, y, color)
    for y in range(24, 32):
        for x in range(36, 45):
            if (x - 40) ** 2 + (y - 28) ** 2 <= 16:
                paint(rows, x, y, color)
    for y in range(36, 58):
        for x in range(36, 45):
            paint(rows, x, y, color)
    return rows


def write_icons():
    ASSETS.mkdir(parents=True, exist_ok=True)
    gray = (152, 162, 179, 255)
    active = (22, 50, 79, 255)
    write_png(ASSETS / "tab-home.png", icon_home(gray))
    write_png(ASSETS / "tab-home-active.png", icon_home(active))
    write_png(ASSETS / "tab-catalog.png", icon_catalog(gray))
    write_png(ASSETS / "tab-catalog-active.png", icon_catalog(active))
    write_png(ASSETS / "tab-about.png", icon_about(gray))
    write_png(ASSETS / "tab-about-active.png", icon_about(active))


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    categories = merge_categories(parse_readme(README.read_text(encoding="utf-8")))
    catalog = build_catalog(categories)
    write_js(DATA / "catalog.js", catalog)
    write_copy()
    write_copy_markdown(catalog)
    write_icons()
    print("categories", catalog["stats"]["categories"])
    print("items", catalog["stats"]["items"])
    for category in catalog["categories"]:
        print("%3d  %s" % (len(category["items"]), category["name"]))


if __name__ == "__main__":
    main()
