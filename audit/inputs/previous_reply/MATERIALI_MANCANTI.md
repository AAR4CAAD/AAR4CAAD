# Materiali ancora necessari per completare le richieste del revisore

Le matrici non sono ricostruite digitizzando i grafici e i pesi non sono ricalcolati con una pipeline diversa.

1. **Embedding originali** delle 600 fotografie e degli output BASE/AESTHETIC/CONTROL, con colonne delle 768 dimensioni, identificativi, ordine delle righe, preprocessing e normalizzazione. Per le repliche: chiave esplicita del seed di training e del seed di generazione. Servono per definire una direzione corretta per periodo/geografia e ripetere le proiezioni. `source_affinity.csv` non li sostituisce: conserva soltanto alcune proiezioni/similarità.
2. **Matrice dei 31 descrittori visivi per immagine**, per fotografie e generazioni, con codebook, nomi esatti, valori prima/dopo standardizzazione, modello CLIP e stringhe testuali usate. Occorrono anche script e output numerici della figura composita. Servono per il contrasto per modalità di matching, il confronto lessico–visione e le distanze dai corpus.
3. **Corrispondenze storiche fra fotografie AESTHETIC e CONTROL**, oppure codice e input che le ricostruiscano in modo deterministico. `sort_order` non è assunto come identificatore della coppia. I candidati compatibili presenti nel file 04 non sono coppie originali accertate.
4. **Procedura effettiva di costruzione del repertorio e delle caption**, con liste iniziali, regole, chi ha selezionato/rivisto e log. L’inventario dei 600 edifici non identifica da solo il processo di campionamento.
5. **Trainer e configurazioni effettive**, compresi codice/versioni, text encoder addestrati o congelati, script dell’ICC, regressioni e controlli delle repliche. L’export contiene gli iperparametri principali ma non completa queste informazioni.
6. **Secondo screening umano**, con una persona indipendente e condizioni/precedenti decisioni nascoste. Non è una nuova misurazione di preferenza e non recupera i giudizi mancanti sulle immagini escluse.
7. **Documentazione istituzionale e deposito anonimo**: stato etico realmente attestato, conferma dei conflitti di interesse e URL effettivo del repository. Nessuna esenzione è presunta.

Dopo il recupero dei file si può completare il riscontro senza modificare i corpus o i training originali. Le nuove analisi dovranno essere identificate come post-review ed esplorative, con criteri fissati prima dei loro risultati.
