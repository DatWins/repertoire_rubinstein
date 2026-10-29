"""Stage 3: flashcards. One card per important decision of the player's colour in the tree:
the board after the shown moves, 'what does he play?', and the answer with his counts.
Run from the repo root:  SIDE=white python tools/build_cards.py   (writes build/<side>/cards.md; build_site.py joins both sides)"""
import os, chess, chess.svg
import common

ROOT = os.path.abspath(os.path.join(common.HERE, ".."))
COLORS = {"square light": "#DEE3E6", "square dark": "#8CA2AD", "margin": "#5B6F79"}
PER_GROUP = {"e4": 22, "d4": 12, "c4": 8, "nf3": 8}
MIN_N = 6
MAX_PLY = 14 if common.IS_WHITE else 15     # about 7-8 moves deep
PARITY = 0 if common.IS_WHITE else 1          # ply parity of the positions where the player is to move
BUILD = os.path.join(ROOT, "build", common.SIDE); os.makedirs(BUILD, exist_ok=True)

def pick_nodes(first, k):
    cand = []
    stack = [first]
    while stack:
        x = stack.pop()
        if x.ply % 2 == PARITY and x.n >= MIN_N and len(x.kids) >= 1 and x.ply <= MAX_PLY:
            # a decision worth a card: at least two Black options, or one move played in a big sample
            if len(x.kids) >= 2 or x.n >= 30:
                cand.append(x)
        stack.extend(x.kids.values())
    cand.sort(key=lambda x: -x.n)
    chosen = cand[:k]
    chosen.sort(key=lambda x: (x.ply, -x.n))
    return chosen

def svg_board(path, name, outdir):
    b = chess.Board(); last = None
    for san in path:
        last = b.push_san(san)
    arrows = [chess.svg.Arrow(last.from_square, last.to_square, color="#15781B")] if last else []
    svg = chess.svg.board(board=b, size=300, arrows=arrows, colors=COLORS, orientation=(chess.WHITE if common.IS_WHITE else chess.BLACK))
    open(os.path.join(outdir, name), "w", encoding="utf-8").write(svg)

def main():
    games, _ = common.load_games(); root = common.build_tree(games)
    S, SN, P = common.SIDE, common.SIDE_NAME, common.PLAYER
    outdir = os.path.join(common.OUT, "cards"); os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir): os.remove(os.path.join(outdir, f))
    groups, total = [], 0
    if common.IS_WHITE:       # the very first decision
        kids = sorted(root.kids.values(), key=lambda k: -k.n); top = kids[0]
        svg_board([], "start.svg", outdir)
        groups.append(f'{{{{< flashcards title="White · move 1" >}}}}\n'
                      f'{{{{< flashcard question="Move 1 with White. What does {P} open with?" board="{S}/cards/start.svg" >}}}}\n'
                      f'**1.{top.san}** · {top.n} of {root.n} games ({top.n/root.n:.0%}), score {top.score:.0%}\n\n'
                      "Also: " + ", ".join(f"1.{k.san} ({k.n})" for k in kids[1:4]) + "\n{{< /flashcard >}}\n{{< /flashcards >}}\n")
        total += 1
    for san, label, slug in common.FIRST_MOVES:
        if san not in root.kids:
            continue
        cards = []
        for i, x in enumerate(pick_nodes(root.kids[san], PER_GROUP[slug]), 1):
            path = x.path(); name = f"{slug}-{i:02d}.svg"
            svg_board(path, name, outdir)
            kids = sorted(x.kids.values(), key=lambda k: -k.n)
            best = kids[0]
            q = f"{common.pgn_moves_text(path)} — what does {P} play?"
            ans = f"**{common.move_label(best.ply, best.san)}** · {best.n} of {x.n} games ({best.n/x.n:.0%}), score {best.score:.0%}"
            alts = [f"{common.move_label(k.ply, k.san)} ({k.n})" for k in kids[1:4]]
            if alts: ans += "\n\nAlso: " + ", ".join(alts)
            cards.append(f'{{{{< flashcard question="{q}" board="{S}/cards/{name}" >}}}}\n{ans}\n{{{{< /flashcard >}}}}\n')
        if not cards:
            continue
        total += len(cards)
        title = f"{SN} · {label}" if common.IS_WHITE else f"{SN} · against {label}"
        groups.append(f'{{{{< flashcards title="{title}" >}}}}\n' + "\n".join(cards) + '{{< /flashcards >}}\n')
    open(os.path.join(BUILD, "cards.md"), "w", encoding="utf-8").write("\n".join(groups))
    open(os.path.join(BUILD, "cards.json"), "w").write(str(total))
    print(total, "cards")

if __name__ == "__main__":
    main()
