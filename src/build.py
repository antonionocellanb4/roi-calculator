"""Innesta il calcolatore ROI (codice cliente) nella landing shell.

    python src/build.py        # rigenera index.html

Il codice del calcolatore viene copiato verbatim da src/roi_calculator.html.
Unica modifica ammessa dal brief (container/wrapper): il selettore `body`
diventa `.roi-embed`, il wrapper in cui la landing lo incapsula.
"""
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

LOGOS = [
    ('AIMG', '68b16c1f433e6ceba795b855_AIMG-Logo_white-it.png'),
    ('Crema Diesel', '68a4750b35f6922171a1a7d6_crema_diesel.png'),
    ('Dag Auto', '6978c16efaa7ea96445ea0ef_stella-con-dag-auto.png'),
    ('FM', '68b16c3797bdf317dc0559c7_Logo_FM_Bianco%20(1).png'),
    ('Gruppo GMG', '68b9803d697afeea80f2d46a_LOGO-GRUPPO-GMG.png'),
    ('Lodauto', '6949133f152707c7b374906f_Logo-Vettoriale-Lodauto-2.png'),
    ('Rangoni', '68b181c4bc98e372578e61c6_Logo-Rangoni-Sfondo-Trasparente%20(1).png'),
    ('UCISM', '68b980b0cf2b4d46359d29bb_logo-ucism-last-version.png'),
]
BASE = 'https://cdn.prod.website-files.com/667d1179ca68e73aa5dc5ce6/'
logos_html = '\n        '.join(
    '<img src="%s%s" alt="%s" loading="lazy">' % (BASE, f, n) for n, f in LOGOS
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
