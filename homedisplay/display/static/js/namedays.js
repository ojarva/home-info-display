var Namedays = function() {
  var data = [[null,"Aapeli","Elmo ja Elmer","Ruut","Lea ja Leea","Harri","Aukusti, Aku","Hilppa ja Titta","Veikko, Veli ja Veijo","Nyyrikki","Kari ja Karri","Toini","Nuutti","Sakari ja Saku","Solja","Ilmari ja Ilmo","Toni ja Anttoni","Laura","Heikki ja Henrik","Henna ja Henni","Aune ja Oona","Visa","Eine, Eini ja Enni","Senja","Paavo ja Pauli","Joonatan","Viljo","Kaarlo ja Kalle","Valtteri","Irja","Alli"],["Riitta","Aamu","Valo","Armi","Asser","Terhi, Teija ja Tiia","Riku ja Rikhard","Laina","Raija ja Raisa","Elina ja Elna","Talvikki","Elma ja Elmi","Sulo ja Sulho","Voitto","Sipi ja Sippo","Kai","Väinö ja Väinämö","Kaino","Eija","Heli ja Helinä","Keijo","Tuulikki ja Tuuli","Aslak","Matti ja Mattias","Tuija ja Tuire","Nestori","Torsti","Onni"],["Alpo, Alvi, Alpi","Virve ja Virva","Kauko","Ari, Arsi ja Atro","Laila ja Leila","Tarmo","Tarja ja Taru","Vilppu","Auvo","Aurora, Aura ja Auri","Kalervo","Reijo ja Reko","Erno ja Tarvo","Matilda ja Tilda","Risto","Ilkka","Kerttu ja Kerttuli","Eetu ja Edvard","Jooseppi ja Juuso","Aki, Joakim ja Kim","Pentti","Vihtori","Akseli","Kaapo ja Gabriel","Aija","Manu ja Immanuel","Sauli ja Saul","Armas","Joonas, Jouni ja Joni","Usko ja Tage","Irma ja Irmeli"],["Raita ja Pulmu","Pellervo","Sampo","Ukko","Irene ja Irina","Vilho ja Ville","Allan ja Ahvo","Suoma ja Suometar","Elias ja Eelis","Tero","Verna","Julius ja Julia","Tellervo","Taito","Linda ja Tuomi","Jalo ja Patrik","Otto","Valto ja Valdemar","Päivi ja Pilvi","Lauha","Anssi ja Anselmi","Alina","Yrjö, Jyrki ja Jyri","Pertti ja Albert","Markku, Markus ja Marko","Terttu ja Teresa","Merja","Ilpo ja Ilppo","Teijo","Mirja, Mirva, Mira ja Miia"],["Vappu ja Valpuri","Vuokko ja Viivi","Outi","Ruusu ja Roosa","Maini","Ylermi","Helmi ja Kastehelmi","Heino","Timo","Aino, Aina ja Aini","Osmo","Lotta","Kukka ja Floora","Tuula","Sofia ja Sonja","Esteri ja Essi","Maila ja Maili","Erkki ja Eero","Emilia, Milja ja Emma","Lilja ja Karoliina","Kosti ja Kosta","Hemminki ja Hemmo","Lyydia ja Lyyli","Tuukka ja Touko","Urpo","Minna ja Vilma","Ritva","Alma","Oiva ja Oivi","Pasi","Helka ja Helga"],["Teemu ja Nikodemus","Venla","Orvokki","Toivo","Sulevi","Kustaa ja Kyösti","Suvi","Salomo ja Salomon","Ensio","Seppo","Impi ja Immi","Esko","Raili ja Raila","Kielo","Vieno ja Viena","Päivi ja Päivikki ja Päivä","Urho","Tapio","Siiri","Into","Ahti ja Ahto","Paula, Liina ja Pauliina","Aatto, Aatu ja Aadolf","Johannes, Juhani ja Juha","Uuno","Jorma, Jarmo ja Jarkko","Elviira ja Elvi","Leo","Pietari, Pekka, Petri ja Petra","Päiviö ja Päivö"],["Aaro ja Aaron","Maria, Mari, Maija, Meeri ja Maaria","Arvo","Ulla ja Upu","Unto ja Untamo","Esa ja Esaias","Klaus ja Launo","Turo ja Turkka","Ilta ja Jasmin","Saima ja Saimi","Elli, Noora ja Nelli","Hermanni, Herkko","Ilari, Lari ja Joel","Aliisa","Rauni ja Rauna","Reino","Ossi ja Ossian","Riikka","Saara, Sari, Salli ja Salla","Marketta, Maarit ja Reeta","Johanna, Hanna ja Jenni","Leena, Leeni ja Lenita","Oili ja Olga","Kirsti, Tiina, Kirsi ja Kristiina","Jaakko ja Jaakoppi","Martta","Heidi","Atso","Olavi, Olli, Uolevi ja Uoti","Asta","Helena ja Elena"],["Maire","Kimmo","Linnea, Nea ja Vanamo","Veera","Salme ja Sanelma","Toimi ja Keimo","Lahja","Sylvi, Sylvia ja Silva","Erja ja Eira","Lauri, Lasse ja Lassi","Sanna, Susanna ja Sanni","Klaara","Jesse","Onerva ja Kanerva","Marjatta, Marja ja Jaana","Aulis","Verneri","Leevi","Mauno ja Maunu","Samuli, Sami, Samuel ja Samu","Soini ja Veini","Iivari ja Iivo","Varma ja Signe","Perttu","Loviisa","Ilma, Ilmi ja Ilmatar","Rauli","Tauno","Iines, Iina ja Inari","Eemil ja Eemeli","Arvi"],["Pirkka","Sinikka ja Sini","Soili, Soile ja Soila","Ansa","Mainio","Asko","Arho ja Arhippa","Taimi","Eevert ja Isto","Kalevi ja Kaleva","Santeri, Ali, Ale ja Aleksanteri","Valma ja Vilja ","Orvo","Iida","Sirpa","Hellevi, Hillevi, Hille ja Hilla","Aili ja Aila","Tyyne, Tytti ja Tyyni","Reija","Varpu ja Vaula","Mervi","Mauri","Mielikki","Alvar ja Auno","Kullervo","Kuisma","Vesa","Arja","Mikko, Mika, Mikael, Miika","Sorja ja Sirja"],["Rauno, Rainer, Raine ja Raino","Valio","Raimo","Saila ja Saija","Inkeri ja Inka","Minttu ja Pinja","Pirkko, Pirjo, Piritta ja Pirita","Hilja","Ilona","Aleksi ja Aleksis","Otso ja Ohto","Aarre ja Aarto","Taina, Tanja ja Taija","Elsa, Else ja Elsi","Helvi ja Heta","Sirkka ja Sirkku","Saini ja Saana","Satu ja Säde","Uljas","Kauno ja Kasperi","Ursula","Anja, Anita, Anniina ja Anitta","Severi","Asmo","Sointu","Amanda ja Niina, Manta","Helli, Hellä, Hellin ja Helle","Simo","Alfred ja Urmas","Eila","Artturi, Arto ja Arttu"],["Pyry ja Lyly","Topi ja Topias","Terho","Hertta","Reima","Kustaa Aadolf","Taisto","Aatos","Teuvo","Martti","Panu","Virpi","Ano ja Kristian","Iiris","Janika, Janita ja Janina","Aarne ja Aarno, Aarni","Eino ja Einar","Tenho ja Jousia","Liisa, Eliisa, Elisa ja Elisabet","Jalmari ja Jari","Hilma","Silja ja Selja","Ismo","Lempi, Lemmikki ja Sivi","Katri, Kaisa, Kaija ja Katja","Sisko","Hilkka","Heini","Aimo","Antti, Antero ja Atte"],["Oskari","Anelma ja Unelma","Vellamo ja Meri","Airi ja Aira","Selma","Niilo, Niko ja Niklas","Sampsa","Kyllikki ja Kylli","Anna, Anne, Anni, Anu ja Annikki","Jutta","Taneli, Tatu ja Daniel","Tuovi","Seija","Jouko","Heimo","Auli ja Aulikki","Raakel","Aapo, Aappo ja Rami","Iikka, Iiro, Iisakki ja Isko","Benjamin ja Kerkko","Tuomas, Tuomo ja Tommi","Raafael","Senni","Aatami, Eeva, Eevi ja Eveliina",null,"Tapani ja Teppo","Hannu ja Hannes","Piia","Rauha","Daavid, Taavetti ja Taavi","Sylvester ja Silvo"]],
      update_interval;

  function clearItems() {
    jq("#namedays-modal ul li").remove();
  }

  function addItems() {
    clearItems();
    var now = moment();
    var current_elem;
    var current_index = 0;
    var items_in_current = 1000;
    for (i = 0; i < 365; i++) {
      if (items_in_current > 45) {
        current_elem = jq("#namedays-modal ul").slice(current_index, current_index + 1);
        items_in_current = 0;
        current_index++;
      }
      if (data[now.month()].length == now.day()) {
        // 29th of Feb
      } else {
        current_elem.append("<li>"+data[now.month()][now.day()]+" "+now.format("DD.MM (dd)")+"</li>")
        items_in_current += 1;
      }
      now.add(1, "day");
    }
  }

  function update() {
    addItems();
    var d = clock.getDate();
    var nameday = data[d.getMonth()][d.getDate() - 1];
    jq("#today .list-namedays ul li").remove();
    jq("#today .list-namedays ul").append("<li><i class='fa-li fa fa-calendar'></i> "+nameday+"</li>");
  }

  function startInterval() {
    update();
    stopInterval();
    update_interval = setInterval(update, SLOW_UPDATE);

  }
  function stopInterval() {
    if (update_interval) {
      update_interval = clearInterval(update_interval);
    }
  }
  ge_refresh.register("namedays", update);

  this.update = update;
  this.startInterval = startInterval;
  this.stopInterval = stopInterval;
};

var name_days;

jq(document).ready(function () {
  name_days = new Namedays();
  name_days.startInterval();

  jq(".list-namedays").on("click", function () {
    content_switch.switchContent("#namedays-modal");
  });
  jq("#namedays-modal .close").on("click", function() {
    content_switch.switchContent("#main-content");
  });
});
