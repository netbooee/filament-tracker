const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

// Path for auto-saving inventory data
const dataPath = path.join(app.getPath('userData'), 'filament-vault-data.json');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 900,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',  // macOS native inset traffic lights
    backgroundColor: '#F5F3EE',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    title: 'Filament Vault'
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// ── IPC: Load saved data ──────────────────────────────────────────────────────
ipcMain.handle('load-data', () => {
  try {
    if (fs.existsSync(dataPath)) {
      const raw = fs.readFileSync(dataPath, 'utf-8');
      return JSON.parse(raw);
    }
  } catch (e) {
    console.error('Failed to load data:', e);
  }
  return null;
});

// ── IPC: Auto-save data ───────────────────────────────────────────────────────
ipcMain.handle('save-data', (event, data) => {
  try {
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2), 'utf-8');
    return { success: true };
  } catch (e) {
    console.error('Failed to save data:', e);
    return { success: false, error: e.message };
  }
});

// ── IPC: Open file dialog ─────────────────────────────────────────────────────
ipcMain.handle('open-file-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: options.filters || []
  });
  if (result.canceled || result.filePaths.length === 0) return null;
  try {
    const content = fs.readFileSync(result.filePaths[0], 'utf-8');
    return { filePath: result.filePaths[0], content };
  } catch (e) {
    return { error: e.message };
  }
});

// ── IPC: Save export CSV ──────────────────────────────────────────────────────
ipcMain.handle('save-export-dialog', async (event, csvContent) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: 'filament-vault-export.csv',
    filters: [{ name: 'CSV Files', extensions: ['csv'] }]
  });
  if (result.canceled) return null;
  try {
    fs.writeFileSync(result.filePath, csvContent, 'utf-8');
    return { success: true, filePath: result.filePath };
  } catch (e) {
    return { success: false, error: e.message };
  }
});

// ── IPC: Get data file path (for display) ─────────────────────────────────────
ipcMain.handle('get-data-path', () => dataPath);
