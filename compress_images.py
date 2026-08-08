"""压缩 wiki 中被引用的 >1MB 图片（保持文件名、尺寸、格式不变）。
自动从所有 .md 中提取图片引用并解析为磁盘路径。"""
import os, re, glob
from PIL import Image

ROOT = r"C:\Users\25391\Desktop\J30V2wiki\J30V2wiki"
THRESHOLD = 1 * 1024 * 1024  # 1MB

def resolve(md_file, rel):
    """把 md 文件里的相对引用解析为磁盘绝对路径"""
    if rel.startswith(("http", "/")):
        return None
    return os.path.normpath(os.path.join(os.path.dirname(md_file), rel))

paths = set()
for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    with open(md, encoding="utf-8") as f:
        content = f.read()
    # <img src="..."> 与 ![alt](...)
    for m in re.finditer(r'src="([^"]*\.(?:png|jpe?g|gif))"', content, re.I):
        r = resolve(md, m.group(1))
        if r and os.path.isfile(r):
            paths.add(r)
    for m in re.finditer(r'!\[[^\]]*\]\(([^)]*\.(?:png|jpe?g|gif))\)', content, re.I):
        r = resolve(md, m.group(1))
        if r and os.path.isfile(r):
            paths.add(r)

total_before = total_after = 0
for p in sorted(paths):
    size = os.path.getsize(p)
    if size <= THRESHOLD:
        continue
    ext = os.path.splitext(p)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        continue
    try:
        img = Image.open(p)
        img.load()
        w, h = img.size
        if ext == ".png":
            if img.mode in ("RGBA", "LA"):
                img.quantize(colors=256, method=Image.FASTOCTREE).save(p, format="PNG", optimize=True)
            else:
                img.convert("RGB").quantize(colors=256, method=Image.MEDIANCUT).save(p, format="PNG", optimize=True)
        else:
            img.convert("RGB").save(p, format="JPEG", quality=85, optimize=True, progressive=True)
        after = os.path.getsize(p)
        total_before += size
        total_after += after
        print(f"{size//1024:>7}KB -> {after//1024:>7}KB  {w}x{h}  {os.path.relpath(p, ROOT)}")
    except Exception as e:
        print(f"跳过 {os.path.basename(p)}: {e}")

print(f"\n总计: {total_before//1024//1024}MB -> {total_after//1024//1024}MB  (节省 {(total_before-total_after)*100//max(total_before,1)}%)")
