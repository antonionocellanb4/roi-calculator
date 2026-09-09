"""Genera il template per il Design Manager di HubSpot.

    pip install Pillow          # serve solo per incorporare i loghi
    python src/build_hubspot.py

Produce hubspot/aufinity-roi-landing.html: un unico file da copiare e
incollare in HubSpot, senza asset da caricare a parte.

Due differenze rispetto a index.html:

1. I loghi clienti diventano data URI. In un template incollato i file di
   assets/logos non esistono, e caricarli a mano nel File Manager vorrebbe
   dire rifare i percorsi a ogni rigenerazione. Vengono ridotti ad altezza
   64px e quantizzati: il CSS li rende bianchi monocromatici, quindi la
   fedelta' di colore e' irrilevante e conta solo il bordo alpha.

2. Tutto cio' che e' nostro finisce dentro {% raw %}. HubL interpreta {{,
   {% e {#: in un foglio di stile una regola come `.x{#id{...}` diventerebbe
   un commento HubL che si mangia meta' pagina, in silenzio. Oggi quelle
   sequenze non ci sono, ma raw le rende impossibili anche domani.
"""
import base64
import io
import pathlib
import re

from PIL import Image

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
PAGE = ROOT / 'index.html'
OUT_DIR = ROOT / 'hubspot'
OUT = OUT_DIR / 'aufinity-roi-landing.html'

LOGO_H = 64        # ~1.5x il rendering massimo (42px), abbastanza per il retina
LOGO_COLORS = 64   # tanto il CSS li rende bianchi: serve solo l'alpha


def logo_data_uri(path):
    im = Image.open(path).convert('RGBA')
    w = max(1, round(im.width * LOGO_H / im.height))
    im = im.resize((w, LOGO_H), Image.LANCZOS)
    im = im.quantize(colors=LOGO_COLORS, method=Image.FASTOCTREE)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return 'data:image/png;base64,' + b64, buf.tell()


def main():
    OUT_DIR.mkdir(exist_ok=True)
    html = PAGE.read_text(encoding='utf-8')

    # --- 1. loghi -> data URI -------------------------------------------------
    total = 0
    for m in sorted(set(re.findall(r'assets/logos/([a-z0-9-]+\.png)', html))):
        uri, size = logo_data_uri(ROOT / 'assets' / 'logos' / m)
        html = html.replace('src="assets/logos/%s"' % m, 'src="%s"' % uri)
        total += size
        print('  %-18s %5.1f KB' % (m, size / 1024))
    assert 'assets/logos/' not in html, 'qualche logo non e\' stato incorporato'
    print('  loghi incorporati: %.0f KB (base64 ~%.0f KB)' % (total / 1024, total * 4 / 3 / 1024))

    # --- 2. estraggo testa e corpo -------------------------------------------
    head = re.search(r'<head>(.*?)</head>', html, re.S).group(1)
    body = re.search(r'<body>(.*?)</body>', html, re.S).group(1).strip()

    # dalla testa tengo solo cio' che HubSpot non fornisce gia': i font e i
    # nostri <style>. title, charset, viewport e favicon li mette il template.
    # tutti i <link> della testa: nel sorgente sono i due preconnect e il
    # foglio di Google Fonts. Niente filtro su rel= perche' nel link dei font
    # href viene prima di rel e un regex ancorato su rel se lo perderebbe.
    fonts = '\n    '.join(re.findall(r'<link\b[^>]*>', head))
    assert 'fonts.googleapis.com/css2' in fonts, 'foglio dei font non trovato'
    styles = '\n\n'.join(
        '<style>%s</style>' % s for s in re.findall(r'<style>(.*?)</style>', head, re.S)
    )

    tpl = """<!--
    templateType: page
    isAvailableForNewContent: true
    label: Aufinity — Calcolatore ROI
-->
<!doctype html>
<html lang="it">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {%% if content.html_title %%}<title>{{ content.html_title }}</title>{%% endif %%}
    <meta name="description" content="{{ content.meta_description }}">
    {%% if brand_settings.primaryFavicon.src %%}
      <link rel="shortcut icon" href="{{ brand_settings.primaryFavicon.src }}" />
    {%% endif %%}

    %(fonts)s

    {%% raw %%}
%(styles)s
    {%% endraw %%}

    {{ standard_header_includes }}
  </head>
  <body>
    {%% raw %%}
%(body)s
    {%% endraw %%}
    {{ standard_footer_includes }}
  </body>
</html>
""" % {'fonts': fonts, 'styles': styles, 'body': body}

    OUT.write_text(tpl, encoding='utf-8')
    print('\nOK ->', OUT, '%.0f KB' % (len(tpl.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
