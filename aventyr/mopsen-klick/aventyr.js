/* ==========================================================================
   MOPSEN SOM FÖRSVANN (KLICKVERSIONEN)
   Samma fall som aventyr/mopsen, men spelas genom att peka och klicka i
   bilderna i stället för att skriva. Ljuden lånas från aventyr/mopsen.
   Ett äventyr för spelmotorn i motor/. Allt här är konfiguration: platser,
   föremål, personer, texter, pussel (regler), poäng, ledtrådar, bilder och ljud.
   Formatet beskrivs i README.md.
   ========================================================================== */
window.AVENTYR = {
  id: "mopsen-klick",
  titel: "Mopsen som försvann",
  ljudmapp: "../mopsen/ljud/",   // samma musik och ljud som textversionen
  lage: "klick",   // "text" (skriv kommandon) eller "klick" (peka och klicka). Bestäms av den som gör spelet.
  start: "kontor",

  startskarm: {
    bild: "bilder/splash.jpg",
    bildStaende: "bilder/splash_staende.jpg",
    alt: "En detektiv i trenchcoat och hatt står med ryggen mot oss under en gatlykta i regnet. Längre bort lyser en röd neonskylt.",
    ort: "Grand Harbor · 1947",
    titel: "Mopsen",
    under: "som försvann",
    regn: true,
  },

  intro: [
    { text: "Mopsen som försvann", klass: "banner" },
    { text: "Ett interaktivt deckaräventyr", klass: "sys" },
    "Grand Harbor, 1947. Regnet faller som om det fått betalt per droppe. Du är privatdetektiv, och just nu är du en privatdetektiv utan uppdrag, utan pengar och utan kaffe. Två av tre är ditt eget fel.",
    { text: "Tryck på saker i bilden, eller på det du bär, för att välja vad du vill göra. Tryck på en tom del av bilden för att se dig omkring. Under MENY finns hjälp, ledtrådar, sparning och ljud.", klass: "sys" },
  ],

  // Motorns standardtexter som det här äventyret byter ut (resten finns i motorn)
  texter: {
    ingenUtgang: ["Du kan inte gå åt det hållet. Inte ens om du ber snällt.", "Där finns bara en vägg, och den är inte intresserad.", "Grand Harbor är stort, men inte åt det hållet."],
    taPerson: "Det vore olämpligt. Och troligen olagligt. Och troligen smärtsamt.",
    taFast: "Det sitter fast, eller är för stort, eller både och.",
    taIngetAtt: "Det finns inget här som är värt att ta. Du har kollat.",
    barInget: "Du har ingenting. Fickorna ekar.",
    prataSjalv: "Du pratar för dig själv en stund. Det är det bästa samtal du haft på hela veckan.",
    lyssna: "Du hör regnet, trafiken och ditt eget samvete. Inget av dem har något nytt att säga.",
    lukta: "Regn och avgaser. Grand Harbors parfym.",
    at: "Det där ska inte ätas. Inte ens i den här stan.",
    vanta: ["Tiden går. Regnet faller. Ingen ringer.", "Du väntar. Det är en del av jobbet som ingen pratar om.", "Du tänder en imaginär cigarett och funderar."],
    spelSlut: "Fallet är redan löst. Välj Börja om i menyn för att spela igen.",
    tillbaka: "Du är tillbaka i fallet.",
    hjalp: [
      "Du styr detektiven genom att skriva vad du vill göra, med korta meningar på svenska. Oftast räcker ett verb, ibland följt av vad eller vem det gäller.",
      "TITTA (eller T): se dig omkring\nUNDERSÖK något (eller U): titta närmare på något\nTA, SLÄPP, ÖPPNA, LÄS: hantera saker\nPRATA MED, GE, VISA: ta kontakt med folk\nUPP, NER, IN, UT: gå åt ett håll\nÅK TILL: res med tunnelbanan från en perrong\nINVENTARIE (eller I): se vad du bär på",
      "Undersök det du ser och prata med dem du möter. Kör du fast kan du skriva LEDTRÅD.",
    ],
  },

  snabbknappar: [["Titta", "titta"], ["Ägodelar", "inventarie"], ["Upp", "upp"], ["Ner", "ner"], ["In", "in"], ["Ut", "ut"], ["Ledtråd", "ledtråd"], ["Bild", "bild"], ["Ljud", "ljud"], ["Hjälp", "hjälp"]],

  // Verb som bara det här äventyret använder (motorns egna verb finns redan)
  verb: {
    köp: ["köp", "beställ"],
    dyrka: ["dyrka", "bänd", "lås upp"],
    lås: ["lås"],
    bryt: ["bryt", "knäck"],
    slå: ["slå", "sparka", "döda", "skjut", "attackera", "brotta"],
    sov: ["sov"], svär: ["svär"], hoppa: ["hoppa"], tänk: ["tänk", "fundera"], ring: ["ring"],
    taxi: ["ta taxi", "åk taxi"],
  },
  alias: { betala: "köp korv" },

  // ------------------------------------------------------------------ resor
  resor: {
    verb: ["åk", "res", "ta tunnelbanan", "ta tåget"],
    ljud: "tunnelbana",
    karta: "karta",   // i klickläget: tryck på linjekartan för att åka
    stationer: {
      p_main:  { namn: "Main Street", ord: ["main", "mainstreet", "main street", "centrum", "kontoret", "hem"] },
      p_park:  { namn: "Park Avenue", ord: ["park", "parkavenue", "park avenue", "avenue"] },
      p_china: { namn: "Chinatown",   ord: ["chinatown", "china", "china town"] },
      p_pir:   { namn: "Pir 9",       ord: ["pir", "pir 9", "pir9", "piren", "hamnen", "hamn", "9"] },
    },
    resetexter: [
      "Ett tåg dundrar in. Du kliver på och hittar en plats mellan en man med en levande gås och en kvinna som läser din tidning över din axel.",
      "Vagnen är så full att du åker hela vägen utan att röra golvet. En saxofonist spelar samma låt fyra gånger.",
      "Du sitter mittemot en man som stirrar på dig hela resan. När du stirrar tillbaka låtsas han vara en reklamskylt.",
      "Tåget skakar, lamporna blinkar, och en röst i högtalaren säger något som kan vara stationsnamnet eller ett recept.",
    ],
    texter: {
      forstNer: "Du måste först gå ner till perrongen.",
      ingenStation: "Det finns ingen tunnelbana här. Leta efter en trappa ner till en perrong.",
      vart: "Vart vill du åka? Tryck på linjekartan och välj en station.",
      okand: "Linjen har bara fyra stationer: Main Street, Park Avenue, Chinatown och Pir 9.",
      redanHar: "Du är redan här. Tunnelbanan är snabb, men inte så snabb.",
      avstigning: "Du kliver av vid {station}.",
    },
  },

  // ------------------------------------------------------------------ platser
  rum: {
    kontor: {
      namn: "Ditt kontor", bild: "kontor", ord: ["kontor", "kontoret"],
      kortBeskrivning: [
        { om: { inteFlagga: "svarare" }, text: "Ditt kontor. Telefonsvararen blinkar fortfarande, som om någon där ute faktiskt behöver dig." },
        { om: { bar: "mops" }, text: "Ditt kontor. Lord Waffles nosar på kundstolen och ser inte imponerad ut. Han har sett finare kontor. Han har sett finare hundkojor." },
        "Ditt kontor. Det ser ut precis som när du gick, och det är just det som är problemet.",
        "Tillbaka på kontoret. Räkningarna har inte betalat sig själva medan du var borta. Du kollade.",
        "Ditt kontor. Dammet har lagt sig i exakt samma mönster som förra gången. Du väljer att se det som stabilitet.",
      ],
      beskrivning: ["Ditt kontor på femte våningen i Hendersonhuset. Ett skrivbord, två stolar (en för dig och en för kunder som aldrig kommer), en klädhängare och ett fönster mot regnet. På dörrens frostade glas står det VITKETEDTAVIRP, vilket är rätt stavat från andra sidan. Trappan leder ner till gatan.",
        { om: { inteFlagga: "svarare" }, text: "\n\nPå skrivbordet blinkar telefonsvararen ilsket rött." }],
      utgangar: { ner: "mainst", ut: "mainst" },
      animationer: {
        lampa: [{ om: { flagga: "svarare" }, ram: 1 }],                     // lampan slocknar när meddelandet är avlyssnat
        rock: [{ om: { inteObjektPa: ["rock", "kontor"] }, ram: 1 }, { ram: 0 }],   // rocken är borta från hängaren
        lada: [{ om: { oppen: "lada" }, ram: 1 }, { ram: 0 }],              // lådan är utdragen
      },
    },
    mainst: {
      namn: "Main Street", bild: "mainst", ord: ["gata", "gatan", "main street"],
      kortBeskrivning: [
        { om: { bar: "dollar", inteFlagga: "korv" }, text: "Main Street. Korvkiosken ångar, och dollarsedeln i fickan känns plötsligt mycket viktig." },
        { om: { bar: "mops" }, text: "Main Street. Sal får syn på mopsen i dina armar. \"Ingen hund i kön\", säger han av gammal vana. Det finns ingen kö." },
        "Main Street. Regnet, bilarna och Sal vid korvkiosken. Allt är som vanligt, och det är sällan ett gott tecken.",
        "Main Street igen. Sal vinkar med korvtången. Du vinkar tillbaka utan korvtång.",
        "Main Street. En taxi kör förbi och stänker ner dina byxor. Det känns nästan som att komma hem.",
      ],
      beskrivning: "Main Street, mitt i Grand Harbor. Regnet smattrar på markiserna och bilarna tutar på varandra som gamla grannar som aldrig blivit sams. Vid trottoarkanten står en korvkiosk med en ångande kastrull, och bredvid den ett tidningsställ. Ovanför dig ligger kontorshuset, och en trappa med en emaljerad skylt leder ner till tunnelbanan.",
      utgangar: { upp: "kontor", in: "kontor", ner: "p_main" },
    },
    p_main: {
      namn: "Perrongen vid Main Street", bild: "p_main", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      kortBeskrivning: [
        "Perrongen under Main Street. Mannen på bänken sover fortfarande. Han har kommit längre i livet än du, och han har inte rört sig.",
        "Perrongen under Main Street. Det luktar järn och jordnötter, och tåget mot Park Avenue, Chinatown och Pir 9 kan komma när som helst. Eller inte.",
        "Perrongen under Main Street. Någon har ätit fler jordnötter sedan sist. Du misstänker mannen på bänken. Du har inga bevis.",
      ],
      beskrivning: "Tunnelbaneperrongen under Main Street. Det luktar järn, regnrockar och gårdagens jordnötter. En linjekarta på väggen visar fyra stationer: MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp till gatan.",
      utgangar: { upp: "mainst", ut: "mainst" },
      passage: "spärren",
    },
    p_park: {
      namn: "Perrongen vid Park Avenue", bild: "p_park", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      kortBeskrivning: [
        "Perrongen vid Park Avenue. Fiolspelaren har gått över till Vivaldi. Ingen märker skillnaden utom han själv.",
        "Perrongen vid Park Avenue. Någon har torkat av bänkarna igen sedan du var här senast. Det var en kvart sedan.",
        "Perrongen vid Park Avenue, där även råttorna verkar ha gått i internatskola.",
      ],
      beskrivning: "Den finaste perrongen i hela systemet. Någon har till och med torkat av bänkarna, och en gatumusikant spelar Bach på en fiol som är värd mer än din bil. Linjekartan visar MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp.",
      utgangar: { upp: "parkave", ut: "parkave" },
      passage: "spärren",
    },
    p_china: {
      namn: "Perrongen vid Chinatown", bild: "p_china", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      kortBeskrivning: [
        "Perrongen vid Chinatown. Den gamle mannen med ankan är kvar. Ankan följer dig med blicken. Den kommer ihåg dig.",
        "Perrongen vid Chinatown. Ingefära, matkassar och folk som har bråttom åt alla håll samtidigt.",
        "Perrongen vid Chinatown. Någon tappar en fiskstjärt framför dig. Du väljer att inte tolka det som ett budskap.",
      ],
      beskrivning: "Perrongen under Chinatown är fylld av folk med matkassar, och det doftar ingefära hela vägen ner hit. Linjekartan visar MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp.",
      utgangar: { upp: "china", ut: "china" },
      passage: "spärren",
    },
    p_pir: {
      namn: "Perrongen vid Pir 9", bild: "p_pir", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      kortBeskrivning: [
        "Perrongen vid Pir 9. Lysrören blinkar fortfarande. Budskapet har inte blivit muntrare.",
        "Perrongen vid Pir 9, linjens sista station. Vattnet droppar ner i samma pöl som förut, med en ihärdighet du kunde lära dig något av.",
        "Perrongen vid Pir 9. En råtta springer längs kanten. Den har bråttom härifrån, och det har den rätt i.",
      ],
      beskrivning: "Den sista stationen på linjen. Lysrören blinkar som om de försöker säga något i morsekod, troligen \"åk härifrån\". Linjekartan visar MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp mot hamnen.",
      utgangar: { upp: "pir", ut: "pir" },
      passage: "spärren",
    },
    parkave: {
      namn: "Park Avenue", bild: "parkave", ord: ["gata", "gatan", "park avenue"],
      kortBeskrivning: [
        { om: { inteFlagga: "svarare" }, text: "Park Avenue. Portiern ser på dig som om du vore regn som har kommit in genom fel dörr." },
        { om: { bar: "mops" }, text: "Park Avenue. Portiern får syn på Lord Waffles i dina armar och tappar fattningen för första gången i sitt liv. Ett ögonbryn rör sig. Nästan en millimeter." },
        "Park Avenue. Duvan med fluga har bytt till en randig. Portiern har inte bytt min sedan 1932.",
        "Park Avenue. Pettigrew Towers glänser i regnet, och portiern står kvar vid entrén som en mycket välklädd bom.",
        "Park Avenue, där trottoarerna är så rena att du skäms över dina skor. Och dig själv.",
      ],
      beskrivning: "Park Avenue, där även duvorna verkar ha butler. Framför dig reser sig Pettigrew Towers i vit marmor och mässing. En portier i grön uniform med guldknappar står vid entrén och betraktar dig som om du vore en fläck på hans matta. Tunnelbanetrappan leder ner.",
      utgangar: { ner: "p_park", in: "vaning" },
    },
    vaning: {
      namn: "Pettigrews takvåning", bild: "vaning", ord: ["takvåning", "takvåningen", "våning", "våningen", "hiss", "hissen"],
      kortBeskrivning: [
        { om: { flagga: "vunnit" }, text: "Takvåningen. Lord Waffles snarkar i sin purpurkorg, och fru Pettigrew nynnar för sig själv. Till och med det lilla molnet under taket ser gladare ut." },
        { om: { bar: "mops" }, text: "Takvåningen. Fru Pettigrew sitter i den vita soffan och snyftar. Sedan får hon syn på vad du har i famnen." },
        "Takvåningen. Fru Pettigrew snyftar i en ny spetsnäsduk. Den förra är på tvätt.",
        "Takvåningen. Det lilla molnet under taket har flyttat sig till andra sidan rummet. Den tomma hundkorgen står kvar.",
      ],
      beskrivning: ["En takvåning så stor att den har eget väder. Kristallkronor, persiska mattor och ett porträtt i olja av en mops i amiralsuniform. Under porträttet står en tom hundkorg sammetsklädd i purpur.",
        { om: { inteFlagga: "vunnit" }, text: " Fru Pettigrew sitter i en vit soffa och snyftar i en spetsnäsduk." },
        " Hissen tar dig ut igen."],
      utgangar: { ut: "parkave", ner: "parkave" },
      animationer: {   // glad änka och mops i korgen efter vinsten
        fru: [{ om: { flagga: "vunnit" }, ram: 2 }],
        mops: [{ om: { flagga: "vunnit" }, ram: 1 }, { ram: 0 }],
      },
      passage: [
        { om: { inteFlagga: "svarare" }, stopp: true, gor: ["Portiern kliver i vägen. \"Är ni väntad, sir?\" Du är inte väntad. Du är knappt ens önskad. Han skickar tillbaka dig ut i regnet."] },
        { om: { inteFlagga: "klient" }, gor: ["\"Ah, detektiven! Fru Pettigrew väntar er.\" Portiern håller upp dörren med två fingrar, som om den vore smittsam. Hissen susar upp till takvåningen."] },
        { gor: [{ ljud: "hiss" }] },
      ],
      vidIntrade: [
        { om: { bar: "mops", inteFlagga: "vunnit" }, gor: [{ kor: "vinst" }] },
        { om: { inteFlagga: "klient" }, gor: [
          { satt: "klient" },
          "Fru Pettigrew rusar fram och griper tag i dina händer. \"Äntligen! Lord Waffles är kidnappad! Han skulle tävla på lördag. Han har vunnit tre år i rad. Han har aldrig förlorat på någonting, utom en gång mot en dammsugare.\"",
          "Hon trycker ett fotografi, ett lösenbrev och en liten påse i dina händer. \"Här är ett foto av honom, och det här brevet kom i morse. Och ta hans kex! Han går ingenstans utan sina kex. Han är som sin far på det sättet.\"",
          { flytta: ["foto", "brev", "kex"], till: "spelare" },
          { sys: "(Du har fått ett foto, ett lösenbrev och en påse hundkex.)" },
          { poang: "klient" },
        ] },
      ],
    },
    china: {
      namn: "Chinatown", bild: "china", ord: ["gata", "gatan", "chinatown"],
      kortBeskrivning: [
        { om: { inteFlagga: "adress" }, text: "Chinatown. Neonskylten lyser GOLDEN DRAGON, NUDLAR & DUMPLINGS, och lösenbrevet i fickan luktar fortfarande sötsur sås." },
        "Chinatown. Neonskylten för Golden Dragon surrar, och D:et blinkar som vanligt.",
        "Chinatown. Gumman i ståndet hälsar på dig som på en gammal stamkund. Du har aldrig köpt något.",
        "Chinatown. Röda lyktor, regn och en cykelklocka någonstans. Tunnelbanan ligger under dina fötter.",
      ],
      beskrivning: "Chinatown. Röda lyktor gungar i regnet över smala gator fulla av folk, cyklar och stånd med torkad bläckfisk. Rakt fram lyser en neonskylt: GOLDEN DRAGON, NUDLAR & DUMPLINGS, ÖPPET TILL SENT. Tunnelbanan ligger under dina fötter.",
      utgangar: { ner: "p_china", in: "restaurang" },
    },
    restaurang: {
      namn: "Golden Dragon", bild: "restaurang", ord: ["restaurang", "restaurangen", "golden", "dragon"],
      kortBeskrivning: [
        { om: { inteFlagga: "adress" }, text: "Golden Dragon. Benny slår upp lågor i wokpannan och tittar på dig som om han väntar på att du ska visa honom något." },
        "Golden Dragon. Karpen i akvariet har inte ändrat uppfattning om dig.",
        "Golden Dragon. Benny vinkar med sleven, porslinskatten vinkar med tassen, och du står mittemellan och känner dig omvinkad.",
      ],
      beskrivning: "En smal restaurang med röda bås, ett akvarium med en djupt uttråkad karp och ett kök som syns genom en lucka. Bakom luckan står kocken Benny och slår upp wokpannan i lågor som en trollkarl. Vid kassan står en skål med lyckokakor.",
      utgangar: { ut: "china" },
      lukt: "Ingefära, vitlök och lyckokakor.",
    },
    pir: {
      namn: "Pir 9", bild: "pir", ord: ["pir", "piren", "hamn", "hamnen"],
      kortBeskrivning: [
        { om: { inteFlagga: "bruno" }, text: "Pir 9. Bruno står kvar framför Lager 13. Hans mage kurrar som en mistlur med halsont." },
        { om: { flagga: "bruno", inteFlagga: "dorr" }, text: "Pir 9. Bruno är borta och letar senap. Dörren till Lager 13 är fortfarande låst med ett hänglås." },
        { om: { flagga: "dorr" }, text: "Pir 9. Dörren till Lager 13 står på glänt. Dimman smiter in före dig." },
      ],
      beskrivning: ["Pir 9 i hamnen. Dimman ligger tjock över vattnet och mistlurarna låter som valar med halsont. Längs kajen står slitna lagerlokaler. På den närmaste står en stor etta bredvid en ännu större trea: LAGER 13.",
        { om: { inteFlagga: "bruno" }, text: " Framför dörren står en man byggd som ett kylskåp med två kylskåp på axlarna." },
        { om: { flagga: "dorr" }, text: " Dörren står på glänt." },
        " Tunnelbanetrappan leder ner."],
      utgangar: { ner: "p_pir", in: "lager" },
      animationer: { lage: [{ om: { flagga: "dorr" }, ram: 2 }, { om: { flagga: "bruno" }, ram: 1 }, { ram: 0 }] },   // Bruno går, sedan öppnas dörren
    },
    lager: {
      namn: "Lager 13", bild: "lager", ord: ["lager", "lagret", "lagerlokal", "lagerlokalen"],
      kortBeskrivning: [
        { om: { objektPa: ["mops", "lager"], inteFlagga: "mopsVan" }, text: "Lager 13. Lord Waffles morrar i sin bur. Det luktar fortfarande friterade räkor." },
        { om: { objektPa: ["mops", "lager"], flagga: "mopsVan" }, text: "Lager 13. Lord Waffles sitter och väntar på dig, och på fler kex. Mest på kexen." },
        { om: { inteObjektPa: ["mops", "lager"] }, text: "Lager 13. Den tomma buren står kvar bland fruktlådorna. Tolv hämtmatskartonger och inte en enda mops." },
      ],
      beskrivning: ["Ett dammigt lager fullt av trälådor märkta FRUKTKONSERVER, vilket inte förklarar varför det luktar friterade räkor. På golvet står tolv tomma hämtmatskartonger från Golden Dragon.",
        { om: { objektPa: ["mops", "lager"] }, text: " Mitt på golvet står en hundbur, och i den sitter en mops med en liten krona broderad på halsbandet. Han ser ut som en mycket upprörd potatis." },
        " Dörren leder ut till piren."],
      utgangar: { ut: "pir" },
      lukt: "Friterade räkor och skräckslagen mops.",
      animationer: { mops: [{ om: { inteObjektPa: ["mops", "lager"] }, ram: 3 }, { om: { flagga: "mopsVan" }, ram: 2 }] },   // morrar i buren, kommer ut, försvinner
      passage: [
        { om: { inteFlagga: "bruno" }, stopp: true, gor: ["Kylskåpet i mänsklig form kliver i vägen. \"Stängt\", säger han. \"Ingen kommer in. Bruno vaktar. Bruno är hungrig. Bruno vaktar ändå.\"", { ljud: "mage", fordrojning: 0.6 }] },
        { om: { inteFlagga: "dorr" }, stopp: true, gor: ["Lagerdörren är låst med ett stort hänglås."] },
      ],
    },
  },

  // ------------------------------------------------------------------ föremål och personer
  // plats: rum, "spelare", ett annat föremål (behållare) eller null (finns inte än).
  objekt: {
    skrivbord: { namn: ["skrivbord", "skrivbordet", "bord", "bordet"], kort: "ett skrivbord", plats: "kontor", fast: true,
      beskrivning: "Ett bastant ekskrivbord med brännmärken efter cigaretter som inte är dina. Det har en låda." },
    lada: { namn: ["låda", "lådan", "skrivbordslåda", "skrivbordslådan"], kort: "en låda", plats: "kontor", fast: true, behallare: true, oppningsbar: true,
      oppnaText: "Du rycker i lådan. Den kärvar, du svär, den ger med sig.", oppnaLjud: "lada", redanOppenText: "Lådan är redan öppen.",
      stangText: "Du stänger lådan.", stangdText: "Lådan är stängd.",
      beskrivning: [{ om: { oppen: "lada" }, text: "Skrivbordslådan är öppen." }, { om: { stangd: "lada" }, text: "Skrivbordslådan är stängd. Den kärvar lite, som allt annat i ditt liv." }] },
    svarare: { namn: ["telefonsvarare", "telefonsvararen", "svarare", "svararen", "telefon", "telefonen", "knapp", "knappen", "maskin", "maskinen"], kort: "en telefonsvarare", plats: "kontor", fast: true, klickverb: ["lyssna på"],
      beskrivning: [{ om: { flagga: "svarare" }, text: "Telefonsvararen har slutat blinka. Den ser nöjd ut." }, { om: { inteFlagga: "svarare" }, text: "En telefonsvarare med en blinkande röd lampa. Ett meddelande väntar." }] },
    hangare: { namn: ["klädhängare", "klädhängaren", "hängare", "hängaren"], kort: "en klädhängare", plats: "kontor", fast: true,
      beskrivning: "En klädhängare av böjträ. Den har sett bättre dagar, och bättre rockar." },
    rock: { namn: ["rock", "rocken", "trenchcoat", "trenchcoaten", "kappa", "kappan", "ficka", "fickan", "fickor", "fickorna"], kort: "din trenchcoat", plats: "kontor",
      beskrivning: "Din beigea trenchcoat. Den har två fickor, tre fläckar och en historia." },
    fonster: { namn: ["fönster", "fönstret", "regn", "regnet", "utsikt", "utsikten", "stad", "staden", "persienn", "persienner", "persiennerna", "neonskylt", "neonskylten", "hotell"], kort: "ett fönster", plats: "kontor", fast: true,
      beskrivning: "Grand Harbor ligger utbredd nedanför, grå och blank av regn. Någonstans där ute finns ett fall. Förhoppningsvis ett som betalar." },
    // Saker i kontoret som mest finns för stämningens skull
    lampa: { namn: ["lampa", "lampan", "bankirlampa", "bankirlampan", "skärm", "skärmen"], kort: "en bankirlampa", plats: "kontor", fast: true,
      beskrivning: "En bankirlampa med grön glasskärm. Den kastar ett varmt ljus över skrivbordet och får till och med dina räkningar att se trivsamma ut." },
    stol: { namn: ["stol", "stolen", "stolar", "stolarna", "kontorsstol", "kontorsstolen"], kort: "en stol", plats: "kontor", fast: true,
      beskrivning: "Din kontorsstol. Sätet har formats efter tjugo år av väntan. Kundstolen bredvid ser fortfarande ny ut, av förklarliga skäl." },
    diplom: { namn: ["diplom", "diplomet", "examen", "examensbevis"], kort: "ett diplom", plats: "kontor", fast: true, lasbar: true,
      beskrivning: "Ett inramat diplom från Grand Harbors korrespondensinstitut för privatdetektiver. Längst ner står det med liten stil: \"Godkänd i skuggning, med anmärkningen att eleven skuggade fel person i tre veckor.\"" },
    kalender: { namn: ["kalender", "kalendern", "almanacka", "almanackan"], kort: "en kalender", plats: "kontor", fast: true, lasbar: true,
      beskrivning: "En kalender för 1947 med en bild på hamnen i månsken. Fredagen är inringad med rött och där står det HYRA. Någon har lagt till tre utropstecken. Det var hyresvärden." },
    rakningar: { namn: ["räkning", "räkningen", "räkningar", "räkningarna", "hög", "högen"], kort: "en hög räkningar", klicknamn: "räkningarna", plats: "kontor", fast: true, lasbar: true,
      beskrivning: "En hög obetalda räkningar, sorterade efter hur arga de låter. Den översta är från telefonbolaget och slutar med ordet SISTA i versaler." },
    askkopp: { namn: ["askkopp", "askkoppen", "cigarett", "cigaretten", "rök", "röken", "fimp", "fimpen"], kort: "en askkopp", plats: "kontor", fast: true,
      beskrivning: "En överfull askkopp. I kanten pyr en cigarett som du inte minns att du tände. Det är ett mysterium du har slutat utreda." },
    flaska: { namn: ["flaska", "flaskan", "whisky", "whiskyflaska", "whiskyflaskan", "sprit"], kort: "en whiskyflaska", plats: "kontor", fast: true,
      beskrivning: "En whiskyflaska. Den är tom, precis som kassaskåpet, plånboken och kundregistret." },
    hatt: { namn: ["hatt", "hatten", "fedora", "fedoran"], kort: "en hatt", plats: "kontor", fast: true,
      beskrivning: "Din fedora, gråbrun och lite tilltufsad av regnet. En privatdetektiv utan hatt är bara en man med åsikter." },
    kort: { namn: ["tunnelbanekort", "tunnelbanekortet", "kort", "kortet", "månadskort", "månadskortet", "biljett", "biljetten"], kort: "ett tunnelbanekort", plats: "lada",
      beskrivning: "Ditt tunnelbanekort, giltigt på alla stationer. Fotot på det är taget en dag när du hade ännu mindre sömn än vanligt.",
      lasText: "Det står GRAND HARBOR TRANSIT, GILTIGT TILLS VIDARE. Det är det mest optimistiska du har läst på länge.",
      vidTa: [{ poang: "kort" }] },
    dyrk: { namn: ["dyrk", "dyrken", "dyrkar", "dyrkset", "dyrkverktyg"], kort: "en dyrk", plats: "lada",
      beskrivning: "En dyrk i fjäderstål. Strikt taget olaglig att bära. Strikt taget." },
    dollar: { namn: ["dollar", "dollarn", "dollarsedel", "dollarsedeln", "sedel", "sedeln", "pengar", "pengarna"], kort: "en skrynklig dollarsedel", plats: null,
      beskrivning: "En skrynklig dollarsedel. George Washington ser lika trött ut som du." },
    kiosk: { namn: ["korvkiosk", "korvkiosken", "kiosk", "kiosken", "sal", "försäljare", "försäljaren", "korvgubbe", "korvgubben", "kastrull", "kastrullen"], kort: "en korvkiosk", plats: "mainst", fast: true, person: true, lasbar: true,
      beskrivning: "Korvkiosken drivs av Sal, en man med en mustasch så stor att den borde ha egen hyra. På skylten står VARMKORV 1 $. MED SENAP 1 $. UTAN SENAP OCKSÅ 1 $." },
    tidning: { namn: ["tidning", "tidningen", "tidningar", "tidningarna", "tidningsställ", "tidningsstället", "rubrik", "rubriken"], kort: "ett tidningsställ", plats: "mainst", fast: true, lasbar: true,
      beskrivning: "Grand Harbor Gazette. Löpsedeln skriker: \"FAVORITEN LORD WAFFLES KLAR FÖR LÖRDAGENS HUNDUTSTÄLLNING\". Under den, med mindre stil: \"Borgmästaren lovar mindre regn\"." },
    korv: { namn: ["varmkorv", "varmkorven", "korv", "korven", "hotdog"], kort: "en varmkorv med senap", plats: null,
      beskrivning: "En varmkorv med extra senap, insvept i papper. Den doftar som en barndom du aldrig hade." },
    karta: { namn: ["linjekarta", "linjekartan", "karta", "kartan", "skylt", "skylten"], kort: "en linjekarta", plats: "överallt", grupp: "station", fast: true, lasbar: true,
      beskrivning: "Linjekartan visar en enda linje: MAIN STREET – PARK AVENUE – CHINATOWN – PIR 9. Tryck på den och välj vart du vill åka." },
    portier: { namn: ["portier", "portiern", "dörrvakt", "dörrvakten", "reginald", "man", "mannen"], kort: "en portier", plats: "parkave", fast: true, person: true,
      beskrivning: "Portiern heter Reginald, enligt mässingsskylten på bröstet. Han har en näsa som är byggd för att se ner på folk, och han använder den flitigt." },
    pettigrew: { namn: ["pettigrew", "fru", "frun", "änka", "änkan", "dam", "damen", "kvinna", "kvinnan", "klient", "klienten"], kort: "fru Pettigrew", plats: "vaning", fast: true, person: true,
      beskrivning: "Fru Cornelia Pettigrew, änka efter konservkungen Horace Pettigrew. Hon bär tillräckligt med pärlor för att sänka en mindre båt." },
    portratt: { namn: ["porträtt", "porträttet", "tavla", "tavlan", "målning", "målningen", "amiral", "amiralen"], kort: "ett porträtt", plats: "vaning", fast: true,
      beskrivning: "Lord Waffles i amiralsuniform, målad i olja. Konstnären har varit generös med hakan. Mopsar har ingen haka." },
    foto: { namn: ["foto", "fotot", "fotografi", "fotografiet", "bild", "bilden"], kort: "ett foto av Lord Waffles", plats: null,
      beskrivning: "Ett fotografi av Lord Waffles: en ljusbrun mops med svart nos, utstående ögon och ett halsband med en liten broderad krona." },
    brev: { namn: ["lösenbrev", "lösenbrevet", "brev", "brevet", "papper", "papperet", "meny", "menyn"], kort: "ett lösenbrev", plats: null, lasbar: true,
      beskrivning: "Lösenbrevet är hopklistrat av urklippta tidningsbokstäver: \"VI HAR HUNDEN. 50 000 $ ANNARS MISSAR HAN UTSTÄLLNINGEN. INVÄNTA INSTRUKTIONER.\" När du vänder på det ser du att det är klistrat på baksidan av en meny. Överst står det GOLDEN DRAGON, CHINATOWN. Någon har spillt sötsur sås på nummer 47." },
    kex: { namn: ["hundkex", "kex", "kexen", "kexet", "påse", "påsen", "kexpåse", "kexpåsen"], kort: "en påse hundkex", plats: null, lasbar: true,
      beskrivning: "En liten sidenpåse med hundkex. Påsen är broderad med orden FÖR HANS NÅD." },
    benny: { namn: ["benny", "kock", "kocken", "kök", "köket", "lucka", "luckan", "wok", "wokpanna", "wokpannan"], kort: "kocken Benny", plats: "restaurang", fast: true, person: true,
      beskrivning: "Benny är kock på Golden Dragon och kan allt om alla i kvarteret. Han lagar mat med ena handen och läser travresultat med den andra." },
    akvarium: { namn: ["akvarium", "akvariet", "karp", "karpen", "fisk", "fisken"], kort: "ett akvarium", plats: "restaurang", fast: true,
      beskrivning: "Karpen tittar på dig. Du tittar på karpen. Ingen av er får ut något av det." },
    lyckokaka: { namn: ["lyckokaka", "lyckokakan", "lyckokakor", "lyckokakorna", "kaka", "kakan", "skål", "skålen"], kort: "en lyckokaka", plats: "restaurang", klickverb: ["bryt"],
      beskrivning: "En lyckokaka. Det ligger en lapp inuti. Du får bryta den för att läsa den." },
    bruno: { namn: ["bruno", "gorilla", "gorillan", "vakt", "vakten", "kylskåp", "kylskåpet", "man", "mannen", "torped", "torpeden"], kort: "en jättelik vakt", plats: "pir", fast: true, person: true,
      beskrivning: "Han har en tatuering på knogarna som stavar B-R-U-N-O, och en på andra handen som stavar M-A-M-M-A. Hans mage kurrar så högt att måsarna lyfter." },
    dorr: { namn: ["dörr", "dörren", "lager", "lagret", "lagerdörr", "lagerdörren", "lås", "låset", "hänglås", "hänglåset"], kort: "en dörr", plats: "pir", fast: true, utgang: "in",
      beskrivning: [{ om: { flagga: "dorr" }, text: "Lagerdörren står på glänt. Hänglåset hänger öppet och skäms." }, { om: { inteFlagga: "dorr" }, text: "En plåtdörr med ett stort hänglås. Ett ganska enkelt lås, för den som har rätt verktyg." }] },
    mops: { namn: ["mops", "mopsen", "hund", "hunden", "lord", "waffles", "lord waffles", "bur", "buren", "hundbur", "hundburen", "potatis"], kort: "Lord Waffles", plats: "lager", person: true,
      beskrivning: [{ om: { flagga: "mopsVan" }, text: "Lord Waffles flämtar förnöjt och har kexsmulor i rynkorna. Han litar på dig nu. I alla fall tills kexen tar slut." }, { om: { inteFlagga: "mopsVan" }, text: "Lord Waffles sitter i en olåst bur och morrar mot dig. Han är kanske tjugo centimeter hög, men hans självförtroende är minst två meter." }] },
    ladar: { namn: ["trälåda", "trälådor", "trälådorna", "lådor", "lådorna", "kartong", "kartonger", "kartongerna", "hämtmat", "konserver"], kort: "lådor", plats: "lager", fast: true,
      beskrivning: "Du öppnar en låda märkt FRUKTKONSERVER. Den innehåller frukt i konserv. Det här är uppenbarligen en mycket genomtänkt kamouflering." },

    // ---- Stämningssaker på gator, i lokaler och på perronger (klickbara i bilderna)
    // Main Street
    kontorsfonster: { namn: ["kontorsfönster", "kontorsfönstret", "fönster", "fönstret", "kontorshus", "kontorshuset", "hendersonhuset"], kort: "ditt kontorsfönster", plats: "mainst", fast: true,
      beskrivning: "Ditt eget kontorsfönster på femte våningen. Härifrån ser det nästan ut som ett kontor där det händer saker. Avstånd gör underverk." },
    diner: { namn: ["diner", "dinern", "fik", "fiket", "kafé", "kaféet", "markis", "markisen"], kort: "en diner", plats: "mainst", fast: true,
      beskrivning: "Rosie's Diner. Kaffet är svart, pajen är gårdagens och servitrisen kallar alla för \"sötnos\" med en ton som betyder motsatsen. Du har skuld där också." },
    gatlykta: { namn: ["gatlykta", "gatlyktan", "lykta", "lyktan", "lyktstolpe", "lyktstolpen"], kort: "en gatlykta", plats: "mainst", fast: true,
      beskrivning: "En gatlykta som lyser upp en liten cirkel av regn. Det är den mest pålitliga invånaren på Main Street. Den står där varje natt och ställer inga frågor." },
    bil: { namn: ["bil", "bilen", "sedan", "sedanen", "taxi"], kort: "en bil", plats: "mainst", fast: true,
      beskrivning: "En svart sedan med motorn i gång och ingen bakom ratten. I Grand Harbor betyder det antingen att någon är inne och köper cigaretter, eller att någon aldrig kommer tillbaka. Du låter den vara." },
    // Park Avenue
    towers: { namn: ["pettigrew towers", "towers", "hus", "huset", "skyskrapa", "skyskrapan", "fasad", "fasaden", "marmor", "marmorn"], kort: "Pettigrew Towers", plats: "parkave", fast: true,
      beskrivning: "Pettigrew Towers, tjugo våningar vit marmor. Huset är byggt på konservpengar, vilket syns: det ser ut som en mycket dyr burk." },
    trad: { namn: ["träd", "trädet", "träden", "kruka", "krukan", "krukor", "buske", "busken"], kort: "träd i krukor", plats: "parkave", fast: true,
      beskrivning: "Två små träd i krukor, klippta i perfekta klot. De har en egen trädgårdsmästare. Trädgårdsmästaren har en egen trädgårdsmästare." },
    duva: { namn: ["duva", "duvan", "fågel", "fågeln", "fluga", "flugan"], kort: "en duva", plats: "parkave", fast: true, person: true,
      beskrivning: "En duva med en liten svart fluga runt halsen. Hon trippar fram och tillbaka som om hon väntade på en droska. Hon har bättre kläder än du." },
    // Takvåningen
    matta: { namn: ["matta", "mattan", "mattor", "mattorna"], kort: "en persisk matta", plats: "vaning", fast: true,
      beskrivning: "En persisk matta som är så tjock att dina skor försvinner i den. Du ställer dig lite åt sidan. Det känns som att den tar betalt per steg." },
    korg: { namn: ["korg", "korgen", "hundkorg", "hundkorgen", "sammet", "kudde", "kudden"], kort: "en hundkorg", plats: "vaning", fast: true,
      beskrivning: [{ om: { flagga: "vunnit" }, text: "Lord Waffles ligger i sin purpurkorg och snarkar som en liten dieselmotor. Ordningen är återställd." },
        { om: { inteFlagga: "vunnit" }, text: "En hundkorg i purpursammet med guldtofsar. Den är tom, och den tomheten är det sorgligaste i hela rummet. Förutom priset på korgen." }] },
    krona: { namn: ["kristallkrona", "kristallkronan", "krona", "kronan", "kristallkronor", "ljuskrona", "ljuskronan"], kort: "en kristallkrona", plats: "vaning", fast: true,
      beskrivning: "En kristallkrona stor som din lägenhet. Den klirrar lite varje gång hissen går. Du räknar prismorna och tappar bort dig vid trehundra." },
    vaningsfonster: { namn: ["fönster", "fönstret", "fönstren", "utsikt", "utsikten", "draperi", "draperier", "draperierna", "gardin", "gardinerna", "stad", "staden"], kort: "höga fönster", plats: "vaning", fast: true,
      beskrivning: "Härifrån ser Grand Harbor ut som en leksaksstad. Du letar efter ditt eget kontor. Det syns inte. Det syns sällan." },
    moln: { namn: ["moln", "molnet", "väder", "vädret"], kort: "ett litet moln", plats: "vaning", fast: true,
      beskrivning: "Ett litet moln svävar under taket. Takvåningen är så stor att den har eget väder. Fru Pettigrew har säkert en meteorolog anställd för att hålla det borta från soffan." },
    palm: { namn: ["palm", "palmen", "palmer", "växt", "växten"], kort: "en palm", plats: "vaning", fast: true,
      beskrivning: "En palm i en mässingskruka. Den har aldrig sett en strand, men den har sett fler cocktailpartyn än de flesta palmer." },
    soffa: { namn: ["soffa", "soffan", "vit soffa", "kuddar"], kort: "en vit soffa", plats: "vaning", fast: true,
      beskrivning: "En vit soffa, så vit att den nästan lyser. Du sätter dig inte. Du har sett hur dina byxor ser ut efter en regnig dag." },
    // Chinatown
    dragonskylt: { namn: ["neonskylt", "neonskylten", "skylt", "skylten", "golden dragon", "neon"], kort: "en neonskylt", plats: "china", fast: true, lasbar: true,
      beskrivning: "GOLDEN DRAGON, NUDLAR & DUMPLINGS, ÖPPET TILL SENT. Neonet surrar som en geting i en burk. D:et i DRAGON blinkar lite, men det gör de flesta av oss vid den här tiden." },
    lyktor: { namn: ["lykta", "lyktan", "lyktor", "lyktorna", "röda lyktor", "lina", "linan"], kort: "röda lyktor", plats: "china", fast: true,
      beskrivning: "Röda papperslyktor på en lina tvärs över gatan. De gungar i vinden som om de lyssnade på en melodi som bara de kan höra." },
    stand: { namn: ["stånd", "ståndet", "bläckfisk", "bläckfisken", "försäljare", "försäljaren", "gumma", "gumman", "tant", "tanten", "kvinna", "kvinnan"], kort: "ett stånd", plats: "china", fast: true, person: true,
      beskrivning: "Ett stånd med torkad bläckfisk som hänger i rader, som tvätt från ett mycket underligt hushåll. Bakom disken sitter en liten gumma som har sett allt och tänker inte berätta något av det gratis." },
    folkmassa: { namn: ["folk", "folket", "folkmassa", "folkmassan", "paraply", "paraplyer", "paraplyerna", "människor"], kort: "folk med paraplyer", plats: "china", fast: true,
      beskrivning: "Folk med paraplyer skyndar förbi i regnet. Ingen av dem tittar på dig. I Chinatown betyder det att alla redan har sett dig." },
    cykel: { namn: ["cykel", "cykeln", "cyklar", "cyklarna"], kort: "en cykel", plats: "china", fast: true,
      beskrivning: "En budcykel med en korg full av hämtmat. Den är fastlåst med en kedja som är dyrare än cykeln. Det säger något om kvarteret." },
    // Golden Dragon
    papperslyktor: { namn: ["papperslykta", "papperslyktan", "papperslyktor", "papperslyktorna", "lykta", "lyktan", "lyktor", "lyktorna", "tak", "taket"], kort: "papperslyktor", plats: "restaurang", fast: true,
      beskrivning: "Runda papperslyktor med tecken som betyder lycka, enligt Benny. Enligt hans kusin betyder de \"kontant betalning\"." },
    bas: { namn: ["bås", "båset", "båsen", "bänk", "bänken", "bord", "bordet", "ätpinnar", "pinnar"], kort: "röda bås", plats: "restaurang", fast: true,
      beskrivning: "Röda bås med bord av laminat. Någon har ristat in \"F.M. WAS HERE\" i bordskanten. Fingers Malloy? Eller Frank från tvätteriet. Det är alltid Frank från tvätteriet." },
    disk: { namn: ["disk", "disken", "kassa", "kassan", "kassadisk", "kassadisken", "kassaapparat", "kassaapparaten"], kort: "en kassadisk", plats: "restaurang", fast: true,
      beskrivning: "Kassadisken. Kassaapparaten har en klocka som plingar varje gång den öppnas. Den plingar inte ofta." },
    katt: { namn: ["katt", "katten", "lyckokatt", "lyckokatten", "tass", "tassen"], kort: "en vinkande katt", plats: "restaurang", fast: true,
      beskrivning: "En porslinskatt som vinkar med ena tassen. Den har vinkat i tjugo år utan att någon vinkat tillbaka. Du vinkar lite. Det känns bättre för er båda." },
    // Pir 9
    fyr: { namn: ["fyr", "fyren", "ljus", "ljuset", "ljuskägla", "ljuskäglan"], kort: "en fyr", plats: "pir", fast: true,
      beskrivning: "Långt ute i dimman sveper en fyr runt, runt. Den letar efter något den också. Den har hållit på längre än du, och har inte hittat det heller." },
    fartyg: { namn: ["fartyg", "fartyget", "båt", "båten", "skepp", "skeppet", "lastfartyg"], kort: "ett fartyg", plats: "pir", fast: true,
      beskrivning: "Ett lastfartyg ligger förtöjt i dimman. På aktern står det HAPPY HARBOR. Ingen som jobbar på det ser glad ut." },
    vatten: { namn: ["vatten", "vattnet", "hav", "havet", "dimma", "dimman", "kaj", "kajen"], kort: "vattnet", plats: "pir", fast: true,
      beskrivning: "Hamnvattnet är svart och oljigt, och dimman ligger som en våt filt över det. Något flyter förbi. Du bestämmer dig för att det var en gammal stövel." },
    lagerskylt: { namn: ["skylt", "skylten", "lagerskylt", "lagerskylten", "lager 13", "13", "etta", "ettan", "trea", "trean"], kort: "en skylt", plats: "pir", fast: true, lasbar: true,
      beskrivning: "LAGER 13, med en stor etta och en ännu större trea. Ingen vet varför trean är större. Kanske var ettan blygsam." },
    pirlador: { namn: ["trälåda", "trälådan", "lådor", "lådorna", "låda", "lådan", "pollare", "pollaren", "rep", "repet"], kort: "lådor", plats: "pir", fast: true,
      beskrivning: "Några trälådor och en pollare med ett rep som någon har knutit med en knut du inte kan namnet på. Det heter troligen \"jag hade bråttom\"." },
    // Lager 13
    lagerfonster: { namn: ["fönster", "fönstret", "galler", "gallret"], kort: "ett fönster", plats: "lager", fast: true,
      beskrivning: "Ett högt fönster med galler. Lite gatuljus silar in och lägger randiga skuggor på golvet, som i alla filmer du har sett om fängelser." },
    glodlampa: { namn: ["glödlampa", "glödlampan", "lampa", "lampan", "ljus", "ljuset", "damm", "dammet"], kort: "en glödlampa", plats: "lager", fast: true,
      beskrivning: "En ensam glödlampa hänger i en sladd över buren. Dammet svävar i ljuset som små tankar som inte vill landa." },
    // Perrongerna
    spar: { namn: ["spår", "spåret", "räls", "rälsen", "spårområde", "spårområdet", "kant", "kanten"], kort: "spåret", plats: "överallt", grupp: "station", fast: true,
      beskrivning: "Rälsen glänser i mörkret. Strömskenan surrar svagt och lovar att göra slut på alla dina problem. Du tar ett steg tillbaka från kanten." },
    glodlampor: { namn: ["glödlampa", "glödlampor", "glödlamporna", "lampa", "lampor", "lamporna", "ljus"], kort: "glödlampor", plats: "p_main", fast: true,
      beskrivning: "Nakna glödlampor i taket. Varannan fungerar. Det är tunnelbanebolagets idé om stämningsbelysning." },
    jordnotter: { namn: ["jordnöt", "jordnötter", "jordnötsskal", "skal", "skalen", "tidning", "tidningen", "golv", "golvet"], kort: "jordnötsskal", plats: "p_main", fast: true,
      beskrivning: "Jordnötsskal och en blöt tidning på golvet. Någon har haft en bättre middag än du här nere, och det säger en del." },
    sovare: { namn: ["man", "mannen", "sovande", "sovare", "gubbe", "gubben", "bänk", "bänken", "luffare", "luffaren"], kort: "en sovande man", plats: "p_main", fast: true, person: true,
      beskrivning: "En man sover på bänken med en tidning över ansiktet. Han snarkar i takt med tågen. Han har troligen den lugnaste natten av alla i Grand Harbor." },
    armaturer: { namn: ["armatur", "armaturer", "armaturerna", "lampa", "lampor", "lamporna", "vägglampa", "vägglampor"], kort: "vägglampor", plats: "p_park", fast: true,
      beskrivning: "Vägglampor i mässing och opalglas. På de andra stationerna har lamporna galler. Här har de lampskärmar." },
    bankar: { namn: ["bänk", "bänken", "bänkar", "bänkarna"], kort: "två bänkar", plats: "p_park", fast: true,
      beskrivning: "Två avtorkade bänkar. Det sitter en liten skylt på den ena: SKÄNKT AV FAMILJEN PETTIGREW. Det förklarar en del." },
    ormbunke: { namn: ["ormbunke", "ormbunken", "växt", "växten", "kruka", "krukan"], kort: "en ormbunke", plats: "p_park", fast: true,
      beskrivning: "En ormbunke i en mässingskruka, under jorden, utan dagsljus. Den lever ändå. Du känner en viss släktskap." },
    fiolspelare: { namn: ["fiolspelare", "fiolspelaren", "musikant", "musikanten", "gatumusikant", "gatumusikanten", "fiol", "fiolen", "man", "mannen", "bach"], kort: "en fiolspelare", plats: "p_park", fast: true, person: true,
      beskrivning: "En fiolspelare i frack spelar Bach med slutna ögon. Han ser ut att ha kommit hit direkt från en konsertsal och gått fel i trappan." },
    fiollada: { namn: ["fiollåda", "fiollådan", "låda", "lådan", "mynt", "mynten", "fodral", "fodralet"], kort: "en fiollåda", plats: "p_park", fast: true,
      beskrivning: "Fiollådan ligger öppen på golvet. Där ligger mynt, en biljett till operan och ett visitkort från en bank. Folk på Park Avenue ger på sitt eget sätt." },
    vagn: { namn: ["vagn", "vagnen", "tågvagn", "tågvagnen", "vagnar", "dörr", "dörrarna"], kort: "en tågvagn", plats: "p_china", fast: true,
      beskrivning: "En tågvagn står inne med öppna dörrar och väntar på ingen särskild. Konduktören läser en tidning. Han ser ut att ha väntat sedan 1931." },
    perronglyktor: { namn: ["lykta", "lyktan", "lyktor", "lyktorna", "röda lyktor"], kort: "röda lyktor", plats: "p_china", fast: true,
      beskrivning: "Röda lyktor hänger även här nere. Någon har tyckt att tunnelbanan också förtjänar lite tur. Den behöver det." },
    resenarer: { namn: ["resenär", "resenärer", "resenärerna", "folk", "folket", "matkassar", "kassar", "kasse"], kort: "resenärer", plats: "p_china", fast: true,
      beskrivning: "Folk med matkassar som det sticker ut purjolök och fiskstjärtar ur. En gammal man bär en levande anka under armen. Ankan ser ut att veta något." },
    lysror: { namn: ["lysrör", "lysröret", "lysrören", "lampa", "lampor", "ljus", "ljuset"], kort: "lysrör", plats: "p_pir", fast: true,
      beskrivning: "Lysrören blinkar kort, kort, långt. Du har lärt dig lite morse en gång. Det står antingen \"SOS\" eller \"SOPOR\". Ingetdera är uppmuntrande." },
    stoppbock: { namn: ["stoppbock", "stoppbocken", "tunnel", "tunneln", "tunnelmynning", "slut", "linjen"], kort: "en stoppbock", plats: "p_pir", fast: true,
      beskrivning: "Här tar linjen slut, mot en randig stoppbock. Bortom den är det bara mörker och droppande vatten. Som slutet på de flesta av dina fall." },
    pol: { namn: ["pöl", "pölen", "vattenpöl", "vattenpölen", "dropp", "droppet", "spricka", "sprickan"], kort: "en pöl", plats: "p_pir", fast: true,
      beskrivning: "En pöl under en spricka i taket. Det droppar ner i den med jämna mellanrum. Du ser din spegelbild i den. Den ser trött ut. Den har rätt." },
  },

  // ------------------------------------------------------------------ handlingar som flera regler använder
  handlingar: {
    // Detektiven hittar dollarn i rocken (första gången)
    rockfynd: [
      { om: { inteFlagga: "dollar" }, flytta: "dollar", till: "spelare", text: "Du rotar i fickorna och hittar en skrynklig dollarsedel. Din förmögenhet har just ökat med oändligt många procent." },
      { poang: "dollar" },
      { satt: "dollar" },
    ],
    // Benny känner igen fotot eller menyn och ger adressen
    adress: [
      { om: { flagga: "adress" }, text: "\"Jag har redan sagt det\", säger Benny. \"Lager 13 på Pir 9. Tolv räkor. Och vatten.\"" },
      { om: { inteFlagga: "adress", objekt: "brev" }, text: "Benny tittar på menyn. \"Det där är vår meny. Och sötsur sås på nummer 47, det är friterade räkor. Bara en kund beställer så mycket nummer 47 just nu.\"" },
      { om: { inteFlagga: "adress", inte: { objekt: "brev" } }, text: "Benny tittar på fotot och skrattar till. \"Den där fula lilla potatisen! Jag såg honom i går. Han satt i en låda medan en kille hämtade mat.\"" },
      { om: { inteFlagga: "adress" }, text: "\"En gorilla som heter Bruno har beställt tolv portioner friterade räkor till Lager 13 på Pir 9 tre dagar i rad. Och en skål vatten. Vem beställer vatten med hämtmat? Någon med en hund, så klart.\"" },
      { om: { inteFlagga: "adress" }, poang: "adress" },
      { satt: "adress" },
    ],
    lyckokaka: [
      { flytta: "lyckokaka", ljud: "krack" },
      "Du bryter lyckokakan och vecklar ut lappen. Det står: \"DEN SOM FÖLJER RÄKORNA HITTAR SANNINGEN.\" På baksidan: \"Dina lyckotal: 9 och 13.\"",
      { sys: "Du äter upp kakan. Den smakar papp och förhoppning." },
    ],
    vinst: [
      { satt: "vunnit", ljud: "hiss" },
      { ljud: "fanfar", fordrojning: 1.6, ljudFordrojning: -1 },
      { flytta: "mops", till: "vaning", flyttaSpelare: "vaning" },
      "Lord Waffles hoppar ur dina armar och springer, så fort hans korta ben tillåter, rakt in i fru Pettigrews famn. Hon skriker av lycka. Mopsen slickar hennes pärlor.",
      "\"Ni är ett geni! Ett mirakel! En hjälte!\" Hon skriver en check med så många nollor att de inte får plats på raden och fortsätter ut på bordsduken.",
      "Samma kväll grips Bruno på en korvkiosk i hamnen med senap på hakan. Han erkänner allt efter tio minuter och ber om mer senap. Hans chef, den ökända hundtjuven Fingers Malloy, grips två dagar senare på ett hundcafé.",
      "På lördagen vinner Lord Waffles hundutställningen för fjärde året i rad. Du står längst bak i publiken med hatten nerdragen. Ingen vet vem du är. Det passar dig bra.",
      { poang: "vunnit" },
      { stampel: "Fallet avslutat" },
      { slutsummering: true },
      { sys: "Välj Börja om i menyn för att spela igen." },
      { spelSlut: true },
    ],
  },

  // ------------------------------------------------------------------ regler (pussel och särskilda svar)
  // Varje regel: verb, eventuellt objekt/mottagare, villkor (om) och handlingar (gor).
  // Första regeln som passar används i stället för motorns standardbeteende.
  // nar: "efter" körs efter standardbeteendet i stället.
  regler: [
    // Spärren till tunnelbanan (används av perrongerna via passage: "spärren", se längst ner)

    // Kontoret
    { verb: "undersök", objekt: "rock", nar: "efter", gor: [{ kor: "rockfynd" }] },
    { verb: "undersök", objekt: "skrivbord", nar: "efter", om: { stangd: "lada" }, gor: [{ sys: "Lådan är stängd." }] },
    { verb: "sök", objekt: "rock", om: { flagga: "dollar" }, gor: ["Fickorna är tomma nu, bortsett från ludd."] },
    { verb: "sök", objekt: "rock", gor: [{ kor: "rockfynd" }] },
    { verb: "sök", objekt: "skrivbord", gor: [{ utfor: "sök lådan" }] },
    { verb: "öppna", objekt: "skrivbord", gor: [{ utfor: "öppna lådan" }] },
    { verb: "ta på", objekt: "rock", gor: [{ flytta: "rock", till: "spelare" }, "Du drar på dig trenchcoaten och slår upp kragen. Nu ser du ut som en riktig privatdetektiv. Eller som en man som väntar på en buss.", { kor: "rockfynd" }] },
    { verb: "inventarie", nar: "efter", om: { inventarieTom: true, har: "rock" }, gor: [{ sys: "(Din trenchcoat hänger fortfarande på hängaren.)" }] },

    // Stämningssaker i kontoret
    { verb: "ta", objekt: "lampa", gor: ["Lampan är det enda i kontoret som är avbetalt. Den får stå kvar."] },
    { verb: "ta", objekt: "flaska", gor: ["Du lyfter flaskan mot ljuset och hoppas på ett mirakel. Det kommer inget. Du ställer tillbaka den."] },
    { verb: "ta", objekt: "rakningar", gor: ["Du lyfter upp räkningarna. De känns tyngre än papper borde göra. Du lägger tillbaka dem, med den argaste underst."] },
    { verb: "ta", objekt: "hatt", gor: ["Du låter hatten hänga kvar. Den har haft en lång vecka, den också."] },
    { verb: "ta", objekt: "askkopp", gor: ["Du tänker tömma askkoppen. Sedan tänker du om. Den är nästan det enda här som fungerar som det ska."] },
    { verb: "ta", objekt: "stol", gor: ["Du sätter dig en stund i stolen och funderar. Den gnisslar instämmande. Sedan reser du dig. Fallet löser inte sig självt."] },
    { verb: "ta", objekt: "kalender", gor: ["Kalendern får hänga kvar. Om du tar ner den blir det inte fredag senare för det."] },
    { verb: "ta", objekt: "diplom", gor: ["Diplomet får hänga kvar. Det är det enda beviset på att du har gått en kurs i något."] },
    { verb: "ät", objekt: "askkopp", gor: ["Nej. Inte ens på en tisdag."] },

    // Stämningssaker på gator, i lokaler och på perronger
    { verb: "ta", objekt: "bil", gor: ["Du är privatdetektiv, inte biltjuv. Dessutom har du inget körkort sedan händelsen med fruktvagnen."] },
    { verb: ["gå", "öppna"], objekt: "diner", gor: ["Du har redan skuld hos Rosie. Hon har skrivit upp ditt namn på en tavla bakom disken. Det står i rött."] },
    { verb: "gå", objekt: "kontorsfonster", gor: [{ utfor: "in" }] },
    { verb: "ta", objekt: "trad", gor: ["Du böjer dig mot krukan. Portiern harklar sig. Du rätar på dig och låtsas att du knöt skorna."] },
    { verb: "prata", objekt: "duva", gor: ["Duvan kuttrar något som låter som \"avgå\". Hon tittar på din rock och går därifrån."] },
    { verb: ["ta", "klappa"], objekt: "duva", gor: ["Duvan flaxar upp på portiern och sätter sig på hans mössa. Han rör inte en min. Det har hänt förut."] },
    { verb: ["ge", "visa"], mottagare: "duva", gor: ["Duvan tittar på {objekt}, sedan på dig, och vänder dig ryggen. Den har sett bättre erbjudanden på Park Avenue."] },
    { verb: "ta", objekt: "korg", gor: ["Korgen ska stå kvar och vänta på sin ägare. Det är det enda den kan göra. Du förstår precis hur den känner sig."] },
    { verb: "ta", objekt: "krona", gor: ["Du når inte upp. Och om du gjorde det skulle du hänga i en kristallkrona inför fru Pettigrew, vilket inte är professionellt."] },
    { verb: "ta", objekt: "soffa", gor: ["Du tänker sätta dig. Sedan tittar du ner på din regnrock. Du står kvar."] },
    { verb: "ta", objekt: "palm", gor: ["Palmen är tung och dessutom inte din. Två goda skäl, och du behöver egentligen bara ett."] },
    { verb: "ta", objekt: "matta", gor: ["Mattan väger mer än du och är värd mer än hela ditt kvarter. Du låter den ligga."] },
    { verb: "prata", objekt: "stand", gor: ["Gumman säger något på kantonesiska som får en förbipasserande att skratta högt. Sedan pekar hon på bläckfisken. Du förstår att det är ett erbjudande."] },
    { verb: ["ta", "ät", "köp"], objekt: "stand", gor: ["En torkad bläckfisk kostar en dollar, och smakar som en sko som har varit till sjöss. Du avstår."] },
    { verb: "visa", objekt: "foto", mottagare: "stand", gor: ["Gumman tittar på fotot och pekar bestämt mot Golden Dragon. \"Fråga Benny\", säger hon. \"Benny vet allt. Benny pratar för mycket.\""] },
    { verb: ["ge", "visa"], mottagare: "stand", gor: ["Gumman skakar på huvudet och pekar på bläckfisken. Hon gör affärer, inte byteshandel."] },
    { verb: "ta", objekt: "cykel", gor: ["Cykeln sitter fast med en kedja som är tjockare än din arm. Du hade ändå inte kommit långt i det här regnet."] },
    { verb: "ta", objekt: "lyktor", gor: ["Lyktorna hänger för högt, och dessutom vore det otur. Det är hela poängen med dem."] },
    { verb: ["klappa", "prata"], objekt: "katt", gor: ["Du vinkar tillbaka till katten. Benny tittar på dig genom luckan. Du slutar vinka."] },
    { verb: "ta", objekt: "katt", gor: ["\"Rör inte katten\", säger Benny utan att titta upp. \"Den har jobbat här längre än jag.\""] },
    { verb: "ta", objekt: "akvarium", gor: ["Karpen tittar på dig med ett uttryck som säger: försök bara."] },
    { verb: "ta", objekt: "vatten", gor: ["Du doppar fingrarna i hamnvattnet. Det är kallt och oljigt och luktar diesel. Du torkar av handen på rocken. Rocken har varit med om värre."] },
    { verb: "ta", objekt: "pirlador", gor: ["Lådorna är spikade igen och väger som ett dåligt samvete. Du låter dem stå."] },
    { verb: "prata", objekt: "sovare", gor: ["Mannen muttrar \"inte nu, mamma\" och vänder sig om under tidningen."] },
    { verb: ["ta", "klappa"], objekt: "sovare", gor: ["Du låter honom sova. Han är den ende i stan som inte har några problem just nu."] },
    { verb: ["ge", "visa"], mottagare: "sovare", gor: ["Mannen snarkar. Det är ett nej."] },
    { verb: "prata", objekt: "fiolspelare", gor: ["Fiolspelaren öppnar ena ögat och spelar lite starkare. Du förstår att samtalet är över."] },
    { verb: "ta", objekt: "fiolspelare", gor: ["Han är mitt i en fuga. Man avbryter inte en man mitt i en fuga."] },
    { verb: "ge", objekt: "dollar", mottagare: "fiolspelare", gor: ["Du tänker lägga dollarn i fiollådan. Sedan tänker du på varmkorv. Bach får klara sig utan dig ikväll."] },
    { verb: ["ge", "visa"], mottagare: "fiolspelare", gor: ["Fiolspelaren nickar artigt utan att sluta spela. Han tar inte emot något som inte klingar."] },
    { verb: "ta", objekt: "fiollada", gor: ["Du är privatdetektiv, inte ficktjuv. Dessutom ligger det mest operabiljetter där, och du hatar opera."] },
    { verb: "ta", objekt: "spar", gor: ["Du böjer dig inte ner mot strömskenan. Du har ett fall att lösa och en hyra att betala, i den ordningen."] },
    { verb: "ta", objekt: "jordnotter", gor: ["Du är hungrig, men det finns gränser. Den här ligger precis på andra sidan om jordnötsskal från golvet."] },
    { verb: ["gå", "ta"], objekt: "vagn", gor: ["Vagnen står inne, men tåget åker inte förrän du bestämmer vart. Tryck på linjekartan för att välja station."] },
    { verb: "ta", objekt: "resenarer", gor: ["Du knuffar ingen. Ankan har redan valt dig som fiende, och du vill inte ge den fler skäl."] },
    { verb: "ta", objekt: "pol", gor: ["Du doppar inte handen i pölen. Det har gått råttor genom den. Du har sett dem."] },

    // Telefonsvararen: meddelandet skrivs ut i takt med rösten
    { verb: "lyssna", om: { har: "svarare", nagon: [{ fras: false }, { objekt: "svarare" }, { ord: ["telefon*", "svarare*", "meddelande*", "knapp*"] }] }, gor: [
      "Du trycker på knappen. Bandet spolar tillbaka med ett ljud som en dammsugare som ångrar sig. Sedan en darrande kvinnoröst:",
      { replik: "svarare", sedan: [{ sys: "Klick. Pip. Vad som helst. Det är din favoritsumma." }, { poang: "svarare" }] },
      { satt: "svarare" },
    ] },
    { verb: "lyssna", om: { plats: "p_park", fras: true }, gor: ["Fiolspelaren spelar Bach. Du blir rörd. Det går över."] },

    // Sals korvkiosk
    { verb: "köp", om: { inteHar: "kiosk" }, gor: ["Det finns inget att köpa här. Du skulle ändå inte ha råd."] },
    { verb: "köp", om: { fras: true, inteOrd: ["korv*", "hotdog*", "mat*"] }, gor: ["\"Jag säljer korv\", säger Sal. \"Bara korv. Har alltid sålt korv. Kommer att dö som korvförsäljare.\""] },
    { verb: "köp", om: { bar: "korv" }, gor: ["Du har redan en korv. Sal tittar misstänksamt på dig, som om du samlade på dem."] },
    { verb: "köp", om: { inteBar: "dollar" }, gor: ["\"En dollar\", säger Sal och håller fram handen. Du klappar på fickorna. Han drar tillbaka handen."] },
    { verb: "köp", gor: [
      { flytta: "dollar" }, { flytta: "korv", till: "spelare" }, { satt: "korv", ljud: "kassa", ljudFordrojning: 1 },
      "Du ger Sal dollarsedeln. Han lägger en korv i ett bröd, kväver den i senap och räcker över den. \"Smaklig måltid, deckare.\"",
      { poang: "korv" },
    ] },

    // Ge
    { verb: "ge", objekt: "korv", mottagare: "bruno", gor: [
      { flytta: ["korv", "bruno"] }, { satt: "bruno", ljud: "gulp", fordrojning: 0.3, ljudFordrojning: 1.2 },
      "Du håller fram korven. Brunos näsa vrids mot den som en kompassnål. \"Är den till Bruno?\" Du nickar. Han sväljer den hel, papperet också.",
      "\"Den behövde mer senap\", säger han tankfullt. \"Bruno går och hämtar senap. Ingen går in medan Bruno är borta, okej?\" Han lunkar bort i dimman utan att vänta på svar.",
      { poang: "bruno" },
    ] },
    { verb: "ge", mottagare: "bruno", gor: ["Bruno tittar på {objekt}. \"Kan man äta det?\" Det kan man inte. Han tappar intresset."] },
    { verb: "ge", objekt: "kex", mottagare: "mops", om: { flagga: "mopsVan" }, gor: ["Lord Waffles äter ett kex till. Han tackar inte."] },
    { verb: "ge", objekt: "kex", mottagare: "mops", gor: [
      { satt: "mopsVan", ljud: "prassel" }, { ljud: "skall", fordrojning: 0.8, ljudFordrojning: 1.4 },
      "Du prasslar med kexpåsen. Lord Waffles öron reser sig. Du lägger ett kex på golvet framför buren. Han tittar på kexet, sedan på dig, sedan på kexet igen. Kexet vinner.",
      "Han kommer ut ur buren, äter upp kexet och sätter sig sedan på din fot med ett belåtet grymtande. Ni är vänner nu. Han kan bäras.",
      { poang: "mops" },
    ] },
    { verb: "ge", objekt: "korv", mottagare: "mops", gor: ["Lord Waffles nosar på korven och vänder bort huvudet med avsmak. Han äter bara kex från Paris."] },
    { verb: "ge", objekt: "dollar", mottagare: "kiosk", gor: [{ utfor: "köp korv" }] },   // att ge Sal dollarn är att köpa en korv
    { verb: "ge", mottagare: "kiosk", gor: ["Sal skakar på huvudet. \"Jag tar bara kontanter, kompis.\""] },
    { verb: "ge", objekt: "mops", mottagare: "pettigrew", gor: [{ kor: "vinst" }] },
    { verb: "ge", objekt: ["foto", "brev"], mottagare: "benny", gor: [{ kor: "adress" }] },
    { verb: "ge", mottagare: "benny", gor: ["Benny skakar på huvudet. \"Behåll den. Jag har nog skräp.\""] },
    { verb: "ge", mottagare: "portier", gor: ["Portiern tittar på {objekt} som om det vore något katten släpat in. Han tar inte emot det."] },
    { verb: "ge", mottagare: "pettigrew", gor: ["\"Nej, nej, behåll den, ni behöver den mer än jag! Hitta bara min lilla Waffles!\""] },

    // Visa
    { verb: "visa", objekt: ["foto", "brev", "mops"], mottagare: "benny", gor: [{ kor: "adress" }] },
    { verb: "visa", mottagare: "benny", gor: ["Benny rycker på axlarna. \"Snyggt. Ska du beställa något eller?\""] },
    { verb: "visa", objekt: "foto", mottagare: "kiosk", gor: ["Sal kisar mot fotot. \"Snygg korv\", säger han. \"Ah, en hund. Nej. Har inte sett honom. Alla hundar ser ut som korvar för mig.\""] },
    { verb: "visa", mottagare: "portier", gor: ["Portiern tittar på det utan att röra en min. Det är hans enda min."] },
    { verb: "visa", mottagare: "bruno", gor: ["Bruno tittar länge på {objekt}. \"Bruno har inte sett något\", säger han. \"Bruno ser aldrig något. Det är därför Bruno får jobb.\""] },
    { verb: "visa", mottagare: "pettigrew", gor: ["\"Ja, ja, det vet jag! Hitta honom bara!\""] },

    // Prata
    { verb: "prata", objekt: "kiosk", om: { flagga: "korv" }, gor: ["\"Smakade korven?\" frågar Sal. Han väntar inte på svar."] },
    { verb: "prata", objekt: "kiosk", gor: ["\"Varmkorv, en dollar\", säger Sal. \"Vill du ha en får du betala för den. Det är så handel fungerar.\""] },
    { verb: "prata", objekt: "portier", om: { flagga: "svarare" }, gor: ["\"Fru Pettigrew väntar er, sir. Hissen är till höger. Torka av skorna.\""] },
    { verb: "prata", objekt: "portier", gor: ["\"Endast boende och inbjudna gäster, sir. Ni är varken eller. Dessutom droppar ni.\""] },
    { verb: "prata", objekt: "pettigrew", om: { flagga: "vunnit" }, gor: ["\"Tack, tack, tusen gånger tack!\""] },
    { verb: "prata", objekt: "pettigrew", gor: ["\"Brevet luktade friterade räkor\", snyftar fru Pettigrew. \"Tänk om de matar honom med räkor! Han är van vid kaviar.\""] },
    { verb: "prata", objekt: "benny", om: { flagga: "adress" }, gor: ["\"Lager 13, Pir 9. Ta en lyckokaka på vägen ut. De är bättre än mina råd.\""] },
    { verb: "prata", objekt: "benny", gor: ["\"Jag vet allt om alla i kvarteret\", säger Benny och vänder en dumpling i luften. \"Men jag behöver något att gå på. Visa mig vad du har.\""] },
    { verb: "prata", objekt: "bruno", gor: [{ ljud: "mage", fordrojning: 0.8 }, "\"Bruno pratar inte med snutar\", säger Bruno. Du säger att du inte är snut. \"Bruno pratar inte med icke-snutar heller.\" Hans mage kurrar. \"Bruno är hungrig, men Bruno får inte gå.\""] },
    { verb: "prata", objekt: "mops", om: { flagga: "mopsVan" }, gor: [{ ljud: "skall" }, "Lord Waffles fnyser vänligt."] },
    { verb: "prata", objekt: "mops", gor: [{ ljud: "morr" }, "Lord Waffles morrar. Du tolkar det som \"inte utan kex\"."] },

    // Mopsen
    { verb: "ta", objekt: "mops", om: { inteFlagga: "mopsVan" }, gor: ["Du sträcker in handen i buren. Lord Waffles visar tänderna. Alla tre. Du drar tillbaka handen medan du fortfarande har fem fingrar.", { ljud: "morr" }] },
    { verb: "ta", objekt: "mops", gor: [{ ljud: "skall" }, "Du lyfter upp Lord Waffles. Han är förvånansvärt tung för sin storlek, ungefär som ett bowlingklot med åsikter.", { flytta: "mops", till: "spelare" }] },
    { verb: "släpp", objekt: "mops", gor: ["Lord Waffles vägrar att sättas ner. Han har betalat för första klass."] },
    { verb: "klappa", objekt: "mops", om: { flagga: "mopsVan" }, gor: ["Lord Waffles låter sig klappas med kunglig nedlåtenhet."] },
    { verb: "klappa", objekt: "mops", gor: ["Lord Waffles hugger efter dina fingrar. Han missar, men bara för att han inte ser så bra."] },
    { verb: "öppna", objekt: "mops", gor: ["Burens dörr är inte låst. Problemet är vad som sitter i den."] },

    // Lyckokakan
    { verb: "ta", objekt: "lyckokaka", gor: ["Du tar en lyckokaka ur skålen. Benny tittar upp. \"Gratis\", säger han. \"Fram till att du läser den.\"", { flytta: "lyckokaka", till: "spelare" }] },
    { verb: "bryt", om: { inteInom: "lyckokaka" }, gor: ["Du har ingen lyckokaka."] },
    { verb: "bryt", gor: [{ kor: "lyckokaka" }] },
    { verb: ["läs", "öppna", "ät"], objekt: "lyckokaka", gor: [{ kor: "lyckokaka" }] },

    // Använd X på Y (i klickläget, men det går också att skriva)
    { verb: "använd", objekt: "dyrk", mottagare: "dorr", gor: [{ utfor: "dyrka upp dörren" }] },
    { verb: "använd", objekt: "kex", mottagare: "mops", gor: [{ utfor: "ge kex till mopsen" }] },
    { verb: "använd", objekt: "korv", mottagare: "bruno", gor: [{ utfor: "ge korv till bruno" }] },
    { verb: "använd", objekt: "dollar", mottagare: "kiosk", gor: [{ utfor: "köp korv" }] },
    { verb: "använd", objekt: "kort", mottagare: "karta", gor: ["Kortet ska användas vid spärren, inte på kartan. Det sköter sig själv när du går ner till perrongen."] },
    { verb: "använd", objekt: "dyrk", gor: ["Dyrken passar bara i lås. Riktiga lås, inte metaforiska."] },

    // Lagerdörren
    { verb: "dyrka", om: { intePlats: "pir" }, gor: ["Det finns inget här att dyrka upp."] },
    { verb: "dyrka", om: { inteBar: "dyrk" }, gor: ["Du saknar verktyg. Du har inte ens en hårnål, och du har inget hår att fästa den i."] },
    { verb: "dyrka", om: { inteFlagga: "bruno" }, gor: ["Du böjer dig mot låset. En hand stor som en stekpanna landar på din axel. \"Nej\", säger Bruno. Det är ett ord han är bra på."] },
    { verb: "dyrka", om: { flagga: "dorr" }, gor: ["Den är redan öppen."] },
    { verb: "dyrka", gor: [
      { satt: "dorr", ljud: "dyrk", ljudFordrojning: 2.8 },
      "Du sticker in dyrken i hänglåset, lyssnar efter klick som en kassaskåpssprängare i en gammal film, och ... klick. Hänglåset ger upp. Dörren glider upp på gnisslande gångjärn.",
      { poang: "dorr" },
    ] },
    { verb: "öppna", objekt: "dorr", om: { flagga: "dorr" }, gor: ["Den är redan öppen."] },
    { verb: "öppna", objekt: "dorr", gor: ["Dörren är låst med ett hänglås. Med rätt verktyg skulle det gå att dyrka upp."] },
    { verb: "lås", gor: ["Du har inget att låsa med."] },

    // Övrigt
    { verb: "öppna", objekt: "kex", gor: ["Du öppnar påsen och luktar. Leverbiff och vanilj. Det är faktiskt inte så dumt. Du stänger påsen innan du gör något du ångrar."] },
    { verb: "ät", objekt: "korv", gor: ["Du höjer korven mot munnen. Sedan sänker du den. Du har en känsla av att den kommer att göra större nytta någon annanstans. Och dessutom är senapen alldeles för gul."] },
    { verb: "ät", objekt: "kex", gor: ["Du är desperat, men inte så desperat. Inte än."] },
    { verb: "slå", gor: ["Våld är den sista utvägen för en privatdetektiv. Det är dessutom den första utvägen för Bruno, och han är större."] },
    { verb: "sov", gor: ["Du kan sova när du är död, eller när fallet är löst. Helst i den ordningen."] },
    { verb: "svär", gor: ["Du svär en ramsa som skulle få en hamnarbetare att rodna. Det hjälper inte, men du mår lite bättre."] },
    { verb: "hoppa", gor: ["Du hoppar. Grand Harbor är inte imponerat."] },
    { verb: "tänk", gor: [{ ledtrad: true }] },
    { verb: "ring", gor: ["Din telefon kan bara ta emot samtal. Telefonbolaget och du har en överenskommelse."] },
    { verb: "taxi", gor: [{ ejDrag: true }, "Med din ekonomi? Taxichaufförerna i Grand Harbor tar betalt bara för att titta på dig. Ta tunnelbanan."] },
  ],

  // Gemensamma passageregler som flera rum kan använda (rum.passage: "namn")
  passager: {
    // Spärren vid tunnelbanan: kortet behövs när man kommer från gatan
    spärren: [
      { om: { inteFranGrupp: "station", inteBar: "kort" }, stopp: true, gor: ["Du går ner för trappan, men spärren säger KLONK och vägrar släppa in dig. Utan tunnelbanekort kommer du ingenstans. Det är en metafor för hela ditt liv.", { ljud: "klonk" }] },
      { om: { inteFranGrupp: "station" }, gor: ["Du blippar tunnelbanekortet och spärren släpper motvilligt in dig.", { ljud: "blipp" }] },
    ],
  },

  // ------------------------------------------------------------------ poäng, rang och ledtrådar
  poang: {
    svarare: [5, "lyssnat på telefonsvararen"],
    dollar:  [5, "hittat en dollar i rocken"],
    kort:    [5, "hittat tunnelbanekortet"],
    korv:    [5, "köpt en varmkorv"],
    klient:  [10, "träffat fru Pettigrew"],
    adress:  [15, "fått adressen av Benny"],
    bruno:   [15, "blivit av med Bruno"],
    dorr:    [10, "dyrkat upp lagerdörren"],
    mops:    [15, "vunnit Lord Waffles förtroende"],
    vunnit:  [15, "lämnat tillbaka Lord Waffles"],
  },
  rangar: [[100, "Mästerdetektiv"], [70, "Skarpsynt spårhund"], [40, "Lovande nos"], [15, "Glasögonlös amatör"], [0, "Kaffeautomat i trenchcoat"]],
  ledtradar: [
    { om: { inteFlagga: "svarare" }, text: "Telefonsvararen på skrivbordet blinkar. Kanske borde du lyssna på den?" },
    { om: { inteBar: "kort", objektPa: ["kort", "lada"] }, text: "Utan tunnelbanekort kommer du ingenstans. Var brukar man lägga saker man inte vill hitta? I en skrivbordslåda." },
    { om: { inteFlagga: "dollar" }, text: "En detektiv utan pengar är bara en man i rock. Undersök din rock." },
    { om: { inteFlagga: "klient" }, text: "Fru Pettigrew bor på Park Avenue. Gå ner i tunnelbanan och tryck på linjekartan." },
    { om: { inteFlagga: "adress" }, text: "Läs lösenbrevet noga. Vems meny är det skrivet på? Visa sedan det du har för någon som kan känna igen det." },
    { om: { inteFlagga: ["korv", "bruno"] }, text: "Bruno på Pir 9 är hungrig, och Sal på Main Street säljer korv för en dollar." },
    { om: { inteFlagga: "bruno" }, text: "Ta med korven till Pir 9 och ge den till Bruno." },
    { om: { inteFlagga: "dorr", bar: "dyrk" }, text: "Du har en dyrk. Använd den på dörren." },
    { om: { inteFlagga: "dorr" }, text: "Dörren är låst. Låg det inte en dyrk i skrivbordslådan på kontoret?" },
    { om: { inteFlagga: "mopsVan" }, text: "Lord Waffles går ingenstans utan sina kex. Ge honom kexen." },
    { om: { inteBar: "mops", inteFlagga: "vunnit" }, text: "Ta mopsen." },
    { text: "Lämna tillbaka Lord Waffles till fru Pettigrew på Park Avenue." },
  ],

  // ------------------------------------------------------------------ ljud
  ljud: {
    musik: "jazz",
    // Effekternas volym (övriga spelas på 0.8)
    effektvolym: { poang: 0.45, fanfar: 0.9, svarare: 1, tunnelbana: 0.85, hiss: 0.6, prassel: 0.6 },
    forladda: ["poang", "fanfar", "svarare", "tunnelbana", "hiss", "prassel", "blipp", "klonk", "lada", "kassa", "gulp", "mage", "morr", "skall", "dyrk", "krack"],
    // Miljöljud per plats: slingor [fil, volym] och händelser [fil, sekunder emellan, volym, villkor]
    miljo: {
      kontor:     { slingor: [["regn_inne", 0.75]], handelser: [["tuta", 18, 0.18]] },
      mainst:     { slingor: [["regn_ute", 0.55]], handelser: [["tuta", 9, 0.45]] },
      parkave:    { slingor: [["duggregn", 0.5]], handelser: [["duva", 10, 0.45]] },
      vaning:     { slingor: [["vaning", 0.55]] },
      china:      { slingor: [["regn_ute", 0.4], ["sorl", 0.5]], handelser: [["cykelklocka", 11, 0.3]] },
      restaurang: { slingor: [["wok", 0.22], ["sorl", 0.45]], handelser: [["klirr", 7, 0.35]] },
      pir:        { slingor: [["hamn", 0.7]], handelser: [["mistlur", 15, 0.55], ["masar", 11, 0.3]] },
      lager:      { slingor: [["lager", 0.6]], handelser: [["knarr", 12, 0.45], ["morr", 7, 0.35, { objektPa: ["mops", "lager"], inteFlagga: "mopsVan" }]] },
      p_main:     { slingor: [["tunnel", 0.6]], handelser: [["tagforbi", 20, 0.55]] },
      p_park:     { slingor: [["tunnel", 0.4], ["fiol", 0.75]], dampaMusik: true },
      p_china:    { slingor: [["tunnel", 0.55], ["sorl", 0.35]], handelser: [["tagforbi", 22, 0.55]] },
      p_pir:      { slingor: [["tunnel", 0.5]], handelser: [["dropp", 2.8, 0.5], ["rattpip", 13, 0.35]] },
    },
  },
};
