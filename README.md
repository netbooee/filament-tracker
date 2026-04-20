# 🧵 Filament Vault

A desktop inventory tracker for Bambu Lab filament spools.

---

## Quick Start

### Requirements
- [Node.js](https://nodejs.org/) v18 or higher

### Run in development
```bash
cd filament-vault
npm install
npm start
```

### Build a distributable Mac .app
```bash
npm run build
```
The `.dmg` installer will be output to the `dist/` folder.

---

## Usage

### 1. Import your Catalog
Go to **Import → Filament Catalog** and upload a CSV with columns:
```
UPC, Brand, Material, Color
```
A header row is optional but auto-detected. Download the sample to see the format.

### 2. Import your Scan File
Go to **Import → UPC Scan File** and upload a `.txt` file with one barcode per line.
- Duplicate UPCs automatically add +1 spool each
- Unmatched UPCs go to the **Unmatched** queue

### 3. Manage Inventory
- Use **+/−** buttons to adjust spool counts inline
- Click **Edit** or a location tag to set storage location
- Use the search bar and filters to find filaments quickly
- Low-stock alert appears when any filament hits 1 spool

### 4. Resolve Unmatched UPCs
Head to the **Unmatched** tab to fill in details for any unrecognized barcodes.

### 5. Export
Click **Export CSV** in the sidebar to save your full inventory to a file.

---

## Data Storage

Inventory is auto-saved to:
```
~/Library/Application Support/filament-vault/filament-vault-data.json
```
The exact path is shown at the bottom of the sidebar.

---

## Building for Distribution

To sign/notarize for macOS distribution, add your Apple credentials to `package.json` under the `build.mac` section. See [electron-builder docs](https://www.electron.build/code-signing) for details.

---

## Deploying to Netlify (Web Version)

The same `renderer/index.html` also runs in any modern browser — on Mac, iPhone, or Android — and is fully responsive. When there's no Electron bridge, the app automatically:
- saves inventory to the browser's **localStorage** (so data persists per-browser)
- uses the **HTML file picker** for catalog/scan imports
- uses **direct download** for CSV exports
- shows a **hamburger menu** below 900 px wide with a slide-in sidebar

### Option A — Drag-and-drop (easiest)
1. Zip the `renderer/` folder.
2. Go to [app.netlify.com/drop](https://app.netlify.com/drop).
3. Drag the zip (or the folder itself) onto the page. Done — you get a public URL.

### Option B — Netlify CLI
```bash
npm install -g netlify-cli
netlify login
cd filament-vaultV4
netlify deploy --dir=renderer          # preview URL
netlify deploy --dir=renderer --prod   # production URL
```

### Option C — Git-based continuous deploy
1. Push this folder to a GitHub repo.
2. In Netlify: **Add new site → Import an existing project**, pick the repo.
3. Leave the build command **empty** — `netlify.toml` already sets `publish = "renderer"`.
4. Deploy. Every git push will redeploy.

### Notes
- **Data is per-browser.** Open the site on your Mac and on your phone and you'll have two independent inventories. Use **Export CSV** on one and re-import on the other to move data between them.
- localStorage typically holds ~5 MB, which is ample for thousands of filament entries.
- To clear the browser's copy, use the **Clear Inventory** button in the sidebar, or clear the site's storage in the browser settings.
