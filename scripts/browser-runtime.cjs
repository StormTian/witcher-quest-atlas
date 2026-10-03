// Cloud-first runtime; no dependency on a user computer.
const path = require('node:path');
let playwright;
if (process.env.PLAYWRIGHT_MODULE_PATH) playwright = require(process.env.PLAYWRIGHT_MODULE_PATH);
else {
  try { playwright = require('playwright'); }
  catch (error) {
    if (!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES) throw new Error('Playwright unavailable: set PLAYWRIGHT_MODULE_PATH or install playwright in the cloud runtime', {cause:error});
    playwright = require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, 'playwright'));
  }
}
const launchOptions = {headless:true, args:['--no-sandbox']};
if (process.env.CHROMIUM_EXECUTABLE_PATH) launchOptions.executablePath = process.env.CHROMIUM_EXECUTABLE_PATH;
const baseURL = process.env.ATLAS_BASE_URL || 'http://127.0.0.1:8765/';
const provenance = {executionEnvironment:'cloud-linux', browser:'Playwright Chromium', startedAt:new Date().toISOString()};
module.exports = {chromium:playwright.chromium, launchOptions, baseURL, provenance};
