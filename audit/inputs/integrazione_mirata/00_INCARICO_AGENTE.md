# AAR — Integrazione mirata dopo l’audit v2

## Mandato e perimetro

Parti dall’audit rev12 v2 e dal manoscritto revisione 13. Completa esclusivamente l’elenco dell’autore riportato qui. Non ricominciare l’audit generale, non avviare nuovi training o nuovi questionari e non modificare dati, selezione o campioni storici. Questa consegna riguarda nuovi calcoli sui dati esistenti e documentazione. La successiva integrazione nel Word è separata e deve restare entro 15 pagine senza ridurre la leggibilità.

Il centro del paper resta la traccia del repertorio AESTHETIC della Fase 1 negli output. Gli esiti nuovi determinano la portata delle affermazioni; non scegliere specificazioni in funzione del segno o della significatività. La persistenza del contrasto risponde alla priorità del reviewer, ma non garantisce l’accettazione editoriale.

## 1. Priorità: DINOv2 aggiustato anche per tipologia e stile

Usa le matrici già identificate nel tuo ambiente:
- `analysis/metrics/embeddings_dinov2_vitb14.npz`;
- `analysis/metrics/embeddings_replication_dinov2_vitb14.npz`;
- `analysis/baseline/direction_dinov2.npz`;
- metadati e manifest originali.

Non dichiararle mancanti perché non erano comprese negli ZIP inviati all’altro assistente. Non ricavare embedding dai grafici. Mantieni identici preprocessing, fotografie, output, condizioni e identificativi.

Confronta: (i) direzione originale; (ii) periodo + area già effettuato; (iii) periodo + area + tipologia + stile. L’ultimo elenco dell’autore non richiede di estendere anche all’autore dell’edificio: non aggiungere automaticamente quel controllo.

Prima dei nuovi risultati salva la specifica: codifica dei metadati, modello, campione, normalizzazione, unità di ricampionamento e trattamento delle categorie rare. I metadati grezzi hanno 236 stringhe di tipologia (182 presenti una sola volta) e 206 di stile (133 presenti una sola volta). Sono stringhe del catalogo, non necessariamente categorie ontologiche distinte: verifica alias, rango del modello, numerosità per categoria e sovrapposizione A/C. Non unire o separare categorie per ottenere un esito favorevole e non presentare un aggiustamento saturo come identificazione di un effetto autonomo.

Per ciascuna direzione e per ciascuno dei tre training seed 1254, 9865, 42160, consegna:
- norma del contrasto fotografico d e coseno con la direzione originale;
- proiezioni P di A−C, A−BASE e C−BASE, con IC95%;
- R, denominatore esplicito e controllo della sua stabilità;
- ΔD verso il proprio corpus e l’altro, distinguendo media delle distanze individuali e distanza fra centroidi; contrasto proprio−altro;
- 192 celle con stesso prompt/generation seed; sintesi descrittiva dei seed distinta dall’inferenza su futuri training.

**Vincolo geometrico:** cambiare soltanto u non produce un ΔD “residuo”. La residualizzazione per regressione sulle righe delle fotografie non può essere applicata agli output assegnando tipologie o stili inventati. Per P/R puoi estendere la sensibilità precedente, dichiarando che si proiettano output originali su una direzione fotografica aggiustata. Per ΔD residuo definisci e congela una trasformazione comune nello spazio degli embedding, stimata sulle sole fotografie e applicabile identicamente a fotografie e output, oppure una diversa procedura giustificata che renda confrontabili le distanze. Dichiara esplicitamente se questa geometria differisce da quella usata nel precedente aggiustamento; riporta P/R coerenti con essa e non mescolare denominatori o centroidi di spazi diversi. Non presentare semplicemente la distanza tra un output grezzo e un centroide residualizzato come “avvicinamento depurato”.

Documenta gli IC condizionati alla direzione stimata. Non riutilizzare senza verifica i precedenti quantili del bootstrap delle fotografie come IC definitivi del rapporto. Non cercare una soglia che renda il risultato “positivo”: mostra stime e incertezza anche in caso di attenuazione.

Output: `dino_aggiustamento_completo.csv`, specifica, codice e breve interpretazione dei risultati effettivi.

## 2. Affidabilità della selezione: verifiche locali già disponibili

Questo pacchetto contiene nuovi calcoli su tutti i 166 valutatori / 23.012 giudizi. Riproducili e verifica la regola contro il codice storico, invece di duplicarli con un criterio diverso:
- conteggio di giudizi e valutatori distinti, media, SD campionaria e SE per ciascuna delle 89 AESTHETIC; disponibile anche il file delle 600;
- estimatore ICC storico riprodotto e dichiarato, completo e filtrato separati;
- 3.000 bootstrap dei valutatori, con tutte le loro risposte conservate insieme e selezione ricalcolata sulle 600 fotografie. Il numero selezionato non è forzato a 89. La specifica è nel JSON;
- conteggi per lotto del 25 e del 26 settembre, usando importazione e `corpus_batch`, non il giorno di compilazione del questionario.

Verifica il percentile e i filtri della regola eseguita; la riproduzione sui dati originali restituisce esattamente le 89 AESTHETIC. Le copie bootstrap di un valutatore devono conservare la loro molteplicità. Le frequenze di inclusione misurano stabilità interna della selezione, non generalizzazione a popolazioni nuove. Non usare il leave-one-out top-89 come sostituto di questa regola se impone cardinalità diversa.

L’ICC qui riprodotto è quello ANOVA a una via dopo centratura per valutatore e correzione dei gradi di libertà usato nell’audit; non rinominarlo ICC di un modello incrociato. Riporta formula, k0, numerosità e limite dell’estimatore sul disegno incompleto. Un risultato ottenuto con un estimatore diverso deve essere etichettato separatamente.

## 3. Caption v2: documentazione, non un nuovo training

Conferma 89 fotografie e 89 caption in ciascuna condizione. Distingui:
1. copertura finale: 178 immagini con caption;
2. testi materialmente modificati tra snapshot v1/v2: 89 AESTHETIC, 62 CONTROL;
3. eventuale revisione umana dell’intero insieme, anche quando il testo è stato confermato senza modifica.

La presenza di 27 testi invariati non dimostra che siano stati ignorati. Recupera chi ha redatto/revisionato, strumento, versione, istruzioni e applicazione all’intero insieme dai record o dalla dichiarazione esplicita degli autori. Non trasformare la richiesta di descrivere un’applicazione alle 178 immagini in un fatto già documentato.

Quantifica che cosa è stato **aggiunto** in v2, confrontando v1 e v2 con lo stesso dizionario: 0→1, 1→0 e invariato per descrittore e corpus. Le frequenze finali da sole non sono frequenze delle aggiunte. Se alcune informazioni non risultano dai record, poni soltanto una domanda raccolta all’autore su chi/strumento/istruzioni/copertura; non inventare il workflow.

## 4. Verifica sulle fotografie non usate nella LoRA

L’analisi delle 422 fotografie esterne ai due training set esiste già. Il pacchetto riproduce ρ=0,39312 con i rating filtrati storici e ρ=0,39657 con tutti i giudizi dei 166 partecipanti. L’affinità sorgente salvata è proporzionale alla proiezione su u e dà gli stessi ranghi. Verificala sulle matrici originali e usa nel testo il perimetro corretto.

Recupera e riporta anche dispersione intra-corpus, sua definizione (media delle distanze oppure RMS, senza confonderle) e confronto A/C con l’incertezza disponibile.

Questo controllo verifica che la direzione fotografica sia associata ai rating anche fuori dai dataset LoRA. **Non prova da solo che gli output non memorizzino esempi.** Denominalo verifica fuori training della direzione, senza promettere assenza di memorizzazione. Non serve creare un nuovo held-out ad alto rating se quello richiesto come alternativa è già sufficiente; qualunque subset aggiuntivo deve avere criterio fissato prima degli esiti. Held-out dalla LoRA non implica assenza dal pretraining di SDXL.

## 5. Tabella umana completa e criteri di inclusione

Mantieni le stesse specificazioni già dichiarate nell’audit v2 e completa tutti i contrasti A−C, BASE−C e A−BASE:
- test per partecipante originale;
- modello misto con intercette incrociate già usato;
- bootstrap partecipanti×prompt corretto, con molteplicità dei partecipanti conservata nella media finale;
- modello Davidson già disponibile, con pareggi.

Per A−BASE nel modello misto usa il contrasto lineare e la matrice di covarianza dei coefficienti: non sottrarre i limiti di due IC. Nel bootstrap ricava tutti i contrasti dalle stesse replicazioni e riporta eventuali repliche senza dati ammissibili.

Verifica e conserva il binomiale diretto incluso qui: 677/1320, 51,2879%, p bilaterale esatto 0,3637276593; IC95% Clopper–Pearson 48,5533–54,0167%. È una sintesi marginale che assume confronti indipendenti: dichiaralo e non usarlo in sostituzione dell’inferenza che considera giudizi ripetuti.

Definisci operativamente “filtro globale” e “Fase 2 incompleta” sulla base dei campi/sessioni/codice originali, distinguendo flag dell’export, motivo manuale e regola d’analisi. Non invalidare retroattivamente la Fase 1 e non introdurre nuovi criteri di esclusione.

Output unico `tabella3_completa.csv`, con una riga per contrasto/metodo, unità, n, stima, IC e p quando appropriato.

## 6. Hardware, calendario e dettagli mancanti

Recupera hardware effettivo e scala LoRA applicata in inferenza dal worker e dai job: alpha/rank non è automaticamente la stessa cosa della scala esterna in generazione. Non usare i default di una libreria come prova della configurazione storica.

Chiarisci 599/600 (copertura dei gruppi, non rimozione di una fotografia), ultimo voto/ultimo confronto Fase 2 e chiusura amministrativa: un ultimo timestamp non dimostra da solo che il questionario fosse chiuso.

## 7. Cosa NON deve fare l’agente in questa consegna

Non riscrivere tutto il paper; non riproporre il controllo caption neutre come nuova attività in questo incarico; non modificare il campione storico; non promettere l’accettazione; non chiamare equivalenti AESTHETIC e BASE in assenza di un test d’equivalenza; non trasformare il risultato dei 20 casi in una prova che i 28 casuali causino tutto il trasferimento.

## Consegna

Un solo ZIP aggiornato con:
1. `RISCONTRO_INTEGRAZIONE.md`, risposta breve nell’ordine di questo incarico, con risultati reali;
2. tabella DINOv2 completa e Tab. 3 completa;
3. verifica delle tabelle locali e degli eventuali scarti;
4. riepilogo caption v1→v2 e campi mancanti soltanto agli autori;
5. codice, specifica e hash degli input; includi le matrici redistribuibili o indica esattamente come trasferirle senza ricavare dati da grafici;
6. elenco di sostituzioni mirate per abstract, risultati e conclusioni, basate sull’esito e senza applicarle ancora al Word.

Le correzioni bibliografiche, i sei “Si” formattati come S_i, le 11 immagini obsolete e la proprietà abstract vecchia saranno integrate nel documento insieme ai risultati. Non attribuire una proprietà scientifica al vincolo di 15 pagine.
