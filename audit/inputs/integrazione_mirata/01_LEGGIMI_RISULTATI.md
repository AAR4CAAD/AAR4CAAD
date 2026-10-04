# Verifiche locali completate per l’integrazione

Questi sono calcoli nuovi o riproduzioni sull’export originale, non risultati ricavati dalla sola relazione dell’agente. Nessun Word o training è stato modificato. I file non comprendono dati individuali o immagini, ma statistiche aggregate, specifica e codice.

## Fase 1 completa

Tutti i 23.012 giudizi di 166 identificativi; nessuna coppia partecipante–fotografia duplicata. Le 89 AESTHETIC sono riprodotte dalla regola sui dati completi. Per ciascuna sono disponibili n, SD e SE: da 14 a 64 giudizi; SE da 0,1533 a 0,4871 punti.

L’ICC storico dell’audit è riprodotto esplicitamente: ICC(1)=0,138184; ICC(k)=0,860065; k0=38,331948. Nel filtro 164/22.712 si ottengono 0,138146 e 0,858439, k0=37,831990. La riproduzione non certifica che il modello storico sia un modello incrociato: non lo è. La funzione nel codice riporta formula e correzione dei gradi di libertà.

## Stabilità della selezione — nuova analisi esplorativa

3.000 bootstrap dei valutatori, mantenendo le loro risposte insieme, riselezionando sulle 600 fotografie con regola congelata senza forzare 89 casi. Specifica salvata prima del calcolo dei nuovi risultati; i risultati precedenti erano conosciuti.

- Numero selezionato medio: 100.939; quantili 2,5/50/97,5%: [70.97500000000001, 100.0, 134.0].
- Frazione media delle 89 originali recuperata: 0.788004, cioè 78,8%; non equivale all’identità completa dei set.
- Jaccard medio fra set bootstrap e set originale: 0.587737; quantili 2,5/50/97,5%: [0.4859154929577465, 0.5882352941176471, 0.6880733944954128].
- Le probabilità di inclusione delle 89 originali vanno da 0,5067 a 1; mediana 0,7953.

L’insieme non è quindi invariabile. Non presentare il 78,8% come una probabilità che il training sia efficace. Le repliche, i conteggi e le probabilità individuali sono nei CSV. Verificare la convenzione del percentile con il codice storico prima di integrare; il risultato sui dati originali coincide esattamente.

## Lotti

Lotto importato il 25 settembre: 300 foto, 43 AESTHETIC e 46 CONTROL, 18.143 giudizi complessivi. Lotto del 26 settembre: 300 foto, 46 AESTHETIC e 43 CONTROL, 4.869 giudizi. Le persone possono contribuire a entrambi: non sommare le numerosità dei valutatori per stimare persone distinte. Le date sono date di importazione delle fotografie, non esclusivamente dei giudizi.

## Binomiale diretto

Il dato grezzo incluso è verificato: 677 scelte AESTHETIC su 1.320 scelte decisive contro CONTROL (51,2879%). Test esatto bilaterale H0=0,5: p=0,3637276593; IC95% Clopper–Pearson 0,4855326–0,5401675. Il test tratta i confronti come indipendenti: è una sintesi marginale, non sostituisce le analisi con partecipanti e prompt ripetuti.

## Fotografie esterne al training

Sulle 422 fotografie non appartenenti ai due dataset LoRA: Spearman fra affinità sorgente salvata e media dei rating completi = 0,396569. Con le medie filtrate storiche si riproduce 0,393121. L’affinità è proporzionale alla proiezione su u; la trasformazione positiva non cambia i ranghi. Non sono stati estratti nuovi embedding e non è stato dimostrato che gli output non contengano copie.

## Stato

**Eseguito:** tabelle per foto e lotto, riproduzione ICC storico, bootstrap della selezione, binomiale, correlazione esterna con i rating completi; controllo strutturale del docx e ricerca bibliografica mirata.

**Da eseguire nell’ambiente dell’agente:** DINOv2 su tipologia/stile oltre periodo/area con P,R e distanze coerenti; Tab. 3 completa dal modello e bootstrap v2; confronto frequenze delle aggiunte alle caption v2; conferma hardware e scala LoRA.

**Da documentare dagli autori quando non emerge dai log:** chi, strumento e istruzioni della riscrittura e revisione delle 178 caption.

**Da applicare al manoscritto dopo i nuovi risultati:** testo di abstract/conclusioni e tutte le correzioni editoriali. Nessuna nuova revisione del Word è contenuta in questo pacchetto.
