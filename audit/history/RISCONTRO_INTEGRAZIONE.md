# Riscontro all'incarico di integrazione mirata (4 ottobre 2026)

Perimetro: solo i punti dell'elenco in `00_INCARICO_AGENTE.md`. Nessun training, nessun questionario, nessuna modifica a dati, selezione o campioni. Nuovi calcoli in `integrazione/` (script `scripts/b0*.py`, specifiche salvate prima dei risultati, log in `logs/`). Le analisi sono post-review; dove un esito attenua il risultato lo si riporta così com'è.

## 1. DINOv2 aggiustato anche per tipologia e stile — `dino_aggiustamento_completo.csv`, `report_dino_aggiustamento_completo.md`, `SPEC_dino_aggiustamento_completo.json`

Matrici del progetto (1176×768 e 960×768, direzione congelata d = 0,235229), stesso preprocessing. Metadati: periodo (pre-1919 unito a 1919–45), area (8 etichette), tipologia (236 stringhe → 35 con ≥ 3 fotografie + livello «rara», 220 foto) e stile (205 → 41 + «raro», 197 foto); nessuna fusione di alias; A e C condividono 27 tipologie su 49/47 e 15 stili su 46/52. Modello additivo OLS per dimensione sulle 600 fotografie: rango pieno (12 colonne per (ii), 88 per (iii)).

Due geometrie dichiarate e mai mescolate. **G1** (come nell'audit): output originali proiettati sulla direzione fotografica aggiustata; nessuna distanza. **G2**: trasformazione lineare comune T = I − Π (Π proiettore sulle direzioni degli effetti delle covariate, stimata sulle sole fotografie, applicata identicamente a fotografie e output): direzione, P, R e distanze tutti in T-spazio; dimensioni rimosse 11 per (ii) e 87 per (iii) (18,6% e 57,4% della varianza delle fotografie).

| direzione | geom. | d | cos | P A−C 1254 / 9865 / 42160 | media 3 seed | R (media) |
|---|---|---|---|---|---|---|
| (i) originale | G1=G2 | 0,2352 | 1,000 | +0,0435 / +0,0412 / +0,0504 (IC > 0) | +0,0451 [+0,032; +0,059] | 0,192 |
| (ii) periodo+area | G1 | 0,2092 | 0,982 | +0,0437 / +0,0380 / +0,0454 (IC > 0) | +0,0423 [+0,030; +0,056] | 0,202 |
| (ii) periodo+area | G2 | 0,1623 | — | +0,0274 / +0,0181 / +0,0201 (IC > 0) | +0,0219 [+0,015; +0,030] | 0,135 |
| (iii) +tipologia+stile | G1 | 0,1603 | 0,925 | +0,0427 / +0,0355 / +0,0439 (IC > 0) | +0,0407 [+0,030; +0,053] | 0,254 |
| (iii) +tipologia+stile | G2 | 0,1005 | — | +0,0148 / +0,0089 / +0,0106 (IC > 0) | +0,0114 [+0,008; +0,016] | 0,114 |

A−BASE e C−BASE per seed nel CSV. Lettura: in G1 la proiezione degli output cambia poco (il contrasto fotografico residuo ha coseno 0,93 con l'originale) e R sale perché cala il denominatore (d 0,235 → 0,160): non è un aumento del trasferimento. In G2, che rimuove dagli output le stesse direzioni, P e R si riducono (R 0,19 → 0,135 → 0,114) e restano positivi con IC > 0 per ogni seed; l'attenuazione è attesa per costruzione perché le direzioni rimosse contengono anche differenze genuine fra i corpora allineate a tipologia e stile. **Distanze (solo G2)**: in (ii) e (iii) le adapter AESTHETIC si avvicinano al proprio centroide in un seed su tre (distanza media per immagine; seed 1254) e in due (ii) o tre (iii) seed su tre (centroide-centroide), ma il contrasto proprio−altro si riduce a −0,001/−0,002 (IC che includono o sfiorano zero): l'avvicinamento specifico al proprio corpus osservato nello spazio originale non sopravvive alla rimozione delle direzioni di composizione; per CONTROL proprio−altro −0,001/−0,004 (IC < 0 in 5 casi su 6, valori piccoli). Stabilità del denominatore (ricampionamento delle due serie di fotografie): d_T (iii) fra 0,100 e 0,127 (quantili, non IC di R).

Conclusione per il testo: il contrasto A−C lungo la direzione sorgente persiste con segno positivo in ogni specificazione e seed; la sua grandezza relativa dipende dalla geometria scelta (0,11–0,25); l'avvicinamento differenziale di AESTHETIC al proprio corpus è un risultato dello spazio non aggiustato e non va più presentato come robusto alla composizione. L'aggiustamento è additivo su stringhe di catalogo, con livelli rari aggregati: non identifica un effetto autonomo della preferenza.

## 2. Verifiche locali — `verifica_tabelle_locali.csv`, `report_verifiche_locali.md`, `stabilita_bootstrap_riprodotta.csv`, `stabilita_inclusione_per_foto.csv`

Riprodotti esattamente: statistiche per fotografia (600 righe, differenza massima 0), range n 14–64 e SE 0,153–0,487 delle 89; ICC storico completo 0,138184/0,860065 (k0 38,33) e filtrato 0,138146/0,858439 (k0 37,83), con MS e df identici; lotti 300/18.143/166 e 300/4.869/54, 43/46 e 46/43; binomiale 677/1320, p 0,3637276593, CP 0,485533–0,540167; ρ fuori training 0,396569 (completo) e 0,393121 (filtrato) **sulle matrici**, con Spearman(affinità salvata, proiezione su u) = 1 sulle 422.

Regola: il codice storico (`SelectionService.Evaluate`) calcola il percentile sulle immagini **ammissibili** (attive, n ≥ 10) con interpolazione lineare; la specifica del pacchetto usa tutte le attive. Sui dati originali entrambe danno le 89 (cutoff 4,562 < 5, registrato 4,563). Bootstrap dei valutatori (3.000, molteplicità conservata, seed diverso) con entrambe le convenzioni: cardinalità media 101,4/101,6 (pacchetto 100,9), quantili 72/101/135, recupero 0,794/0,792 (0,788), Jaccard 0,592/0,590 (0,588), inclusione delle 89 min/mediana/max 0,506/0,801/1,000 (0,507/0,795/1,000); correlazione delle probabilità per immagine con il pacchetto 0,9998. Distribuzioni coincidenti entro l'errore Monte Carlo. Lettura: stabilità interna della selezione sotto ricampionamento dei valutatori (l'insieme non è invariabile: Jaccard ≈ 0,59), non generalizzazione a nuove popolazioni.

## 3. Caption v2 — `report_caption_v1_v2.md`, `caption_v1_v2_transizioni.csv`, `caption_v1_v2_copertura.csv`

Copertura: 89 + 89 caption v2. Testi materialmente diversi fra snapshot v1 e v2: 89/89 AESTHETIC, 62/89 CONTROL. Revisione: tutte le 178 caption correnti hanno `reviewed = true` (admin 151, researcher 27), `source = Imported`, campo `model` vuoto; i **27 testi CONTROL invariati portano solo il timestamp di revisione della fase v1 (27/09 20:48)** e nessun evento di rilettura durante la riscrittura v2 (28/09 01:28–01:29): i record non documentano una riconferma sotto le istruzioni v2. Workflow visibile: 1–9 versioni per fotografia, prime bozze in italiano, testi inglesi importati da CSV, 554 `caption.changed` e 444 `caption.reviewed` da due account fra il 27/09 13:48 e il 28/09 01:29.

Aggiunte v1→v2 (stesso lessico dell'audit; conteggi di caption 0→1 / 1→0): AESTHETIC — greenery +37/−1, white +32/−1, people +13/0, curve +13/−5, water +11/0, low_angle +6/−1, cars +6/0; rimozioni urban −39 (50→14), concrete −16 (31→17), contemporary −10 (10→0), complex_form −8; CONTROL — white +12, poche altre variazioni (urban −3, brightness −6, contemporary −3). La riscrittura ha quindi **aggiunto soprattutto all'AESTHETIC** vegetazione, bianco, persone, forme curve e acqua, e **tolto** termini urbani e «contemporary»/«concrete»; le differenze lessicali finali fra i corpora (acqua 28/10, curve 37/27, persone 15/9) nascono in buona parte dalle aggiunte v2 all'AESTHETIC. Le frequenze finali non sono frequenze delle aggiunte.

Domanda unica per gli autori: chi ha prodotto i testi inglesi v1 e la riscrittura v2 (persona/strumento e versione), con quali istruzioni scritte, se identiche per i due corpora, e se i 27 testi CONTROL invariati sono stati riletti sotto le istruzioni v2.

## 4. Fotografie non usate nella LoRA — in `verifica_tabelle_locali.csv` (sezioni fuori_training, dispersione)

ρ = 0,3966 (166/23.012) e 0,3931 (perimetro filtrato) riprodotti dalle matrici; l'affinità salvata è una trasformazione affine positiva della proiezione (stessi ranghi). Dispersione intra-corpus (definizioni distinte): RMS dalla propria media A 0,910 vs C 0,923 (differenza −0,013, bootstrap −0,035/+0,008); distanza media dal centroide 0,906 vs 0,921 (−0,015, −0,039/+0,007); distanza media a coppie 1,287 vs 1,309 (−0,021, −0,054/+0,009); dispersione RMS aggregata 0,916 → d/dispersione = 0,257 (il «0,26»). Nome corretto: **verifica fuori training della direzione sorgente**; non prova l'assenza di memorizzazione negli output e «held-out» riguarda la LoRA, non il pretraining di SDXL.

## 5. Tab. 3 completa — `tabella3_completa.csv`, `report_tabella3.md`

| contrasto | t per partecipante | misto incrociato (contrasto lineare, cov. coefficienti) | bootstrap due vie (stesse repliche) | BT OR (cluster) | Davidson OR (cluster) | Davidson OR due vie | binomiale marginale |
|---|---|---|---|---|---|---|---|
| A−C | +0,104 [+0,029; +0,178] p ,0067 | +0,101 [+0,016; +0,186] p ,020 | +0,104 [−0,019; +0,237] | 1,090 [0,985; 1,206] p ,096 | 1,089 [0,985; 1,205] p ,095 | 1,089 [0,909; 1,306] | 677/1320 = 51,3% [48,6; 54,0] p ,364 |
| BASE−C | +0,140 [+0,068; +0,212] p ,0002 | +0,134 [+0,049; +0,219] p ,002 | +0,140 [+0,000; +0,278] | 1,133 [1,039; 1,237] p ,005 | 1,133 [1,038; 1,237] p ,005 | 1,133 [0,944; 1,357] | 728/1349 = 54,0% [51,3; 56,7] p ,004 |
| A−BASE | −0,036 [−0,108; +0,035] p ,31 | −0,033 [−0,118; +0,052] p ,44 | −0,036 [−0,162; +0,100] | 0,962 [0,874; 1,058] p ,42 | 0,961 [0,874; 1,058] p ,42 | 0,961 [0,795; 1,149] | 669/1341 = 49,9% [47,2; 52,6] p ,96 |

Bootstrap a due vie: 2.000 repliche, molteplicità dei partecipanti conservata nella media esterna, tre contrasti dalle stesse repliche, 0 repliche senza dati ammissibili, 0 partecipanti estratti scartati in media; l'intervallo A−C (−0,019/+0,237) differisce da quello dell'audit v2 (−0,025/+0,233) per il solo flusso casuale. Il binomiale assume confronti indipendenti: sintesi marginale, non sostituisce le inferenze con partecipanti e prompt ripetuti; verificato 677/1320, p 0,3637276593, CP 48,55–54,02%. Nessun test d'equivalenza: A−BASE va descritto come «nessun vantaggio chiaro», non come equivalenza. Definizioni operative di «filtro globale» (flag `participants.excluded_from_analysis`, 18 partecipanti, motivi registrati) e «Fase 2 incompleta» (motivo manuale «non finito/non completo/…», sessioni non Completed) in `report_tabella3.md`; nessun criterio nuovo.

## 6. Hardware, calendario, dettagli — `report_hardware_calendario.md`

GPU NVIDIA L4 (L4-1-24G), Python 3.10.12, torch 2.4.1+cu121, diffusers 0.30.3, peft 0.12.0, transformers 4.44.2 (ambiente registrato in 34/37 job). Scala LoRA in inferenza: `lora_scale` nullo in tutti i 1.536 record → `set_adapters` non chiamato → peso adapter 1,0; alpha/rank = 16/16 = 1 → contributo ΔW·1,0 (letto dal codice del worker e dai record, non dai default). 599/600 = copertura degli architetti (599 fotografie valutate), non rimozione. Ultimo rating Fase 2 01/10 11:55:54, ultimo confronto 11:52:17, chiusura amministrativa (stato → Analysis) 12:52:27, export 13:46; 15 sessioni Active mai concluse, 3 Abandoned.

## Stato

**Eseguito e verificato:** 1 (tre direzioni × due geometrie × tre seed, P/R/ΔD con IC), 2 (tutte le tabelle locali riprodotte; scarti solo Monte Carlo), 3 (copertura, modifiche, revisione, aggiunte 0→1/1→0), 4 (ρ sulle matrici; dispersione A/C), 5 (Tab. 3 completa), 6 (hardware, scala, calendario). **Spetta agli autori:** la risposta alla domanda unica sulle caption. **Non fatto per mandato:** training a caption neutre, modifiche al Word.
