# Secondo passaggio (3 ottobre 2026, sera) — verifica delle correzioni esterne e stato dell'audit

Input: `AAR_correzioni_puntuali_audit.zip` (`LETTURA_CRITICA_AUDIT.md`, `verifica_bootstrap.py/.json`, `verifica_tabelle.py/.json`, `bootstrap_confronto_2000.csv`), che esamina l'`AAR_audit_rev12.zip` della versione 1 (SHA-256 `2adb3e38…`). Ogni punto è stato verificato sul codice e sui dati, non accettato per fiducia. Nessun training avviato; manoscritto non toccato; dati storici non modificati.

## 1. Punti del controllo esterno: verifica e correzione

| punto | affermazione del controllo | verifica dell'audit | esito | file corretti |
|---|---|---|---|---|
| §2 bootstrap a due vie dei rating | la media esterna `d_.mean()` ignora la molteplicità dei partecipanti estratti; IC corretto −0,025245/+0,233021 | **confermato**: la molteplicità del partecipante si cancella nella media entro partecipante e non veniva reintrodotta. Corretto (`np.average(d_, weights=wp)`); rieseguito con lo stesso seed → **−0,0252 / +0,2330** (identico all'indipendente). Partecipanti estratti privi di A o C: 0,00 per ricampionamento (documentato). La v1 (−0,0075/+0,2197) è conservata nel log come stimatore superato | corretto | `scripts/a01_human.py`, `outputs/human_sensitivities.csv`, `outputs/report_human.md`, RISPOSTA §8 e sintesi, TABELLA riga h, PATCH 4.2/5.2/6 |
| §3 etichette varianze | `mf.vcomp` associato a una lista scritta a mano; il log dice cella 0,4355, immagine 0,0704, partecipante 1,05 | **confermato** (`mf.model.exog_vc.names` è in ordine alfabetico: cell, image, participant). Corretto usando i nomi del modello: **partecipante 1,05, cella 0,44, immagine 0,07**, residuo 1,54; coefficienti fissi invariati (+0,1011; +0,1344) | corretto | idem |
| §4 due metriche di distanza | centroide→centroide e media immagine→centroide danno quadri diversi per AESTHETIC nei descrittori; «CONTROL senza avvicinamento differenziale» troppo generale (seed 42160 IC < 0) | **confermato**. Aggiunto per entrambi gli spazi il Δ della distanza fra centroidi con IC bootstrap sui prompt (centroidi ricalcolati in ogni ricampionamento): `dino_centroid_distance_changes.csv`, `descriptors_centroid_distance_changes.csv`. Descrittori, AESTHETIC centroide→proprio profilo: −0,24 (n.s.) / −0,42 (IC < 0) / −0,07 (n.s.) → «riduzione descrittiva, chiara in un seed»; media immagini: n.s. → «non emerge una riduzione chiara», non «non si avvicina». DINOv2 CONTROL: «non coerente nei tre seed» | corretto; formulazioni riscritte | `a03_dino.py`, `a04_descriptors.py`, report, RISPOSTA §6, TABELLA riga i, PATCH 4.3/4.4 |
| §5 protocollo caption | «effetto perso» da IC che include zero non è lecito; soglie 0,020/0,010 arbitrarie; stringa comune da verificare; worker da bloccare; script da scrivere | **accolto**: protocollo v2 con tre quantità separate (stima neutra, incertezza, Δ appaiata fra regimi), categorie mantenuto / ridotto / non distinguibile e minore / inconclusivo / invertito, nessuna soglia di rilevanza; stringa `photograph of architecture` dopo verifica delle 178 caption (168 «exterior photograph», 1 interior, 1 aerial, 10 soggetti non-building: la v1 era falsa per 2 e impropria per 10); worker bloccato a `266541cf…` (= RUN-*-4, generazioni finali e repliche; = file attuale); `a10_caption_control_analysis.py` scritto e collaudato in `--dry-run`; costo con listino verificato (0,79 €/h, pagina Scaleway del 3/10/2026) | corretto | `PROTOCOLLO_CAPTION_CONTROLLATE.md`, `config_caption_controllate.json`, `scripts/a10_caption_control_analysis.py`, `outputs/caption_control_DRYRUN_*`, `report_caption_control_DRYRUN.md` |
| §1 e §6 formulazioni | quota del termine CONTROL = rapporto di covarianze, non «apprendimento»; «termine AESTHETIC nullo» → stima con incertezza; R aggiustato cambia anche per il denominatore; 18,23% (159) distinto da 19,16% (repliche); quantili del bootstrap delle fotografie ≠ IC sui prompt, calibrazione da verificare; modello incrociato ≠ bootstrap a due vie; quote 8/33/57/65% non rieseguite; p n.s. sugli squilibri non provano equilibrio | **accolti**; testi riformulati | RISPOSTA §2, §6, §8, sintesi; PATCH |
| §6 screening | lo zip non conteneva i 576 JPEG | corretto: lo zip di consegna escludeva le immagini per dimensione; il bundle completo per il valutatore è `outputs/second_screening/` nel progetto (576 JPEG, ~80 MB); per la consegna esterna va trasferito separatamente (`AAR_second_screening_bundle.zip`, vedi §4) | chiarito | README |

Verifica delle verifiche: `verifica_tabelle.json` riproduce r(x,a−c) = 0,706593, r(x,a) = −0,006200, r(x,c) = −0,427162, quota 1,014597 e i r per strato 0,026289 / 0,632367 / 0,433979 / 0,709219 dai CSV esportati: coincidono con `descriptors_reproduction.csv` e `descriptors_by_stratum.csv`. `bootstrap_confronto_2000.csv` riproduce il consumo del generatore: i 2000 valori «audit originale» coincidono con la v1 e i valori corretti con la v2.

## 2. Stato dell'audit dopo il secondo passaggio

### Risultati confermati (ottenuti e verificati; non cambiano con le correzioni)
- Perimetri 166/164/161/159, 599/600, Fase 2 158/9.413/4.736/726/4.010, 32/16/99/11; filtro = 2 esclusioni globali «non finito».
- Contrasti umani, OR Bradley–Terry e Davidson (implementazione indipendente), ICC con estimatore documentato, LOO +0,915 (+0,944 sul campione completo), collegati/non collegati −0,116 (−0,289/+0,056).
- Modello misto incrociato A−C +0,101 (+0,016/+0,186), BASE−C +0,134 (+0,049/+0,219).
- CONTROL: riesecuzione esatta (stessi 89, stesso ordine, stesse motivazioni) → 20/41/28, conteggi per strato, nessuna coppia 1:1; Tab. 1 riprodotta; squilibri periodo/area non controllati (χ² n.s.: non prova equilibrio).
- DINOv2: d = 0,2352; S = d·P; Fig. 1 = S; 18,23% (159) e 19,16% (media repliche); replica +0,0435/+0,0412/+0,0504; direzione aggiustata per periodo/area: R 0,196/0,200/0,202 (sensibilità lineare, due variabili).
- Avvicinamento ai corpora con entrambe le metriche e IC (tabella in RISPOSTA §6).
- Descrittori: r +0,707/−0,006/−0,427; Cov(x,a−c) interamente dal termine CONTROL (stima 101%, IC 73–139%); identità r(x,(a−c)/2) = r(x,a−c); contrasti per strato; numero effettivo di descrittori ≈ 14.
- Caption: conteggi 28/28 identici; dizionario auditato con varianti strette/estese; «acqua» unica differenza significativa; riscrittura v2 asimmetrica (89/89 vs 62/89); «cars e glass» concordi in direzione.
- Run e cronologia: 4 configurazioni simmetriche, seed mai variati, RUN-4 scelto per difetti tecnici prima di dati umani; 292 immagini di prova prima del congelamento prompt; Fase 1 non proseguita; screening: flag 13:25–15:14, regola 15:29–15:31.
- Cinque misure VLM identificate (ANALYSIS_PLAN §8.6).
- Riscontro precedente: 14/19 file identici, 5 con differenze float.

### Controlli ancora da eseguire (richiedono training, raccolta o decisione del responsabile)
1. **Training a caption identiche** (protocollo v2; ≈ 7,5 h GPU, ≈ 6,0–6,6 €, ≈ 4–4,5 h di calendario; approvazione necessaria; nessun training avviato).
2. **Secondo screening cieco** da un valutatore indipendente (bundle pronto; valutatore da reclutare).
3. **Verifica della calibrazione** del bootstrap delle fotografie prima di usare i quantili 0,11–0,18 come IC della quota di trasferimento.
4. **Riesecuzione delle quote 8/33/57/65% e del residuo 0,166** (`direction_decomposition.py`), non rifatta: fino ad allora l'analisi computazionale non è dichiarata integralmente replicata.
5. **Dichiarazioni degli autori**: costruzione delle liste del corpus («brief», batch-1 list), redazione delle caption v1/v2, motivazione del filtro 166→164, etica, conflitti, host del repository anonimo.
6. **Verifica bibliografica esterna** (già fatta dal riscontro precedente, non rieseguita qui) e figure a stampa.

## 3. Che cosa NON cambia
Dati, campioni, soglie, direzione congelata, manoscritto. Nessuna delle correzioni modifica una stima storica: cambiano un intervallo (bootstrap a due vie), le etichette di tre componenti di varianza, e le formulazioni sulle distanze.

## 4. Consegna
`Downloads\AAR_audit_rev12_v2.zip` (audit completo senza immagini, chiave e pacchetto ricevuto) e `Downloads\AAR_second_screening_bundle.zip` (576 JPEG + manifest + scheda + istruzioni, senza chiave).
