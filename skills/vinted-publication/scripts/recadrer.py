#!/usr/bin/env python3
"""Recadre des photos de vêtements : retire les bandes noires des captures Android,
redresse les photos paysage, limite la taille.

    python recadrer.py source/ destination/ [--rotate 90|180|270]
"""
import sys, os, glob, argparse
from PIL import Image
import numpy as np


def zone_utile(im, seuil=12):
    """Plus haute bande contiguë de lignes contrastées."""
    g = np.asarray(im.convert('L').resize((108, 240)), dtype=float)
    contraste = g.std(axis=1) > seuil
    best, debut = (0, 0), None
    for i, v in enumerate(contraste):
        if v and debut is None:
            debut = i
        if (not v or i == len(contraste) - 1) and debut is not None:
            fin = i if not v else i + 1
            if fin - debut > best[1] - best[0]:
                best = (debut, fin)
            debut = None
    return best


def recadrer(im, seuil=12):
    y0, y1 = zone_utile(im, seuil)
    h = im.height
    y0, y1 = int(y0 / 240 * h), int(y1 / 240 * h)
    # détection peu fiable sur les vêtements unis : repli sur un rognage fixe
    if y1 - y0 < h * 0.30:
        return im.crop((0, int(h * 0.13), im.width, int(h * 0.82)))
    return im.crop((0, y0, im.width, y1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source')
    p.add_argument('destination')
    p.add_argument('--rotate', type=int, default=0, choices=[0, 90, 180, 270])
    p.add_argument('--max', type=int, default=1900)
    a = p.parse_args()

    os.makedirs(a.destination, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(a.source, '*.jpg'))):
        im = Image.open(f)
        if a.rotate:
            im = im.rotate(a.rotate, expand=True)
        elif im.width > im.height:          # paysage : redressement par défaut
            im = im.rotate(90, expand=True)
        else:
            im = recadrer(im)
        im.thumbnail((1400, a.max))
        out = os.path.join(a.destination, os.path.basename(f))
        im.save(out, quality=90)
        print(os.path.basename(out), im.size)


if __name__ == '__main__':
    main()
