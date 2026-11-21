// Spelar hela Borgmästarens långkalsonger i klickläget på en simulerad iPhone, bara med tryck.
// Kör: node aventyr/kalsongerna/verktyg/klicktest.js [mapp för skärmbild]  (kräver Playwright)
const { chromium, devices } = require('playwright');
const path = require('path');
const S = process.argv[2] || '.', URL = 'file://' + path.resolve(__dirname, '../index.html');
(async () => {
  const b = await chromium.launch(); const fel = [];
  const ctx = await b.newContext(devices['iPhone 13']); const m = await ctx.newPage();
  m.on('pageerror', e => fel.push(e.message)); m.on('console', x => { if (x.type() === 'error' && !x.text().includes('URL scheme "file"')) fel.push(x.text()) });
  await m.goto(URL); await m.waitForTimeout(400);
  await m.tap('#splash'); await m.waitForTimeout(1500);
  let steg = 0;
  const rum = () => m.evaluate(() => document.querySelector('#scenbild').dataset.bild || '');
  const sista = (n = 2) => m.evaluate(n => [...document.querySelectorAll('#log p')].slice(-n).map(e => e.textContent.slice(0, 110)), n);
  // En punkt mitt i en klickyta (den pixel i ytan som ligger längst från ytans kant)
  const punkt = namn => m.evaluate(namn => {
    const D = window.AVENTYRSDATA, bild = document.querySelector("#scenbild").dataset.bild;
    const y = D.bilder.ytor && D.bilder.ytor[bild]; if (!y) return null;
    const bin = atob(y.karta), k = new Uint8Array(192 * 120); let p = 0;
    for (let i = 0; i < bin.length; i += 2) { k.fill(bin.charCodeAt(i), p, p + bin.charCodeAt(i + 1)); p += bin.charCodeAt(i + 1); }
    const v = y.namn.indexOf(namn) + 1; if (!v) return null;
    let bast = null, bd = -1;
    for (let yy = 0; yy < 120; yy++) for (let xx = 0; xx < 192; xx++) {
      if (k[yy * 192 + xx] !== v) continue;
      let d = 0; while (d < 40) { d++; const ok = [[d, 0], [-d, 0], [0, d], [0, -d]].every(([dx, dy]) => { const X = xx + dx, Y = yy + dy; return X >= 0 && Y >= 0 && X < 192 && Y < 120 && k[Y * 192 + X] === v; }); if (!ok) break; }
      if (d > bd) { bd = d; bast = [xx, yy]; }
    }
    return bast;
  }, namn);
  const tryck = async namn => {
    const pt = await punkt(namn); if (!pt) throw new Error('Ingen klickyta ' + namn + ' i ' + await rum());
    const r = await m.locator('#scenbild').boundingBox();
    await m.tap('#scenbild', { position: { x: (pt[0] + 0.5) * r.width / 192, y: (pt[1] + 0.5) * r.height / 120 } });
    await m.waitForTimeout(350); steg++;
  };
  const valj = async text => {
    const knapp = m.locator('.klickmeny:not([hidden]) button', { hasText: new RegExp('^' + text) }).first();
    if (!await knapp.count()) throw new Error(`Inget menyval "${text}". Menyn: ` + JSON.stringify(await m.evaluate(() => [...document.querySelectorAll('.klickmeny:not([hidden]) button')].map(e => e.textContent))));
    await knapp.tap(); await m.waitForTimeout(400); steg++;
  };
  const sak = async text => { await m.locator('#agodelar button', { hasText: text }).first().tap(); await m.waitForTimeout(300); steg++; };
  const logg = async (vad, n = 1) => console.log(('[' + await rum() + ']').padEnd(13), vad.padEnd(28), '→', (await sista(n)).join(' | '));
  const vanta = ms => m.waitForTimeout(ms);

  // Svara i ett samtal: tryck på svarsknappen som börjar med texten
  const svara = async text => {
    const knapp = m.locator('.samtalsval:not([hidden]) button', { hasText: new RegExp('^' + text.replace(/[.?*+()]/g, '\\$&')) }).first();
    if (!await knapp.count()) throw new Error(`Inget svar "${text}". Svaren: ` + JSON.stringify(await m.evaluate(() => [...document.querySelectorAll('.samtalsval button')].map(e => e.textContent))));
    await knapp.tap(); await m.waitForTimeout(300); steg++;
  };
  const svarAlla = async (...t) => { for (const x of t) await svara(x); };
  // Kontoret
  await tryck('svarare'); await valj('Svara i'); await svarAlla('Det beror på', 'Varför inte polisen', 'Hur kommer jag'); await logg('telefonsamtalet', 2);
  await tryck('lada'); await valj('Öppna'); await tryck('lada'); await valj('Ta tunnelbanekortet'); await tryck('lada'); await valj('Ta ficklampan');
  await tryck('tvattlapp'); await valj('Ta'); await logg('kort, ficklampa, tvättlapp');
  await tryck('utgang:ut'); await tryck('utgang:ner'); await tryck('karta'); await valj('Åk till Boulevarden'); await vanta(3000);
  await tryck('utgang:upp'); await tryck('utgang:v'); await tryck('utgang:v'); await tryck('utgang:n'); await logg('rådhuset');
  await tryck('receptionist'); await valj('Prata med'); await svara('Jag kommer från tvätteriet'); await logg('receptionen', 2);
  await tryck('utgang:upp'); await svarAlla('Jag lovar', 'Vad står det', 'Fortsätt', 'Var ligger tvätteriet', 'Fortsätt', 'Jag ska hitta dem'); await logg('borgmästaren', 2);
  await tryck('utgang:ner'); await tryck('utgang:ut'); await tryck('utgang:ö'); await tryck('utgang:n'); await tryck('utgang:in'); await logg('tvätteriet');
  await tryck('grubb'); await valj('Prata med');
  await svarAlla('Här är min tvättlapp', 'Får jag fråga', 'Hur såg han ut', 'Något mer', 'Sa han något', 'Något mer', 'Märkte du', 'Något mer', 'Tack, fru Grubb'); await logg('fru Grubb', 2);
  await tryck('utgang:ut'); await tryck('utgang:s'); await tryck('utgang:ö'); await tryck('utgang:ö'); await tryck('utgang:n'); await logg('radiohuset');
  await tryck('rex'); await valj('Prata med'); await svarAlla('Varje kväll', 'Gärna'); await logg('Rex Rapp', 2);
  await tryck('utgang:s'); await tryck('utgang:v'); await tryck('utgang:ner'); await tryck('karta'); await valj('Åk till Main Street'); await vanta(3000);
  await tryck('utgang:upp'); await tryck('utgang:ö'); await tryck('utgang:in'); await logg('hotellet');
  await tryck('piccolo'); await valj('Prata med'); await svarAlla('Kan du hjälpa', 'Jag ska se'); await logg('piccolon 1');
  await tryck('piccolo'); await valj('Prata med'); await svara('Här är en autograf'); await logg('piccolon 2', 2);
  await tryck('gastbok'); await valj('Läs'); await logg('gästboken', 2);
  await tryck('utgang:n'); await logg('baren');
  await sak('Utpressningsbrevet'); await valj('Använd'); await valj('Bordslampan'); await logg('brevet mot lampan', 2);
  await tryck('vane'); await valj('Prata med'); await svarAlla('Lila bläck', 'Varför kalsonger', 'Ni får förklara'); await logg('Vivian Vane', 2);
  await tryck('utgang:s'); await tryck('utgang:ut'); await tryck('utgang:v'); await tryck('utgang:ner'); await tryck('karta'); await valj('Åk till Chinatown'); await vanta(3000);
  await tryck('utgang:upp'); await tryck('utgang:in'); await tryck('lyckokaka'); await valj('Bryt'); await logg('lyckokakan', 2);
  await tryck('utgang:ut'); await tryck('utgang:n'); await tryck('titthal'); await valj('Slå på'); await svara('Den gyllene draken'); await logg('lösenordet', 2);
  await tryck('utgang:ö'); await tryck('skuldsedel'); await valj('Ta'); await logg('skuldsedeln', 2);
  await tryck('utgang:ut'); await tryck('utgang:s'); await tryck('utgang:ner'); await tryck('karta'); await valj('Åk till Pir 9'); await vanta(3000);
  await tryck('utgang:upp'); await tryck('utgang:s'); await logg('fiskmarknaden');
  await tryck('fiskhandlare'); await valj('Prata med'); await svarAlla('Har du sett', 'Tack'); await logg('fiskhandlaren', 2);
  await tryck('utgang:ö'); await tryck('utgang:in'); await logg('in utan frågesport');
  await tryck('lou'); await valj('Prata med'); await svarAlla('Jag tar frågesporten', 'Ezekiel Harbor', '1889', 'Femte'); await logg('frågesporten', 2);
  await tryck('lou'); await valj('Prata med'); await svarAlla('Jag vet att du stal', 'Din skuldsedel', 'Fortsätt', 'Erkänn'); await logg('Lou erkänner', 2);
  await tryck('utgang:in'); await tryck('utgang:in'); await logg('spöktåget', 2);
  await tryck('kalsonger'); await valj('Ta'); await logg('långkalsongerna', 2);
  await tryck('utgang:ut'); await tryck('utgang:ut'); await tryck('utgang:v'); await tryck('utgang:n'); await tryck('utgang:ner'); await tryck('karta'); await valj('Åk till Main Street'); await vanta(3000);
  await tryck('utgang:upp'); await tryck('utgang:v'); await tryck('utgang:in'); await tryck('utgang:in');
  await tryck('ohara'); await valj('Prata med'); await svara('Jag har både'); await logg('kommissarien', 2);
  await tryck('utgang:ut'); await tryck('utgang:ut'); await tryck('utgang:ö'); await tryck('utgang:ner'); await tryck('karta'); await valj('Åk till Boulevarden'); await vanta(3000);
  await tryck('utgang:upp'); await tryck('utgang:v'); await tryck('utgang:v'); await tryck('utgang:n'); await tryck('utgang:upp'); await vanta(9000); await logg('tillbaka till borgmästaren', 3);
  await m.screenshot({ path: S + '/helspel_slut.png' });
  console.log('Tryck totalt:', steg);
  console.log('Status:', await m.evaluate(() => document.querySelector('header').textContent.replace(/\s+/g, ' ').trim()));
  console.log('FEL', fel); await b.close();
})().catch(e => { console.error('AVBRÖTS:', e.message); process.exit(1); });
