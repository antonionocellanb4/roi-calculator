"""Innesta il calcolatore ROI (codice cliente) nella landing shell.

    python src/build.py        # rigenera index.html

Il codice del calcolatore viene copiato verbatim da src/roi_calculator.html.
Unica modifica ammessa dal brief (container/wrapper): il selettore `body`
diventa `.roi-embed`, il wrapper in cui la landing lo incapsula.
"""
import json
import re
import pathlib

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent

CALC = SRC / 'roi_calculator.html'
SHELL = SRC / 'landing_shell.html'
LOGO = SRC / 'logo.svg'
OUT = ROOT / 'index.html'

calc = CALC.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')

# --- split del file calcolatore -------------------------------------------
css = re.search(r'<style>(.*?)</style>', calc, re.S).group(1)
body = re.search(r'<body>(.*?)<script>', calc, re.S).group(1)
js = re.search(r'<script>(.*?)</script>\s*</body>', calc, re.S).group(1)

# --- unica adattazione: body -> wrapper .roi-embed -------------------------
before = css
css = css.replace('\nbody {\n', '\n.roi-embed {\n', 1)
assert css != before, 'regola body non trovata nel CSS del calcolatore'
css = css.replace(' min-height: 100vh;', '', 1)          # il wrapper non deve forzare 100vh

# --- logo ufficiale Aufinity: classi -> attributi fill ---------------------
# (le classi .cls-* di un <svg> inline non sono isolate e sporcherebbero il CSS)
logo = LOGO.read_text(encoding='utf-8')
logo = re.sub(r'<defs>.*?</defs>', '', logo, flags=re.S)
logo = logo.replace('class="cls-1"', 'fill="#009df9"')
logo = logo.replace('class="cls-2"', 'fill="#f13d65"')
logo = logo.replace('class="cls-3"', 'fill="#ffffff"')
logo = re.sub(r'\s*id="Ebene_1"|\s*data-name="Ebene 1"', '', logo)
logo = re.sub(r'\n\s*\n', '\n', logo).strip()

# I loghi sono ritagliati e normalizzati per area da src/fetch_logos.py, che
# scrive src/logos.json con la dimensione di resa di ognuno. Qui basta la
# stdlib: nessuna dipendenza da Pillow per rigenerare la pagina.
manifest = json.loads((SRC / 'logos.json').read_text(encoding='utf-8'))
SEP = chr(10) + ' ' * 8
logos_html = SEP.join(
    '<img src="assets/logos/%s" alt="%s" width="%d" height="%d" '
    'style="--w:%dpx;--h:%dpx" loading="lazy">'
    % (l['file'], l['name'], l['w'], l['h'], l['w'], l['h'])
    for l in manifest
)

# --- splice ----------------------------------------------------------------
out = shell
for marker, payload in (
    ('<!--CALC_CSS-->', css.strip('\n')),
    ('<!--CALC_HTML-->', body.strip('\n')),
    ('<!--CALC_JS-->', js.strip('\n')),
    ('<!--LOGOS-->', logos_html),
):
    assert marker in out, 'marker mancante: ' + marker
    out = out.replace(marker, payload)

assert out.count('<!--LOGO-->') == 2, 'attesi 2 slot logo'
out = out.replace('<!--LOGO-->', logo)

OUT.write_text(out, encoding='utf-8')

# --- sanity check ----------------------------------------------------------
assert '<!--CALC' not in out and '<!--LOGO' not in out
for needle in ('function compute()', 'const SALES_MIN   = 30;',
               'id="inSales"', 'id="page-results"', 'portalId: "5985319"'):
    assert needle in out, 'codice calcolatore perso: ' + needle
print('OK ->', OUT, len(out), 'bytes')
