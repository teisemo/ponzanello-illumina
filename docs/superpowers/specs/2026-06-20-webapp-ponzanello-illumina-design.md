# Web app "Ponzanello Illuminà" — Design

## Contesto

Volantino cartaceo per la festa medievale "Ponzanello Illuminà" (24-25 luglio, ore 19:30, borgo di Ponzanello, Comune di Fosdinovo MS) ha sul retro un QR code placeholder. Deve puntare a una web app responsive (tablet/smartphone) con tutte le info dell'evento.

## Obiettivo

Singolo file `index.html` (HTML + CSS + JS inline, nessuna build), pubblicato staticamente, con landing page e sezioni di dettaglio navigabili senza reload (mostra/nasconde sezioni via JS).

## Stile visivo

- Sfondo nero, palette oro (#d4af37-ish) e bordeaux, coerente con `logo sfondo nero.png` e il volantino.
- Font titoli "medievale"/serif marcato (es. Cinzel o simile da Google Fonts), font corpo leggibile sans-serif.
- Mobile-first, touch target grandi per le card.

## Struttura pagina (sezioni nello stesso file)

### 1. Landing
- Logo centrato, titolo "PONZANELLO ILLUMINÀ"
- Date "24-25 Luglio", orario "Ore 19:30"
- Sottotitolo "Ponzanello, Comune di Fosdinovo (MS)"
- Nota "Bus navetta gratuito"
- Griglia di card-pulsanti (una per ogni sezione sotto), icona + etichetta

### 2. Menù (Supabase)
- Tabella Supabase `menu_items`: `id, categoria (text), nome (text), descrizione (text, nullable), prezzo (numeric, sesterzi), disponibile (bool, default true), ordine (int, per sort)`.
- RLS: SELECT pubblico (anon) per tutte le righe; INSERT/UPDATE/DELETE solo per utenti autenticati (authenticated role).
- Vista pubblica: raggruppata per categoria, ordinata per `ordine`/nome; voci con `disponibile = false` mostrate con badge "esaurito" e stile attenuato (non nascoste, per trasparenza durante la festa).
- Bottone "Accedi" in alto nella sezione menù → Supabase Auth, provider Google (OAuth).
- Dopo login: controllo client-side che l'email sia nella whitelist:
  - gabriele.correrini@gmail.com
  - bertagninilorenzo@gmail.com
  - castrumponzanello@gmail.com
  - francesco.correrini@gmail.com
  - Se NON in whitelist: messaggio "Accesso non autorizzato" e nessuna funzione di modifica (anche se la sessione Supabase resta autenticata, l'app non mostra/non invoca azioni admin).
- Se in whitelist: form admin inline (stessa pagina) per aggiungere nuova voce, editare campi esistenti, cambiare `disponibile`, eliminare voce. Operazioni dirette via Supabase JS client (CRUD su `menu_items`).
- Bottone "Esci" per fare logout.

### 3. Come arrivare
- Indirizzo testuale, embed Google Maps (iframe) centrato sul borgo di Ponzanello.
- Istruzioni dal volantino: parcheggi esterni con bus navetta gratuito indicato dal personale VAB, paese in salita (sconsigliate scarpe con tacchi).

### 4. Info utili
- Sesterzi: moneta locale, cambio euro presso "Banca Castrum Ponzanello" nel borgo.
- Niente servizio al tavolo: si acquista e si trova posto ai tavoli lungo il borgo.
- Piatto vegano disponibile.
- Musica dal vivo nelle cantine e per le vie del borgo durante le due serate.

### 5. Galleria foto
- Griglia responsive di immagini, predisposta ma vuota per ora.
- Le foto verranno aggiunte in un secondo momento in una cartella `/foto` del progetto; la griglia carica dinamicamente i file presenti (lista hardcoded di filename da aggiornare a mano quando le foto arrivano, dato il vincolo di file singolo senza backend per il listing).

### 6. Contatti
- Telefono: 333 6545564 (link `tel:`)
- Email: castrumponzanello@gmail.com (link `mailto:`)
- Facebook: https://www.facebook.com/castrum.ponzanello
- Instagram: https://www.instagram.com/castrumponzanello/

## Backend: Supabase

- Nuovo progetto Supabase dedicato (non condiviso con Gymbrotracker).
- Provider Auth: Google OAuth (nuovo client OAuth da configurare su Google Cloud Console, redirect URI verso il progetto Supabase).
- Tabella `menu_items` con RLS come sopra.
- Chiavi pubbliche (`project URL` + `anon public key`) incluse direttamente nel file HTML (uso previsto e sicuro lato client per progetti Supabase con RLS correttamente configurata).

## Sicurezza

- La protezione reale è lato Supabase: RLS limita le scritture a utenti autenticati; la whitelist email è un controllo applicativo lato client per nascondere la UI admin ai loggati non autorizzati (deterrente, non barriera assoluta — eventualmente rinforzabile in futuro con una RLS policy che controlla l'email in `auth.users`, miglioramento possibile ma non richiesto ora).

## Fuori scope (per ora)

- Pagina "Programma serate" (non richiesta in questa fase).
- Caricamento foto via upload nella galleria (si aggiungono foto manualmente in cartella).
- Hardening RLS basato su email in tabella (whitelist resta solo client-side).
