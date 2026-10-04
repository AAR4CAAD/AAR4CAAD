"""Second pass (2026-10-03 evening): propagates the corrections of the external control into RISPOSTA_REVIEWER.md and
PATCH_MANOSCRITTO.md. Kept for traceability; idempotent."""
import os

from common import AUDIT


def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for old, new in pairs:
        if old not in s:
            print("NOT FOUND in", os.path.basename(path), ":", old[:70]); continue
        s = s.replace(old, new)
    open(path, "w", encoding="utf-8").write(s)


R = os.path.join(AUDIT, "RISPOSTA_REVIEWER.md")
s = open(R, encoding="utf-8").read()
head = "# Risposta al revisore — basata sui risultati ottenuti dall'audit indipendente (revisione 12)"
if "versione 2" not in s:
    s = s.replace(head, head + " — versione 2\n\n**Versione 2 (3 ottobre 2026, sera):** integra il controllo esterno `AAR_correzioni_puntuali_audit.zip` (vedi `CORREZIONI_SECONDO_PASSAGGIO.md`): corretto l'intervallo del bootstrap a due vie dei rating, corrette le etichette delle componenti di varianza, riformulate le distanze dai corpora con entrambe le metriche e relativi IC, protocollo caption rivisto. Ogni sezione è marcata **[confermato]** (risultato ottenuto e verificato) o **[da eseguire]** (richiede nuova raccolta, training o decisione).")
a, b = s.find("**Avvicinamento ai corpora (test esplicito, due spazi).**"), s.find("## 7. Agentività")
if a > 0:
    new_dist = """**Avvicinamento ai corpora (test esplicito, due spazi, due metriche).** Le due metriche rispondono a domande diverse e sono riportate entrambe con IC bootstrap sui prompt (`dino_distance_changes.csv`, `dino_centroid_distance_changes.csv`, `descriptors_distance_changes.csv`, `descriptors_centroid_distance_changes.csv`): (i) **distanza fra centroidi** (posizione media degli output rispetto al centroide delle fotografie); (ii) **distanza media delle singole immagini** dal centroide (posizione e dispersione insieme).

| spazio | metrica | AESTHETIC (seed 1254 / 9865 / 42160) | CONTROL (seed 1254 / 9865 / 42160) |
|---|---|---|---|
| DINOv2 | centroide→centroide, Δ vs BASE | verso il proprio corpus −0,053 / −0,040 / −0,049 (IC < 0); verso CONTROL −0,028 / −0,014 (n.s.) / −0,031 | verso il proprio −0,042 / −0,053 (IC < 0) / −0,009 (n.s.); verso AESTHETIC −0,035 / −0,047 (IC < 0) / +0,004 (n.s.) |
| DINOv2 | media immagine→centroide, Δ vs BASE | verso il proprio −0,015 / −0,008 / −0,010 (IC < 0); verso CONTROL n.s.; «proprio − altro» −0,011 / −0,011 / −0,009 (IC < 0) | verso il proprio −0,007 (IC < 0) / +0,001 / −0,003 (n.s.); «proprio − altro» −0,001 (n.s.) / +0,000 (n.s.) / **−0,005 (IC < 0)** |
| 31 descrittori | centroide→centroide, Δ vs BASE | verso il proprio −0,24 (n.s.) / −0,42 (IC < 0) / −0,07 (n.s.) | verso il proprio −0,50 / −1,16 / −0,92 (IC < 0); verso AESTHETIC −0,33 / −0,86 / −0,43 (IC < 0) |
| 31 descrittori | media immagine→centroide, Δ vs BASE | −0,01 / +0,11 / +0,20 (tutti n.s.); «proprio − altro» n.s. | verso il proprio −0,25 / −0,53 / −0,33 (IC < 0); «proprio − altro» −0,09 / −0,17 / −0,22 (IC < 0) |

Formulazioni sostenute. **DINOv2**: le adapter AESTHETIC si avvicinano al centroide del proprio corpus in entrambe le metriche e in tutti i seed, e più di quanto si avvicinino a quello CONTROL; le adapter CONTROL si avvicinano a entrambi i centroidi in due seed su tre (metrica dei centroidi) e **non mostrano un avvicinamento differenziale coerente nei tre seed** (metrica delle immagini: un seed su tre con IC < 0). **Descrittori**: la distanza fra il centroide degli output AESTHETIC e il profilo delle proprie fotografie si riduce descrittivamente nei tre seed, in modo statisticamente chiaro in uno; la distanza media delle singole immagini AESTHETIC non si riduce in modo chiaro (IC che includono zero: assenza di evidenza, non evidenza di assenza); CONTROL mostra una riduzione consistente in entrambe le metriche, maggiore verso il proprio profilo. Le due geometrie non concordano su quale adapter si muova di più verso il proprio repertorio; la causa non è identificata. r(x,a) ≈ 0 non era il test di avvicinamento. **[confermato]**

"""
    s = s[:a] + new_dist + s[b:]
open(R, "w", encoding="utf-8").write(s)
sub(R, [
    ("**Il termine CONTROL vale il 101% della covarianza del contrasto** (bootstrap sui prompt 73–139%; sui descrittori 31–174%); il termine AESTHETIC è nullo.",
     "**Il termine CONTROL vale, come stima puntuale, il 101% della covarianza del contrasto** (bootstrap sui prompt 73–139%; sui descrittori 31–174%); la stima del termine AESTHETIC è −1,5% con intervallo che include zero (r(x,a) = −0,006, IC −0,14/+0,13 sui prompt). È un rapporto di covarianze, non una percentuale di «apprendimento» o di immagini trasferite."),
    ("| bootstrap a due vie partecipanti × prompt (pigeonhole) della media per partecipante | +0,104 | **−0,008 / +0,220** |",
     "| bootstrap a due vie partecipanti × prompt (pigeonhole) della media per partecipante — **corretto in v2** (media esterna ponderata per la molteplicità dei partecipanti estratti; la v1, −0,008/+0,220, contava una sola volta ogni identificativo estratto) | +0,104 | **−0,025 / +0,233** |"),
    ("Il modello incrociato (componenti di varianza: partecipante 0,44, cella 0,07, immagine 1,05, residuo 1,54) conserva il contrasto; il bootstrap a due vie — che include la variabilità fra prompt in modo conservativo — non lo distingue da zero.",
     "Il modello incrociato (componenti di varianza lette dal modello: **partecipante 1,05, cella prompt×seed 0,44, immagine 0,07**, residuo 1,54; in v1 le etichette erano scambiate) conserva il contrasto; il bootstrap a due vie — che include la variabilità fra prompt in modo conservativo (pigeonhole) — non lo distingue da zero. **La robustezza dipende dalla specificazione**: i due strumenti non sono equivalenti e non si può scrivere che qualsiasi inferenza con i prompt annulli l'effetto."),
    ("Il contrasto umano resiste al modello incrociato (p ,02) ma non al bootstrap a due vie; le coppie restano nulle in ogni analisi. Le conclusioni computazionali tengono; quella umana va indebolita ulteriormente.",
     "Il contrasto umano resiste al modello incrociato (p ,02) ma non al bootstrap a due vie (−0,025/+0,233): la robustezza dipende dalla specificazione; le coppie non mostrano vantaggio in alcuna analisi. Le conclusioni computazionali tengono nella specificazione provata (la sensibilità alla composizione è lineare e limitata alle variabili registrate: sostiene la persistenza del contrasto, non l'irrilevanza causale della composizione); quella umana va indebolita ulteriormente."),
    ("Il trasferimento DINOv2 non cambia con la direzione aggiustata per periodo e geografia (R 0,19–0,20) ed è specifico: le adapter AESTHETIC si avvicinano al proprio corpus più che all'altro in tutti e tre i seed. Nei descrittori, invece, il r = +0,71 è spiegato dal movimento di CONTROL (≈ 100% della covarianza) e AESTHETIC non si avvicina al proprio profilo.",
     "Il trasferimento DINOv2 non cambia con la direzione aggiustata per periodo e geografia (R 0,192 → 0,196/0,200/0,202; cambia anche il denominatore d_adj) ed è specifico in quello spazio: le adapter AESTHETIC si avvicinano al centroide del proprio corpus più che all'altro in tutti e tre i seed. Nei descrittori il r = +0,71 è spiegato dal movimento di CONTROL (stima ≈ 100% della covarianza); l'avvicinamento di AESTHETIC al proprio profilo dipende dalla metrica (centroidi: riduzione descrittiva, chiara in un seed; immagini: non distinguibile da zero)."),
    ("(≈ 18–20% della separazione, stabile su tre seed accoppiati, robusto all'aggiustamento per periodo e area, con avvicinamento specifico dell'adapter AESTHETIC al proprio corpus); nei 31 proxy visivi",
     "(18% sulle 159 triplette originali; 19–20% in media sulle tre repliche; stabile su tre seed accoppiati; invariato con la direzione aggiustata per periodo e area; con avvicinamento dell'adapter AESTHETIC al centroide del proprio corpus in quello spazio); nei 31 proxy visivi"),
    ("che non sopravvive a un'inferenza che includa la variabilità fra prompt,", "che resiste a un modello con effetti casuali incrociati ma non a un bootstrap a due vie partecipanti×prompt,"),
    ("Fino ad allora il trattamento va descritto come «corpus di fotografie con le rispettive caption».",
     "Fino ad allora il trattamento va descritto come «corpus di fotografie con le rispettive caption». Versione 2 del protocollo (dopo il controllo esterno): stringa comune `photograph of architecture` (verificata sui 178 riferimenti: la v1 era falsa per 2 e impropria per 10), worker bloccato all'hash storico `266541cf…`, tre quantità separate (stima neutra, incertezza, differenza appaiata fra regimi) e categorie di lettura con «inconclusivo», nessuna soglia di rilevanza; script di analisi scritto e collaudato in dry run; costo aggiornato ≈ 6,0–6,6 € (0,79 €/h verificato), ≈ 7,5 ore GPU, ≈ 4–4,5 ore di calendario. **[da eseguire]**"),
    ("## 1. Seed di training e confronto umano (review a; replica 1)", "## 1. Seed di training e confronto umano (review a; replica 1) — [confermato come limite]"),
    ("## 2. CONTROL: matching reale e sensibilità della composizione (review b; replica 2; condizione minima)", "## 2. CONTROL: matching reale e sensibilità della composizione (review b; replica 2; condizione minima) — [confermato]"),
    ("## 3. Fig. 1 e testo: S, P, R (review c; replica 3)", "## 3. Fig. 1 e testo: S, P, R (review c; replica 3) — [confermato]"),
    ("## 4. Caption (review d; replica 4; condizione «training a caption controllate»)", "## 4. Caption (review d; replica 4; condizione «training a caption controllate») — [analisi lessicale confermata; training da eseguire]"),
    ("## 5. Campioni e cronologia (review minore; replica 5; «problemi nuovi 2–4»)", "## 5. Campioni e cronologia (review minore; replica 5; «problemi nuovi 2–4») — [confermato; costruzione del corpus da dichiarare]"),
    ("## 6. Sonde: contributo di CONTROL e distanze vere dai corpora (review i; replica 6)", "## 6. Sonde: contributo di CONTROL e distanze vere dai corpora (review i; replica 6) — [confermato; formulazioni corrette in v2]"),
    ("## 7. Agentività, personalizzazione (review g; replica 7)", "## 7. Agentività, personalizzazione (review g; replica 7) — [confermato]"),
    ("## 8. Statistica umana: unità di analisi e filtri (review h e minori; replica 8; «problemi nuovi 5–6»)", "## 8. Statistica umana: unità di analisi e filtri (review h e minori; replica 8; «problemi nuovi 5–6») — [confermato; bootstrap corretto in v2]"),
    ("## 9. Riproducibilità, figure, bibliografia (review f; replica 9)", "## 9. Riproducibilità, figure, bibliografia (review f; replica 9) — [contenuti confermati; deposito e figure da eseguire]"),
    ("## 10. Adempimenti (replica 10)", "## 10. Adempimenti (replica 10) — [da eseguire: responsabile]"),
    ("Non riprodotti in questo audit (letti dal report storico): le quote 8/33/57/65% e il residuo 0,166.", "Non riprodotti in questo audit (letti dal report storico): le quote 8/33/57/65% e il residuo 0,166 — l'analisi computazionale non è quindi dichiarata integralmente replicata."),
    ("ricampionando le fotografie la quota è 0,11–0,18", "ricampionando le fotografie i quantili della quota sono 0,11–0,18 (incertezza della direzione, distinta dagli IC sui prompt; la norma del bootstrap è distorta verso l'alto: calibrazione da verificare prima di usarli come IC)"),
    ("Incertezza della direzione (ricampionando le 89+89 fotografie): R fra 0,11 e 0,18 per tutte le versioni.", "Incertezza della direzione (ricampionando le 89+89 fotografie): quantili di R fra 0,11 e 0,18 per tutte le versioni — misura dell'incertezza della direzione, non IC sostitutivo della stima puntuale (0,192), e distorta verso il basso perché la norma del bootstrap è distorta verso l'alto."),
])
P = os.path.join(AUDIT, "PATCH_MANOSCRITTO.md")
sub(P, [
    ("un bootstrap a due vie partecipanti×prompt dà −0,008/+0,220: l'inferenza riguarda i partecipanti e i prompt di queste due realizzazioni", "un bootstrap a due vie partecipanti×prompt dà −0,025/+0,233: la robustezza dipende dalla specificazione e l'inferenza riguarda i partecipanti e i prompt di queste due realizzazioni"),
    ("«Rispetto a BASE, le immagini delle tre adapter AESTHETIC sono più vicine al centroide delle proprie fotografie (Δ −0,015, −0,008, −0,010; IC < 0) e non a quello CONTROL; le adapter CONTROL non mostrano avvicinamento differenziale»",
     "«Rispetto a BASE, le adapter AESTHETIC sono più vicine al centroide delle proprie fotografie (distanza fra centroidi −0,053/−0,040/−0,049; distanza media delle immagini −0,015/−0,008/−0,010; IC < 0) e più di quanto lo siano a quello CONTROL; le adapter CONTROL si avvicinano a entrambi i centroidi in due seed su tre, senza un avvicinamento differenziale coerente nei tre seed»"),
    ("«Nello spazio dei descrittori le adapter CONTROL si avvicinano a entrambi i profili fotografici (di più al proprio); le adapter AESTHETIC a nessuno. Le due sonde non concordano su quale adapter si muova verso il proprio repertorio; la causa non è identificata»",
     "«Nello spazio dei descrittori le adapter CONTROL si avvicinano a entrambi i profili fotografici, di più al proprio (entrambe le metriche, IC < 0); per le adapter AESTHETIC la distanza fra centroidi si riduce descrittivamente (chiara in un seed su tre) mentre la distanza media delle singole immagini non si riduce in modo chiaro. Le due sonde non concordano su quale adapter si muova di più verso il proprio repertorio; la causa non è identificata»"),
    ("il termine di CONTROL rende conto dell'intera covarianza (101%, IC 73–139%) e quello di AESTHETIC è nullo", "il termine di CONTROL rende conto, come stima puntuale, dell'intera covarianza (101%, IC 73–139%) e la stima di quello di AESTHETIC è prossima a zero con intervallo che include zero"),
    ("«il contrasto umano non è distinguibile da zero quando l'incertezza include la variabilità fra prompt (bootstrap a due vie)»", "«il contrasto umano resiste a un modello con effetti casuali incrociati per partecipante, cella e immagine, ma non a un bootstrap a due vie partecipanti×prompt (−0,025/+0,233): la robustezza dipende dalla specificazione»"),
    ("(una realizzazione per condizione; non robusto all'inclusione della variabilità fra prompt)", "(una realizzazione per condizione; robustezza dipendente dalla specificazione dell'incertezza)"),
    ("ricampionando le fotografie la quota è 0,11–0,18", "[opzionale, dopo verifica della calibrazione] ricampionando le fotografie i quantili della quota sono 0,11–0,18"),
])
print("done")
