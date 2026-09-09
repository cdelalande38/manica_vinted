#!/usr/bin/env python3
"""Assemble des planches-contact de 5 photos, pour identifier les vêtements
en quelques lectures d'images au lieu d'une par article.

    python planche_contact.py dossier/ sortie/ [--par 5] [--depart 1]
"""
import os, glob, argparse
from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source')
    p.add_argument('destination')
    p.add_argument('--par', type=int, default=5)
    p.add_argument('--depart', type=int, default=1)
    p.add_argument('--largeur', type=int, default=330)
    a = p.parse_args()

    os.makedirs(a.destination, exist_ok=True)
    fichiers = sorted(glob.glob(os.path.join(a.source, '*.jpg')))
    W = a.largeur

    for lot in range((len(fichiers) + a.par - 1) // a.par):
        groupe = fichiers[lot * a.par:(lot + 1) * a.par]
        images = []
        for j, f in enumerate(groupe):
            im = Image.open(f)
            if im.width > im.height:
                im = im.rotate(90, expand=True)
            im.thumbnail((W, 10000))
            images.append((a.depart + lot * a.par + j, im))

        H = max(i.height for _, i in images)
        planche = Image.new('RGB', (W * len(images), H + 24), 'white')
        d = ImageDraw.Draw(planche)
        for k, (n, im) in enumerate(images):
            planche.paste(im, (k * W, 24))
            d.text((k * W + 6, 6), '#%d' % n, fill='black')

        out = os.path.join(a.destination, 'planche%d.png' % lot)
        planche.save(out)
        print(out, [n for n, _ in images])


if __name__ == '__main__':
    main()
