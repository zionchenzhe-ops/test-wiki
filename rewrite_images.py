"""把 wiki 中所有图片引用重写为 jsDelivr CDN 绝对 URL（中文/非 ASCII 字符做百分号编码）。
- <img src="相对路径">  ->  <img src="https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/绝对路径">
- ![alt](相对路径)     ->  ![alt](同一 jsDelivr URL)
视频(<video>/<source>)和下载链接(<a href>)不动。"""
import os, re, glob
from urllib.parse import quote

ROOT = r"C:\Users\25391\Desktop\J30V2wiki\J30V2wiki"
BASE = "https://cdn.jsdelivr.net/gh/zionchenzhe-ops/test-wiki@main/J30V2wiki/"

def resolve(md_file, rel):
    if rel.startswith(("http", "/")):
        return None
    return os.path.normpath(os.path.join(os.path.dirname(md_file), rel))

def to_url(abs_path):
    rel = os.path.relpath(abs_path, ROOT).replace("\\", "/")
    return BASE + quote(rel, safe="/-._~")

count = [0]
for md in sorted(glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)):
    with open(md, encoding="utf-8") as f:
        content = f.read()
    orig = content

    # 1. <img src="...">
    def repl_img(m):
        r = resolve(md, m.group(1))
        if r and os.path.isfile(r):
            count[0] += 1
            return m.group(0).replace(m.group(1), to_url(r))
        return m.group(0)
    content = re.sub(r'src="([^"]*\.(?:png|jpe?g|gif))"', repl_img, content, flags=re.I)

    # 2. ![alt](...)
    def repl_md(m):
        r = resolve(md, m.group(2))
        if r and os.path.isfile(r):
            count[0] += 1
            return f"![{m.group(1)}]({to_url(r)})"
        return m.group(0)
    content = re.sub(r'!\[([^\]]*)\]\(([^)]*\.(?:png|jpe?g|gif))\)', repl_md, content, flags=re.I)

    if content != orig:
        with open(md, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"已改写: {os.path.relpath(md, ROOT)}")

print(f"\n共重写 {count[0]} 处图片引用")
