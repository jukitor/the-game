// Spelar hela Mopsen som försvann i klickläget på en simulerad iPhone, bara med tryck.
// Kör: node aventyr/mopsen-klick/verktyg/klicktest.js [mapp för skärmbild]  (kräver Playwright)
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

  // Kontoret
  await tryck('svarare'); await valj('Lyssna på'); await vanta(16000); await logg('lyssna på telefonsvararen');
  await tryck('lada'); await valj('Öppna'); await logg('öppna lådan');
  await tryck('lada'); await valj('Ta tunnelbanekortet'); await logg('ta kortet');
  await tryck('lada'); await valj('Ta dyrken'); await logg('ta dyrken');
  await tryck('rock'); await valj('Undersök'); await logg('undersök rocken', 2);
  await tryck('utgang:ut'); await logg('gå ut');
  // Main Street
  await sak('Dollar'); await valj('Ge till'); await valj('Korvkiosk'); await vanta(1500); await logg('ge dollarn till Sal', 2);
  await tryck('utgang:ner'); await logg('ner i tunnelbanan');
  await tryck('karta'); await valj('Åk till Park Avenue'); await vanta(3500); await logg('åk till Park Avenue');
  await tryck('utgang:upp'); await tryck('utgang:in'); await vanta(800); await logg('in i Pettigrew Towers', 2);
  await tryck('utgang:ut'); await tryck('utgang:ner');
  await tryck('karta'); await valj('Åk till Chinatown'); await vanta(3500); await logg('åk till Chinatown');
  await tryck('utgang:upp'); await tryck('utgang:in'); await logg('in på Golden Dragon');
  await tryck('benny'); await valj('Visa'); await valj('Foto'); await logg('visa fotot för Benny', 2);
  await tryck('lyckokaka'); await valj('Bryt'); await logg('bryt lyckokakan', 2);
  await tryck('utgang:ut'); await tryck('utgang:ner');
  await tryck('karta'); await valj('Åk till Pir 9'); await vanta(3500); await logg('åk till Pir 9');
  await tryck('utgang:upp'); await logg('upp till piren');
  await tryck('dorr'); await valj('Gå in'); await logg('gå in (Bruno i vägen)');
  await tryck('bruno'); await valj('Ge'); await valj('Varmkorv'); await vanta(2500); await logg('ge korven till Bruno', 2);
  await sak('Dyrk'); await valj('Använd'); await valj('Dörr'); await vanta(3500); await logg('använd dyrken på dörren');
  await tryck('dorr'); await valj('Gå in'); await logg('gå in i lagret');
  await tryck('mops'); await valj('Ta'); await logg('ta mopsen (morrar)');
  await sak('Kex'); await valj('Använd'); await valj('Mopsen'); await vanta(2500); await logg('använd kexen på mopsen', 2);
  await tryck('mops'); await valj('Ta'); await logg('ta mopsen');
  await tryck('utgang:ut'); await tryck('utgang:ner');
  await tryck('karta'); await valj('Åk till Park Avenue'); await vanta(3500);
  await tryck('utgang:upp'); await tryck('utgang:in'); await vanta(9000); await logg('tillbaka till fru Pettigrew', 3);
  await m.screenshot({ path: S + '/helspel_slut.png' });
  console.log('Tryck totalt:', steg);
  console.log('Status:', await m.evaluate(() => document.querySelector('header').textContent.replace(/\s+/g, ' ').trim()));
  console.log('FEL', fel); await b.close();
})().catch(e => { console.error('AVBRÖTS:', e.message); process.exit(1); });
