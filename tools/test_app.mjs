// Playwright smoke test: boot, GPS projection, heading-up rotation, search, route.
// Serve the repo root (e.g. `python3 -m http.server 8123`) then:
//   node tools/test_app.mjs [url]
import { chromium } from 'playwright';
const URL = process.argv[2] || 'http://127.0.0.1:8123/index.html';
const NF = { latitude: 41.32115, longitude: -74.12842, accuracy: 12 };   // The North Face
const KIPLING = { latitude: 41.319804, longitude: -74.128075, accuracy: 12 };
const errors = [];
const results = {};

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' });
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true,
  geolocation: NF, permissions: ['geolocation'],
});
const page = await ctx.newPage();
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
page.on('console', m => { if (m.type() === 'error' && !m.text().includes('404')) errors.push('CONSOLE: ' + m.text()); });

await page.goto(URL);
await page.waitForTimeout(1600);
results.posAtNF = await page.evaluate(() => S.pos && [Math.round(S.pos.x), Math.round(S.pos.y)]);  // expect [821,964]
await page.screenshot({ path: 'shot1_boot.png' });

await ctx.setGeolocation(KIPLING);
await page.waitForTimeout(1200);
results.posAtKipling = await page.evaluate(() => S.pos && [Math.round(S.pos.x), Math.round(S.pos.y)]);  // expect [1128,737]

await ctx.setGeolocation(NF);
await page.waitForTimeout(1200);
await page.click('#locateFab');
await page.waitForTimeout(500);

// heading-up: synthetic orientation events, true heading 160°
await page.click('#compassFab');
await page.waitForTimeout(300);
await page.evaluate(() => {
  const fire = a => window.dispatchEvent(new DeviceOrientationEvent('deviceorientation', { alpha: a, beta: 0, gamma: 0, absolute: true }));
  let n = 0;
  fire(187.4);
  const iv = setInterval(() => { n++; fire(187.4 + Math.sin(n) * 0.2); if (n > 40) clearInterval(iv); }, 33);
});
await page.waitForTimeout(2000);
results.rot = await page.evaluate(() => S.rot);           // expect ≈ -(160-115.5)°
results.rotExpected = -(160 - 115.5) * Math.PI / 180;
await page.screenshot({ path: 'shot2_headingup.png' });
await page.click('#compassFab');
await page.waitForTimeout(400);

await page.fill('#q', 'nike');
await page.waitForTimeout(400);
await page.click('.storeitem');
await page.waitForTimeout(600);
if (await page.isVisible('#goBtn')) { await page.click('#goBtn'); await page.waitForTimeout(800); }
results.routeDist = await page.evaluate(() => S.route ? Math.round(S.route.distM) : null);
await page.screenshot({ path: 'shot3_route.png' });

console.log(JSON.stringify({ errors, ...results }, null, 1));
await browser.close();
