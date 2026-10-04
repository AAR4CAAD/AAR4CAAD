# Verifiche editoriali e fonti per la prossima integrazione

Il manoscritto revisione 13 non è stato modificato in questo passaggio.

## File Word verificato direttamente

- Sono presenti sei pronomi italiani “Si” erroneamente suddivisi in S corsiva e i a pedice: uno in 3.2 (“Si cerca”), due in 3.4 (“Si chiede”, “Si raccolgono”), tre in 3.6 (“Si tratta”, “Si confrontano”, “Si contano”). Correggere solo queste occorrenze; mantenere S_i nella definizione matematica della differenza di affinità.
- Il file contiene 16 risorse immagine, delle quali 5 hanno relazioni effettivamente richiamate nel corpo (tre figure, una con tre pannelli) e 11 relazioni immagine non utilizzate nel corpo. Prima di rimuoverne i file, controllare tutte le parti e tutte le relazioni del pacchetto, comprese intestazioni/piè di pagina.
- `docProps/custom.xml` contiene una proprietà `abstract` obsoleta. Eliminarla o sincronizzarla al testo finale, non riutilizzarla per riscrivere l’abstract visibile.
- Verificare testo e destinazione reale dei collegamenti bibliografici, non soltanto quanto appare stampato.
- Nessuna pulizia OOXML deve eliminare immagini referenziate, didascalie, campi, formule o riferimenti. Dopo la modifica occorre rendering e controllo visivo.

## Fonti pubbliche consultate (4 ottobre 2026)

### Vartanian et al. 2013 — verificato sulla pubblicazione PNAS

Vartanian, O., Navarrete, G., Chatterjee, A., Brorson Fich, L., Leder, H., Modroño, C., Nadal, M., Rostrup, N., Skov, M.: Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. Proceedings of the National Academy of Sciences 110(Suppl. 2), 10446–10453 (2013). DOI: 10.1073/pnas.1301227110.

Fonte: https://doi.org/10.1073/pnas.1301227110

Uso pertinente: collega contorno e giudizi su rappresentazioni di spazi architettonici e distingue tali giudizi dalle decisioni di approccio/evitamento. Non è una dimostrazione del meccanismo del nostro fine-tuning e non misura la distanza negli embedding.

### Precedente eCAADe sulla costruzione di dati per la generazione — record istituzionale verificato

Kavakoglu, A.A., Almaç, B., Eser, B., Alaçam, S.: AI Driven Creativity in Early Design Education: A pedagogical approach in the age of Industry 5.0. In: eCAADe 2022 — Co-creating the Future: Inclusion in and through Design, vol. 1, pp. 133–142 (2022).

Fonte istituzionale: https://research.itu.edu.tr/en/publications/ai-driven-creativity-in-early-design-education-a-pedagogical-appr/

Il record descrive analisi di precedenti di facciata, estrazione di caratteristiche, produzione di nuove rappresentazioni e training StyleGAN2-ADA su tali rappresentazioni, poi usate nell’esplorazione progettuale. È un precedente sull’intervento nella costruzione dei dati di training, non la stessa sperimentazione preference-guided controllata di AAR. Il record ITU rende il cognome di Almaç come “Almag”; la grafia va confrontata con la prima pagina del paper prima della versione editoriale definitiva. Il DOI 10.52842/conf.ecaade.2022.1.133 è riportato nella pagina dell’articolo su ResearchGate, ma il resolver CumInCAD non è stato caricato qui: non dichiarare una verifica diretta del testo integrale.

### [4] LoRA — atti ICLR verificati

Record della conferenza: https://iclr.cc/virtual/2022/poster/6319

Conservare anno 2022 e pubblicazione ICLR; il riferimento OpenReview indicato nel manoscritto è `nZeVKeeFYf9`. La pagina forum diretta ha restituito un controllo browser in questa sessione. Il testo visibile e il link effettivo dovranno essere coerenti.

### [10] DINOv2 — identificatore OpenReview da usare per la versione TMLR

Identificatore: `a68SUt6zFt`, URL https://openreview.net/forum?id=a68SUt6zFt .

L’identificatore è richiamato anche dalla documentazione ufficiale Microsoft del modello RAD-DINO, https://huggingface.co/microsoft/rad-dino/blame/main/README.md . Il forum OpenReview ha restituito un controllo browser qui: non dichiarare di averne letto direttamente la scheda in questa sessione. La pubblicazione TMLR 2024 è già documentata nel precedente controllo bibliografico; evitare di usare il DOI della prepubblicazione arXiv come identificatore della versione TMLR.

## Testo dei risultati umani

Presentare “nessun vantaggio chiaro nelle coppie e rispetto a BASE”, con stime e IC. I dati non giustificano trasformare la mancata significatività in equivalenza dimostrata. BASE−CONTROL = +0,140 è la stima originaria per partecipante; affiancare la relativa sensibilità, non applicarle implicitamente l’IC di A−C.

## Generalizzazione e memorizzazione

La correlazione sulle fotografie non usate nella LoRA verifica la portata esterna della direzione sorgente, non l’assenza di copie nelle generazioni. Non aggiungere una frase “memorizzazione esclusa”. Il termine held-out riguarda l’adattamento AAR, non il pretraining di SDXL.
