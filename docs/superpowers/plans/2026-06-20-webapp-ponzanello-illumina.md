# Web app "Ponzanello Illuminà" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file responsive web app (`index.html`) for the "Ponzanello Illuminà" event, with a landing page, info sections, and a Supabase-backed menu page with Google-OAuth-gated admin editing.

**Architecture:** One static HTML file with inline CSS and JS. Sections are `<div>` blocks toggled via JS (no router, no build step). The Supabase JS client (loaded from CDN as an ES module) handles menu reads (public) and writes (authenticated + email-whitelisted). Auth uses Supabase Auth's Google provider.

**Tech Stack:** HTML5, CSS3, vanilla JS (ES modules), `@supabase/supabase-js` via CDN (`https://esm.sh/@supabase/supabase-js@2`), Supabase Postgres + Auth.

**Note on this project:** the working directory is not a git repository, so steps that would normally say "commit" instead say "save the file" — there is nothing to commit to.

---

## Task 1: Create the Supabase project

**Files:** none (uses Supabase MCP tools)

- [ ] **Step 1: List organizations**

Call `mcp__plugin_supabase_supabase__list_organizations`. Ask the user which organization to use if more than one exists.

- [ ] **Step 2: Confirm cost and create project**

Call `mcp__plugin_supabase_supabase__confirm_cost` with type `project` for the chosen organization, then call `mcp__plugin_supabase_supabase__create_project` with:
- `name`: `ponzanello-illumina`
- `region`: `eu-central-1` (closest to Italy)
- `organization_id`: from Step 1
- `confirm_cost_id`: from the cost confirmation

- [ ] **Step 3: Wait for project to become active**

Poll `mcp__plugin_supabase_supabase__get_project` with the returned `id` until `status` is `ACTIVE_HEALTHY`.

- [ ] **Step 4: Record project URL and anon key**

Call `mcp__plugin_supabase_supabase__get_project_url` and `mcp__plugin_supabase_supabase__get_publishable_keys` with the project id. Save both values — they go into `index.html` in Task 3.

---

## Task 2: Create the `menu_items` table with RLS

**Files:** none (Supabase migration via MCP)

- [ ] **Step 1: Apply the migration**

Call `mcp__plugin_supabase_supabase__apply_migration` with `project_id` from Task 1, `name: create_menu_items`, and this `query`:

```sql
create table public.menu_items (
  id bigint generated always as identity primary key,
  categoria text not null,
  nome text not null,
  descrizione text,
  prezzo numeric(10,2) not null,
  disponibile boolean not null default true,
  ordine integer not null default 0,
  created_at timestamptz not null default now()
);

alter table public.menu_items enable row level security;

create policy "menu_items are publicly readable"
  on public.menu_items for select
  to anon, authenticated
  using (true);

create policy "authenticated users can insert menu_items"
  on public.menu_items for insert
  to authenticated
  with check (true);

create policy "authenticated users can update menu_items"
  on public.menu_items for update
  to authenticated
  using (true)
  with check (true);

create policy "authenticated users can delete menu_items"
  on public.menu_items for delete
  to authenticated
  using (true);
```

- [ ] **Step 2: Verify the table**

Call `mcp__plugin_supabase_supabase__list_tables` with the project id and confirm `menu_items` appears with the 4 policies.

- [ ] **Step 3: Seed a few sample rows (optional, for testing)**

Call `mcp__plugin_supabase_supabase__execute_sql` with:

```sql
insert into public.menu_items (categoria, nome, descrizione, prezzo, disponibile, ordine) values
  ('Primi', 'Tordelli al ragù', 'Tordelli fatti a mano con ragù di carne', 8.00, true, 1),
  ('Secondi', 'Tagliata di manzo', 'Con rucola e grana', 12.00, true, 1),
  ('Vino', 'Vermentino colli di Luni', 'Calice', 4.00, true, 1),
  ('Dolci', 'Torta della nonna', null, 3.50, true, 1);
```

---

## Task 3: Configure Google OAuth provider

**Files:** none (manual console steps — document for the user, cannot be fully automated via MCP)

- [ ] **Step 1: Get the OAuth callback URL**

The Supabase Auth callback URL is `<project_url>/auth/v1/callback` (project URL from Task 1, Step 4).

- [ ] **Step 2: Create Google OAuth client**

Tell the user to go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials), create an OAuth 2.0 Client ID (Web application), and add the callback URL from Step 1 as an Authorized redirect URI. They need the resulting Client ID and Client Secret.

- [ ] **Step 3: Enable Google provider in Supabase**

This step requires the Supabase dashboard (no MCP tool enables auth providers). Tell the user: in the Supabase dashboard → Authentication → Providers → Google, paste the Client ID and Client Secret from Step 2, and enable the provider.

- [ ] **Step 4: Set the Site URL**

In the Supabase dashboard → Authentication → URL Configuration, set Site URL to wherever `index.html` will be hosted (e.g. a GitHub Pages URL or the user's own domain) — this is required for the OAuth redirect to return to the right page.

---

## Task 4: Build `index.html` — structure, styling, and landing page

**Files:**
- Create: `index.html`

- [ ] **Step 1: Create the file with base structure, fonts, and CSS variables**

```html
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ponzanello Illuminà</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=EB+Garamond:ital@0;1&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0a;
    --gold: #d4af37;
    --bordeaux: #5c1f2a;
    --text: #f1e9d8;
    --muted: #9c9c9c;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'EB Garamond', serif;
    min-height: 100vh;
  }
  h1, h2, .brand { font-family: 'Cinzel', serif; }
  .section { display: none; padding: 24px 16px 64px; max-width: 720px; margin: 0 auto; }
  .section.active { display: block; }
  header.hero { text-align: center; padding: 32px 16px 16px; }
  header.hero img { width: 140px; height: 140px; object-fit: contain; }
  header.hero h1 { color: var(--gold); font-size: 2rem; letter-spacing: 2px; margin: 12px 0 4px; }
  header.hero p { color: var(--text); margin: 4px 0; }
  .card-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    padding: 16px;
    max-width: 720px;
    margin: 0 auto;
  }
  .card-btn {
    background: linear-gradient(160deg, var(--bordeaux), #2c0d12);
    border: 1px solid var(--gold);
    border-radius: 10px;
    color: var(--gold);
    font-family: 'Cinzel', serif;
    font-size: 0.95rem;
    padding: 22px 10px;
    text-align: center;
    cursor: pointer;
  }
  .card-btn:active { transform: scale(0.97); }
  .back-btn {
    background: none;
    border: 1px solid var(--gold);
    color: var(--gold);
    border-radius: 6px;
    padding: 8px 16px;
    margin-bottom: 16px;
    cursor: pointer;
    font-family: 'EB Garamond', serif;
  }
  .section h2 { color: var(--gold); border-bottom: 1px solid var(--bordeaux); padding-bottom: 8px; }
  .menu-category h3 { color: var(--gold); margin-top: 24px; }
  .menu-item { display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; border-bottom: 1px solid #2a2a2a; }
  .menu-item.unavailable { opacity: 0.5; }
  .menu-item .name { font-weight: 600; }
  .menu-item .desc { color: var(--muted); font-size: 0.85rem; display: block; }
  .menu-item .price { color: var(--gold); white-space: nowrap; }
  .badge { font-size: 0.7rem; background: var(--bordeaux); color: var(--text); padding: 2px 6px; border-radius: 4px; margin-left: 6px; }
  iframe.map { width: 100%; height: 300px; border: 0; border-radius: 8px; margin-top: 12px; }
  .contact-list a { color: var(--gold); display: block; margin: 10px 0; text-decoration: none; }
  .gallery-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 16px; }
  .gallery-grid img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 6px; }
  #admin-area { margin-top: 24px; border-top: 1px solid var(--bordeaux); padding-top: 16px; }
  #admin-area input, #admin-area textarea { width: 100%; margin-bottom: 8px; padding: 8px; background: #1a1a1a; color: var(--text); border: 1px solid var(--bordeaux); border-radius: 4px; }
  #admin-area button { background: var(--gold); color: #1a1a1a; border: none; padding: 8px 14px; border-radius: 4px; cursor: pointer; margin-right: 8px; }
</style>
</head>
<body>

<div id="landing" class="section active">
  <header class="hero">
    <img src="logo sfondo nero.png" alt="Castrum Ponzanello">
    <h1>PONZANELLO ILLUMINÀ</h1>
    <p>24 - 25 Luglio · Ore 19:30</p>
    <p>Ponzanello, Comune di Fosdinovo (MS)</p>
    <p>Bus navetta gratuito</p>
  </header>
  <div class="card-grid">
    <button class="card-btn" data-target="menu">🍷 Menù</button>
    <button class="card-btn" data-target="come-arrivare">🗺️ Come arrivare</button>
    <button class="card-btn" data-target="info-utili">ℹ️ Info utili</button>
    <button class="card-btn" data-target="galleria">📷 Galleria</button>
    <button class="card-btn" data-target="contatti">✉️ Contatti</button>
  </div>
</div>

<div id="menu" class="section">
  <button class="back-btn" data-target="landing">← Indietro</button>
  <h2>Menù</h2>
  <div id="menu-content">Caricamento...</div>
  <div id="auth-area"></div>
  <div id="admin-area" style="display:none;"></div>
</div>

<div id="come-arrivare" class="section">
  <button class="back-btn" data-target="landing">← Indietro</button>
  <h2>Come arrivare</h2>
  <p>Ponzanello, Comune di Fosdinovo (MS).</p>
  <p>I bus navetta gratuiti partono dai parcheggi allestiti vicino al paese, indicati dal personale del VAB. Il paese è in salita: sono sconsigliate le scarpe con i tacchi.</p>
  <iframe class="map" loading="lazy" src="https://www.google.com/maps?q=Ponzanello,Fosdinovo,MS&output=embed"></iframe>
</div>

<div id="info-utili" class="section">
  <button class="back-btn" data-target="landing">← Indietro</button>
  <h2>Info utili</h2>
  <p>Tutti i prodotti si acquistano con i <strong>sesterzi</strong>, la moneta del paese di Ponzanello. Si cambiano euro/sesterzi alla "Banca Castrum Ponzanello" nel borgo.</p>
  <p>Non è previsto il servizio al tavolo: dopo aver cambiato i soldi e acquistato cibo e bevande, troverete posto ai tavoli nei vari punti allestiti lungo il borgo.</p>
  <p>È previsto un piatto vegano.</p>
  <p>Durante le due serate vari gruppi suoneranno e canteranno per le vie del borgo e nelle cantine.</p>
</div>

<div id="galleria" class="section">
  <button class="back-btn" data-target="landing">← Indietro</button>
  <h2>Galleria</h2>
  <p>Le foto della festa arriveranno presto qui.</p>
  <div class="gallery-grid" id="gallery-grid"></div>
</div>

<div id="contatti" class="section">
  <button class="back-btn" data-target="landing">← Indietro</button>
  <h2>Contatti</h2>
  <div class="contact-list">
    <a href="tel:+393336545564">📞 333 6545564</a>
    <a href="mailto:castrumponzanello@gmail.com">✉️ castrumponzanello@gmail.com</a>
    <a href="https://www.facebook.com/castrum.ponzanello" target="_blank" rel="noopener">📘 Facebook</a>
    <a href="https://www.instagram.com/castrumponzanello/" target="_blank" rel="noopener">📸 Instagram</a>
  </div>
</div>

<script type="module">
  document.querySelectorAll('[data-target]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      document.getElementById(btn.dataset.target).classList.add('active');
      window.scrollTo(0, 0);
    });
  });
</script>

</body>
</html>
```

- [ ] **Step 2: Open the file in a browser and verify navigation**

Open `index.html` directly in a browser (double-click or `start index.html` on Windows). Confirm: logo and event info show on landing, all 5 card buttons switch to their section, every "← Indietro" returns to landing, layout looks correct on a narrow window (resize to ~390px wide to simulate phone).

---

## Task 5: Wire up the Supabase menu (public read)

**Files:**
- Modify: `index.html` (`<script type="module">` block)

- [ ] **Step 1: Add the Supabase client and public menu rendering**

Replace the closing `<script type="module">...</script>` block at the end of `index.html` with:

```html
<script type="module">
  import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

  const SUPABASE_URL = 'PASTE_PROJECT_URL_HERE';
  const SUPABASE_ANON_KEY = 'PASTE_ANON_KEY_HERE';
  const ADMIN_WHITELIST = [
    'gabriele.correrini@gmail.com',
    'bertagninilorenzo@gmail.com',
    'castrumponzanello@gmail.com',
    'francesco.correrini@gmail.com'
  ];

  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  document.querySelectorAll('[data-target]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
      document.getElementById(btn.dataset.target).classList.add('active');
      window.scrollTo(0, 0);
    });
  });

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  async function loadMenu() {
    const { data, error } = await supabase
      .from('menu_items')
      .select('*')
      .order('categoria')
      .order('ordine')
      .order('nome');

    const container = document.getElementById('menu-content');
    if (error) {
      container.textContent = 'Errore nel caricamento del menù.';
      return;
    }
    if (!data.length) {
      container.textContent = 'Il menù sarà disponibile a breve.';
      return;
    }

    const byCategory = {};
    for (const item of data) {
      (byCategory[item.categoria] ??= []).push(item);
    }

    container.innerHTML = Object.entries(byCategory).map(([categoria, items]) => `
      <div class="menu-category">
        <h3>${escapeHtml(categoria)}</h3>
        ${items.map(item => `
          <div class="menu-item ${item.disponibile ? '' : 'unavailable'}">
            <span>
              <span class="name">${escapeHtml(item.nome)}</span>
              ${item.disponibile ? '' : '<span class="badge">esaurito</span>'}
              ${item.descrizione ? `<span class="desc">${escapeHtml(item.descrizione)}</span>` : ''}
            </span>
            <span class="price">${Number(item.prezzo).toFixed(2)} sesterzi</span>
          </div>
        `).join('')}
      </div>
    `).join('');
  }

  loadMenu();
</script>
```

- [ ] **Step 2: Fill in real Supabase credentials**

Replace `PASTE_PROJECT_URL_HERE` and `PASTE_ANON_KEY_HERE` with the values recorded in Task 1, Step 4.

- [ ] **Step 3: Verify in browser**

Open `index.html`, go to the Menù section, and confirm the seeded items from Task 2 Step 3 render grouped by category with prices in "sesterzi".

---

## Task 6: Add Google login and admin editing to the menu page

**Files:**
- Modify: `index.html` (`<script type="module">` block, append to the same block used in Task 5)

- [ ] **Step 1: Add auth UI and whitelist check**

Append this code inside the same `<script type="module">` block, after `loadMenu();`:

```html
<script type="module">
  // ... (existing code from Task 5 stays above) ...

  const authArea = document.getElementById('auth-area');
  const adminArea = document.getElementById('admin-area');

  function renderLoggedOut() {
    authArea.innerHTML = `<button class="back-btn" id="login-btn">Accedi con Google</button>`;
    document.getElementById('login-btn').addEventListener('click', () => {
      supabase.auth.signInWithOAuth({ provider: 'google' });
    });
    adminArea.style.display = 'none';
    adminArea.innerHTML = '';
  }

  function renderUnauthorized(email) {
    authArea.innerHTML = `<p>Accesso non autorizzato per ${escapeHtml(email)}. <button class="back-btn" id="logout-btn">Esci</button></p>`;
    document.getElementById('logout-btn').addEventListener('click', () => supabase.auth.signOut());
    adminArea.style.display = 'none';
    adminArea.innerHTML = '';
  }

  function renderAdmin(email) {
    authArea.innerHTML = `<p>Connesso come ${escapeHtml(email)}. <button class="back-btn" id="logout-btn">Esci</button></p>`;
    document.getElementById('logout-btn').addEventListener('click', () => supabase.auth.signOut());
    adminArea.style.display = 'block';
    adminArea.innerHTML = `
      <h3>Aggiungi voce al menù</h3>
      <form id="add-item-form">
        <input name="categoria" placeholder="Categoria (es. Primi)" required>
        <input name="nome" placeholder="Nome" required>
        <textarea name="descrizione" placeholder="Descrizione (opzionale)"></textarea>
        <input name="prezzo" type="number" step="0.01" placeholder="Prezzo" required>
        <label><input type="checkbox" name="disponibile" checked> Disponibile</label>
        <button type="submit">Aggiungi</button>
      </form>
      <div id="admin-list"></div>
    `;
    document.getElementById('add-item-form').addEventListener('submit', async e => {
      e.preventDefault();
      const f = e.target;
      await supabase.from('menu_items').insert({
        categoria: f.categoria.value,
        nome: f.nome.value,
        descrizione: f.descrizione.value || null,
        prezzo: parseFloat(f.prezzo.value),
        disponibile: f.disponibile.checked
      });
      f.reset();
      f.disponibile.checked = true;
      await loadMenu();
      await renderAdminList();
    });
    renderAdminList();
  }

  async function renderAdminList() {
    const { data } = await supabase.from('menu_items').select('*').order('categoria').order('nome');
    const list = document.getElementById('admin-list');
    if (!list) return;
    list.innerHTML = '<h3>Voci esistenti</h3>' + (data || []).map(item => `
      <div class="menu-item">
        <span>${escapeHtml(item.categoria)} — ${escapeHtml(item.nome)} (${Number(item.prezzo).toFixed(2)})</span>
        <span>
          <button data-toggle="${item.id}" data-available="${item.disponibile}">${item.disponibile ? 'Segna esaurito' : 'Segna disponibile'}</button>
          <button data-delete="${item.id}">Elimina</button>
        </span>
      </div>
    `).join('');

    list.querySelectorAll('[data-toggle]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.toggle;
        const current = btn.dataset.available === 'true';
        await supabase.from('menu_items').update({ disponibile: !current }).eq('id', id);
        await loadMenu();
        await renderAdminList();
      });
    });
    list.querySelectorAll('[data-delete]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.delete;
        await supabase.from('menu_items').delete().eq('id', id);
        await loadMenu();
        await renderAdminList();
      });
    });
  }

  async function refreshAuthUI() {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      renderLoggedOut();
      return;
    }
    const email = session.user.email;
    if (ADMIN_WHITELIST.includes(email)) {
      renderAdmin(email);
    } else {
      renderUnauthorized(email);
    }
  }

  supabase.auth.onAuthStateChange(() => refreshAuthUI());
  refreshAuthUI();
</script>
```

This replaces the closing `</script>` from Task 5 with the continuation above, i.e. the final file has one `<script type="module">` block containing all of: imports, constants, navigation handler, `loadMenu`, the auth/admin functions, and the `refreshAuthUI()` bootstrap call.

- [ ] **Step 2: Verify login is gated correctly**

Open `index.html` in a browser served over `http://` or `https://` (Google OAuth redirects won't work from a bare `file://` URL — use e.g. `npx serve .` or any static file server in the project directory). Go to Menù → "Accedi con Google":
- Log in with an email NOT in the whitelist → confirm "Accesso non autorizzato" shows and no form appears.
- Log out, log in with `gabriele.correrini@gmail.com` (or another whitelisted email) → confirm the add-item form and the editable list of existing items appear.
- Add a new item, confirm it appears both in the admin list and in the public menu view.
- Toggle "Segna esaurito" on an item, confirm the public menu shows the "esaurito" badge.
- Delete an item, confirm it disappears from both lists.

---

## Task 7: Final responsive and content check

**Files:** none (manual verification)

- [ ] **Step 1: Test on a real phone or device emulation**

Serve `index.html` over local network (e.g. `npx serve .` and visit `http://<your-lan-ip>:3000` from a phone on the same Wi-Fi), or use browser dev tools device emulation (iPhone SE, a small Android width, and an iPad width). Confirm:
- Card grid stays 2 columns and tappable on phone width.
- Menu items don't overflow horizontally.
- Map embed and contact links work on touch.

- [ ] **Step 2: Generate the real QR code**

Once the page is hosted at its final URL (e.g. GitHub Pages), generate a QR code pointing to that URL and replace the placeholder QR code on the flyer back (`pieghevoli 2026.indd` / `.pdf`) — this is a manual step outside this plan's scope (graphic design file), flagged here so it isn't forgotten.
