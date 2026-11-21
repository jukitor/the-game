/* ==========================================================================
   SPELMOTORN
   En generisk motor för textäventyr på svenska med bilder, animationer, ljud
   och startskärm. Själva äventyret beskrivs i en konfiguration (window.AVENTYR)
   och genererad data (window.AVENTYRSDATA). Se README för formatet.
   ========================================================================== */
"use strict";
function startaSpelmotorn() {
const A = window.AVENTYR;
const D = window.AVENTYRSDATA || {};
if (!A) { document.body.textContent = "Inget äventyr hittades (window.AVENTYR saknas)."; return; }

// ---------------------------------------------------------------------------
//  Standardtexter. Äventyret kan byta ut vilka som helst via A.texter.
// ---------------------------------------------------------------------------
const TEXTER = Object.assign({
  tomtKommando: "Ursäkta?",
  okantOrd: 'Jag förstår inte ordet "{ord}". Skriv HJÄLP för exempel på kommandon.',
  okantObjekt: 'Ordet "{ord}" känner jag inte till. Försök med något annat.',
  inteHar: "Det ser du inte här.",
  sagVad: "Du måste säga vad du menar.",
  ingenUtgang: ["Du kan inte gå åt det hållet."],
  gaVart: "Vart vill du gå? Prova UPP, NER, IN eller UT.",
  harFinns: "Här finns {lista}.",
  och: "och",
  taget: "Taget.",
  tagetLista: "{Objekt}: taget.",
  redanBuren: "Den har du redan.",
  taPerson: "Det vore olämpligt.",
  taFast: "Det sitter fast.",
  taIngetAtt: "Det finns inget här som är värt att ta.",
  slappt: "Släppt.",
  harInte: "Du har inte den.",
  barPa: "Du bär på {lista}.",
  barInget: "Du har ingenting.",
  iDenLigger: "I den ligger {lista}.",
  denArTom: "Den är tom.",
  stangd: "Den är stängd.",
  redanOppen: "Den är redan öppen.",
  oppnad: "Du öppnar {objekt}.",
  kanInteOppna: "Det går inte att öppna.",
  stangdNu: "Du stänger {objekt}.",
  kanInteStanga: "Det går inte att stänga.",
  stangVad: "Vad vill du stänga?",
  ingetAttLasa: "Det finns inget att läsa på den.",
  letarRunt: "Du letar runt, men hittar inget du inte redan sett.",
  geVem: "Vem vill du ge den till?",
  geIngen: "Ingen här verkar intresserad.",
  visaIngen: "Det finns ingen här att visa den för.",
  visaReaktion: "Ingen reaktion.",
  prataSjalv: "Du pratar för dig själv en stund.",
  prataInget: "Du får inget svar.",
  lyssna: "Du hör inget särskilt.",
  lukta: "Du känner ingen särskild lukt.",
  at: "Det där ska inte ätas.",
  klappa: "Det vill inte bli klappat.",
  taPaSig: "Det kan du inte ta på dig.",
  anvand: "Du kommer inte på hur det skulle gå till.",
  hjalpKlick: [
    "Tryck på saker i bilden för att se vad du kan göra med dem. Det du bär visas under texten. Tryck på en sak där för att undersöka, använda eller ge bort den.",
    "Tryck på en tom del av bilden för att se dig omkring igen. Under MENY finns ledtrådar, poäng, sparning, ljud och hjälp.",
  ],
  ejMojligt: "Det går inte.",
  vanta: ["Tiden går."],
  mataMed: "Vad vill du mata med?",
  spelSlut: "Spelet är slut. Skriv OMSTART för att spela igen, eller POÄNG för att se hur det gick.",
  poangOkade: "[Din poäng ökade med {n}.]",
  poangRapport: "Du har {poang} av {max} möjliga poäng efter {drag} drag.",
  poangHittills: "Hittills har du {lista}.",
  rang: "Rang: {rang}.",
  slutsummering: "Du fick {poang} av {max} möjliga poäng på {drag} drag.",
  ledtrad: "Ledtråd: {text}",
  sparat: "Spelet är sparat.",
  kanInteSpara: "Det gick inte att spara här. Webbläsaren tillåter inte lagring på den här sidan.",
  ingetSparat: "Det finns inget sparat spel.",
  laddat: "Sparat spel laddat.",
  kanInteLadda: "Det gick inte att ladda det sparade spelet.",
  tillbaka: "Du är tillbaka i spelet.",
  omstartRubrik: "Börja om?",
  omstartFraga: "Allt du har gjort hittills försvinner och spelet börjar från början. Ett spel du har sparat med Spara finns kvar.",
  omstartJa: "Börja om", omstartNej: "Fortsätt spela",
  omstartAvbruten: "Du fortsätter där du är.",
  fortsatter: "Du fortsätter där du slutade förra gången. Vill du börja om från början skriver du OMSTART.",
  fortsatterKlick: "Du fortsätter där du slutade förra gången. Vill du börja om från början väljer du Börja om i menyn.",
  bilderPa: "Bilderna är påslagna.",
  bilderAv: "Bilderna är avstängda. Skriv BILD för att slå på dem igen.",
  ljudPa: "Ljudet är påslaget.",
  ljudAv: "Ljudet är avstängt. Skriv LJUD för att slå på det igen.",
  musikPa: "Musiken är påslagen.",
  musikAv: "Musiken är avstängd. Miljöljud och effekter hörs fortfarande.",
  ljudknappPa: "Ljud på", ljudknappAv: "Ljud av",
  inmatning: "Skriv vad du vill göra…",
  hjalp: [
    "Du styr spelet genom att skriva vad du vill göra, med korta meningar på svenska. Oftast räcker ett verb, ibland följt av vad eller vem det gäller.",
    "TITTA (eller T): se dig omkring\nUNDERSÖK något (eller U): titta närmare på något\nTA, SLÄPP, ÖPPNA, LÄS: hantera saker\nPRATA MED, GE, VISA: ta kontakt med folk\nUPP, NER, IN, UT: gå åt ett håll\nINVENTARIE (eller I): se vad du bär på",
    "Undersök det du ser och prata med dem du möter. Kör du fast kan du skriva LEDTRÅD.",
  ],
  hjalpOvrigt: "Övrigt: POÄNG, LEDTRÅD, BILD (bilder av/på), LJUD (allt ljud av/på), MUSIK (musiken av/på), SPARA, LADDA, OMSTART. Pil upp hämtar förra kommandot.",
  // Varianter för klickläget, där man inte kan skriva. Används i stället för texten med samma namn utan "Klick".
  spelSlutKlick: "Spelet är slut. Välj Börja om i menyn för att spela igen.",
  ljudAvKlick: "Ljudet är avstängt. Du kan slå på det igen under Meny.",
  bilderAvKlick: "Bilderna är avstängda.",
}, A.texter || {});
// I klickläget används <namn>Klick i stället för <namn>, utom när äventyret självt har bytt ut <namn> men inte <namn>Klick
if (A.lage === "klick") for (const k of Object.keys(TEXTER)) {
  const bas = k.slice(0, -5), egna = A.texter || {};
  if (k.endsWith("Klick") && k !== "hjalpKlick" && !(egna[bas] !== undefined && egna[k] === undefined)) TEXTER[bas] = TEXTER[k];
}

// ---------------------------------------------------------------------------
//  Svenska: riktningar, utfyllnadsord och verb
// ---------------------------------------------------------------------------
const RIKTNINGAR = {
  n: "n", norr: "n", nord: "n", s: "s", söder: "s", syd: "s", ö: "ö", öster: "ö", öst: "ö", o: "ö",
  v: "v", väster: "v", väst: "v", upp: "upp", uppåt: "upp", ner: "ner", nedåt: "ner", ned: "ner",
  in: "in", innanför: "in", ut: "ut", utåt: "ut", ute: "ut",
};
const UTFYLLNAD = new Set(["den", "det", "de", "en", "ett", "min", "mitt", "mina", "lite", "the", "och", "så", "sedan", "då", "försiktigt", "snabbt"]);
// Motorns verb: kanoniskt namn -> ord som betyder samma sak. Äventyret kan lägga till egna verb och ord.
const MOTORVERB = {
  titta: ["titta", "t", "se", "beskriv", "kolla"],
  undersök: ["undersök", "u", "granska", "studera", "inspektera", "betrakta"],
  sök: ["sök", "leta", "rota", "känn"],
  "ta på": ["ta på"],
  ta: ["ta", "plocka", "hämta", "grip", "lyft", "bär"],
  släpp: ["släpp", "lägg", "ställ", "kasta"],
  inventarie: ["i", "inv", "inventarie", "inventering", "ägodelar", "fickor"],
  öppna: ["öppna"], stäng: ["stäng"], läs: ["läs"],
  lyssna: ["lyssna", "spela", "tryck"],
  ge: ["ge", "erbjud", "räck"], mata: ["mata"], visa: ["visa"],
  prata: ["prata", "tala", "fråga", "säg", "hälsa", "förhör"],
  ät: ["ät", "smaka"], klappa: ["klappa", "kela"],
  vänta: ["vänta", "z"], lukta: ["lukta", "nosa", "bli"],
  gå: ["gå", "spring", "promenera", "kliv", "kryp"],
  använd: ["använd", "använda", "nyttja"],
};
const VERB = {};   // ord -> kanoniskt verb (två ord före ett)
function laggTillVerb(tabell) {
  for (const [kanon, ord] of Object.entries(tabell)) for (const o of ord) VERB[o] = kanon;
}
laggTillVerb(MOTORVERB);
laggTillVerb(A.verb || {});
if (A.resor) laggTillVerb({ "åk": A.resor.verb || ["åk", "res"] });
const META = {
  hjälp: ["hjälp", "help", "?", "instruktioner"], ledtråd: ["ledtråd", "tips", "hint"], poäng: ["poäng", "score", "status"],
  spara: ["spara", "save"], ladda: ["ladda", "load", "återställ"], bild: ["bild", "bilder"], ljud: ["ljud"], musik: ["musik"],
  omstart: ["omstart", "restart", "börja om"],
};

// ---------------------------------------------------------------------------
//  Spelets tillstånd
// ---------------------------------------------------------------------------
const RUM = A.rum, OBJ = A.objekt, POANG = A.poang || {};
const MAX = A.maxPoang || Object.values(POANG).reduce((a, p) => a + p[0], 0);
const NYCKEL = A.id || "aventyr";
let S;
function nyttTillstand() {
  const loc = {}, oppen = {};
  for (const [id, o] of Object.entries(OBJ)) { loc[id] = o.plats === undefined ? null : o.plats; if (o.oppen) oppen[id] = true; }
  return { room: A.start, moves: 0, score: 0, loc, f: {}, oppen, scored: {}, over: false, besokt: {}, kortNr: {} };
}

// ---------------------------------------------------------------------------
//  Gränssnittet (byggs av motorn)
// ---------------------------------------------------------------------------
const sk = A.startskarm;
// Bilder kan lånas från ett annat äventyr med A.bildmapp, t.ex. "../annat/bilder/"
const bildvag = p => A.bildmapp && p.startsWith("bilder/") ? A.bildmapp + p.slice(7) : p;
document.title = A.titel;
document.body.insertAdjacentHTML("afterbegin", `
${sk ? `<div class="splash" id="splash" role="button" tabindex="0" aria-label="${esc(A.titel)}. Klicka för att börja spela.">
  <picture>${sk.bildStaende ? `<source media="(orientation: portrait)" srcset="${esc(bildvag(sk.bildStaende))}">` : ""}
    <img src="${esc(bildvag(sk.bild))}" alt="${esc(sk.alt || "")}"></picture>
  ${sk.regn ? `<canvas id="splashregn" aria-hidden="true"></canvas>` : ""}
  <h1 class="logo" id="splashtitel">${sk.ort ? `<span class="ort">${esc(sk.ort)}</span>` : ""}<span class="titel">${esc(sk.titel || A.titel)}</span>${sk.under ? `<span class="under">${esc(sk.under)}</span>` : ""}</h1>
</div>` : ""}
<header class="status"><div class="wrap">
  <span class="title">${esc(A.titel)}</span><span class="where" id="where">–</span><span class="nums" id="nums"></span>
</div></header>
<figure class="scen" id="scen" hidden><canvas id="scenbild" role="img" aria-label="Bild"></canvas></figure>
<main id="scroller"><div class="wrap"><div id="log" aria-live="polite"></div><div id="fyll" aria-hidden="true"></div></div></main>
<footer class="input"><div class="wrap">
  <form id="f" autocomplete="off"><label for="cmd">&gt;</label>
    <input id="cmd" type="text" spellcheck="false" autocapitalize="off" aria-label="Skriv ett kommando" placeholder="${esc(TEXTER.inmatning)}"></form>
  <div class="quick" id="quick">${(A.snabbknappar || [["Titta", "titta"], ["Ägodelar", "inventarie"], ["Upp", "upp"], ["Ner", "ner"], ["In", "in"], ["Ut", "ut"], ["Ledtråd", "ledtråd"], ["Bild", "bild"], ["Ljud", "ljud"], ["Hjälp", "hjälp"]])
    .map(([t, c]) => `<button type="button" data-c="${esc(c)}"${c === "ljud" ? ' id="ljudknapp"' : ""}>${esc(t)}</button>`).join("")}</div>
</div></footer>`);
function esc(t) { return String(t).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

const logEl = document.getElementById("log");
const scroller = document.getElementById("scroller");
const fyll = document.getElementById("fyll");
const input = document.getElementById("cmd");
const pekskarm = !!(window.matchMedia && window.matchMedia("(pointer: coarse)").matches);
const rorelseOk = !(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

function out(text, cls) {
  const p = document.createElement("p");
  if (cls) p.className = cls;
  p.textContent = text;
  logEl.appendChild(p);
  return p;
}
function scrollDown() { requestAnimationFrame(() => { scroller.scrollTop = scroller.scrollHeight; }); }
function scrollTill(el) {
  requestAnimationFrame(() => {
    if (!el || !el.isConnected) { fyll.style.height = "0px"; scroller.scrollTop = 0; return; }
    const kvar = logEl.getBoundingClientRect().bottom - el.getBoundingClientRect().top;
    fyll.style.height = Math.max(0, scroller.clientHeight - kvar - 12) + "px";
    scroller.scrollTop += el.getBoundingClientRect().top - scroller.getBoundingClientRect().top - 12;
  });
}
let haller = null;
function hallKvar() { if (haller && performance.now() < haller.tills) scrollTill(haller.el); }
window.addEventListener("resize", hallKvar);
if (window.visualViewport) window.visualViewport.addEventListener("resize", hallKvar);
["touchstart", "wheel"].forEach(ev => scroller.addEventListener(ev, () => { haller = null; }, { passive: true }));

// En liten gul pil till höger när det finns mer text att läsa längre ner
const merPil = document.createElement("div");
merPil.id = "merpil"; merPil.hidden = true;
merPil.setAttribute("aria-hidden", "true");   // bara en visuell indikering, går inte att klicka på
merPil.innerHTML = '<svg viewBox="0 0 9 6" shape-rendering="crispEdges" aria-hidden="true"><path fill="currentColor" d="M0 0h2v1H0zM7 0h2v1H7zM1 1h2v1H1zM6 1h2v1H6zM2 2h2v1H2zM5 2h2v1H5zM3 3h3v1H3zM4 4h1v1H4z"/></svg>';
document.body.appendChild(merPil);
let pilRaf = 0;
function visaMerPil() {
  if (pilRaf) return;
  pilRaf = requestAnimationFrame(() => {
    pilRaf = 0;
    const kvar = scroller.scrollHeight - scroller.clientHeight - scroller.scrollTop - fyll.offsetHeight;
    const mer = kvar > 24;
    merPil.hidden = !mer;
    if (!mer) return;
    const r = scroller.getBoundingClientRect();
    merPil.style.top = (r.bottom - merPil.offsetHeight) + "px";
    merPil.style.left = r.left + "px";
    merPil.style.width = (Math.min(r.right, window.innerWidth) - r.left) + "px";
  });
}
scroller.addEventListener("scroll", visaMerPil, { passive: true });
window.addEventListener("resize", visaMerPil);
if (window.visualViewport) window.visualViewport.addEventListener("resize", visaMerPil);
new MutationObserver(visaMerPil).observe(logEl, { childList: true, subtree: true, characterData: true });
if (window.ResizeObserver) new ResizeObserver(visaMerPil).observe(scroller);

// ---------------------------------------------------------------------------
//  Textmallar och hjälpfunktioner
// ---------------------------------------------------------------------------
function mall(t, ctx = {}) {
  return String(t).replace(/\{(\w+)\}/g, (m, k) => {
    if (k === "objekt" && ctx.objekt) return OBJ[ctx.objekt].kort;
    if (k === "Objekt" && ctx.objekt) return stor(OBJ[ctx.objekt].kort);
    if (k === "mottagare" && ctx.mottagare) return OBJ[ctx.mottagare].kort;
    if (k === "poang") return S.score;
    if (k === "max") return MAX;
    if (k === "drag") return S.moves;
    return ctx[k] !== undefined ? ctx[k] : m;
  });
}
const stor = t => t.replace(/^./, c => c.toUpperCase());
const valj = v => Array.isArray(v) ? v[S.moves % v.length] : v;
function lista(a) { return a.length <= 1 ? a.join("") : a.slice(0, -1).join(", ") + " " + TEXTER.och + " " + a[a.length - 1]; }
// En text kan vara en sträng eller en lista med delar, där varje del kan ha ett villkor.
function text(v, ctx) {
  if (v == null) return "";
  if (typeof v === "string") return mall(v, ctx);
  if (Array.isArray(v)) return v.map(d => typeof d === "string" ? mall(d, ctx) : (uppfyllt(d.om, ctx) ? mall(d.text, ctx) : "")).join("");
  return uppfyllt(v.om, ctx) ? mall(v.text, ctx) : "";
}

// ---------------------------------------------------------------------------
//  Föremål och var de finns
// ---------------------------------------------------------------------------
const har = id => {
  const l = S.loc[id], o = OBJ[id];
  return l === S.room || (o.grupp && l != null && RUM[S.room].grupp === o.grupp);
};
const bar = id => S.loc[id] === "spelare";
const oppen = id => OBJ[id].oppningsbar ? !!S.oppen[id] : true;
function inom(id) {
  if (har(id) || bar(id)) return true;
  const c = S.loc[id];
  return !!(c && OBJ[c] && OBJ[c].behallare && oppen(c) && inom(c));
}
const iNarheten = () => Object.keys(OBJ).filter(inom);
function hitta(fras) {
  if (!fras) return null;
  const p = " " + fras + " ";
  let basta = null, langd = 0;
  for (const id of iNarheten()) for (const n of OBJ[id].namn) if (p.includes(" " + n + " ") && n.length > langd) { basta = id; langd = n.length; }
  return basta;
}
const kandsIgen = fras => { const p = " " + fras + " "; return Object.values(OBJ).some(o => o.namn.some(n => p.includes(" " + n + " "))); };
function inteHar(fras) {
  if (!fras) return out(TEXTER.sagVad);
  if (kandsIgen(fras)) out(TEXTER.inteHar);
  else out(mall(TEXTER.okantObjekt, { ord: fras.split(" ").pop() }));
}
function gissaPerson() {
  return Object.keys(OBJ).find(id => OBJ[id].person && har(id) && S.loc[id] !== "spelare") || null;
}
function listaInnehall(c) {
  const inne = Object.keys(OBJ).filter(id => S.loc[id] === c);
  out(inne.length ? mall(TEXTER.iDenLigger, { lista: lista(inne.map(id => OBJ[id].kort)) }) : TEXTER.denArTom);
}

// ---------------------------------------------------------------------------
//  Villkor
// ---------------------------------------------------------------------------
const somLista = v => Array.isArray(v) ? v : [v];
function uppfyllt(om, ctx = {}) {
  if (!om) return true;
  if (Array.isArray(om)) return om.every(o => uppfyllt(o, ctx));
  for (const [k, v] of Object.entries(om)) {
    let ok;
    switch (k) {
      case "flagga": ok = somLista(v).every(f => S.f[f]); break;
      case "inteFlagga": ok = somLista(v).every(f => !S.f[f]); break;
      case "bar": ok = somLista(v).every(bar); break;
      case "inteBar": ok = somLista(v).every(id => !bar(id)); break;
      case "har": ok = somLista(v).every(har); break;
      case "inteHar": ok = somLista(v).every(id => !har(id)); break;
      case "inom": ok = somLista(v).every(inom); break;
      case "inteInom": ok = somLista(v).every(id => !inom(id)); break;
      case "plats": ok = somLista(v).includes(S.room); break;
      case "intePlats": ok = !somLista(v).includes(S.room); break;
      case "objektPa": ok = S.loc[v[0]] === v[1]; break;
      case "inteObjektPa": ok = S.loc[v[0]] !== v[1]; break;
      case "oppen": ok = !!S.oppen[v]; break;
      case "stangd": ok = !S.oppen[v]; break;
      case "inventarieTom": ok = !Object.keys(OBJ).some(bar) === v; break;
      case "objekt": ok = somLista(v).includes(ctx.objekt); break;
      case "mottagare": ok = somLista(v).includes(ctx.mottagare); break;
      case "fras": ok = !!ctx.fras === v; break;
      case "ord": ok = somLista(v).some(o => (" " + (ctx.fras || "") + " ").includes(" " + o + " ") || (o.endsWith("*") && (ctx.fras || "").includes(o.slice(0, -1)))); break;
      case "inteOrd": ok = !uppfyllt({ ord: v }, ctx); break;
      case "franGrupp": ok = !!ctx.fran && RUM[ctx.fran].grupp === v; break;
      case "inteFranGrupp": ok = !ctx.fran || RUM[ctx.fran].grupp !== v; break;
      case "fran": ok = somLista(v).includes(ctx.fran); break;
      case "poangMinst": ok = S.score >= v; break;
      case "alla": ok = v.every(o => uppfyllt(o, ctx)); break;
      case "nagon": ok = v.some(o => uppfyllt(o, ctx)); break;
      case "inte": ok = !uppfyllt(v, ctx); break;
      default: console.warn("Okänt villkor", k); ok = false;
    }
    if (!ok) return false;
  }
  return true;
}

// ---------------------------------------------------------------------------
//  Handlingar
// ---------------------------------------------------------------------------
let ljudFordrojning = 0;     // väntar med poängljudet tills en längre effekt har spelat klart
let spelOmgang = 0;          // ökar vid omstart, så att gamla repliker inte skriver vidare
let nyScen = false;          // sätts när en platsbeskrivning skrivs ut
let stoppaRorelse = false;   // sätts av en spärr som hindrar förflyttning
let raknaDrag = true;

function gor(handlingar, ctx = {}) {
  for (const h of somLista(handlingar || [])) {
    if (typeof h === "string") { out(mall(h, ctx)); continue; }
    if (h.om && !uppfyllt(h.om, ctx)) continue;
    if (h.text !== undefined) { const t = text(h.text, ctx); if (t) out(t); }
    if (h.texter) out(mall(valj(h.texter), ctx));
    if (h.sys) out(mall(h.sys, ctx), "sys");
    if (h.stampel) out(h.stampel, "stamp");
    if (h.flytta) somLista(h.flytta).forEach(id => { S.loc[id] = h.till === "här" ? S.room : h.till === undefined ? null : h.till; });
    if (h.satt) somLista(h.satt).forEach(f => { S.f[f] = true; });
    if (h.nollstall) somLista(h.nollstall).forEach(f => { delete S.f[f]; });
    if (h.oppna) S.oppen[h.oppna] = true;
    if (h.stang) delete S.oppen[h.stang];
    if (h.lista) listaInnehall(h.lista);
    if (h.ljudFordrojning !== undefined) ljudFordrojning = h.ljudFordrojning;
    if (h.ljud) Ljud.effekt(h.ljud, h.fordrojning || 0);
    if (h.poang) belona(h.poang);
    if (h.ejDrag) raknaDrag = false;
    if (h.ledtrad) ledtrad();
    if (h.beskriv) titta();
    if (h.flyttaSpelare) S.room = h.flyttaSpelare;
    if (h.ga) { S.room = h.ga; titta(true); vidIntrade(); }
    if (h.utfor) utfor(mall(h.utfor, ctx), true);
    if (h.kor) gor(A.handlingar[h.kor], ctx);
    if (h.replik) replik(h);
    if (h.samtal) startaSamtal(h.samtal, h.nod);
    if (h.avslutaSamtal) avslutaSamtal();
    if (h.slutsummering) out(mall(TEXTER.slutsummering));
    if (h.spelSlut) { S.over = true; uppdateraStatus(); }
    if (h.stopp) stoppaRorelse = true;
  }
}
function belona(nyckel) {
  if (S.scored[nyckel] || !POANG[nyckel]) return;
  S.scored[nyckel] = true;
  S.score += POANG[nyckel][0];
  if (ljudFordrojning >= 0) Ljud.effekt("poang", ljudFordrojning);
  out(mall(TEXTER.poangOkade, { n: POANG[nyckel][0] }), "score");
}

// Regler: { verb, objekt, mottagare, om, gor, nar }. Första regeln som passar används.
function provaRegler(ctx, nar = "fore") {
  let traff = false;
  for (const r of A.regler || []) {
    if ((r.nar || "fore") !== nar) continue;
    if (!somLista(r.verb).includes(ctx.verb)) continue;
    if (r.objekt !== undefined && !somLista(r.objekt).includes(ctx.objekt)) continue;
    if (r.mottagare !== undefined && !somLista(r.mottagare).includes(ctx.mottagare)) continue;
    if (!uppfyllt(r.om, ctx)) continue;
    gor(r.gor, ctx);
    traff = true;
    if (nar === "fore") return true;
  }
  return traff;
}

// ---------------------------------------------------------------------------
//  Rum och förflyttning
// ---------------------------------------------------------------------------
// Kort beskrivning vid återbesök. rum.kortBeskrivning är en sträng eller en lista där varje
// del är en sträng eller { om, text }. Delar med villkor som stämmer går före delar utan villkor,
// och bland dem som passar växlar motorn i tur och ordning.
function kortBeskrivning(r) {
  const alla = somLista(r.kortBeskrivning).map(d => typeof d === "string" ? { text: d } : d);
  const passar = alla.filter(d => d.om && uppfyllt(d.om));
  const val = passar.length ? passar : alla.filter(d => !d.om);
  if (!val.length) return null;
  const nr = S.kortNr[S.room] || 0;
  S.kortNr[S.room] = nr + 1;
  return text(val[nr % val.length].text);
}
// vidAnkomst: spelaren har just kommit hit. Har platsen besökts förut och har en kort
// beskrivning visas den. Annars, och när spelaren själv tittar, visas hela beskrivningen.
function titta(vidAnkomst = false) {
  nyScen = true;
  S.besokt = S.besokt || {}; S.kortNr = S.kortNr || {};
  const r = RUM[S.room];
  out(r.namn, "room");
  const kort = vidAnkomst && S.besokt[S.room] && r.kortBeskrivning ? kortBeskrivning(r) : null;
  out(kort || text(r.beskrivning));
  S.besokt[S.room] = true;
  const saker = Object.keys(OBJ).filter(id => har(id) && !OBJ[id].fast && !OBJ[id].person);
  if (saker.length) out(mall(TEXTER.harFinns, { lista: lista(saker.map(id => OBJ[id].kort)) }));
  uppdateraStatus();
}
function vidIntrade() {
  const r = RUM[S.room];
  for (const regel of r.vidIntrade || []) {
    if (!uppfyllt(regel.om)) continue;
    gor(regel.gor);
    if (regel.stopp !== false) break;
  }
}
function ga(dir) {
  const fran = S.room, till = RUM[fran].utgangar[dir];
  if (!till) { out(valj(TEXTER.ingenUtgang)); return; }
  stoppaRorelse = false;
  // passage kan vara en lista med regler eller namnet på en gemensam lista i A.passager
  const passage = typeof RUM[till].passage === "string" ? (A.passager || {})[RUM[till].passage] : RUM[till].passage;
  for (const regel of passage || []) {
    if (!uppfyllt(regel.om, { fran })) continue;
    gor(regel.gor, { fran });
    if (regel.stopp) return;
  }
  S.room = till;
  titta(true);
  vidIntrade();
}
// "gå till restaurangen": hitta en utgång som leder till ett rum med något av orden
function gaTill(ord) {
  const d = ord.find(x => RIKTNINGAR[x]);
  if (d) return ga(RIKTNINGAR[d]);
  const fras = " " + ord.join(" ") + " ";
  for (const [dir, till] of Object.entries(RUM[S.room].utgangar)) {
    const ord = (RUM[till].ord || []).concat([RUM[till].namn.toLowerCase()]);
    if (ord.some(o => fras.includes(" " + o + " "))) return ga(dir);
  }
  out(TEXTER.gaVart);
}

// Resor mellan stationer (t.ex. tunnelbana), om äventyret har det
function resa(fras) {
  const R = A.resor, T = R.texter;
  if (!R.stationer[S.room]) {
    const ner = RUM[S.room].utgangar.ner;
    out(ner && R.stationer[ner] ? T.forstNer : T.ingenStation);
    return;
  }
  if (!fras) { out(T.vart); return; }
  const p = " " + fras + " ";
  const mal = Object.keys(R.stationer).find(id => R.stationer[id].ord.some(w => p.includes(" " + w + " ")));
  if (!mal) { out(T.okand); return; }
  if (mal === S.room) { out(T.redanHar); return; }
  out(valj(R.resetexter));
  if (R.ljud) Ljud.effekt(R.ljud);
  out(mall(T.avstigning, { station: R.stationer[mal].namn }), "sys");
  S.room = mal;
  titta(true);
}

// ---------------------------------------------------------------------------
//  Verb
// ---------------------------------------------------------------------------
function rensa(ord) { return ord.filter(w => !UTFYLLNAD.has(w)).join(" ").trim(); }
function delaVid(ord, prep) {
  const i = ord.findIndex(w => prep.includes(w));
  if (i < 0) return [rensa(ord), ""];
  return [rensa(ord.slice(0, i)), rensa(ord.slice(i + 1))];
}
// Kör regler för ett verb, annars standardbeteendet. Därefter eventuella "efter"-regler.
function verb(ctx, standard) {
  if (provaRegler(ctx)) return;
  standard();
  provaRegler(ctx, "efter");
}
const V = {
  titta(ord) {
    if (ord[0] === "på") return V.undersök(ord.slice(1));
    if (ord[0] === "i" || ord[0] === "under") return V.sök(ord.slice(1));
    if (rensa(ord)) return V.undersök(ord);
    verb({ verb: "titta" }, titta);
  },
  undersök(ord) {
    const fras = rensa(ord);
    if (!fras) return titta();
    const id = hitta(fras);
    if (!id) return inteHar(fras);
    verb({ verb: "undersök", objekt: id, fras }, () => {
      out(text(OBJ[id].beskrivning, { objekt: id }));
      if (OBJ[id].behallare && OBJ[id].oppningsbar && oppen(id)) listaInnehall(id);
    });
  },
  sök(ord) {
    const fras = rensa(ord.filter(x => !["i", "igenom", "genom", "efter", "på"].includes(x)));
    const id = hitta(fras);
    if (!id) return out(TEXTER.letarRunt);
    verb({ verb: "sök", objekt: id, fras }, () => {
      if (OBJ[id].behallare) { if (!oppen(id)) out(OBJ[id].stangdText || TEXTER.stangd); else listaInnehall(id); }
      else V.undersök([fras]);
    });
  },
  ta(ord) {
    const fras = rensa(ord.filter(x => x !== "upp"));
    if (/\b(allt|alla|allting)\b/.test(fras)) {
      const saker = iNarheten().filter(id => !bar(id) && !OBJ[id].fast && !OBJ[id].person);
      if (!saker.length) return out(TEXTER.taIngetAtt);
      saker.forEach(id => { out(mall(TEXTER.tagetLista, { objekt: id })); gor(OBJ[id].vidTa, { objekt: id }); S.loc[id] = "spelare"; });
      return;
    }
    const id = hitta(fras);
    if (!id) return inteHar(fras);
    if (bar(id)) return out(TEXTER.redanBuren);
    verb({ verb: "ta", objekt: id, fras }, () => {
      if (OBJ[id].person) return out(TEXTER.taPerson);
      if (OBJ[id].fast) return out(TEXTER.taFast);
      out(TEXTER.taget);
      gor(OBJ[id].vidTa, { objekt: id });
      S.loc[id] = "spelare";
    });
  },
  "ta på"(ord) {
    const fras = rensa(ord), id = hitta(fras);
    verb({ verb: "ta på", objekt: id, fras }, () => out(TEXTER.taPaSig));
  },
  släpp(ord) {
    let r = rensa(ord); if (r.startsWith("ner ")) r = r.slice(4);
    const fras = delaVid(r.split(" "), ["i", "på"])[0];
    const id = hitta(fras);
    if (!id) return inteHar(fras);
    if (!bar(id)) return out(TEXTER.harInte);
    verb({ verb: "släpp", objekt: id, fras }, () => { S.loc[id] = S.room; out(TEXTER.slappt); });
  },
  inventarie() {
    verb({ verb: "inventarie" }, () => {
      const saker = Object.keys(OBJ).filter(bar);
      out(saker.length ? mall(TEXTER.barPa, { lista: lista(saker.map(id => OBJ[id].kort)) }) : TEXTER.barInget);
    });
  },
  öppna(ord) {
    const fras = rensa(ord), id = hitta(fras);
    if (!id) return inteHar(fras);
    verb({ verb: "öppna", objekt: id, fras }, () => {
      const o = OBJ[id];
      if (!o.oppningsbar) return out(TEXTER.kanInteOppna);
      if (S.oppen[id]) return out(o.redanOppenText || TEXTER.redanOppen);
      S.oppen[id] = true;
      if (o.oppnaLjud) Ljud.effekt(o.oppnaLjud);
      out(mall(o.oppnaText || TEXTER.oppnad, { objekt: id }));
      if (o.behallare) listaInnehall(id);
    });
  },
  stäng(ord) {
    const fras = rensa(ord), id = hitta(fras);
    verb({ verb: "stäng", objekt: id, fras }, () => {
      if (id && OBJ[id].oppningsbar) { delete S.oppen[id]; out(mall(OBJ[id].stangText || TEXTER.stangdNu, { objekt: id })); return; }
      out(id ? TEXTER.kanInteStanga : TEXTER.stangVad);
    });
  },
  läs(ord) {
    const fras = rensa(ord), id = hitta(fras);
    if (!id) return inteHar(fras);
    verb({ verb: "läs", objekt: id, fras }, () => {
      const o = OBJ[id];
      if (o.lasText) out(text(o.lasText, { objekt: id }));
      else if (o.lasbar) out(text(o.beskrivning, { objekt: id }));
      else out(TEXTER.ingetAttLasa);
    });
  },
  lyssna(ord) {
    const fras = rensa(ord.filter(x => !["på", "av", "upp"].includes(x)));
    verb({ verb: "lyssna", objekt: hitta(fras), fras }, () => out(text(TEXTER.lyssna)));
  },
  ge(ord, rad, delar) {
    const [a, b] = delar || delaVid(ord, ["till", "åt", "för"]);
    const id = hitta(a);
    if (!id) return inteHar(a);
    if (!bar(id)) return out(TEXTER.harInte);
    const t = b ? hitta(b) : gissaPerson();
    if (!t) return out(TEXTER.geVem);
    verb({ verb: "ge", objekt: id, mottagare: t, fras: a }, () => out(TEXTER.geIngen));
  },
  mata(ord) {
    const [vem, med] = delaVid(ord, ["med"]);
    if (!med) return out(TEXTER.mataMed);
    V.ge([], null, [med, vem]);
  },
  visa(ord) {
    const [a, b] = delaVid(ord, ["för", "till", "åt"]);
    const id = hitta(a);
    if (!id) return inteHar(a);
    if (!bar(id)) return out(TEXTER.harInte);
    const t = b ? hitta(b) : gissaPerson();
    if (!t) return out(TEXTER.visaIngen);
    verb({ verb: "visa", objekt: id, mottagare: t, fras: a }, () => out(TEXTER.visaReaktion));
  },
  prata(ord) {
    const fras = delaVid(ord, ["med", "till", "på"])[1] || rensa(ord.filter(x => x !== "om"));
    const t = hitta(fras) || gissaPerson();
    if (!t || !OBJ[t].person) return out(TEXTER.prataSjalv);
    verb({ verb: "prata", objekt: t, mottagare: t, fras }, () => out(TEXTER.prataInget));
  },
  ät(ord) {
    const fras = rensa(ord), id = hitta(fras);
    if (!id) return inteHar(fras);
    verb({ verb: "ät", objekt: id, fras }, () => out(TEXTER.at));
  },
  // "använd dyrken på dörren": äventyrets regler bestämmer vad som händer
  använd(ord) {
    const [a, b] = delaVid(ord, ["på", "med", "i", "till", "mot"]);
    const id = hitta(a);
    if (!id) return inteHar(a);
    const t = b ? hitta(b) : null;
    if (b && !t) return inteHar(b);
    verb({ verb: "använd", objekt: id, mottagare: t, fras: a }, () => out(TEXTER.anvand));
  },
  klappa(ord) {
    const fras = rensa(ord);
    verb({ verb: "klappa", objekt: hitta(fras), fras }, () => out(TEXTER.klappa));
  },
  vänta() { verb({ verb: "vänta" }, () => out(valj(TEXTER.vanta))); },
  lukta() { verb({ verb: "lukta" }, () => out(text(RUM[S.room].lukt || TEXTER.lukta))); },
  gå(ord) { gaTill(ord); },
  åk(ord, rad) { const m = rad.match(/\btill\b (.+)$/); resa(m ? m[1] : ""); },
};
// Verb som bara äventyret känner till: regler, annars "Det går inte."
function egetVerb(kanon, ord) {
  const fras = rensa(ord);
  verb({ verb: kanon, objekt: hitta(fras), fras }, () => out(TEXTER.ejMojligt));
}

// ---------------------------------------------------------------------------
//  Ordtolkaren
// ---------------------------------------------------------------------------
// intern = kommandot kommer från en regel (t.ex. "öppna skrivbordet" som öppnar lådan) och räknas inte som ett nytt drag.
function utfor(rad, intern = false) {
  let s = rad.toLowerCase().replace(/[.,!?;:"'()]/g, " ").replace(/\s+/g, " ").trim();
  if (!s) return out(TEXTER.tomtKommando);
  if (A.alias) for (const [fran, till] of Object.entries(A.alias)) if (s === fran || s.startsWith(fran + " ")) s = till + s.slice(fran.length);
  const w = s.split(" ");
  // Metakommandon räknas inte som drag
  if (!intern) {
    for (const [m, ord] of Object.entries(META)) if (ord.includes(w[0]) || ord.includes(s)) return meta(m);
    if (S.over) return out(TEXTER.spelSlut, "sys");
    S.moves++;
    raknaDrag = true;
  }
  if (RIKTNINGAR[w[0]] && w.length === 1) return ga(RIKTNINGAR[w[0]]);
  // Verb på två ord först (t.ex. "ta på", "lås upp"), sedan ett ord
  let kanon = VERB[w[0] + " " + w[1]], resten = w.slice(2);
  if (!kanon) { kanon = VERB[w[0]]; resten = w.slice(1); }
  if (kanon) {
    if (V[kanon]) V[kanon](resten, s);
    else egetVerb(kanon, resten);
    if (!raknaDrag && !intern) { S.moves--; raknaDrag = true; }
    return;
  }
  if (!intern) S.moves--;
  out(mall(TEXTER.okantOrd, { ord: w[0] }));
}

// ---------------------------------------------------------------------------
//  Metakommandon: hjälp, ledtråd, poäng, spara, ladda, bild, ljud, omstart
// ---------------------------------------------------------------------------
function meta(m) {
  switch (m) {
    case "hjälp":
      if (klicklage) { TEXTER.hjalpKlick.forEach(t => out(t)); return; }
      TEXTER.hjalp.forEach(t => out(t)); out(TEXTER.hjalpOvrigt, "sys"); return;
    case "ledtråd": return ledtrad();
    case "poäng": return poangRapport();
    case "spara": return spara();
    case "ladda": return ladda();
    case "bild": return vaxlaBilder();
    case "ljud": { const pa = Ljud.vaxlaLjud(); visaLjudknapp(); return out(pa ? TEXTER.ljudPa : TEXTER.ljudAv, "sys"); }
    case "musik": { const pa = Ljud.vaxlaMusik(); return out(pa ? TEXTER.musikPa : TEXTER.musikAv, "sys"); }
    case "omstart": return fragaOmstart();
  }
}
function ledtrad() {
  const l = (A.ledtradar || []).find(x => uppfyllt(x.om));
  if (l) out(mall(TEXTER.ledtrad, { text: text(l.text) }), "sys");
}
function poangRapport() {
  out(mall(TEXTER.poangRapport));
  const fatt = Object.keys(S.scored).filter(k => POANG[k]).map(k => POANG[k][1]);
  if (fatt.length) out(mall(TEXTER.poangHittills, { lista: lista(fatt) }), "sys");
  const r = (A.rangar || []).find(([min]) => S.score >= min);
  if (r) out(mall(TEXTER.rang, { rang: r[1] }), "sys");
}
const SPARNYCKEL = NYCKEL + "-sparning";
// Spelet sparas också automatiskt efter varje drag, så att man fortsätter där man var när sidan laddas om.
// SPARA och LADDA är en separat sparning som spelaren själv styr över.
const PAGAR_NYCKEL = NYCKEL + "-pagar";
let autosparaPa = false;
function autospara() {
  if (!autosparaPa) return;
  try {
    if (S.over) localStorage.removeItem(PAGAR_NYCKEL);
    else localStorage.setItem(PAGAR_NYCKEL, JSON.stringify(S));
  } catch (e) {}
}
function pagaendeSpel() {
  try {
    const raw = localStorage.getItem(PAGAR_NYCKEL);
    return raw ? Object.assign(nyttTillstand(), JSON.parse(raw)) : null;
  } catch (e) { return null; }
}
function spara() {
  try { localStorage.setItem(SPARNYCKEL, JSON.stringify(S)); out(TEXTER.sparat, "sys"); }
  catch (e) { out(TEXTER.kanInteSpara, "sys"); }
}
function ladda() {
  try {
    const raw = localStorage.getItem(SPARNYCKEL);
    if (!raw) return out(TEXTER.ingetSparat, "sys");
    S = Object.assign(nyttTillstand(), JSON.parse(raw));
    spelOmgang++;
    out(TEXTER.laddat, "sys");
    titta();
  } catch (e) { out(TEXTER.kanInteLadda, "sys"); }
}
function intro() {
  for (const d of A.intro || []) {
    if (typeof d === "string") out(d);
    else out(d.text, d.klass);
  }
  titta();
}
// Fråga innan spelet börjar om, utom när det inte finns något att förlora
let omstartDialog = null;
function fragaOmstart() {
  if (S.over || S.moves === 0 || typeof HTMLDialogElement === "undefined") return omstart();
  if (!omstartDialog) {
    omstartDialog = document.createElement("dialog");
    omstartDialog.className = "bekrafta";
    omstartDialog.setAttribute("aria-labelledby", "bekrafta-rubrik");
    omstartDialog.innerHTML = `<h2 id="bekrafta-rubrik"></h2><p></p>
      <div class="knappar"><button type="button" class="nej"></button><button type="button" class="ja"></button></div>`;
    omstartDialog.querySelector(".nej").addEventListener("click", () => omstartDialog.close("nej"));
    omstartDialog.querySelector(".ja").addEventListener("click", () => omstartDialog.close("ja"));
    omstartDialog.querySelector("h2").textContent = TEXTER.omstartRubrik;
    omstartDialog.querySelector("p").textContent = TEXTER.omstartFraga;
    omstartDialog.querySelector(".nej").textContent = TEXTER.omstartNej;
    omstartDialog.querySelector(".ja").textContent = TEXTER.omstartJa;
    omstartDialog.addEventListener("click", e => { if (e.target === omstartDialog) omstartDialog.close("nej"); });   // tryck utanför rutan
    omstartDialog.addEventListener("close", () => {
      if (omstartDialog.returnValue === "ja") { omstart(); uppdateraStatus(); scrollTill(null); }
      else { out(TEXTER.omstartAvbruten, "sys"); }
      if (!pekskarm && !klicklage) input.focus();
    });
    document.body.appendChild(omstartDialog);
  }
  omstartDialog.returnValue = "";
  omstartDialog.showModal();
  omstartDialog.querySelector(".nej").focus();
}
function omstart() {
  spelOmgang++;
  S = nyttTillstand();
  logEl.innerHTML = "";
  intro();
}
function uppdateraStatus() {
  uppdateraScen();
  Ljud.miljo(S.room);
  document.getElementById("where").textContent = RUM[S.room].namn;
  document.getElementById("nums").textContent = `Poäng ${S.score}/${MAX} · Drag ${S.moves}`;
  uppdateraAgodelar();
  ritaSamtalsval();
  autospara();
}

// ---------------------------------------------------------------------------
//  Repliker: orden skrivs ut i takt med rösten
// ---------------------------------------------------------------------------
function replik(h) {
  const el = out("", "replik pratar");
  const omgang = spelOmgang;
  const delar = (D.texttider || {})[h.replik] || [];
  if (!delar.length) { el.textContent = "””"; gor(h.sedan); return; }
  const ord = [];
  for (const [t0, t1, mening] of delar) {
    let acc = 0;
    for (const o of mening.split(" ")) { ord.push([t0 + (t1 - t0) * acc / mening.length, o]); acc += o.length + 1; }
  }
  const slut = delar[delar.length - 1][1] + 0.4;
  Ljud.effekt(h.ljud || h.replik).then(f => {
    const t0 = performance.now() + (f == null ? -(delar[0][0] - 0.4) : f) * 1000;
    let i = 0;
    const steg = () => {
      if (omgang !== spelOmgang) return;
      const t = (performance.now() - t0) / 1000;
      let nytt = false;
      while (i < ord.length && ord[i][0] <= t) { i++; nytt = true; }
      if (nytt) {
        el.textContent = "”" + ord.slice(0, i).map(o => o[1]).join(" ") + (i === ord.length ? "”" : "");
        if (!pekskarm) scroller.scrollTop = scroller.scrollHeight;
      }
      if (t >= slut) {
        el.classList.remove("pratar");
        ljudFordrojning = 0;
        gor(h.sedan);
        uppdateraStatus();
        if (!pekskarm) scrollDown();
        return;
      }
      setTimeout(steg, 40);
    };
    steg();
  });
}

// ---------------------------------------------------------------------------
//  Bilder och animationer
// ---------------------------------------------------------------------------
const BD = D.bilder || { palett: [], bilder: {} };
const BREDD = BD.bredd || 192, HOJD = BD.hojd || 120;
const FARG = BD.palett.map(([r, g, b]) => `rgb(${r},${g},${b})`);
for (const anims of Object.values(BD.bilder)) {
  for (const a of anims) {
    a.ramar = a.ramar.map(str => {
      if (typeof str !== "string") return str;
      const bin = atob(str), ut = new Uint16Array(bin.length);
      for (let i = 0; i < bin.length; i += 3) {
        const pos = (bin.charCodeAt(i) << 8) | bin.charCodeAt(i + 1);
        ut[i] = pos % BREDD; ut[i + 1] = Math.floor(pos / BREDD); ut[i + 2] = bin.charCodeAt(i + 2);
      }
      return ut;
    });
  }
}
const cv = document.getElementById("scenbild");
cv.width = BREDD; cv.height = HOJD;
const scen = { namn: null, bas: null, klar: false, start: 0, senaste: "", raf: 0 };
const BILD_KEY = NYCKEL + "-bilder";
let visaBilder = true;
try { visaBilder = localStorage.getItem(BILD_KEY) !== "av"; } catch (e) {}

function uppdateraScen() {
  const fig = document.getElementById("scen");
  const namn = RUM[S.room].bild;
  if (!namn || !visaBilder) { fig.hidden = true; stoppaAnim(); scen.namn = null; return; }
  fig.hidden = false;
  anpassaScen();
  if (scen.namn !== namn) {
    scen.namn = namn; scen.klar = false; scen.senaste = "";
    cv.setAttribute("aria-label", "Bild: " + RUM[S.room].namn);
    cv.dataset.bild = namn;   // för automatiska tester
    const img = new Image();
    img.onload = () => {
      if (scen.namn !== namn) return;
      scen.bas = img; scen.klar = true; scen.start = performance.now();
      ritaScen(true); startaAnim();
    };
    img.src = bildvag("bilder/" + namn + ".png");
    cv.classList.remove("ritar"); void cv.offsetWidth; cv.classList.add("ritar");
  } else { ritaScen(true); startaAnim(); }
}
function ramIndex(anim, t) {
  const n = anim.slinga || anim.ms.length;
  let r = t % anim.ms.slice(0, n).reduce((a, b) => a + b, 0);
  for (let i = 0; i < n; i++) { if (r < anim.ms[i]) return i; r -= anim.ms[i]; }
  return 0;
}
// Rummets "animationer" kan låsa en animation på en viss ruta: { namn: [{ om, ram }] }
function lastRam(namn) {
  const regler = (RUM[S.room].animationer || {})[namn];
  if (!regler) return null;
  const r = regler.find(x => uppfyllt(x.om));
  return r ? r.ram : null;
}
function ritaScen(tvinga) {
  if (!scen.klar) return;
  const anims = BD.bilder[scen.namn] || [];
  const t = performance.now() - scen.start;
  const val = anims.map(a => {
    const fast = lastRam(a.namn);
    if (fast !== null && fast !== undefined) return fast;
    return rorelseOk ? ramIndex(a, t) : -1;
  });
  const nyckel = val.join(",");
  if (!tvinga && nyckel === scen.senaste) return;
  scen.senaste = nyckel;
  const ctx = cv.getContext("2d");
  ctx.drawImage(scen.bas, 0, 0);
  anims.forEach((a, i) => {
    if (val[i] < 0) return;
    const p = a.ramar[val[i]];
    for (let k = 0; k < p.length; k += 3) { ctx.fillStyle = FARG[p[k + 2]]; ctx.fillRect(p[k], p[k + 1], 1, 1); }
  });
}
function startaAnim() {
  if (scen.raf || !rorelseOk) return;
  const loop = () => { ritaScen(); scen.raf = requestAnimationFrame(loop); };
  scen.raf = requestAnimationFrame(loop);
}
function stoppaAnim() { cancelAnimationFrame(scen.raf); scen.raf = 0; }
// Heltalsskalning så att alla pixlar blir lika stora. På mobil i stående läge fyller bilden bredden.
function anpassaScen() {
  const vw = document.documentElement.clientWidth || window.innerWidth;
  if (vw < 700 && window.innerHeight > window.innerWidth) {
    cv.style.width = vw + "px";
    cv.style.height = Math.round(vw * HOJD / BREDD) + "px";
    return;
  }
  const maxW = Math.min(window.innerWidth, 1200), maxH = window.innerHeight * 0.36;
  let k = Math.floor(Math.min(maxW / BREDD, maxH / HOJD));
  if (k < 1) k = 1;
  if (k < 2 && maxW >= BREDD * 2) k = 2;
  cv.style.width = BREDD * k + "px";
  cv.style.height = HOJD * k + "px";
}
window.addEventListener("resize", anpassaScen);
function vaxlaBilder() {
  visaBilder = !visaBilder;
  try { localStorage.setItem(BILD_KEY, visaBilder ? "pa" : "av"); } catch (e) {}
  out(visaBilder ? TEXTER.bilderPa : TEXTER.bilderAv, "sys");
  uppdateraScen();
}

// ---------------------------------------------------------------------------
//  Ljud: musik, miljöljud och effekter (filer i ljud/, spelas med Web Audio)
// ---------------------------------------------------------------------------
const Ljud = (() => {
  const L = A.ljud || {};
  const KEY = NYCKEL + "-ljud-v2";
  const inst = { ljud: true, musik: true };
  try { Object.assign(inst, JSON.parse(localStorage.getItem(KEY)) || {}); } catch (e) {}
  const sparaInst = () => { try { localStorage.setItem(KEY, JSON.stringify(inst)); } catch (e) {} };
  const AC = window.AudioContext || window.webkitAudioContext;
  const MUSIKNIVA = L.musikniva || 0.42;
  const MILJO = L.miljo || {};
  const EFFEKTVOLYM = L.effektvolym || {};
  const SLINGOR = D.slingor || {};
  let ctx = null, master, musikBus, miljoBus, sfxBus;
  let rum = null, lager = [], handelser = [], musikKalla = null;
  const buffertar = {}, langder = {};
  const slump = (a, b) => a + Math.random() * (b - a);
  function bygg() {
    try { if (navigator.audioSession) navigator.audioSession.type = "playback"; } catch (e) {}
    ctx = new AC();
    master = ctx.createGain(); master.gain.value = inst.ljud ? 1 : 0; master.connect(ctx.destination);
    musikBus = ctx.createGain(); musikBus.gain.value = 0; musikBus.connect(master);
    miljoBus = ctx.createGain(); miljoBus.gain.value = 0.85; miljoBus.connect(master);
    sfxBus = ctx.createGain(); sfxBus.gain.value = 1; sfxBus.connect(master);
  }
  function ladda(namn) {
    if (!buffertar[namn]) {
      buffertar[namn] = fetch(D.ljudfiler ? (D.ljudfiler[namn] || "ljud/" + namn + ".mp3") : (A.ljudmapp || "ljud/") + namn + ".mp3")
        .then(r => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
        .then(data => new Promise((ok, fel) => ctx.decodeAudioData(data, ok, fel)))
        .then(buf => { langder[namn] = buf.duration; return buf; })
        .catch(() => null);
    }
    return buffertar[namn];
  }
  // mp3 kan ha lite tystnad i början; loopa exakt den längd generatorn angav.
  function slingpunkter(buf, namn) {
    const n44 = SLINGOR[namn] || 0;
    if (!n44) return [0, buf.duration];
    const n = Math.round(n44 * buf.sampleRate / 44100);
    if (buf.length < n) return [0, buf.duration];
    const d = buf.getChannelData(0);
    let start = 0;
    const max = Math.min(buf.length - n, 4096);
    while (start < max && Math.abs(d[start]) < 1e-4) start++;
    return [start / buf.sampleRate, (start + n) / buf.sampleRate];
  }
  function spelaSlinga(namn, buss, vol, fadein = 1.2) {
    const g = ctx.createGain(); g.gain.value = 0; g.connect(buss);
    const post = { g, kalla: null, stoppad: false };
    ladda(namn).then(buf => {
      if (!buf || post.stoppad) return;
      const s = ctx.createBufferSource();
      s.buffer = buf; s.loop = true;
      const [a, b] = slingpunkter(buf, namn);
      s.loopStart = a; s.loopEnd = b;
      s.connect(g);
      s.start(ctx.currentTime + 0.05, a + (buss === musikBus ? 0 : Math.random() * Math.max(0, b - a - 1)));
      g.gain.setTargetAtTime(vol, ctx.currentTime, fadein / 3);
      post.kalla = s;
    });
    return post;
  }
  function stoppaSlinga(post, fadeut = 1.2) {
    post.stoppad = true;
    const nu = ctx.currentTime;
    post.g.gain.cancelScheduledValues(nu);
    post.g.gain.setTargetAtTime(0, nu, fadeut / 3);
    if (post.kalla) post.kalla.stop(nu + fadeut + 0.5);
  }
  function spelaEn(namn, vid, vol, buss = sfxBus) {
    return ladda(namn).then(buf => {
      if (!buf) return null;
      const s = ctx.createBufferSource(), g = ctx.createGain();
      s.buffer = buf; g.gain.value = vol;
      s.connect(g); g.connect(buss);
      const nar = Math.max(ctx.currentTime + 0.02, vid);
      s.start(nar);
      return nar;
    });
  }
  const musikNiva = () => !inst.musik ? 0 : (MILJO[rum] && MILJO[rum].dampaMusik ? MUSIKNIVA * 0.15 : MUSIKNIVA);
  function startaMusik() {
    if (!L.musik) return;
    if (!musikKalla) musikKalla = spelaSlinga(L.musik, musikBus, 1, 0.5);
    musikBus.gain.setTargetAtTime(musikNiva(), ctx.currentTime, 0.8);
  }
  function bytMiljo(id) {
    if (id === rum) return;
    rum = id;
    lager.forEach(l => stoppaSlinga(l));
    const m = MILJO[id] || {};
    lager = (m.slingor || []).map(([namn, vol]) => spelaSlinga(namn, miljoBus, vol));
    const nu = ctx.currentTime;
    handelser = (m.handelser || []).map(([namn, mellan, vol, om]) => ({ namn, mellan, vol, om, nasta: nu + slump(1.5, mellan) }));
    handelser.forEach(h => ladda(h.namn));
    musikBus.gain.setTargetAtTime(musikNiva(), nu, 0.8);
  }
  function tick() {
    if (!ctx || ctx.state !== "running") return;
    const nu = ctx.currentTime;
    for (const h of handelser) {
      if (nu >= h.nasta) {
        if (!h.om || uppfyllt(h.om)) spelaEn(h.namn, nu, h.vol * slump(0.7, 1), miljoBus);
        h.nasta = nu + h.mellan * slump(0.6, 1.4);
      }
    }
  }
  return {
    vakna() {
      if (!AC) return;
      if (!ctx) {
        try { bygg(); } catch (e) { return; }
        setInterval(tick, 250);
        (L.forladda || Object.keys(EFFEKTVOLYM)).forEach(ladda);
      }
      if (ctx.state === "suspended" && inst.ljud && !document.hidden) ctx.resume();
      startaMusik();
      if (S) bytMiljo(S.room);
    },
    miljo(id) { if (ctx) bytMiljo(id); },
    // Svarar med hur många sekunder det dröjer innan ljudet börjar, eller null om inget spelas.
    effekt(namn, fordrojning = 0) {
      if (!ctx || !inst.ljud || ctx.state !== "running") return Promise.resolve(null);
      return spelaEn(namn, ctx.currentTime + 0.03 + fordrojning, EFFEKTVOLYM[namn] || 0.8)
        .then(nar => nar == null ? null : Math.max(0, nar - ctx.currentTime));
    },
    langd(namn, reserv) { return langder[namn] || reserv; },
    vaxlaLjud() {
      inst.ljud = !inst.ljud; sparaInst(); this.vakna();
      if (ctx) { master.gain.setTargetAtTime(inst.ljud ? 1 : 0, ctx.currentTime, 0.1); if (inst.ljud) ctx.resume(); }
      return inst.ljud;
    },
    vaxlaMusik() {
      inst.musik = !inst.musik; sparaInst(); this.vakna();
      if (ctx) musikBus.gain.setTargetAtTime(musikNiva(), ctx.currentTime, 0.4);
      return inst.musik;
    },
    get pa() { return inst.ljud; },
    get musik() { return inst.musik; },
    pausa(p) { if (!ctx) return; if (p) ctx.suspend(); else if (inst.ljud) ctx.resume(); },
    get status() { return ctx ? { tillstand: ctx.state, rum, slingor: lager.length, musik: !!(musikKalla && musikKalla.kalla) } : null; },
  };
})();
let startskarmVisas = false;
["pointerdown", "touchend", "click", "keydown"].forEach(ev => document.addEventListener(ev, () => { if (!startskarmVisas) Ljud.vakna(); }, { passive: true }));
document.addEventListener("visibilitychange", () => Ljud.pausa(document.hidden));
function visaLjudknapp() {
  const b = document.getElementById("ljudknapp");
  if (!b) return;
  b.textContent = Ljud.pa ? TEXTER.ljudknappPa : TEXTER.ljudknappAv;
  b.setAttribute("aria-pressed", String(Ljud.pa));
}

// ---------------------------------------------------------------------------
//  Startskärmen
// ---------------------------------------------------------------------------
// Långa titlar krymps så att de får plats i bredden (t.ex. på en smal mobil)
function anpassaTitel() {
  const t = document.querySelector("#splashtitel .titel");
  if (!t) return;
  t.style.fontSize = "";
  const max = Math.min(window.innerWidth, document.documentElement.clientWidth || window.innerWidth) * 0.92;
  let fs = parseFloat(getComputedStyle(t).fontSize);
  for (let i = 0; i < 40 && t.scrollWidth > max && fs > 12; i++) { fs *= 0.95; t.style.fontSize = fs + "px"; }
}
function visaStartskarm() {
  const sp = document.getElementById("splash");
  startskarmVisas = true;
  anpassaTitel();
  window.addEventListener("resize", anpassaTitel);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(anpassaTitel);
  let stangd = false, raf = 0;
  const cvr = document.getElementById("splashregn");
  if (cvr && rorelseOk && cvr.getContext) {
    const c = cvr.getContext("2d");
    const droppar = Array.from({ length: 140 }, () => ({ x: Math.random(), y: Math.random(), v: 0.6 + Math.random() * 0.8, l: 0.02 + Math.random() * 0.03 }));
    let senast = performance.now();
    const rita = nu => {
      const dt = Math.min(0.05, (nu - senast) / 1000); senast = nu;
      const dpr = window.devicePixelRatio || 1;
      const w = cvr.width = cvr.clientWidth * dpr, h = cvr.height = cvr.clientHeight * dpr;
      c.clearRect(0, 0, w, h);
      c.strokeStyle = "rgba(210, 205, 195, 0.22)"; c.lineWidth = Math.max(1, dpr * 0.8);
      c.beginPath();
      for (const d of droppar) {
        d.y += d.v * dt * 1.6; d.x -= d.v * dt * 0.25;
        if (d.y > 1.05) { d.y = -0.05; d.x = Math.random() * 1.1; }
        c.moveTo(d.x * w, d.y * h); c.lineTo((d.x - d.l * 0.2) * w, (d.y + d.l) * h);
      }
      c.stroke();
      raf = requestAnimationFrame(rita);
    };
    raf = requestAnimationFrame(rita);
  }
  const stang = () => {
    if (stangd) return;
    stangd = true; startskarmVisas = false;
    Ljud.vakna();
    sp.classList.add("borta");
    setTimeout(() => { sp.hidden = true; cancelAnimationFrame(raf); }, 950);
    if (!pekskarm) input.focus();
  };
  // Bilden ligger kvar tills man klickar på den. Klicket startar också musiken.
  sp.addEventListener("click", stang);
  sp.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); stang(); } });
}

// ---------------------------------------------------------------------------
//  Klickläge (peka och klicka)
//  Ett klick bygger bara ett vanligt kommando ("öppna lådan", "ge dollarn till sal")
//  som går genom ordtolkaren och reglerna. Klicket har ingen egen spellogik, så
//  pusslen fungerar precis som när man skriver.
// ---------------------------------------------------------------------------
const YTOR = {};   // bildnamn -> { namn: [...], karta: Uint8Array(BREDD * HOJD) }
for (const [namn, y] of Object.entries(BD.ytor || {})) {
  const bin = atob(y.karta), karta = new Uint8Array(BREDD * HOJD);
  let p = 0;
  for (let i = 0; i < bin.length; i += 2) { karta.fill(bin.charCodeAt(i), p, p + bin.charCodeAt(i + 1)); p += bin.charCodeAt(i + 1); }
  YTOR[namn] = { namn: y.namn, karta };
}
// Läget bestäms av äventyret, inte av spelaren: "text" (skriv kommandon) eller "klick" (peka och klicka)
const klicklage = A.lage === "klick";
const RIKTNINGSNAMN = { n: "norrut", s: "söderut", ö: "österut", v: "västerut", upp: "upp", ner: "ner", in: "in", ut: "ut" };

// Det namn som används i kommandon och etiketter, t.ex. "lådan"
const kallas = id => OBJ[id].klicknamn || OBJ[id].namn[1] || OBJ[id].namn[0];
const etikett = id => stor(kallas(id));

const scenFig = document.getElementById("scen");
const agodelar = document.createElement("div");
agodelar.className = "agodelar"; agodelar.id = "agodelar";
document.getElementById("quick").before(agodelar);
const namnskylt = document.createElement("div");
namnskylt.className = "namnskylt"; namnskylt.hidden = true;
scenFig.appendChild(namnskylt);
const meny = document.createElement("div");
meny.className = "klickmeny"; meny.hidden = true; meny.setAttribute("role", "menu");
document.body.appendChild(meny);

// Vad finns under en punkt i bilden?
function traff(e) {
  const y = YTOR[scen.namn];
  if (!y || !klicklage) return null;
  const r = cv.getBoundingClientRect();
  const px = Math.floor((e.clientX - r.left) / r.width * BREDD), py = Math.floor((e.clientY - r.top) / r.height * HOJD);
  if (px < 0 || py < 0 || px >= BREDD || py >= HOJD) return null;
  const v = y.karta[py * BREDD + px];
  if (!v) return null;
  const namn = y.namn[v - 1];
  if (namn.startsWith("utgang:")) {
    const dir = namn.slice(7);
    return RUM[S.room].utgangar[dir] ? { utgang: dir } : null;
  }
  // Det man bär nås via ägodelsraden, inte via bilden
  return OBJ[namn] && inom(namn) && !bar(namn) ? { objekt: namn } : null;
}

function visaMeny(val, x, y, rubrik) {
  meny.innerHTML = "";
  if (rubrik) { const h = document.createElement("div"); h.className = "rubrik"; h.textContent = rubrik; meny.appendChild(h); }
  for (const [text, gor] of val) {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = text; b.setAttribute("role", "menuitem");
    b.addEventListener("click", ev => { ev.stopPropagation(); gor(); });
    meny.appendChild(b);
  }
  meny.hidden = false;
  const mw = meny.offsetWidth, mh = meny.offsetHeight;
  meny.style.left = Math.max(8, Math.min(window.innerWidth - mw - 8, x - mw / 2)) + "px";
  meny.style.top = Math.max(8, Math.min(window.innerHeight - mh - 8, y + 12)) + "px";
  const forsta = meny.querySelector("button");
  if (forsta && !pekskarm) forsta.focus({ preventScroll: true });
}
function stangMeny() { meny.hidden = true; }
const kor = cmd => () => { stangMeny(); skicka(cmd); };
const personerHar = () => Object.keys(OBJ).filter(id => OBJ[id].person && har(id) && !bar(id));

// Verben i menyn är allmänna för sorten av sak, aldrig lösningen på ett pussel.
function menyFor(id, x, y) {
  const o = OBJ[id], n = kallas(id), val = [["Undersök", kor("undersök " + n)]];
  // Föremål som också är en utgång, t.ex. en dörr: "Gå in"
  if (o.utgang && RUM[S.room].utgangar[o.utgang]) val.push(["Gå " + RIKTNINGSNAMN[o.utgang], kor(o.utgang)]);
  if (o.person) val.push(["Prata med", kor("prata med " + n)]);
  if (!bar(id)) val.push(["Ta", kor("ta " + n)]);
  if (o.oppningsbar) val.push(S.oppen[id] ? ["Stäng", kor("stäng " + n)] : ["Öppna", kor("öppna " + n)]);
  if (o.lasbar || o.lasText) val.push(["Läs", kor("läs " + n)]);
  for (const v of o.klickverb || []) val.push([stor(v), kor(v + " " + n)]);
  if (o.behallare && (!o.oppningsbar || S.oppen[id])) {
    for (const inne of Object.keys(OBJ).filter(k => S.loc[k] === id)) val.push(["Ta " + kallas(inne), kor("ta " + kallas(inne))]);
  }
  const saker = Object.keys(OBJ).filter(bar);
  if (o.person && saker.length) {
    val.push(["Ge …", () => visaMeny(saker.map(s => [etikett(s), kor(`ge ${kallas(s)} till ${n}`)]), x, y, "Ge vad till " + n + "?")]);
    val.push(["Visa …", () => visaMeny(saker.map(s => [etikett(s), kor(`visa ${kallas(s)} för ${n}`)]), x, y, "Visa vad för " + n + "?")]);
  }
  if (A.resor && A.resor.karta === id && A.resor.stationer[S.room]) {
    for (const [st, info] of Object.entries(A.resor.stationer)) if (st !== S.room) val.push(["Åk till " + info.namn, kor("åk till " + info.ord[0])]);
  }
  if (bar(id)) {
    const mal = Object.keys(OBJ).filter(k => k !== id && (har(k) || bar(k) || (inom(k) && S.loc[k] !== "spelare")));
    if (mal.length) val.push(["Använd …", () => visaMeny(mal.map(m => [etikett(m), kor(`använd ${n} på ${kallas(m)}`)]), x, y, `Använd ${n} på vad?`)]);
    val.push(["Släpp", kor("släpp " + n)]);
    const folk = personerHar();
    if (folk.length) {
      val.push(["Ge till …", () => visaMeny(folk.map(p => [etikett(p), kor(`ge ${n} till ${kallas(p)}`)]), x, y, `Ge ${n} till vem?`)]);
      val.push(["Visa för …", () => visaMeny(folk.map(p => [etikett(p), kor(`visa ${n} för ${kallas(p)}`)]), x, y, `Visa ${n} för vem?`)]);
    }
  }
  visaMeny(val, x, y, etikett(id));
}

cv.addEventListener("click", e => {
  const t = traff(e);
  if (!t) {
    // Ett tryck på en tom del av bilden betyder "titta" (eller stänger en öppen meny)
    if (!meny.hidden) { stangMeny(); return; }
    if (klicklage) { e.stopPropagation(); skicka("titta"); }
    return;
  }
  e.stopPropagation();
  if (t.utgang) { stangMeny(); skicka(t.utgang); return; }
  menyFor(t.objekt, e.clientX, e.clientY);
});
cv.addEventListener("pointermove", e => {
  if (e.pointerType !== "mouse") return;
  const t = traff(e);
  cv.style.cursor = t ? "pointer" : "";
  if (!t) { namnskylt.hidden = true; return; }
  namnskylt.textContent = t.utgang ? "Gå " + RIKTNINGSNAMN[t.utgang] : etikett(t.objekt);
  namnskylt.hidden = false;
  const r = scenFig.getBoundingClientRect();
  namnskylt.style.left = (e.clientX - r.left) + "px";
  namnskylt.style.top = (e.clientY - r.top) + "px";
});
cv.addEventListener("pointerleave", () => { namnskylt.hidden = true; cv.style.cursor = ""; });
document.addEventListener("click", e => { if (!meny.hidden && !meny.contains(e.target)) stangMeny(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") stangMeny(); });

// Utgångar som inte finns som klickytor i bilden visas som knappar, så att man aldrig fastnar.
function utgangarUtanYta() {
  const y = YTOR[RUM[S.room].bild];
  const iBilden = new Set((y ? y.namn : []).map(n => n.startsWith("utgang:") ? n.slice(7) : OBJ[n] && OBJ[n].utgang).filter(Boolean));
  const sedda = new Set(), ut = [];
  for (const [dir, till] of Object.entries(RUM[S.room].utgangar)) {
    if (iBilden.has(dir) || sedda.has(till)) continue;
    if ([...iBilden].some(d => RUM[S.room].utgangar[d] === till)) continue;
    sedda.add(till); ut.push(dir);
  }
  return ut;
}
const lasbarLista = document.createElement("div");
lasbarLista.className = "las-endast"; lasbarLista.setAttribute("aria-label", "Saker du kan trycka på");
scenFig.appendChild(lasbarLista);
function uppdateraAgodelar() {
  document.body.classList.toggle("klicklage", klicklage);
  agodelar.hidden = !klicklage;
  if (!klicklage) { stangMeny(); return; }
  agodelar.innerHTML = "";
  const rad = (rubrik, knappar) => {
    const r = document.createElement("div"); r.className = "klickrad";
    const h = document.createElement("span"); h.className = "rubrik"; h.textContent = rubrik; r.appendChild(h);
    for (const [text, gor] of knappar) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = text;
      b.addEventListener("click", e => { e.stopPropagation(); gor(b); });
      r.appendChild(b);
    }
    agodelar.appendChild(r);
  };
  const saker = Object.keys(OBJ).filter(bar);
  const vidKnapp = id => b => { const r = b.getBoundingClientRect(); menyFor(id, r.left + r.width / 2, r.top - 8); };
  rad(saker.length ? "Du bär:" : "Du bär ingenting.", saker.map(id => [etikett(id), vidKnapp(id)]));
  const utg = utgangarUtanYta();
  if (utg.length) rad("Gå:", utg.map(d => [stor(RIKTNINGSNAMN[d]), () => { stangMeny(); skicka(d); }]));
  // Resor: om linjekartan inte är klickbar i bilden visas stationerna som knappar
  const yt = YTOR[RUM[S.room].bild];
  if (A.resor && A.resor.stationer[S.room] && !(yt && yt.namn.includes(A.resor.karta))) {
    rad("Åk till:", Object.entries(A.resor.stationer).filter(([st]) => st !== S.room).map(([, info]) => [info.namn, () => { stangMeny(); skicka("åk till " + info.ord[0]); }]));
  }
  // Saker i bilden, för skärmläsare (syns inte)
  const y = YTOR[RUM[S.room].bild];
  lasbarLista.innerHTML = "";
  for (const n of (y ? y.namn : [])) {
    const ok = n.startsWith("utgang:") ? RUM[S.room].utgangar[n.slice(7)] : (OBJ[n] && inom(n) && !bar(n));
    if (!ok) continue;
    const b = document.createElement("button"); b.type = "button";
    b.textContent = n.startsWith("utgang:") ? "Gå " + RIKTNINGSNAMN[n.slice(7)] : etikett(n);
    b.addEventListener("click", e => { e.stopPropagation(); if (n.startsWith("utgang:")) skicka(n.slice(7)); else { const r = cv.getBoundingClientRect(); menyFor(n, r.left + r.width / 2, r.top + r.height / 2); } });
    lasbarLista.appendChild(b);
  }
}
// I klickläget ersätts inmatningsfältet och knappraden av en menyknapp.
if (klicklage) {
  document.body.classList.add("klicklage");
  document.getElementById("quick").remove();
  document.querySelector("header.status .wrap").insertAdjacentHTML("beforeend", '<button type="button" id="menyknapp" aria-haspopup="menu">☰ Meny</button>');
  document.getElementById("menyknapp").addEventListener("click", e => {
    e.stopPropagation();
    const r = e.currentTarget.getBoundingClientRect();
    visaMeny([
      ["Ledtråd", kor("ledtråd")], ["Poäng", kor("poäng")], ["Spara", kor("spara")], ["Ladda sparat spel", kor("ladda")],
      [Ljud.pa ? "Stäng av ljudet" : "Slå på ljudet", kor("ljud")], [Ljud.musik ? "Stäng av musiken" : "Slå på musiken", kor("musik")],
      ["Hjälp", kor("hjälp")], ["Börja om", kor("omstart")],
    ], r.left + r.width / 2, r.bottom, "Meny");
  });
}

// ---------------------------------------------------------------------------
//  Samtal: personer som man pratar med genom att välja vad man svarar
//  A.samtal = { id: { start: "nod", noder: { nod: { text, gor, val: [{ text, om, engang, gor, till }] } } } }
//  Handlingen { samtal: "id" } (eller { samtal: "id", nod: "nod" }) startar ett samtal. Ett val utan
//  "till" avslutar samtalet. Svaren visas som knappar, och i textläget också som en numrerad lista.
// ---------------------------------------------------------------------------
const samtalsval = document.createElement("div");
samtalsval.className = "samtalsval"; samtalsval.hidden = true; samtalsval.setAttribute("role", "group");
samtalsval.setAttribute("aria-label", "Vad svarar du?");
logEl.after(samtalsval);   // svaren hamnar direkt efter texten, i den rullbara textytan
const samtalsNod = () => S.samtal && A.samtal && A.samtal[S.samtal.id] && A.samtal[S.samtal.id].noder[S.samtal.nod];
const valNyckel = i => S.samtal.id + "/" + S.samtal.nod + "/" + i;
function samtalsAlternativ() {
  const n = samtalsNod();
  if (!n) return [];
  S.valda = S.valda || {};
  return (n.val || []).map((v, i) => ({ v, i })).filter(({ v, i }) => (!v.om || uppfyllt(v.om)) && !(v.engang && S.valda[valNyckel(i)]));
}
function startaSamtal(id, nod) {
  if (!A.samtal || !A.samtal[id]) return;
  S.samtal = { id, nod: nod || A.samtal[id].start };
  visaNod();
}
function visaNod() {
  const n = samtalsNod(), dettaSamtal = S.samtal;
  if (!n) return avslutaSamtal();
  if (n.text !== undefined) { const t = text(n.text); if (t) out(t); }
  if (n.gor) gor(n.gor);
  if (S.samtal !== dettaSamtal) return;          // handlingarna startade eller avslutade ett samtal
  const alt = samtalsAlternativ();
  if (!alt.length) return avslutaSamtal();
  ritaSamtalsval();
}
function avslutaSamtal() { S.samtal = null; ritaSamtalsval(); }
function ritaSamtalsval() {
  const alt = S && S.samtal ? samtalsAlternativ() : [];
  samtalsval.innerHTML = "";
  samtalsval.hidden = !alt.length;
  document.body.classList.toggle("samtal-pagar", alt.length > 0);
  alt.forEach((a, k) => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = (klicklage ? "" : (k + 1) + ". ") + a.v.text;
    b.addEventListener("click", e => { e.stopPropagation(); valjSvar(k); if (pekskarm) b.blur(); });
    samtalsval.appendChild(b);
  });
}
function valjSvar(k) {
  const a = samtalsAlternativ()[k];
  if (!a) return;
  fyll.style.height = "0px";
  ljudFordrojning = 0;
  nyScen = false;
  const rad = out(a.v.text, "cmd");
  if (a.v.engang) S.valda[valNyckel(a.i)] = true;
  const nasta = a.v.till ? { id: S.samtal.id, nod: a.v.till } : null;
  S.samtal = nasta;
  gor(a.v.gor || []);
  if (nasta && S.samtal === nasta) visaNod(); else ritaSamtalsval();
  uppdateraStatus();
  rullaTill(rad);
}

// ---------------------------------------------------------------------------
//  Inmatning och start
// ---------------------------------------------------------------------------
const historik = []; let hIdx = 0;
function rullaTill(rad) {
  if (pekskarm || nyScen) { scrollTill(rad); haller = { el: rad, tills: performance.now() + 1200 }; }
  else scrollDown();
}
function skicka(t) {
  t = t.trim();
  if (!t) return;
  if (S.samtal) {
    // I textläget väljer en siffra ett svar. Allt annat avslutar samtalet.
    if (/^\d+$/.test(t)) { valjSvar(+t - 1); historik.push(t); hIdx = historik.length; return; }
    avslutaSamtal();
  }
  fyll.style.height = "0px";
  ljudFordrojning = 0;
  const rad = out(t, "cmd");
  historik.push(t); hIdx = historik.length;
  nyScen = false;
  utfor(t);
  uppdateraStatus();
  rullaTill(rad);
}
document.getElementById("f").addEventListener("submit", e => {
  e.preventDefault();
  skicka(input.value);
  input.value = "";
  if (pekskarm) input.blur();
});
input.addEventListener("keydown", e => {
  if (e.key === "ArrowUp" && hIdx > 0) { hIdx--; input.value = historik[hIdx]; e.preventDefault(); }
  else if (e.key === "ArrowDown") { hIdx = Math.min(historik.length, hIdx + 1); input.value = historik[hIdx] || ""; e.preventDefault(); }
});
document.getElementById("quick")?.addEventListener("click", e => {
  const b = e.target.closest("button");
  if (b) { skicka(b.dataset.c); if (pekskarm) b.blur(); else input.focus(); }
});

function start(data) {
  visaLjudknapp();
  const medStartskarm = !!sk && !(data && data.state);
  if (medStartskarm) visaStartskarm();
  else if (sk) document.getElementById("splash").hidden = true;
  const pagar = data && data.state ? null : pagaendeSpel();
  if (data && data.state) { S = data.state; out(TEXTER.tillbaka, "sys"); titta(); }
  else if (pagar && pagar.moves > 0) {
    S = pagar;
    const banner = (A.intro || []).find(d => d && d.klass === "banner");
    if (banner) out(banner.text, "banner");
    out(TEXTER.fortsatter, "sys");
    titta();
  }
  else { S = nyttTillstand(); intro(); }
  autosparaPa = true;
  uppdateraStatus();
  scrollTill(null);
  window.claude?.hot?.snapshot?.(() => ({ state: S }));
  if (!pekskarm && !medStartskarm) input.focus();
}
window.claude?.hot?.ready ? window.claude.hot.ready(start) : start(window.claude?.hot?.data ?? {});

// För tester och felsökning
window.Spelmotor = { utfor: t => { utfor(t); uppdateraStatus(); }, skicka, samtal: (id, nod) => { startaSamtal(id, nod); uppdateraStatus(); }, get tillstand() { return S; }, Ljud };
window.Ljud = Ljud;
}
// Starta när sidan är redo (skripten kan ligga i <head> eller sist i <body>)
if (document.body) startaSpelmotorn();
else document.addEventListener("DOMContentLoaded", startaSpelmotorn);
