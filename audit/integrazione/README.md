# Integrazione mirata (4 ottobre 2026)

Risposta all'incarico `inputs/integrazione_mirata/00_INCARICO_AGENTE.md`. Nessun training, nessuna modifica a dati/campioni/manoscritto.

| file | contenuto |
|---|---|
| `RISCONTRO_INTEGRAZIONE.md` | risposta breve nell'ordine dell'incarico, con i risultati reali |
| `SOSTITUZIONI_MIRATE.md` | sostituzioni per abstract, risultati, conclusioni (non applicate) |
| `SPEC_dino_aggiustamento_completo.json`, `dino_aggiustamento_completo.csv`, `report_dino_aggiustamento_completo.md` | DINOv2: direzione originale, periodo+area, periodo+area+tipologia+stile; due geometrie (G1 proiezione, G2 trasformazione comune); P, R, ΔD per seed |
| `verifica_tabelle_locali.csv`, `report_verifiche_locali.md`, `stabilita_bootstrap_riprodotta.csv`, `stabilita_inclusione_per_foto.csv` | riproduzione delle tabelle locali dell'autore; regola vs codice storico; bootstrap valutatori; ICC; lotti; binomiale; verifica fuori training; dispersione intra-corpus |
| `report_caption_v1_v2.md`, `caption_v1_v2_transizioni.csv`, `caption_v1_v2_copertura.csv` | caption v1→v2: copertura, testi modificati, revisione, aggiunte 0→1 / 1→0 |
| `tabella3_completa.csv`, `report_tabella3.md` | Tab. 3 completa (tre contrasti × metodi) e definizioni operative dei filtri |
| `report_hardware_calendario.md` | hardware, scala LoRA in inferenza, 599/600, chiusura della Fase 2 |
| `HASH_INPUT.txt` | impronte di export, matrici, pacchetto ricevuto e output |

Script: `../scripts/b01_dino_adjust_full.py`, `b02_verifiche_locali.py`, `b03_caption_v1_v2.py`, `b05_tabella3.py`; log in `../logs/`. Seed bootstrap 20261004 (b01, b02) e 20261003 (b05).
