"""Scarica i loghi clienti dal CDN Aufinity, ritaglia i bordi vuoti e li
normalizza per il marquee.

    python src/fetch_logos.py

I file originali hanno margini trasparenti (o bianchi) cotti dentro, di
ampiezza molto diversa fra loro: nel marquee alcuni logotipi risultavano
minuscoli e altri enormi anche a parita' di scatola CSS. Qui il bordo vuoto
viene tolto, cosi' il logo occupa davvero tutta la scatola che gli diamo.

Output: assets/logos/*.png ad altezza 80px (2x circa il rendering, per gli
schermi retina) e src/logos.json con la dimensione di resa di ciascuno,
normalizzata per area. Il build legge il manifest e non ha bisogno di PIL.
"""
import io
import json
import pathlib
import urllib.request

from PIL import Image

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
OUT = ROOT / 'assets' / 'logos'
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = SRC / 'logos.json'

BASE = 'https://cdn.prod.website-files.com/667d1179ca68e73aa5dc5ce6/'
LOGOS = [
    ('aimg', 'AIMG', '68b16c1f433e6ceba795b855_AIMG-Logo_white-it.png'),
    ('crema-diesel', 'Crema Diesel', '68a4750b35f6922171a1a7d6_crema_diesel.png'),
    ('dag-auto', 'Dag Auto', '6978c16efaa7ea96445ea0ef_stella-con-dag-auto.png'),
    ('fm', 'FM', '68b16c3797bdf317dc0559c7_Logo_FM_Bianco%20(1).png'),
    ('gmg', 'Gruppo GMG', '68b9803d697afeea80f2d46a_LOGO-GRUPPO-GMG.png'),
    ('lodauto', 'Lodauto', '6949133f152707c7b374906f_Logo-Vettoriale-Lodauto-2.png'),
    ('rangoni', 'Rangoni & Affini', '68b181c4bc98e372578e61c6_Logo-Rangoni-Sfondo-Trasparente%20(1).png'),
    ('ucism', 'UCISM', '68b980b0cf2b4d46359d29bb_logo-ucism-last-version.png'),
    ('penske', 'Penske Cars', '6a31452360045fb48e4959af_PENSKECARS_scontornato.png'),
]

TARGET_H = 80          # 2x circa il rendering, per gli schermi retina
TOLERANCE = 12         # quanto un pixel puo' discostarsi dallo sfondo

# I logotipi hanno proporzioni estreme: Penske e' 12.6:1, Lodauto 1.4:1.
# Dentro una scatola fissa il primo si schiaccerebbe a 12px di altezza e il
# secondo ne userebbe 40. Li normalizziamo per AREA, non per riquadro: a
# parita' di area il "peso" ottico sulla pagina e' simile.
TARGET_AREA = 3000     # px^2 di area resa
MAX_H = 42
MAX_W = 200


def trim(im):
    """Toglie il bordo vuoto: per alpha se c'e', altrimenti per colore d'angolo."""
    im = im.convert('RGBA')
    alpha = im.getchannel('A')
    if alpha.getextrema()[0] < 255:            # ha davvero trasparenza
        box = alpha.getbbox()
    else:                                      # sfondo pieno: uso il pixel d'angolo
        bg = im.getpixel((0, 0))
        diff = Image.new('L', im.size, 0)
        px_src, px_dst = im.load(), diff.load()
        for y in range(im.height):
            for x in range(im.width):
                p = px_src[x, y]
                if (abs(p[0] - bg[0]) > TOLERANCE or abs(p[1] - bg[1]) > TOLERANCE
                        or abs(p[2] - bg[2]) > TOLERANCE):
                    px_dst[x, y] = 255
        box = diff.getbbox()
    return im.crop(box) if box else im


def display_size(w, h):
    """Larghezza e altezza di resa a parita' di area, con i limiti."""
    ratio = w / h
    dh = (TARGET_AREA / ratio) ** 0.5
    dw = dh * ratio
    if dh > MAX_H:
        dh, dw = MAX_H, MAX_H * ratio
    if dw > MAX_W:
        dw, dh = MAX_W, MAX_W / ratio
    return round(dw), round(dh)


def main():
    manifest = []
    for slug, name, filename in LOGOS:
        raw = urllib.request.urlopen(BASE + filename, timeout=40).read()
        im = Image.open(io.BytesIO(raw))
        before = im.size
        im = trim(im)
        cropped = im.size

        ratio = TARGET_H / im.height
        im = im.resize((max(1, round(im.width * ratio)), TARGET_H), Image.LANCZOS)

        dest = OUT / (slug + '.png')
        im.save(dest, 'PNG', optimize=True)

        dw, dh = display_size(*im.size)
        manifest.append({'file': slug + '.png', 'name': name, 'w': dw, 'h': dh})
        print('%-14s %10s -> %9s  resa %3dx%-3d  %5.1f KB  (%s)' % (
            slug, '%dx%d' % before, '%dx%d' % cropped, dw, dh,
            dest.stat().st_size / 1024, name))

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                        encoding='utf-8')
    print()
    print('manifest ->', MANIFEST)


if __name__ == '__main__':
    main()
