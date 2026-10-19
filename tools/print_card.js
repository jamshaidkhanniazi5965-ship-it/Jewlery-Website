// Export the physical business card: cards/print/michel-business-card.pdf (2 pages, 96 x 61 mm incl. 3 mm bleed)
// and trimmed PNG previews. Run from the repo root while serving the site:  npx http-server -p 8090 .  then  node tools/print_card.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 420, height: 560 }, deviceScaleFactor: 6 });
  await p.goto('http://localhost:8090/cards/print/michel.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: 'cards/print/michel-business-card.pdf', width: '96mm', height: '61mm', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  const mm = 96 / 25.4; // CSS px per mm
  for (const [i, side] of [[0, 'front'], [1, 'back']]) {
    const box = await p.locator('.side').nth(i).boundingBox();
    await p.screenshot({ path: `cards/print/michel-card-${side}.png`, clip: { x: box.x + 3 * mm, y: box.y + 3 * mm, width: 90 * mm, height: 55 * mm } });
  }
  await b.close();
})();
