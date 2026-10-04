# Audit indipendente della revisione 12 (3 ottobre 2026) — versione 2

**Versione 2**: integra il controllo esterno (`CORREZIONI_SECONDO_PASSAGGIO.md`): bootstrap a due vie corretto, etichette delle varianze corrette, distanze con due metriche e IC, protocollo caption v2 con script collaudato. Stato per ogni punto (confermato / da eseguire) in `CORREZIONI_SECONDO_PASSAGGIO.md` §2.

Mandato: `inputs/package/00_prompt/AAR_prompt_agente_verifica_integrale.md`. Tutti i nuovi output sono in questa cartella; nessun file storico (`analysis/*_report`, `analysis/metrics`, `analysis/figures`, dati, manoscritto) è stato modificato. Le analisi nuove sono **post-review**, non preregistrate; le specifiche fissate prima dei risultati sono in `outputs/SPEC_direzione_aggiustata.json` e in `PROTOCOLLO_CAPTION_CONTROLLATE.md` §4.

## Integrazione mirata (4 ottobre 2026)

`integrazione/` risponde all'incarico `inputs/integrazione_mirata/00_INCARICO_AGENTE.md`: direzione DINOv2 aggiustata anche per tipologia e stile (due geometrie, P/R/ΔD per seed), riproduzione delle tabelle locali dell'autore (stabilità della selezione, ICC, lotti, binomiale, verifica fuori training, dispersione), caption v1→v2 (aggiunte per descrittore), Tab. 3 completa, hardware/scala LoRA/calendario, sostituzioni mirate. Vedi `integrazione/README.md` e `integrazione/RISCONTRO_INTEGRAZIONE.md`.

## Consegne

| file | contenuto |
|---|---|
| `RISPOSTA_REVIEWER.md` | risposta punto per punto con i risultati ottenuti e la sintesi delle cinque domande |
| `TABELLA_CHIUSURA.csv` | richiesta, evidenza, analisi, risultato, file, stato (chiuso / limite dichiarato / aperto / richiede nuova raccolta-training), limite residuo, modifica al paper |
| `RIPRODUZIONE_PRECEDENTI.csv` | 107 righe: valore riportato / ricalcolato / differenza / causa / file e comando, per manoscritto, review e riscontro precedente |
| `PROTOCOLLO_CAPTION_CONTROLLATE.md` + `config_caption_controllate.json` + `scripts/a10_caption_control_analysis.py` | controllo con caption identiche (v2): disegno, tre quantità, categorie, costo verificato (non eseguito: serve approvazione; script collaudato in dry run) |
| `CORREZIONI_SECONDO_PASSAGGIO.md` | verifica delle correzioni esterne, elenco di ciò che è confermato e di ciò che resta da eseguire |
| `MATERIALI_O_DECISIONI_MANCANTI.md` | input non reperiti dopo ricerca e decisioni del responsabile |
| `PATCH_MANOSCRITTO.md` | sostituzioni puntuali con stato delle prove (non applicate) |
| `outputs/` | report e tabelle di ogni passo (vedi sotto); `second_screening/` materiale cieco per il secondo valutatore |
| `scripts/` | codice; `logs/` esecuzioni; `env/` Python 3.14.3 e pacchetti; `SHA256SUMS.txt` impronte |

## Passi e output

| script | output principali |
|---|---|
| `a00_inventory.py` | `INVENTARIO_INPUT.csv` (127 file con hash, dimensioni, ruolo), `inventario_controlli.md` |
| `a01_human.py` | `human_reproduction.csv`, `human_sensitivities.csv`, `report_human.md` (contrasti, BT, Davidson, ICC, LOO, filtri, modello incrociato, bootstrap a due vie) |
| `a02_control_matching.py` | `report_control.md`, `control_construction.csv` (strato di ogni fotografia CONTROL), `control_composition.csv`, `control_reexecution.json` |
| `a03_dino.py` | `report_dino.md`, `dino_reproduction.csv`, `dino_distances.csv`, `dino_distance_changes.csv`, `dino_centroid_distance_changes.csv`, `dino_adjusted_direction.csv` |
| `a04_descriptors.py` | `report_descriptors.md`, `descriptors_profile.csv`, `descriptors_by_stratum.csv`, `descriptors_distances.csv`, `descriptors_distance_changes.csv`, `descriptors_centroid_distance_changes.csv` |
| `a05_captions.py` | `report_captions.md`, `caption_hits_audit.csv`, `caption_lexical_vs_visual.csv`, `caption_definition_variants.csv`, `caption_ambiguous_fragments.csv`, `caption_dictionary_audit.json` |
| `a06_runs_timeline.py` | `report_runs_timeline.md`, `runs_all.csv`, `cloud_jobs.csv`, `timeline_full.csv` |
| `a07_documentation.py` | `report_documentation.md`, `second_screening/` (manifest, scheda, istruzioni, 576 immagini), `second_screening_key_DO_NOT_USE.csv` |
| `a10_caption_control_analysis.py --dry-run` | `caption_control_DRYRUN_results.csv`, `report_caption_control_DRYRUN.md` (collaudo del codice; numeri senza significato) |
| `a09_deliverables.py` | `RIPRODUZIONE_PRECEDENTI.csv`, `TABELLA_CHIUSURA.csv`, `SHA256SUMS.txt` |
| riesecuzione del riscontro precedente | `outputs/riscontro_rerun/` (`analisi_riscontro.py --bootstrap 3000`): 14 file identici, 5 con differenze float |

## Riproduzione in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi) in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi) in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi) in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi) in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi) in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi) in questo repository

Gli script leggono per default `../data/export/` (copia anonimizzata dell'export: identificativi dei partecipanti casuali, orari relativi, ruoli rari aggregati). Rieseguiti qui il 4 ottobre 2026: `a00`–`a05`, `a09`, `a10 --dry-run` riproducono gli stessi valori dell'esecuzione sull'export completo; i soli scostamenti sono negli intervalli bootstrap che dipendono dall'ordine degli identificativi (es. bootstrap a due vie dei rating −0,024/+0,235 contro −0,025/+0,233: errore Monte Carlo). `a06_runs_timeline.py` e `a07_documentation.py` richiedono il registro audit completo della piattaforma (non ridistribuito perché contiene eventi sui singoli partecipanti): i loro output, prodotti sull'export completo il 3 ottobre 2026, sono in `outputs/`. `inputs/previous_reply/` contiene gli allegati (dati derivati) del riscontro tecnico precedente; i testi delle review e le bozze del manoscritto non sono ridistribuiti.

## Riproduzione (comandi)

```
# ambiente: Python 3.14.3, pacchetti in env/requirements_frozen.txt (default: ../data/export; per l'export completo impostare ARCH300_EXPORT=<zip>)
set PYTHONIOENCODING=utf-8
cd audit/scripts
python a00_inventory.py && python a01_human.py && python a02_control_matching.py && python a03_dino.py && python a04_descriptors.py && python a05_captions.py && python a06_runs_timeline.py && python a07_documentation.py && python a09_deliverables.py
```
Seed del bootstrap: 20261003 (`common.SEED`). Gli script leggono `analysis/metrics/*.npz|csv`, `analysis/baseline/direction_dinov2.npz`, `analysis/vlm/images/` e il codice della piattaforma in `src/`.

## Distribuzione

La chiave dello screening cieco non è inclusa (sarà pubblicata a screening concluso). Impronte di tutti i file: `SHA256SUMS.txt` alla radice del repository. Nessuna credenziale, nessun dato individuale oltre a quelli già nell'export (che non è in questa cartella).
