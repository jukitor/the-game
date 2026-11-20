/* ==========================================================================
   MOPSEN SOM FÖRSVANN
   Ett äventyr för spelmotorn i motor/. Allt här är konfiguration: platser,
   föremål, personer, texter, pussel (regler), poäng, ledtrådar, bilder och ljud.
   Formatet beskrivs i README.md.
   ========================================================================== */
window.AVENTYR = {
  id: "mopsen-labb",
  titel: "Mopsen som försvann (labb)",
  klick: { pa: true },   // klickläget är på från början i labbet
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
    { text: "Skriv HJÄLP om du inte vet vad du ska göra, eller LEDTRÅD om du kör fast.", klass: "sys" },
    { text: "Spelet har musik och ljud. Det startar när du skriver eller trycker första gången. Skriv LJUD eller MUSIK för att stänga av.", klass: "sys" },

    { text: "Klickläget är på: tryck på saker i bilden, eller på det du bär, för att välja vad du vill göra. Än så länge går det bara att klicka i kontoret. Skriv KLICK för att stänga av.", klass: "sys" },
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
    spelSlut: "Fallet är redan löst. Skriv OMSTART för att spela igen, eller POÄNG för att se hur det gick.",
    tillbaka: "Du är tillbaka i fallet.",
    hjalp: [
      "Du styr detektiven genom att skriva vad du vill göra, med korta meningar på svenska. Oftast räcker ett verb, ibland följt av vad eller vem det gäller.",
      "TITTA (eller T): se dig omkring\nUNDERSÖK något (eller U): titta närmare på något\nTA, SLÄPP, ÖPPNA, LÄS: hantera saker\nPRATA MED, GE, VISA: ta kontakt med folk\nUPP, NER, IN, UT: gå åt ett håll\nÅK TILL: res med tunnelbanan från en perrong\nINVENTARIE (eller I): se vad du bär på",
      "Undersök det du ser och prata med dem du möter. Kör du fast kan du skriva LEDTRÅD.",
    ],
  },

  snabbknappar: [["Titta", "titta"], ["Ägodelar", "inventarie"], ["Upp", "upp"], ["Ner", "ner"], ["In", "in"], ["Ut", "ut"], ["Ledtråd", "ledtråd"], ["Klick", "klick"], ["Bild", "bild"], ["Ljud", "ljud"], ["Hjälp", "hjälp"]],

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
      vart: "Vart vill du åka? Skriv till exempel ÅK TILL CHINATOWN.",
      okand: "Linjen har bara fyra stationer: Main Street, Park Avenue, Chinatown och Pir 9.",
      redanHar: "Du är redan här. Tunnelbanan är snabb, men inte så snabb.",
      avstigning: "Du kliver av vid {station}.",
    },
  },

  // ------------------------------------------------------------------ platser
  rum: {
    kontor: {
      namn: "Ditt kontor", bild: "kontor", ord: ["kontor", "kontoret"],
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
      beskrivning: "Main Street, mitt i Grand Harbor. Regnet smattrar på markiserna och bilarna tutar på varandra som gamla grannar som aldrig blivit sams. Vid trottoarkanten står en korvkiosk med en ångande kastrull, och bredvid den ett tidningsställ. Ovanför dig ligger kontorshuset, och en trappa med en emaljerad skylt leder ner till tunnelbanan.",
      utgangar: { upp: "kontor", in: "kontor", ner: "p_main" },
    },
    p_main: {
      namn: "Perrongen vid Main Street", bild: "p_main", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      beskrivning: "Tunnelbaneperrongen under Main Street. Det luktar järn, regnrockar och gårdagens jordnötter. En linjekarta på väggen visar fyra stationer: MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp till gatan.",
      utgangar: { upp: "mainst", ut: "mainst" },
      passage: "spärren",
    },
    p_park: {
      namn: "Perrongen vid Park Avenue", bild: "p_park", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      beskrivning: "Den finaste perrongen i hela systemet. Någon har till och med torkat av bänkarna, och en gatumusikant spelar Bach på en fiol som är värd mer än din bil. Linjekartan visar MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp.",
      utgangar: { upp: "parkave", ut: "parkave" },
      passage: "spärren",
    },
    p_china: {
      namn: "Perrongen vid Chinatown", bild: "p_china", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      beskrivning: "Perrongen under Chinatown är fylld av folk med matkassar, och det doftar ingefära hela vägen ner hit. Linjekartan visar MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp.",
      utgangar: { upp: "china", ut: "china" },
      passage: "spärren",
    },
    p_pir: {
      namn: "Perrongen vid Pir 9", bild: "p_pir", grupp: "station", ord: ["tunnelbana", "tunnelbanan", "perrong", "perrongen", "trappa", "trappan"],
      beskrivning: "Den sista stationen på linjen. Lysrören blinkar som om de försöker säga något i morsekod, troligen \"åk härifrån\". Linjekartan visar MAIN STREET, PARK AVENUE, CHINATOWN och PIR 9. Trappan leder upp mot hamnen.",
      utgangar: { upp: "pir", ut: "pir" },
      passage: "spärren",
    },
    parkave: {
      namn: "Park Avenue", bild: "parkave", ord: ["gata", "gatan", "park avenue"],
      beskrivning: "Park Avenue, där även duvorna verkar ha butler. Framför dig reser sig Pettigrew Towers i vit marmor och mässing. En portier i grön uniform med guldknappar står vid entrén och betraktar dig som om du vore en fläck på hans matta. Tunnelbanetrappan leder ner.",
      utgangar: { ner: "p_park", in: "vaning" },
    },
    vaning: {
      namn: "Pettigrews takvåning", bild: "vaning", ord: ["takvåning", "takvåningen", "våning", "våningen", "hiss", "hissen"],
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
      beskrivning: "Chinatown. Röda lyktor gungar i regnet över smala gator fulla av folk, cyklar och stånd med torkad bläckfisk. Rakt fram lyser en neonskylt: GOLDEN DRAGON, NUDLAR & DUMPLINGS, ÖPPET TILL SENT. Tunnelbanan ligger under dina fötter.",
      utgangar: { ner: "p_china", in: "restaurang" },
    },
    restaurang: {
      namn: "Golden Dragon", bild: "restaurang", ord: ["restaurang", "restaurangen", "golden", "dragon"],
      beskrivning: "En smal restaurang med röda bås, ett akvarium med en djupt uttråkad karp och ett kök som syns genom en lucka. Bakom luckan står kocken Benny och slår upp wokpannan i lågor som en trollkarl. Vid kassan står en skål med lyckokakor.",
      utgangar: { ut: "china" },
      lukt: "Ingefära, vitlök och lyckokakor.",
    },
    pir: {
      namn: "Pir 9", bild: "pir", ord: ["pir", "piren", "hamn", "hamnen"],
      beskrivning: ["Pir 9 i hamnen. Dimman ligger tjock över vattnet och mistlurarna låter som valar med halsont. Längs kajen står slitna lagerlokaler. På den närmaste står en stor etta bredvid en ännu större trea: LAGER 13.",
        { om: { inteFlagga: "bruno" }, text: " Framför dörren står en man byggd som ett kylskåp med två kylskåp på axlarna." },
        { om: { flagga: "dorr" }, text: " Dörren står på glänt." },
        " Tunnelbanetrappan leder ner."],
      utgangar: { ner: "p_pir", in: "lager" },
      animationer: { lage: [{ om: { flagga: "dorr" }, ram: 2 }, { om: { flagga: "bruno" }, ram: 1 }, { ram: 0 }] },   // Bruno går, sedan öppnas dörren
    },
    lager: {
      namn: "Lager 13", bild: "lager", ord: ["lager", "lagret", "lagerlokal", "lagerlokalen"],
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
      beskrivning: [{ om: { flagga: "svarare" }, text: "Telefonsvararen har slutat blinka. Den ser nöjd ut." }, { om: { inteFlagga: "svarare" }, text: "En telefonsvarare med en blinkande röd lampa. Ett meddelande väntar. Du kan LYSSNA på det." }] },
    hangare: { namn: ["klädhängare", "klädhängaren", "hängare", "hängaren"], kort: "en klädhängare", plats: "kontor", fast: true,
      beskrivning: "En klädhängare av böjträ. Den har sett bättre dagar, och bättre rockar." },
    rock: { namn: ["rock", "rocken", "trenchcoat", "trenchcoaten", "kappa", "kappan", "ficka", "fickan", "fickor", "fickorna"], kort: "din trenchcoat", plats: "kontor",
      beskrivning: "Din beigea trenchcoat. Den har två fickor, tre fläckar och en historia." },
    fonster: { namn: ["fönster", "fönstret", "regn", "regnet", "utsikt", "utsikten", "stad", "staden"], kort: "ett fönster", plats: "kontor", fast: true,
      beskrivning: "Grand Harbor ligger utbredd nedanför, grå och blank av regn. Någonstans där ute finns ett fall. Förhoppningsvis ett som betalar." },
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
      beskrivning: "Linjekartan visar en enda linje: MAIN STREET – PARK AVENUE – CHINATOWN – PIR 9. Skriv till exempel ÅK TILL CHINATOWN för att resa." },
    portier: { namn: ["portier", "portiern", "dörrvakt", "dörrvakten", "reginald", "man", "mannen"], kort: "en portier", plats: "parkave", fast: true, person: true,
      beskrivning: "Portiern heter Reginald, enligt mässingsskylten på bröstet. Han har en näsa som är byggd för att se ner på folk, och han använder den flitigt." },
    pettigrew: { namn: ["pettigrew", "fru", "frun", "änka", "änkan", "dam", "damen", "kvinna", "kvinnan", "klient", "klienten"], kort: "fru Pettigrew", plats: "vaning", fast: true, person: true,
      beskrivning: "Fru Cornelia Pettigrew, änka efter konservkungen Horace Pettigrew. Hon bär tillräckligt med pärlor för att sänka en mindre båt." },
    portratt: { namn: ["porträtt", "porträttet", "tavla", "tavlan", "målning", "målningen", "korg", "korgen", "hundkorg", "hundkorgen"], kort: "ett porträtt", plats: "vaning", fast: true,
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
    lyckokaka: { namn: ["lyckokaka", "lyckokakan", "lyckokakor", "lyckokakorna", "kaka", "kakan", "skål", "skålen"], kort: "en lyckokaka", plats: "restaurang",
      beskrivning: "En lyckokaka. Det ligger en lapp inuti. Du får BRYTA den för att läsa den." },
    bruno: { namn: ["bruno", "gorilla", "gorillan", "vakt", "vakten", "kylskåp", "kylskåpet", "man", "mannen", "torped", "torpeden"], kort: "en jättelik vakt", plats: "pir", fast: true, person: true,
      beskrivning: "Han har en tatuering på knogarna som stavar B-R-U-N-O, och en på andra handen som stavar M-A-M-M-A. Hans mage kurrar så högt att måsarna lyfter." },
    dorr: { namn: ["dörr", "dörren", "lager", "lagret", "lagerdörr", "lagerdörren", "lås", "låset", "hänglås", "hänglåset"], kort: "en dörr", plats: "pir", fast: true,
      beskrivning: [{ om: { flagga: "dorr" }, text: "Lagerdörren står på glänt. Hänglåset hänger öppet och skäms." }, { om: { inteFlagga: "dorr" }, text: "En plåtdörr med ett stort hänglås. Ett ganska enkelt lås, för den som har rätt verktyg." }] },
    mops: { namn: ["mops", "mopsen", "hund", "hunden", "lord", "waffles", "lord waffles", "bur", "buren", "hundbur", "hundburen", "potatis"], kort: "Lord Waffles", plats: "lager", person: true,
      beskrivning: [{ om: { flagga: "mopsVan" }, text: "Lord Waffles flämtar förnöjt och har kexsmulor i rynkorna. Han litar på dig nu. I alla fall tills kexen tar slut." }, { om: { inteFlagga: "mopsVan" }, text: "Lord Waffles sitter i en olåst bur och morrar mot dig. Han är kanske tjugo centimeter hög, men hans självförtroende är minst två meter." }] },
    ladar: { namn: ["trälåda", "trälådor", "trälådorna", "lådor", "lådorna", "kartong", "kartonger", "kartongerna", "hämtmat", "konserver"], kort: "lådor", plats: "lager", fast: true,
      beskrivning: "Du öppnar en låda märkt FRUKTKONSERVER. Den innehåller frukt i konserv. Det här är uppenbarligen en mycket genomtänkt kamouflering." },
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
      { sys: "Skriv OMSTART för att spela igen." },
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
    { verb: "prata", objekt: "kiosk", gor: ["\"Varmkorv, en dollar\", säger Sal. \"Vill du ha en får du KÖPA den. Det är så handel fungerar.\""] },
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
    { verb: "öppna", objekt: "dorr", gor: ["Dörren är låst med ett hänglås. Du skulle kunna försöka DYRKA upp det."] },
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
    { om: { inteFlagga: "svarare" }, text: "Telefonsvararen på skrivbordet blinkar. Kanske borde du LYSSNA på den?" },
    { om: { inteBar: "kort", objektPa: ["kort", "lada"] }, text: "Utan tunnelbanekort kommer du ingenstans. Var brukar man lägga saker man inte vill hitta? I en skrivbordslåda." },
    { om: { inteFlagga: "dollar" }, text: "En detektiv utan pengar är bara en man i rock. UNDERSÖK din rock." },
    { om: { inteFlagga: "klient" }, text: "Fru Pettigrew bor på Park Avenue. Gå ner i tunnelbanan och ÅK TILL PARK AVENUE." },
    { om: { inteFlagga: "adress" }, text: "LÄS lösenbrevet noga. Vems meny är det skrivet på? Visa sedan det du har för någon som kan känna igen det." },
    { om: { inteFlagga: ["korv", "bruno"] }, text: "Bruno på Pir 9 är hungrig, och Sal på Main Street säljer korv för en dollar." },
    { om: { inteFlagga: "bruno" }, text: "Ta med korven till Pir 9 och GE den TILL BRUNO." },
    { om: { inteFlagga: "dorr", bar: "dyrk" }, text: "Du har en dyrk. DYRKA UPP DÖRREN." },
    { om: { inteFlagga: "dorr" }, text: "Dörren är låst. Låg det inte en dyrk i skrivbordslådan på kontoret?" },
    { om: { inteFlagga: "mopsVan" }, text: "Lord Waffles går ingenstans utan sina kex. GE KEXEN TILL MOPSEN." },
    { om: { inteBar: "mops", inteFlagga: "vunnit" }, text: "TA MOPSEN." },
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
