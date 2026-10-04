# Protocollo — controllo sperimentale con caption identiche e non valutative (versione 2, 3 ottobre 2026, dopo il controllo esterno)

Stato: **protocollo completo ed eseguibile, NON eseguito.** Nessun training a caption controllate esiste nei record (`training_runs.csv`: le 17 run usano le caption v1/v2 del proprio corpus). Nessun training è stato avviato dall'audit: serve un'unica approvazione del responsabile con il costo di §6. Analisi post-review, non preregistrata; endpoint, categorie di lettura e soglie sono fissati qui, prima di qualsiasi risultato. Lo script di analisi (`scripts/a10_caption_control_analysis.py`) è scritto e **collaudato in modalità `--dry-run`** sulle adapter esistenti (percorsi di codice verificati; i numeri del dry run non hanno significato e sono in `outputs/caption_control_DRYRUN_*`).

Modifiche rispetto alla versione 1 (richieste dal controllo esterno §5): stima, incertezza e differenza appaiata fra regimi tenute separate; categoria «inconclusivo»; nessuna lettura di «effetto perso» da un intervallo che include zero; soglie di rilevanza eliminate (restano solo criteri di segno/intervallo dichiarati); stringa comune verificata sui 178 riferimenti e cambiata; worker bloccato all'hash storico; costo aggiornato al listino verificato.

## 1. Domanda

Il contrasto rappresentazionale AESTHETIC−CONTROL negli output (DINOv2 lungo la direzione sorgente congelata; profilo dei 31 descrittori) si osserva anche quando le due LoRA sono addestrate sulle **stesse fotografie** dei dataset congelati con **una medesima caption identica per tutte le 178 immagini**, cioè quando il canale testuale non può differire fra i corpora?

## 2. Che cosa identifica e che cosa no

- Contrasto presente sotto caption comuni → i due corpora producono adapter diversi lungo la direzione sorgente anche senza differenze testuali, in questa configurazione; sostiene «differenza fra i corpora», **non** il trasferimento della «bellezza», non la causa del giudizio umano.
- Contrasto non distinguibile da zero sotto caption comuni → **non** dimostra che il risultato originale fosse testuale: il regime originale resta immagini+caption e con due sole condizioni l'interazione non è separabile. Le caption si dicono «necessarie» solo se la differenza appaiata fra regimi è > 0 **e** il contrasto neutro non è distinguibile da zero (vedi §4).
- Uno scambio di caption fra immagini è un esperimento diverso e non va confuso con questo controllo.
- Il controllo riguarda le sonde computazionali: nessun dato umano, nessuna replica dell'endpoint umano, nessun effetto sulla regola di selezione.

## 3. Disegno

| elemento | valore | invariato rispetto al regime originale? |
|---|---|---|
| fotografie | AESTHETIC-v2 (89) e CONTROL-v2 (89): stesse immagini e stessi file (sha256 in `01_training_manifest.csv`) | sì |
| caption | **una sola stringa per tutte le 178 immagini: `photograph of architecture`** | NO (è il trattamento) |
| dataset | AESTHETIC-v3-neutral / CONTROL-v3-neutral: copia dell'elenco immagini delle v2 (nessuna riselezione, nessun nuovo seed di controllo), caption sostituita, congelati | — |
| base model | stabilityai/stable-diffusion-xl-base-1.0 @ 462165984030d82259a11f4367a4eed129e94a7b | sì |
| LoRA | UNet attention (to_q, to_k, to_v, to_out.0), rank 16, alpha 16, init gaussian; text encoder congelati | sì |
| ottimizzazione | lr 1e-4, batch 1, 1500 step, 1024 px, fp16, noise_offset 0.0357, timestep_min 250 (= RUN-*-4) | sì |
| seed di training | accoppiati: 1254, 9865, 42160 per entrambi i corpora (6 training) | sì (= replica §8) |
| worker | `aar_worker.py` **sha256 `266541cf200e590dd5a1d6fd68429c50858b0c48eb64172507220882f833b95f`** = versione usata per RUN-*-4 (job 22/23), per tutte le generazioni finali (job 24–38) e per le repliche; coincide con il file attuale del repository; da verificare nel record del job prima dell'avvio | sì |
| generazione | piano congelato: prompt set 15 (48 prompt) × 4 seed (25478, 85, 6127, 7), 1216×832, DPM++ 2M Karras, 40 step, CFG 5 | sì |
| output | 6 × 192 = 1152 immagini; BASE già disponibile (192, piani 22/23) | — |
| embedding/descrittori | stessa pipeline (dinov2-base CLS su thumbnail 480 px, L2; `image_scripts/covariates.py`); direzione sorgente **congelata** `baseline/direction_dinov2.npz` | sì |

**Scelta della stringa comune.** Le 178 caption congelate iniziano con «exterior photograph» in 168 casi, «photograph of» 6, «interior photograph» 1, «aerial photograph» 1, «exterior night/black-and-white photograph» 2; 10 soggetti non sono «building» in senso stretto (ponte, torre televisiva, skyline, arcata). La stringa della versione 1 (`exterior photograph of a building`) era quindi falsa per almeno 2 immagini e impropria per altre 10. `photograph of architecture` è vera per tutte le 178, non valutativa, priva di termini vietati e priva di qualsiasi contenuto differenziale. Alternativa scartata: `architecture` da sola (troppo lontana dal formato delle caption di training SDXL, introdurrebbe un cambiamento di regime ulteriore). La scelta è fissata qui.

Numero di repliche: 3 seed accoppiati (identico alla replica §8). Nessuna run aggiuntiva senza nuova approvazione.

## 4. Endpoint, quantità separate e categorie di lettura (fissati ora)

Per ogni seed s e per la media dei tre seed, lo script riporta **tre quantità separate**, ciascuna con IC bootstrap sui 48 prompt (5000 ricampionamenti, seed 20261003):
1. **P_s^neutro** = media sulle 192 celle di (e_A − e_C)·u nel regime a caption comune, con R = P/d;
2. **P_s^orig** nel regime originale (adapter esistenti, stesse celle), per riferimento;
3. **Δ_s = P_s^orig − P_s^neutro**, differenza **appaiata per cella** (stesso prompt, stesso seed di generazione, stesso seed di training).

Categorie (decise dagli intervalli della media dei tre seed; i tre seed singoli sono riportati, non usati come criterio «3 segni» per evitare la probabilità 1/8 sotto l'ipotesi nulla):
- **mantenuto**: IC(P^neutro) > 0 e IC(Δ) include 0;
- **ridotto**: IC(P^neutro) > 0 e IC(Δ) > 0;
- **non distinguibile da zero sotto caption comuni, e minore dell'originale**: IC(P^neutro) include 0 e IC(Δ) > 0 — unico caso in cui si può scrivere che le caption differenziate contribuiscono al contrasto osservato;
- **inconclusivo**: IC(P^neutro) include 0 e IC(Δ) include 0;
- **invertito**: IC(P^neutro) < 0.
Nessuna soglia di rilevanza o non-inferiorità: non ne esiste una giustificata dal disegno; se ne serve una, va stabilita e motivata dagli autori **prima** di guardare i risultati e scritta qui.

Secondari: r fra x (fotografie, inalterato) e a−c nei 31 descrittori sotto caption comuni, con IC sui descrittori, accanto a +0,71; distanze ai centroidi dei corpora (entrambe le metriche, come in `report_dino.md`). VLM non previsto.

## 5. Esecuzione (ogni passo registrato nell'audit log della piattaforma)

1. Impostare come caption corrente e «reviewed» la stringa `photograph of architecture` per le 178 immagini (nessun termine vietato).
2. Generare AESTHETIC-v3-neutral e CONTROL-v3-neutral copiando gli elenchi delle v2; congelare (lo snapshot registra la stringa unica). Verificare: 89+89, stessi codici, caption identica.
3. Verificare che il worker in uso abbia hash `266541cf…`; creare le 6 run con `config_caption_controllate.json` (NEU-CTL-S42160, NEU-AES-S9865 / NEU-AES-S42160, NEU-CTL-S1254 / NEU-AES-S1254, NEU-CTL-S9865), due alla volta (limite L4).
4. Piano di generazione di test (`IsPilot`) con prompt set 15, 4 seed, le 6 condizioni; import; export; download thumbnail 480 px e 1216 px.
5. Estrazione embedding (`metrics/embeddings_neutral_dinov2_vitb14.npz`) e descrittori (append a `covariates_images.csv`) con la pipeline storica.
6. `python scripts/a10_caption_control_analysis.py <export con le NEU-*>` → `outputs/caption_control_results.csv`, `report_caption_control.md`.
7. Nessuna analisi prima del completamento delle sei run; nessuna modifica di §4 dopo aver visto gli output.

## 6. Risorse, tempi e costo (dalle run reali in `outputs/cloud_jobs.csv`; listino verificato)

- Training: 23,0–23,8 min per adapter (14 run SDXL complete) → 6 × ~24 min ≈ **2,4 ore GPU**.
- Generazione: 192 immagini ≈ 50,6–51,5 min per adapter (piani 13/14/16/17) → 6 × ~51 min ≈ **5,1 ore GPU**.
- Totale ≈ **7,5 ore GPU** (+ ~10% avvio/upload → ≈ 8,3 ore fatturate), ≈ **4–4,5 ore di calendario** con due istanze.
- Prezzo L4-1-24G: **0,79 €/ora** (pagina pricing Scaleway consultata il 3 ottobre 2026) → **≈ 6,0–6,6 €** (IVA esclusa), storage e trasferimento trascurabili; nessun costo API.
- Lavoro umano: ~1 ora (caption, dataset, run, piano), ~1 ora analisi e verifica.

## 7. Limiti dichiarati in anticipo

- Una caption identica rimuove anche l'informazione descrittiva utile al text-conditioning: le LoRA neutre possono differire globalmente dalle originali (p.es. aderenza al prompt); i contrasti A−C restano appaiati per cella e seed, ma il regime non è «uguale a prima meno il testo».
- Tre seed: potenza limitata; le categorie dipendono dagli intervalli sui prompt (48 cluster).
- Il controllo non tocca l'endpoint umano né la regola di selezione; non quantifica l'interazione immagine×testo.
