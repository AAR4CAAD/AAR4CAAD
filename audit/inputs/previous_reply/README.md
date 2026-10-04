# AAR — Allegati al riscontro tecnico al revisore

Questo pacchetto contiene verifiche riproducibili e due nuove analisi esplorative: lessico delle caption e sensibilità dei confronti a coppie includendo i pareggi. Non è il repository completo dello studio e non attesta la chiusura della major revision. Nessun training, dataset congelato o manoscritto è stato modificato.

## Input necessari per rieseguire il codice

Il pacchetto non redistribuisce l’export individuale dei partecipanti. Per rieseguire servono i quattro file originali, i cui SHA-256 sono in `verification_summary.json`:

- `FULL_EXPERIMENT_EXPORT_ARCH300_20261001-134634.zip`
- `triplet_transfer.csv`
- `source_affinity.csv`
- `results.csv`

Lo script e `caption_lexicon_v1.json` devono restare nella stessa cartella. Dipendenze usate: NumPy e SciPy; versioni effettive in `verification_summary.json`. I CSV sono UTF-8 con separatore virgola e punto decimale. I campi vuoti nei risultati lessicali indicano assenza di una definizione applicabile o di variabilità sufficiente, non uno zero.

```bash
python analisi_riscontro.py \
  --export /percorso/FULL_EXPERIMENT_EXPORT_ARCH300_20261001-134634.zip \
  --inputs /cartella_con_i_tre_csv_originali \
  --out /cartella_risultati \
  --bootstrap 3000
```

## File e interpretazione

| File | Contenuto |
|---|---|
| `01_training_manifest.csv` | 178 record congelati AESTHETIC-v2 e CONTROL-v2, con caption, composizione e motivi di selezione |
| `02_control_construction.csv` | 20 abbinamenti congiunti, 41 per tipologia, 28 completamenti casuali |
| `03_composition_by_stratum.csv` | Periodo, aree registrate, paesi, tipologie e stili; sottogruppi del controllo separati |
| `04_pairing_identifiability.csv` | Candidati AESTHETIC compatibili con le etichette; NON ricostruzione delle coppie storiche |
| `05_caption_hits.csv` | Ogni corrispondenza lessicale, termine e contesto, con segnalazione della negazione |
| `06_caption_feature_counts.csv` | Frequenze sulle 89 caption di ciascun gruppo; 31 descrittori elencati, 28 operazionalizzati lessicalmente |
| `06b_caption_presence_matrix.csv` | Presenza lessicale per caption e descrittore; NON matrice dei descrittori visivi |
| `07_caption_affinity_diagnostic.csv` | Associazione fra presenza lessicale e affinità sorgente salvata per fotografia; NON correlazione fra i 31 contrasti testo–immagine |
| `08_exact_word_counts.csv` | Conteggi di parole esatte, separati dai dizionari più ampi |
| `09_transfer_scale_check.csv` | Differenza di affinità, proiezione unitaria e rapporto di trasferimento sulle 159 triplette |
| `10_transfer_triplets.csv` | Valori delle tre misure su tutte le 192 triplette originali |
| `11_sample_counts.csv` | Perimetri Fase 1 e Fase 2, inclusione e sovrapposizione |
| `12_human_contrasts_recomputed.csv` | Ricalcolo dei contrasti umani per partecipante e sensibilità con ammissibilità dichiarata |
| `13_pairwise_counts_including_ties.csv` | Vittorie e pareggi per ciascuna coppia di condizioni |
| `14_pairwise_new_sensitivity.csv` | Modello Davidson e punteggio con mezzo punto ai pareggi; bootstrap separati per partecipante e per prompt |
| `15_final_prompts.csv` | I 48 prompt finali, negative prompt, categorie e congelamento; verificati contro le 576 generazioni |
| `16_timeline.csv` | Date e orari UTC dai record, non misure indipendenti della durata dei processi |
| `17_export_inventory.csv` | Inventario dei file realmente presenti nell’export |
| `18_source_inventory.csv` | Metadati e provenienza delle 600 fotografie, in due batch da 300; non certifica la procedura storica di campionamento |
| `19_bibliographic_verification.csv` | Riscontri su [4], [8], [10], [11], [15] e riferimento del modello dei pareggi |
| `transfer_definitions.json` | Fattore di conversione e scala di normalizzazione |
| `test_results.json` | Controlli algebrici e numerici del codice |

## Perimetro e limiti importanti

**Composizione.** Il campo originario `continent` contiene aree miste (ad esempio Japan e Middle East), non soltanto continenti. Le etichette sono conservate, non normalizzate silenziosamente. Le distribuzioni per sottogruppo non sostituiscono una nuova direzione DINOv2 corretta per composizione. Non sono disponibili in questo pacchetto le matrici a 768 dimensioni né quelle dei 31 descrittori.

**Caption.** Analisi post-review esplorativa, non preregistrata e non cieca rispetto ai precedenti grafici. Il dizionario è stato fissato prima di calcolare le nuove frequenze di questa versione e non è stato ottimizzato sui contrasti osservati. Le corrispondenze lessicali non sono punteggi CLIP né misure fotografiche. `sky_brightness`, `dark_share` e `bright_share` non vengono forzati in proxy lessicali. Colorfulness e colourful condividono il lessico: non sono due verifiche indipendenti. La categoria curve comprende forme arrotondate, archi, cupole, sfere e gusci; la sola parola curved è riportata a parte. Le negazioni sono individuate da una regola euristica dichiarata; non è un parser semantico validato. Nei dati analizzati non sono emerse negazioni di termini intercettati. Nessun test causale sulle caption è stato eseguito.

**Diagnostica affinità–lessico.** Per ogni fotografia è utilizzata l’affinità relativa già salvata in `source_affinity.csv`, con leave-one-out per i membri dei training set come nel report originale. Le correlazioni sono descrittive; non hanno intervalli inferenziali né correzioni per confronti multipli perché non sono usate come test. La colonna within_source_set centra entrambe le variabili separatamente in AESTHETIC e CONTROL. Questa diagnostica non è il confronto richiesto fra 31 contrasti testuali e 31 contrasti visivi: quello resta da eseguire sulla matrice originale.

**Rating umani.** Il confronto principale riproduce la differenza delle medie per partecipante e il test t a un campione. La sensibilità senza esclusioni che richiede almeno un voto per A e C include 168 identificativi; richiedendo almeno tre voti per ciascuna condizione se ne ottengono 167 e si riproduce il risultato aggregato precedente (circa +0,130). Le due ammissibilità sono mostrate entrambe: la corrispondenza numerica non dimostra che sia stato recuperato il codice originale. Non è stato ricalcolato l’ICC, la cui implementazione nel disegno incompleto resta da documentare.

**Pareggi.** Il modello Davidson è una nuova sensibilità: un parametro comune di propensione al pareggio, abilità relative delle tre condizioni, BASE come riferimento. Formula: pesi proporzionali a exp(theta_i), exp(theta_j), nu·exp((theta_i+theta_j)/2). Tutte le 4.736 risposte incluse vengono utilizzate. Gli intervalli percentili al 95% provengono da 3.000 ricampionamenti di cluster; una serie ricampiona 158 partecipanti e una serie 48 prompt. Non sono bootstrap congiunti né un modello completo a effetti casuali incrociati. Nessuno dei due risolve la mancanza di repliche umane fra seed di training. Gli OR riguardano le abilità relative del modello su tutte e tre le coppie, non il semplice rapporto di vittorie di una singola coppia. Il punteggio con mezzo punto ai pareggi è invece una sintesi descrittiva diretta.

**Screening ed etica.** Nessun secondo valutatore umano è stato reclutato o sostituito con un’AI. Non è stata ottenuta documentazione istituzionale di approvazione/esenzione. Il presente pacchetto non dichiara chiusi questi punti.
