"""Print the curator card solver's fit log for the main contexts (build.py runs it; DESIGN 6 / placard.py)."""
import placard as PL

CONTEXTS = {
    "Home film 504x598": ([PL.title("t"), PL.byline("b"), PL.line("genres", "g", "top"),
                           PL.box("tagline", "t", "mid", "font_quote", 2, when="x", probe=True),
                           PL.box("premise", "p", "mid", "font_small", 2, gap=12, grow=3, when="y"), PL.flags("ListItem"),
                           PL.line("status", "s", "bot", gap=14), PL.line("collection", "c", "bot", gap=4),
                           PL.rule(), PL.keyline("k")], 598, (28, 30), PL.DROP),
    "Easel 560x478": ([PL.title("t"), PL.byline("b"), PL.line("genres", "f", "top"),
                       PL.box("premise", "p", "mid", "font_small", 2, grow=3), PL.flags("ListItem"),
                       PL.line("state", "s", "bot", gap=14), PL.progress([("true", "ListItem")]), PL.keyline("k")],
                      478, (28, 30), PL.DROP),
    "Salon 540x425": ([PL.title("t"), PL.byline("b"), PL.line("genres", "g", "top"),
                       PL.box("tagline", "t", "mid", "font_quote", 2, when="x", probe=True),
                       PL.box("premise", "p", "mid", "font_small", 1, gap=12, grow=6, when="y"), PL.flags("ListItem"),
                       PL.line("status", "s", "bot", gap=12), PL.rule(), PL.keyline("k")], 425, (20, 26), PL.DROP_SALON),
    "Gallery wall 668x888": ([PL.title("t"), PL.byline("b"), PL.line("genres", "g", "top"), PL.line("made", "m", "top"),
                              PL.box("tagline", "t", "mid", "font_quote", 2, when="x", probe=True),
                              PL.box("premise", "p", "mid", "font_small", 2, gap=12, grow=8, when="y"),
                              PL.flags("ListItem"),
                              PL.line("status", "s", "bot", gap=14), PL.line("collection", "c", "bot", gap=4),
                              PL.line("credit", "a", "bot", gap=4), PL.rule(), PL.keyline("k")], 888, (36, 38), PL.DROP),
}


def main():
    print("placard fit log (worst case per runtime case):")
    for name, (fields, h, pad, drop) in CONTEXTS.items():
        print(" ", name)
        for line in PL.report(fields, h, pad, drop):
            print("    " + line)


if __name__ == "__main__":
    main()
