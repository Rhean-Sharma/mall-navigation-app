import { chromium } from 'playwright';
const errors = [];
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true,
  permissions: [], geolocation: undefined });
page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });
await page.goto('file:///tmp/claude-0/-home-user-atlas/aa26cccc-f0bc-5b2a-8c99-5fcefbeb8ac4/scratchpad/index_full.html');
await page.waitForTimeout(1800);
await page.screenshot({ path: 'shot1_boot.png' });

// dismiss banner if present, enter demo mode via banner
const bannerVisible = await page.isVisible('#bDemo');
if (bannerVisible) { await page.click('#bDemo'); await page.waitForTimeout(600); }
await page.screenshot({ path: 'shot2_demo.png' });

// search for Nike
await page.fill('#q', 'nike');
await page.waitForTimeout(400);
await page.screenshot({ path: 'shot3_search.png' });
await page.click('.storeitem');
await page.waitForTimeout(700);
await page.screenshot({ path: 'shot4_selected.png' });

// navigate
const goVisible = await page.isVisible('#goBtn');
if (goVisible) { await page.click('#goBtn'); await page.waitForTimeout(900); }
await page.screenshot({ path: 'shot5_navigating.png' });

// district chip
await page.click('#closeSel').catch(()=>{});
await page.waitForTimeout(300);
const chips = await page.$$('.chip');
if (chips[1]) { await chips[1].click(); await page.waitForTimeout(600); }
await page.screenshot({ path: 'shot6_district.png' });

console.log(JSON.stringify({
  errors,
  stores: await page.evaluate(() => DATA.stores.length),
  routeDist: await page.evaluate(() => S.route ? Math.round(S.route.distM) : null),
  pos: await page.evaluate(() => S.pos),
}, null, 1));
await browser.close();
