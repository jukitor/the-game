// Spelar hela textversionen av Papegojan som visste för mycket genom att skriva kommandon.
// Kör: node aventyr/papegojan/verktyg/texttest.js  (kräver Playwright)
const { chromium } = require('playwright');
const path = require('path');
const URL = 'file://' + path.resolve(__dirname, '../../papegojan-text/index.html');
const KOMMANDON = [
  'läs telegrammet', 'ta telegrammet', 'öppna lådan', 'ta brevkniven', 'bänd upp lådan med brevkniven', 'ta kortet', 'ta ficklampan',
  'ta rocken', 'ta checken', 'ner', 'ner', 'åk till boulevarden', 'upp', 'ö', 'in', 'visa telegrammet för sid', 'in', 'in', '#600',
  'prata med papegojan', 'täck buren med rocken', '#14000', 'prata med lola', 'ut', 'ut', 'v', 'prata med tidningsförsäljaren', '#1500',
  'v', 'undersök porttelefonen', 'ring hos smith', 'v', 'in', 'köp paraplyet', 'sälj checken', 'köp paraplyet', 'köp batterierna',
  'sätt i batterierna', 'ut', 'ö', 'n', 'klättra upp', 'haka ner stegen med paraplyet', '#1500',
  'klättra till fjärde våningen på urmakarens brandstege', 'klättra till tredje våningen på urmakarens brandstege', 'gå in',
  'öppna hattasken', 'ta noterna', 'ta brevet', 'läs brevet', 'ut', 'ner', 's', 'ö', 'ö', 'in', 'visa brevet för pianisten', 'in', '#9000',
];
(async () => {
  const b = await chromium.launch(); const m = await b.newPage({ viewport: { width: 1000, height: 800 } }); const fel = [];
  m.on('pageerror', e => fel.push(e.message));
  await m.goto(URL); await m.waitForTimeout(400); await m.click('#splash'); await m.waitForTimeout(1200);
  for (const c of KOMMANDON) {
    if (c[0] === '#') { await m.waitForTimeout(+c.slice(1)); continue; }
    const fore = await m.evaluate(() => document.querySelectorAll('#log p').length);
    await m.fill('#cmd', c); await m.press('#cmd', 'Enter'); await m.waitForTimeout(250);
    const svar = await m.evaluate(n => [...document.querySelectorAll('#log p')].slice(n + 1).map(p => p.textContent), fore);
    console.log(('> ' + c).padEnd(58), '→', svar.slice(-2).map(t => t.slice(0, 100)).join(' | '));
  }
  console.log('Status:', await m.evaluate(() => document.getElementById('nums').textContent));
  console.log('FEL', fel); await b.close();
})();
