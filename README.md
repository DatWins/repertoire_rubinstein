# Akiba Rubinstein's repertoire

Every opening Akiba Rubinstein played, with White and with Black, from the big picture down to the games.

- **Home page**: an overview, then a White section and a Black section. Each has a big-picture tree, one tree per first move, and cards for every line.
- **Tree pages** (`white/trees/…`, `black/trees/…`): zoomable trees. The thicker the branch, the more often it was played; each branch shows the number of games and his score.
- **Line pages** (`white/lines/…`, `black/lines/…`): every game in that line, with a board to replay it, a search box, opening-name filters (each filter also swaps the tree) and sorting. The board is shown from the side he played.
- **Flashcards**: positions where he had to choose a move, grouped by first move.

Source: `data/rubinstein_all.pgn` (797 games: 398 with White, 399 with Black). Opening names come from the [Lichess opening list](https://github.com/lichess-org/chess-openings) (CC0).

## Rebuild
Needs Python with `python-chess`, `graphviz`, `cairosvg`, `pillow`, plus the Graphviz program and Hugo.

```
for each SIDE in white black:
    SIDE=white python tools/build_trees.py       # trees (slow)
    SIDE=white python tools/build_variations.py  # one tree per opening name
    SIDE=white python tools/build_pages.py       # line pages and the side's section
    SIDE=white python tools/build_cards.py       # flashcards
python tools/build_site.py                       # joins both sides into the home page
hugo server
```

To make a site for another player, change `PLAYER`, `PLAYER_SHORT`, `FULL_NAME` and `PGN_FILE` at the top of `tools/common.py` and replace the PGN.
