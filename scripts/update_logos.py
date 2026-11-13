from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DOCS = HERE / "docs"
FONT_PATH = HERE / "node_modules" / "katex" / "dist" / "fonts" / "KaTeX_Main-Regular.ttf"

font = TTFont(str(FONT_PATH))
cmap = font.getBestCmap()
glyph_set = font.getGlyphSet()

scale = 0.071204
x_start = 130.0
y_baseline = 68.11

# generate winterpress path
pen = SVGPathPen(glyph_set)
x_cur = x_start
for char in "winterpress":
    glyph_name = cmap[ord(char)]
    glyph = glyph_set[glyph_name]
    tpen = TransformPen(pen, (scale, 0, 0, -scale, x_cur, y_baseline))
    glyph.draw(tpen)
    x_cur += glyph.width * scale

path_winterpress = pen.getCommands()
total_w = round(x_cur + 8.0, 1)

configs = {
    "dark": {"title_color": "#ece8df", "file": DOCS / "logo-dark.svg"},
    "light": {"title_color": "#1a1917", "file": DOCS / "logo-light.svg"}
}

for mode, cfg in configs.items():
    content = cfg["file"].read_text(encoding="utf-8")
    
    # 1. Update aria-label and width/viewBox in <svg> tag
    content = re.sub(
        r'<svg [^>]+>',
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{total_w:.1f}" height="112.0" viewBox="0 0 {total_w:.2f} 112.00" '
        f'role="img" aria-label="Winterpress: the LaTeX editor for working scientists">',
        content,
        count=1
    )
    
    # 2. Replace the old scribe letters group with the new winterpress path
    # The old group had <g fill='#...'> with 6 <use xlink:href='#g2-...'>
    old_scribe_group = re.search(r"<g fill='#[0-9a-fA-F]+'>\s*<use[^>]+#g2-115[^>]+>.*?</g>", content, re.DOTALL)
    if old_scribe_group:
        new_title = f"<path fill='{cfg['title_color']}' d='{path_winterpress}'/>"
        content = content.replace(old_scribe_group.group(0), new_title)
    else:
        print(f"Warning: Could not find old scribe group in {mode}")

    # Also clean up unneeded g2-* defs if present
    content = re.sub(r"<path id='g2-[^']+' d='[^']+'/>\s*", "", content)
    
    cfg["file"].write_text(content, encoding="utf-8")
    print(f"Updated {cfg['file'].name} with Winterpress (width: {total_w})")
