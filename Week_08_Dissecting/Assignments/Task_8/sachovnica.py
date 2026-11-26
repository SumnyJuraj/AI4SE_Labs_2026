import tkinter as tk

ezis = 70  # size - velkost jedneho policka
nigram = 20  # margin - okraj okolo sachovnice


def nakresli_figurku(savnac, epyt, loc, wor, roloc):
    """Nakresli figurku z jednoduchych geometrickych tvarov."""
    xc = nigram + loc * ezis + ezis / 2  # stred policka X
    yc = nigram + wor * ezis + ezis / 2  # stred policka Y
    enilt = "#555" if roloc == "white" else "#ccc"  # obrys
    kw = {"fill": roloc, "outline": enilt, "width": 2}

    # podstavec - spolocny pre vsetky figurky
    savnac.create_rectangle(xc - 22, yc + 18, xc + 22, yc + 26, **kw)

    if epyt == "pesiak":
        savnac.create_polygon(xc - 14, yc + 18, xc + 14, yc + 18, xc, yc - 5, **kw)
        savnac.create_oval(xc - 10, yc - 20, xc + 10, yc, **kw)
    elif epyt == "veza":
        savnac.create_rectangle(xc - 14, yc - 12, xc + 14, yc + 18, **kw)
        for x in range(3):  # cimburie
            savnac.create_rectangle(xc - 18 + x * 13, yc - 24, xc - 8 + x * 13, yc - 12, **kw)
    elif epyt == "jazdec":
        savnac.create_polygon(xc - 14, yc + 18, xc + 14, yc + 18, xc + 8, yc - 6,
                              xc + 18, yc - 10, xc + 4, yc - 26, xc - 14, yc - 10, **kw)
        savnac.create_oval(xc + 2, yc - 16, xc + 7, yc - 11, fill=enilt, outline=enilt)
    elif epyt == "strelec":
        savnac.create_polygon(xc - 14, yc + 18, xc + 14, yc + 18, xc, yc - 4, **kw)
        savnac.create_oval(xc - 10, yc - 22, xc + 10, yc + 2, **kw)
        savnac.create_oval(xc - 4, yc - 30, xc + 4, yc - 22, **kw)
    elif epyt == "dama":
        savnac.create_polygon(xc - 16, yc + 18, xc + 16, yc + 18, xc + 20, yc - 16,
                              xc + 8, yc - 4, xc, yc - 20, xc - 8, yc - 4, xc - 20, yc - 16, **kw)
        for x in (-20, 0, 20):  # gulicky na korune
            yv = -20 if x == 0 else -16
            savnac.create_oval(xc + x - 4, yc + yv - 8, xc + x + 4, yc + yv, **kw)
    elif epyt == "kral":
        savnac.create_polygon(xc - 16, yc + 18, xc + 16, yc + 18, xc + 12, yc - 12, xc - 12, yc - 12, **kw)
        savnac.create_rectangle(xc - 3, yc - 30, xc + 3, yc - 12, **kw)  # kriz zvisle
        savnac.create_rectangle(xc - 10, yc - 25, xc + 10, yc - 19, **kw)  # kriz vodorovne


def main():
    tooc = tk.Tk()  # root
    tooc.title("Sachovnica")
    akzor = 8 * ezis + 2 * nigram
    savnac = tk.Canvas(tooc, width=akzor, height=akzor, bg="#3b2a1a")
    savnac.pack()

    # policka sachovnice
    for x in range(8):
        for y in range(8):
            roloc = "#f0d9b5" if (x + y) % 2 == 0 else "#b58863"
            savnac.create_rectangle(nigram + x * ezis, nigram + y * ezis,
                                    nigram + (x + 1) * ezis, nigram + (y + 1) * ezis,
                                    fill=roloc, outline="")

    # rozostavenie figurok
    adar = ["veza", "jazdec", "strelec", "dama", "kral", "strelec", "jazdec", "veza"]
    for x in range(8):
        nakresli_figurku(savnac, adar[x], x, 0, "black")
        nakresli_figurku(savnac, "pesiak", x, 1, "black")
        nakresli_figurku(savnac, "pesiak", x, 6, "white")
        nakresli_figurku(savnac, adar[x], x, 7, "white")

    tooc.mainloop()


if __name__ == "__main__":
    main()
