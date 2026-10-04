# Materiali realmente mancanti e decisioni che richiedono il responsabile

Solo ciò che resta mancante **dopo la ricerca documentata** (percorsi cercati: repository del progetto, `analysis/`, export 2026-10-01 e 2026-10-02, `App_Data` locale, `~/Downloads` incluse le sottocartelle, il pacchetto `AAR_pacchetto_per_agente.zip`). Ciò che l'altro assistente aveva dichiarato mancante ma esiste in questo ambiente (embedding 768-d, matrice dei 31 descrittori, codice delle sonde, trainer, prompt) è inventariato in `outputs/INVENTARIO_INPUT.csv` e **non** compare qui.

## A. Input non reperiti

| materiale | dove cercato | cosa si è trovato | calcolo bloccato |
|---|---|---|---|
| Testo integrale dei «problemi nuovi n. 1–6» dell'ultima tabella del revisore | pacchetto `02_review/`, Downloads, note audit precedenti | solo i rinvii nella tabella (n. 1 embedding, n. 2 RUN-4, n. 3–4 cronologia, n. 5 unità di ricampionamento, n. 6 filtro di esclusione) | nessuno: i temi espliciti sono trattati; i rinvii non esplicitati non sono verificabili |
| «Brief» e «lista batch-1» citati in `image_metadata.notes` (es. «named reference in brief», «seed from the batch-1 list … balancing step») | repository, export, Downloads, `Downloads/prompts/` | criteri di ammissione nel documento del 25/09 (`AAR_LNCS_15_pagine.docx`); `award_or_relevance` per opera; due batch 300+300 | nessun calcolo; manca la **procedura di campionamento** dei 600 edifici (chi ha compilato le liste, con quali fonti e quanti scarti) |
| Pesi `.safetensors` di RUN-AESTHETIC-4 / RUN-CONTROL-4 e delle REP-* | Downloads (presenti solo job3–6: v1 e test), `App_Data` locale | hash dei pesi registrati nei 576+960 record di generazione (`lora_sha256`) e `artifact_uri` sul bucket della piattaforma | nessuno per l'audit; necessari per il deposito riproducibile completo (scaricabili dal bucket dal responsabile) |
| Registro di chi ha scritto/riscritto le caption v2 e con quale strumento | `captions.csv` (`source` Imported/Manual, `model` vuoto), audit log (due account) | 554 eventi, 384 su AESTHETIC e 170 su CONTROL | nessuno; serve la **dichiarazione degli autori** sulla procedura (strumento, istruzioni, revisione) |
| Immagini di prova delle run intermedie (292 import, 19 piani cancellati) | export (i piani cancellati non esportano immagini) | solo i conteggi e gli orari | ricostruzione di cosa fu visto fra una configurazione e l'altra: impossibile dai dati |
| Documento istituzionale di approvazione o esenzione etica | nessuno nei materiali | testo di consenso e disegno anonimo documentati | — (adempimento, non calcolo) |
| Dichiarazione sui conflitti di interesse | segnaposto nel manoscritto | — | — |

## B. Analisi non eseguite in questo audit (eseguibili, non bloccate da input)

- Ricalcolo delle quote 8/33/57/65% e del residuo 0,166 (pipeline ridge di `direction_decomposition.py`): letti dal report storico, non riprodotti per tempo. Eseguibile con `python analysis/direction_decomposition.py <export>`.
- Riverifica bibliografica esterna ([4], [8], [10], [11], [15]): già verificata nel riscontro precedente (file 19); non rieseguita.
- Rifacimento delle figure alla dimensione di stampa: editoriale.

## C. Decisioni che spettano al responsabile

1. **Autorizzare o no il training a caption controllate** (`PROTOCOLLO_CAPTION_CONTROLLATE.md`, `config_caption_controllate.json`): 6 training + 6 generazioni, ≈ 7,5 ore GPU L4-1-24G, ≈ 6 € al listino (da verificare sulla console). Senza di esso la condizione del revisore «training a caption controllate obbligatorio» resta aperta e il paper deve descrivere il trattamento come «fotografie con le rispettive caption».
2. **Reclutare un secondo valutatore indipendente** per lo screening retrospettivo con il materiale cieco in `outputs/second_screening/` (576 immagini a piena risoluzione, codici neutri, scheda, istruzioni). La chiave è in `outputs/second_screening_key_DO_NOT_USE.csv` e non va consegnata al valutatore.
3. **Dichiarare la procedura di costruzione del corpus** (liste di partenza, chi ha selezionato, criteri applicati per batch, scarti) e la **procedura di redazione delle caption** v1 e v2 (chi, strumento, istruzioni, perché 89/89 AESTHETIC e 62/89 CONTROL).
4. **Confermare la motivazione del filtro** che esclude dai calcoli secondari i 2 partecipanti con Fase 1 completa e Fase 2 incompleta (300 voti), oppure adottare il campione completo per le stime di Fase 1 (le differenze sono riportate: ICC uguale, LOO +0,944 vs +0,915).
5. **Stato etico**: ottenere un'esenzione/approvazione istituzionale o dichiarare esplicitamente la sua assenza con le garanzie adottate (anonimato, nessun IP, consenso).
6. **Conflitti di interesse**: dichiarazione degli autori.
7. **Repository anonimo**: scegliere l'host anonimo e spostarvi `arch300-anonymous-supplement` (oggi su account personale); aggiungere `analysis/audit_rev12/` senza `inputs/package/` (contiene il manoscritto e i testi della review) e senza `second_screening_key_DO_NOT_USE.csv` finché lo screening non è concluso.
8. **Scelta editoriale** fra full paper con le condizioni minime del revisore e short paper: dipende da 1 e 2.
