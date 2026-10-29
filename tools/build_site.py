"""Stage 4: join the White and Black runs into the home page.
Run from the repo root after both:  SIDE=white ... ; SIDE=black ...   then   python tools/build_site.py"""
import os, json, sys
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
P = common.PLAYER; FULL = common.FULL_NAME

def read(side, name):
    return open(os.path.join(ROOT, "build", side, name), encoding="utf-8").read()

def front(title, menu, weight, menu_on=True):
    return f'---\ntitle: "{title}"\nheader_menu_title: "{menu}"\nnavigation_menu_title: "{menu}"\nweight: {weight}\nheader_menu: {"true" if menu_on else "false"}\n---\n'

def wdl(s): return f"+{s['w']} ={s['d']} −{s['l']}"

def main():
    ch = os.path.join(ROOT, "content", "en", "homepage"); os.makedirs(ch, exist_ok=True)
    for f in os.listdir(ch):
        if f.endswith(".md"): os.remove(os.path.join(ch, f))
    open(os.path.join(ch, "index.md"), "w").write("---\nheadless: true\n---\n")
    st = {s: json.load(open(os.path.join(ROOT, "build", s, "stats.json"))) for s in ("white", "black")}
    tw, tb = st["white"]["total"], st["black"]["total"]
    n = tw["n"] + tb["n"]; w = tw["w"] + tb["w"]; d = tw["d"] + tb["d"]; l = tw["l"] + tb["l"]
    sc = (w + d / 2) / n
    open(os.path.join(ch, "01-overview.md"), "w", encoding="utf-8").write(
        front(f"{FULL}", "Overview", 1) +
        f"Every opening {FULL} played, from the big picture down to the games: **{n:,} games**, +{w} ={d} −{l}, a score of **{sc:.0%}**. "
        "Pick a colour. Each side starts with a tree of his whole repertoire, then one tree per first move, then the games in every line.\n\n"
        f"## With White\n**{tw['n']} games**, {wdl(tw)}, score **{(tw['w']+tw['d']/2)/tw['n']:.0%}**.\n\n"
        f"[![{P} with White, the big picture](white/trees/big-picture/preview.jpg)](white/trees/big-picture/)\n\n"
        "- [See his White repertoire](#white)\n\n"
        f"## With Black\n**{tb['n']} games**, {wdl(tb)}, score **{(tb['w']+tb['d']/2)/tb['n']:.0%}**.\n\n"
        f"[![{P} with Black, the big picture](black/trees/big-picture/preview.jpg)](black/trees/big-picture/)\n\n"
        "- [See his Black repertoire](#black)\n")
    open(os.path.join(ch, "02-white.md"), "w", encoding="utf-8").write(front(f"{P} with White", "White", 2) + read("white", "section.md"))
    open(os.path.join(ch, "03-black.md"), "w", encoding="utf-8").write(front(f"{P} with Black", "Black", 3) + read("black", "section.md"))
    nc = sum(int(open(os.path.join(ROOT, "build", s, "cards.json")).read()) for s in ("white", "black"))
    open(os.path.join(ch, "04-flashcards.md"), "w", encoding="utf-8").write(
        front("Flashcards", "Flashcards", 4) +
        f"{nc} cards to learn his choices. Each shows a position and asks what {P} plays next, from his side of the board. "
        "Click a card to reveal his move, how many games, and his score. Open a group below to see its cards.\n\n"
        '{{< flashcards tools="true" >}}{{< /flashcards >}}\n\n' + read("white", "cards.md") + "\n" + read("black", "cards.md"))
    sk = {k: st["white"]["skipped"].get(k, 0) for k in set(st["white"]["skipped"]) | set(st["black"]["skipped"])}
    open(os.path.join(ch, "05-how.md"), "w", encoding="utf-8").write(
        front("How This Is Made", "How It Works", 5, menu_on=False) +
        f"The games come from a database of {FULL}'s games: {n:,} games, {tw['n']} with White and {tb['n']} with Black.\n\n"
        "Every game is replayed move by move and added to one tree per colour, counting how many games pass through each position and how he scored there.\n\n"
        "## Tools\n"
        "- [python-chess](https://github.com/niklasf/python-chess) reads the games and draws the boards\n"
        "- [Graphviz](https://graphviz.org/) lays out the branches\n"
        "- [Lichess opening names](https://github.com/lichess-org/chess-openings) (CC0) give each game its opening name\n"
        "- [chess.js](https://github.com/jhlywa/chess.js) replays the games in your browser\n"
        "- [Hugo](https://gohugo.io/) builds the site\n")
    # cover image: assets/images/header-*.jpg is a chosen photo (used by content/en/_index.md); the tree crop below is only a fallback
    src = os.path.join(ROOT, "build", "white", "big-picture.png")
    if os.path.exists(src) and not any(f.startswith("header-") for f in os.listdir(os.path.join(ROOT, "assets", "images"))):
        im = Image.open(src).convert("RGB"); W, H = im.size
        cw = min(W, 2400); chh = int(cw * 1338 / 2400); x0 = max(0, (W - cw) // 2)
        crop = im.crop((x0, 0, x0 + cw, min(H, chh))).resize((2400, 1338))
        out = Image.blend(crop.filter(ImageFilter.GaussianBlur(9)), Image.new("RGB", crop.size, (20, 35, 50)), 0.86)
        os.makedirs(os.path.join(ROOT, "assets", "images"), exist_ok=True)
        out.save(os.path.join(ROOT, "assets", "images", "cover-image.jpg"), quality=80, optimize=True)
    print("site content written")

if __name__ == "__main__":
    main()
