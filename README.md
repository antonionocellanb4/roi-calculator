# Aufinity — Landing ROI Calculator

Landing page dedicata al Calcolatore ROI di Aufinity. Pagina singola,
self-contained: nessun build step in produzione, nessuna dipendenza da
installare. Si apre `index.html` e basta.

## Struttura

```
index.html              la pagina completa da pubblicare (generata)
src/landing_shell.html  sorgente della landing, con i marker di innesto
src/roi_calculator.html calcolatore fornito dal cliente, non modificato
src/logo.svg            logo Aufinity estratto da aufinity.com
src/build.py            innesta il calcolatore nella shell -> index.html
```

**`index.html` è generato: non modificarlo a mano.** Si lavora su
`src/landing_shell.html` e si rigenera:

```bash
python src/build.py
```

## Il calcolatore

`src/roi_calculator.html` è il codice fornito dal cliente. Logica, calcoli,
JavaScript, input e risultati non sono stati toccati. Il build script lo
inserisce verbatim, con una sola adattazione al contenitore: il selettore
`body` diventa `.roi-embed`, il wrapper in cui la landing lo incapsula.

Il resto degli adattamenti vive nel foglio di stile della landing, scoped su
`.au-calc-frame`, e riguarda solo il layout del contenitore:

- colonna del risultato più larga sopra i 900px, così la CTA sta su una riga
- niente sfondo sul wrapper: il pannello lo disegna il frame
- `overflow:hidden` sul frame, per garantire zero overflow orizzontale

Il bottone "Torna al calcolatore" e la CTA "Parla con un esperto" vengono
riposizionati nella colonna destra via `appendChild`: si sposta il nodo,
`onclick` e `goToCalc()` restano quelli forniti.

Tutte le classi della landing sono prefissate `.au-` e nessun tag nudo è
stilizzato, così non c'è collisione possibile con il CSS del calcolatore.

## Note

- **Il form HubSpot non carica da `file://`.** Lo script è
  protocol-relative (`//js-eu1.hsforms.net/...`), che da file diventa
  `file://js-eu1...`. Per provarlo serve un server:
  `python -m http.server 8000` e poi `http://127.0.0.1:8000`.
- Font: DM Sans + DM Mono da Google Fonts. Colori e tipografia presi da
  aufinity.com e dalla landing Oktoberfest.
- I loghi clienti sono caricati dal CDN Webflow di Aufinity.
