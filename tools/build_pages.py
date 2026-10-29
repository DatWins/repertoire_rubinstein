"""Stage 2: write the line pages (with the game viewer) and this colour's home-page section.
Run from the repo root:  SIDE=white python tools/build_pages.py   (then SIDE=black ...; build_site.py joins them)"""
import os, json, html
import common

ROOT = os.path.abspath(os.path.join(common.HERE, ".."))
BUILD = os.path.join(ROOT, "build", common.SIDE); os.makedirs(BUILD, exist_ok=True)
esc = html.escape
S, SN, P = common.SIDE, common.SIDE_NAME, common.PLAYER

def fmt_wdl(s):
    return f"+{s['w']} ={s['d']} −{s['l']}"

FIRST_LABEL = {"e4": "1.e4", "d4": "1.d4", "c4": "1.c4", "nf3": "1.Nf3", "other": "other first moves"}

def line_page(p, games, tpl, pieces, chessjs):
    ids = p["ids"]
    st = common.wdl(ids, games)
    fams = common.families(ids, games, 3)
    if p["kind"] == "line":
        dek = "Mostly " + ", ".join(f"{esc(f)} ({n})" for f, n in fams)
    elif p["first"] == "other":
        dek = ("His other first moves, played less often" if common.IS_WHITE else "Everything else White has tried against him: 1.b3, 1.g3, 1.f4 and other rare first moves")
    elif p.get("dek"):
        dek = p["dek"]
    else:
        dek = "The less common replies to " + p["title"].split(" ")[0]
    first_label = FIRST_LABEL[p["first"]]
    level, labels, of_game = common.page_groups(p, games)
    mpath = os.path.join(BUILD, "variations.json")
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    chips, trees = [], {}
    for label, n in labels:
        slug = common.group_slug(p["slug"], label)
        has = slug in manifest and os.path.exists(os.path.join(common.OUT, "trees", slug, "preview.jpg"))
        chips.append([label, n])
        if has:
            trees[label] = {"slug": slug, "moves": manifest[slug]["moves"], "n": manifest[slug]["n"]}
    rows = []
    for i in ids:
        g = games[i]
        rows.append([g["date"], g["event"], g["site"], g["round"], g["opp"], g["welo"], g["belo"],
                     g["result"], g["eco"], g["opening"], " ".join(g["moves"]), of_game[i]])
    tree = ""
    if os.path.exists(os.path.join(common.OUT, "trees", p["slug"], "preview.jpg")):
        tree = (f'    <a class="tree" id="treeLink" href="../../trees/{p["slug"]}/"><img id="treeImg" src="../../trees/{p["slug"]}/preview.jpg" '
                f'alt="Opening tree for {esc(p["title"])}"><span id="treeCap">Open the zoomable tree &rarr;</span></a>\n'
                f'    <div class="stats" id="treeNote"></div>\n')
    back = f"../../../#{common.ANCHOR[p['first']]}"
    out = (tpl.replace("__TITLE__", esc(p["title"])).replace("__KICKER__", (f"{P} with {SN} · {first_label}" if common.IS_WHITE else f"{P} with {SN} · against {first_label}"))
              .replace("__DEK__", dek).replace("__TREE__", tree).replace("__BACKHREF__", back).replace("__BACKTXT__", "Repertoire")
              .replace("__PLAYER__", P).replace("__SIDENAME__", SN).replace("__PIECES__", pieces).replace("__CHESSJS__", chessjs)
              .replace("__DATA__", json.dumps({"games": rows, "chips": chips, "trees": trees, "player": P, "playerShort": common.PLAYER_SHORT, "side": S}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")))
    d = os.path.join(common.OUT, "lines", p["slug"]); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    return st


def card(p, st, fams):
    names = " · ".join(f for f, _ in fams[:3])
    return (f'{{{{< linecard href="{S}/lines/{p["slug"]}/" title="{p["title"]}" n="{st["n"]}" w="{st["w"]}" d="{st["d"]}" l="{st["l"]}" '
            f'score="{st["score"]:.0%}" names="{names}" >}}}}\n')

def main():
    games, skipped = common.load_games(); root = common.build_tree(games)
    pages = common.line_groups(games, root)
    tpl = open(os.path.join(common.HERE, "line_template.html"), encoding="utf-8").read()
    pieces = open(os.path.join(common.HERE, "pieces.css"), encoding="utf-8").read()
    chessjs = open(os.path.join(common.HERE, "chess.js"), encoding="utf-8").read()
    stats = {}
    for p in pages:
        stats[p["slug"]] = line_page(p, games, tpl, pieces, chessjs)
        print(f"{p['slug']:18s} {stats[p['slug']]['n']:4d} games", flush=True)

    total = common.wdl([g["id"] for g in games], games)
    sec = []
    sec.append(f"**{total['n']} games** as {SN}, {fmt_wdl(total)}, score **{total['score']:.0%}**. "
               + ("The thicker the branch, the more often he played it." if common.IS_WHITE else "The thicker the branch, the more often it was played against him. Boards are shown from Black's side.") + "\n\n"
               f"[![{P} with {SN}, the big picture]({S}/trees/big-picture/preview.jpg)]({S}/trees/big-picture/)\n\n"
               f"- [Open the zoomable big-picture tree]({S}/trees/big-picture/)\n")
    for san, label, slug in common.FIRST_MOVES:
        ids = root.kids[san].games if san in root.kids else []
        if not ids:
            continue
        s = common.wdl(ids, games); fams = common.families(ids, games, 4)
        cards = "".join(card(p, stats[p["slug"]], common.families(p["ids"], games, 3)) for p in pages if p["first"] == slug)
        head = f"{label}" if common.IS_WHITE else f"Against {label}"
        sec.append(f"\n### {head} {{#{common.ANCHOR[slug]}}}\n\n"
                   f"**{s['n']} games**, {fmt_wdl(s)}, score **{s['score']:.0%}**. Most often: " + ", ".join(f"{esc(f)} ({n})" for f, n in fams) + ".\n\n"
                   f"[![{label} opening tree]({S}/trees/{slug}/preview.jpg)]({S}/trees/{slug}/)\n\n"
                   f"- [Open the zoomable tree]({S}/trees/{slug}/)\n\n"
                   "{{< linecards >}}\n" + cards + "{{< /linecards >}}\n")
    other_ids = [g["id"] for g in games if g["moves"][0] not in {m for m, _, _ in common.FIRST_MOVES}]
    if other_ids:
        so = common.wdl(other_ids, games)
        p = [x for x in pages if x["slug"] == "other-first-moves"][0]
        sec.append(f"\n### Other first moves {{#{common.ANCHOR['other']}}}\n\n"
                   f"**{so['n']} games**, {fmt_wdl(so)}, score **{so['score']:.0%}**.\n\n"
                   "{{< linecards >}}\n" + card(p, stats[p["slug"]], common.families(p["ids"], games, 3)) + "{{< /linecards >}}\n")
    open(os.path.join(BUILD, "section.md"), "w", encoding="utf-8").write("".join(sec))
    json.dump(dict(total=total, skipped=dict(skipped), first={lbl: common.wdl(root.kids[san].games, games) for san, lbl, _ in common.FIRST_MOVES if san in root.kids}),
              open(os.path.join(BUILD, "stats.json"), "w"))
    print("section written", flush=True)

if __name__ == "__main__":
    main()
