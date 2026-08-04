#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const destDir = path.join(os.homedir(), '.gemini', 'config', 'plugins', 'antigravity-boost');

console.log('\n🚀  \x1b[36m\x1b[1mantigravity-boost\x1b[0m — Developer Productivity & Speed Booster');
console.log('─────────────────────────────────────────────────────────────');

try {
  const pluginsParent = path.join(os.homedir(), '.gemini', 'config', 'plugins');
  if (!fs.existsSync(pluginsParent)) {
    fs.mkdirSync(pluginsParent, { recursive: true });
  }

  if (fs.existsSync(destDir)) {
    console.log('📦 Cleaning previous installation...');
    fs.rmSync(destDir, { recursive: true, force: true });
  }

  console.log('📥 Installing plugin files to ~/.gemini/config/plugins/antigravity-boost...');
  
  let success = false;
  try {
    execSync('git clone --depth 1 https://github.com/AndrewMason7/antigravity-boost.git "' + destDir + '"', { stdio: 'ignore' });
    success = true;
  } catch (err) {
    // Fallback to HTTPS tarball if git is unavailable
    try {
      fs.mkdirSync(destDir, { recursive: true });
      execSync('curl -sSL https://github.com/AndrewMason7/antigravity-boost/archive/refs/heads/main.tar.gz | tar -xz -C "' + destDir + '" --strip-components=1', { stdio: 'ignore' });
      success = true;
    } catch (tarErr) {
      // Fallback to copying local plugin dir if running inside cloned repo
      const localRepo = path.resolve(__dirname, '..');
      if (fs.existsSync(path.join(localRepo, 'plugin.json'))) {
        fs.cpSync(localRepo, destDir, { recursive: true });
        success = true;
      }
    }
  }

  if (!success) {
    throw new Error('Could not download or copy plugin files.');
  }

  // Set executable permissions on script files
  const scriptsDir = path.join(destDir, 'scripts');
  if (fs.existsSync(scriptsDir)) {
    try {
      execSync('chmod +x "' + scriptsDir + '"/*.py "' + path.join(scriptsDir, 'core') + '"/*.py', { stdio: 'ignore' });
    } catch (e) {
      // Ignore chmod errors on Windows
    }
  }

  console.log('\n✅  \x1b[32m\x1b[1mSuccessfully installed antigravity-boost!\x1b[0m');
  console.log('💡  Start Google Antigravity and type \x1b[33m/boost\x1b[0m to view status.\n');
} catch (error) {
  console.error('\n❌  \x1b[31mInstallation failed:\x1b[0m', error.message);
  process.exit(1);
}
