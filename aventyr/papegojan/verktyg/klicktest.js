// Spelar hela Papegojan som visste för mycket i klickläget på en simulerad iPhone, bara med tryck.
// Kör: node aventyr/papegojan/verktyg/klicktest.js [mapp för skärmbild]  (kräver Playwright)
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

  const ladda = ms => m.waitForTimeout(ms);
  // Kontoret
  await tryck('telegram'); await valj('Läs'); await logg('läs telegrammet', 2);
  await tryck('telegram'); await valj('Ta'); await logg('ta telegrammet');
  await tryck('lada'); await valj('Öppna'); await logg('öppna lådan (kärvar)');
  await tryck('brevkniv'); await valj('Ta'); await logg('ta brevkniven');
  await sak('Brevkniven'); await valj('Använd'); await valj('Lådan'); await logg('bänd upp lådan', 2);
  await tryck('lada'); await valj('Ta tunnelbanekortet'); await logg('ta kortet');
  await tryck('lada'); await valj('Ta ficklampan'); await logg('ta ficklampan');
  await tryck('rock'); await valj('Ta'); await logg('ta rocken');
  await tryck('check'); await valj('Ta'); await logg('ta checken');
  await tryck('utgang:ut'); await tryck('utgang:ner'); await logg('ner i tunnelbanan');
  await tryck('karta'); await valj('Åk till Boulevarden'); await vanta(3500); await logg('åk till Boulevarden');
  await tryck('utgang:upp'); await tryck('utgang:ö'); await logg('österut');
  await tryck('dorrvakt'); await valj('Visa'); await valj('Telegrammet'); await logg('visa telegrammet för Sid');
  await tryck('utgang:in'); await tryck('utgang:in'); await vanta(500); await logg('in i logen', 2);
  await sak('Rocken'); await valj('Använd'); await valj('Papegojan'); await vanta(14000); await logg('täck buren med rocken', 3);
  await tryck('utgang:ut'); await tryck('utgang:ut'); await tryck('utgang:v');
  await tryck('tidningsforsaljare'); await valj('Prata med'); await vanta(1500); await logg('prata med Lenny', 2);
  await tryck('utgang:v'); await tryck('porttelefon'); await valj('Ring hos Smith'); await logg('ring hos Smith', 2);
  await tryck('utgang:v'); await tryck('utgang:in'); await logg('in i pantbanken');
  await tryck('pantlanare'); await valj('Ge'); await valj('Checken'); await logg('ge checken till Pickles', 2);
  await tryck('paraply'); await valj('Ta'); await logg('köp paraplyet', 2);
  await tryck('batterier'); await valj('Ta'); await logg('köp batterierna', 2);
  await sak('Batterier'); await valj('Använd'); await valj('Ficklampan'); await logg('batterier i ficklampan', 2);
  await tryck('utgang:ut'); await tryck('utgang:ö'); await tryck('utgang:n'); await logg('in i gränden');
  await sak('Paraplyet'); await valj('Använd'); await valj('Urmakarens brandstege'); await vanta(1500); await logg('haka ner stegen', 2);
  await tryck('brandstege_ur'); await valj('Klättra till andra'); await logg('fel våning');
  await tryck('brandstege_ur'); await valj('Klättra till tredje'); await logg('tredje våningen');
  await tryck('fonster3'); await valj('Gå in'); await logg('in genom fönstret', 2);
  await tryck('hattask'); await valj('Öppna'); await logg('öppna hattasken', 2);
  await tryck('hattask'); await valj('Ta noterna'); await logg('ta noterna', 2);
  await tryck('brev_f'); await valj('Ta'); await logg('ta brevet');
  await tryck('utgang:ut'); await tryck('utgang:ner'); await tryck('utgang:s'); await tryck('utgang:ö'); await tryck('utgang:ö');
  await tryck('utgang:in'); await logg('tillbaka på klubben');
  await tryck('pianist'); await valj('Visa'); await valj('Brevet'); await logg('visa brevet för pianisten', 2);
  await tryck('utgang:in'); await vanta(9000); await logg('tillbaka till Lola', 3);
  await m.screenshot({ path: S + '/helspel_slut.png' });
  console.log('Tryck totalt:', steg);
  console.log('Status:', await m.evaluate(() => document.querySelector('header').textContent.replace(/\s+/g, ' ').trim()));
  console.log('FEL', fel); await b.close();
})().catch(e => { console.error('AVBRÖTS:', e.message); process.exit(1); });
