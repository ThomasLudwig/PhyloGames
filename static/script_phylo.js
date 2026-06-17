// =========================
// Varibale global
// =========================

let contenuFichier = "";
let listeTaxIds = [];

const especes = {};

let mappingCourant = {};
let equivalences = {};
let solutionURL = "";

let solutionImage = "";
let mappingFile = "";
let equivalentsFile = "";


// =========================
// Lecture du fichier csv
// =========================

function loadCSV(callback) {

    fetch("/especes")

        .then(r => r.text())

        .then(text => {

            const lines =
                text.trim().split("\n");

            const data = [];

            for (
                let i = 1;
                i < lines.length;
                i++
            ) {

                const cols =
                    lines[i].split(",");

                data.push({

                    taxId:
                        cols[0].trim(),

                    latin:
                        cols[1].trim(),

                    common:
                        cols[2].trim(),

                    reign:
                        cols[3].trim(),

                    clas:
                        cols[4].trim(),

                    order:
                        cols[5].trim()
                });
            }

            callback(data);
        });
}


// =========================
// Classe des espece
// =========================

class Espece {

    constructor(id, latin, common, reign, clas, order) {

        this.id = id;
        this.latinName = latin;
        this.commonName = common;
        this.reign = reign;
        this.clas = clas;
        this.order = order;
    }

    toString() {

        return `${this.commonName} (${this.latinName}) [${this.reign}] {${this.clas}/${this.order}}`;
    }
}


// =========================
// Table espece
// =========================

function buildEspeceTable(array) {

    Object.keys(especes)
        .forEach(k => delete especes[k]);

    array.forEach(row => {

        especes[row.taxId] = new Espece(
            row.taxId,
            row.latin,
            row.common,
            row.reign,
            row.clas,
            row.order
        );
    });
}


// =========================
// Filtre
// =========================

function estMarsupial(e) {

    return [
        "Dasyuromorphia",
        "Didelphimorphia",
        "Diprotodontia",
        "Monotremata",
        "Peramelemorphia"
    ].includes(e.order);
}

function estMammifere(e) {
    return e.clas === "Mammalia" && !estMarsupial(e);
}

function estOiseau(e) {
    return e.clas === "Aves";
}

function estReptile(e) {
    return e.clas === "Reptilia";
}

function estPoisson(e) {
    return ["Actinopterygii", "Hyperoartia"].includes(e.clas);
}

function estInvertebre(e) {
    return ["Arachnida", "Crustacea", "Insecta"].includes(e.clas);
}

function estPlante(e) {
    return e.reign === "Plantae";
}

function estChampignon(e) {
    return ["Chromista", "Fungi"].includes(e.reign);
}


// =========================
// Groupe
// =========================

const GROUPES = {

    "Marsupiaux": estMarsupial,
    "Mammifères": estMammifere,
    "Oiseaux": estOiseau,
    "Reptiles": estReptile,
    "Poisson": estPoisson,
    "Invertébrés": estInvertebre,
    "Plantes": estPlante,
    "Champignons": estChampignon
};

function buildGroups() {

    const groups = {};

    for (const nom in GROUPES) {

        groups[nom] = [];

        for (const id in especes) {

            const esp = especes[id];

            if (GROUPES[nom](esp)) {

                groups[nom].push(esp);
            }
        }
    }

    return groups;
}


// =========================
// Tirage
// =========================

function tirageAleatoire(liste, n = 10) {

    const copie = [...liste];
    const result = [];

    for (let i = 0; i < n; i++) {

        if (copie.length === 0) {
            break;
        }

        const index =
            Math.floor(Math.random() * copie.length);

        result.push(
            copie.splice(index, 1)[0]
        );
    }

    return result;
}

function tirageGroupes(groups, choisis, total = 10) {

    let pool = [];

    choisis.forEach(g => {

        if (groups[g]) {

            pool = pool.concat(groups[g]);
        }
    });

    return tirageAleatoire(pool, total);
}


// =========================
// Affichage resultat
// =========================

function afficherResultats(tirage) {

    // Nettoyage ancienne partie

    document.getElementById(
        "score"
    ).innerHTML = "";

    document.getElementById(
        "solution"
    ).innerHTML = "";

    // Cache la zone de configuration

    document.getElementById(
        "zoneConfiguration"
    ).style.display = "none";

    listeTaxIds =
        tirage.map(e => e.id);

    contenuFichier =
        listeTaxIds.join(",");

    document.getElementById(
        "btnDownload"
    ).style.display =
        "inline-block";

    const noms =
        tirage
        .map(e => e.toString())
        .join("<br>");

    document.getElementById(
        "resultats"
    ).innerHTML =

        "<h3>Espèces tirées :</h3>" +

        noms +

        "<br><br>" +

        "<h3>Tax IDs :</h3>" +

        listeTaxIds.join(", ");

    fetch(
        "http://127.0.0.1:5000/prune",
        {
            method: "POST",

            headers: {
                "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
                tax_ids: listeTaxIds
            })
        }
    )

    .then(response => response.json())

    .then(data => {

        document.getElementById(
            "tree-container"
        ).innerHTML =

            "<img src='" +

            data.tree +

            "?t=" +

            Date.now() +

            "' style='max-width:100%;height:auto;'>";

        solutionURL =
            data.solution;

        mappingFile =
            data.mapping;

        equivalentsFile =
            data.equivalents;

        return fetch(
            mappingFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => r.json())

    .then(mapping => {

        mappingCourant =
            mapping;

        return fetch(
            equivalentsFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => r.json())

    .then(eq => {

        equivalences =
            eq;

        genererQuiz(
            mappingCourant
        );
    })

    .catch(error => {

        console.error(
            error
        );

        document.getElementById(
            "resultats"
        ).innerHTML +=

            "<br><br><b>Erreur Flask</b>";
    });
}
// =========================
// Fonction quiz
// =========================

function genererQuiz(mapping) {

    mappingCourant = mapping;

    const quiz =
        document.getElementById("quiz");

    quiz.innerHTML = "";

    const listeEspeces =
        Object.values(mapping);

    const melange =
        [...listeEspeces]
        .sort(() => Math.random() - 0.5);

    for (const numero in mapping) {

        const ligne =
            document.createElement("div");

        ligne.style.marginBottom = "2px";

        let html =
            "<b>" + numero + "</b> → ";

        html +=
            "<select class='reponse' data-numero='" +
            numero +
            "'>";

        html +=
            "<option value=''>Choisir...</option>";

        melange.forEach(id => {

            const e = especes[id];

            if (e) {

                html +=
                    "<option value='" +
                    id +
                    "'>" +
                    e.commonName +
                    " (" +
                    e.latinName +
                    ")" +
                    "</option>";
            }
        });

        html += "</select>";

        ligne.innerHTML = html;

        quiz.appendChild(ligne);

        const select =
            ligne.querySelector("select");

        select.addEventListener(
            "change",
            gererDoublons
        );
    }
}
// =========================
// verif 
// =========================
function gererDoublons(event) {

    const selectActuel = event.target;

    const valeurChoisie =
        selectActuel.value;

    if (!valeurChoisie) {
        return;
    }

    document
    .querySelectorAll(".reponse")
    .forEach(select => {

        if (
            select !== selectActuel &&
            select.value === valeurChoisie
        ) {

            select.value = "";
        }
    });
}
// =========================
// Correction
// =========================

function corrigerQuiz() {

    const selects =
        document.querySelectorAll(".reponse");

    let score = 0;

    const choixUtilises = {};

    selects.forEach(select => {

        const valeur = select.value;

        if (!valeur) return;

        if (!choixUtilises[valeur]) {

            choixUtilises[valeur] = [];
        }

        choixUtilises[valeur].push(select);
    });

    selects.forEach(select => {

        select.style.backgroundColor = "";

        const numero =
            select.dataset.numero;

        const bonneReponse =
            mappingCourant[numero];

        const valeur =
            select.value;

        let doublon = false;

        if (
            valeur &&
            choixUtilises[valeur] &&
            choixUtilises[valeur].length > 1
        ) {

            doublon = true;
        }

        let correct = false;

        if (!doublon) {

            if (valeur === bonneReponse) {

                correct = true;

            } else {

                const soeurs =
                    equivalences[bonneReponse] || [];

                if (
                    soeurs.includes(valeur)
                ) {

                    correct = true;
                }
            }
        }

        if (correct) {

            select.style.backgroundColor =
                "#90EE90";

            score++;

        } else {

            select.style.backgroundColor =
                "#FFB6B6";
        }
    });

    const total =
        Object.keys(mappingCourant).length;

    const pourcentage =
        Math.round(
            (score / total) * 100
        );

    let message = "";

    if (pourcentage === 100) {

        message =
            total + "/" + total + " !";

        document.getElementById(
            "btnNouvellePartie"
        ).style.display =
            "inline-block";

    } else if (pourcentage >= 75) {

        message =
            "Presque parfait";

    } else if (pourcentage >= 50) {

        message =
            "Pas mal";

    } else {

        message =
            "Insuffisant";
    }

    document.getElementById(
        "score"
    ).innerHTML =

        "<h3>Score : " +

        score +

        " / " +

        total +

        "</h3>" +

        "<h3>" +

        pourcentage +

        "%</h3>" +

        "<b>" +

        message +

        "</b>";
}

// =========================
// Solution + arbre corrigé
// =========================

function voirSolution() {

    let html =
        "<h3>Solution</h3>";

    for (const numero in mappingCourant) {

        const taxid =
            mappingCourant[numero];

        const e =
            especes[taxid];

        if (!e) continue;

        html +=
            "<b>" +
            numero +
            "</b> → " +
            e.commonName +
            " (" +
            e.latinName +
            ")" +
            "<br>";
    }

    html +=
        "<br><h3>Arbre corrigé</h3>" +
        "<img src='" +
        solutionURL +
        "?t=" +
        Date.now() +
        "' style='max-width:100%;border:1px solid #000'>";

    document
        .getElementById("solution")
        .innerHTML = html;
}
// =========================
// Choix nombre tirage
// =========================
function getNombreTirage() {

    return parseInt(
        document.getElementById(
            "selectTirage"
        ).value
    );
}
// =========================
// Nettoyage interface
// =========================

function nettoyerInterface() {

    document.getElementById(
        "resultats"
    ).innerHTML = "";

    document.getElementById(
        "quiz"
    ).innerHTML = "";

    document.getElementById(
        "score"
    ).innerHTML = "";

    document.getElementById(
        "solution"
    ).innerHTML = "";

    document.getElementById(
        "tree-container"
    ).innerHTML = "";

    document.getElementById(
        "btnDownload"
    ).style.display = "none";

    mappingCourant = {};

    equivalences = {};

    listeTaxIds = [];

    contenuFichier = "";
}
// =========================
// Nouvelle partie
// =========================

function nouvellePartie() {

    nettoyerInterface();

    document.getElementById(
        "zoneConfiguration"
    ).style.display =
        "block";

    document.getElementById(
        "btnNouvellePartie"
    ).style.display =
        "none";
}
// =========================
// Tirage simple
// =========================

function lancerTirage() {

    loadCSV(
    function(rows) {

            buildEspeceTable(rows);

            const select =
                document.getElementById(
                    "selectGroupes"
                );

            const choisis =
                [...select.options]
                .filter(o => o.selected)
                .map(o => o.value);

            if (
                choisis.length === 0
            ) {

                alert(
                    "Aucun groupe sélectionné"
                );

                return;
            }

            const groups =
                buildGroups();

           const nombre =
    getNombreTirage();

const tirage =
    tirageGroupes(
        groups,
        choisis,
        nombre
    );

            afficherResultats(
                tirage
            );
        }
    );
}


// =========================
// Tirage double
// =========================

function lancerTirageDouble() {

    loadCSV(function(rows) {

        buildEspeceTable(rows);

        const groupe1 =
            document.getElementById(
                "groupe1"
            ).value;

        const groupe2 =
            document.getElementById(
                "groupe2"
            ).value;

        if (groupe1 === groupe2) {

            alert(
                "Choisis deux groupes différents."
            );

            return;
        }

        const groups =
            buildGroups();

        const nombre =
            getNombreTirage();

        const nb1 =
            Math.floor(nombre / 2);

        const nb2 =
            nombre - nb1;

        const tirage1 =
            tirageAleatoire(
                groups[groupe1],
                nb1
            );

        const tirage2 =
            tirageAleatoire(
                groups[groupe2],
                nb2
            );

        const tirage =
            [...tirage1, ...tirage2];

        afficherResultats(
            tirage
        );
    });
}


// =========================
// Bouton de correction
// =========================

document
.getElementById(
    "btnCorrection"
)
.addEventListener(
    "click",
    corrigerQuiz
);


// =========================
// Bouton solus
// =========================

document
.getElementById(
    "btnSolution"
)
.addEventListener(
    "click",
    voirSolution
);


// =========================
// Bouton pour telecharger le tirage
// =========================

document
.getElementById(
    "btnDownload"
)
.addEventListener(
    "click",
    function() {

        const blob =
            new Blob(
                [contenuFichier],
                {
                    type:
                    "text/plain"
                }
            );

        const lien =
            document.createElement(
                "a"
            );

        lien.href =
            URL.createObjectURL(
                blob
            );

        lien.download =
            "taxons.txt";

        lien.click();

        URL.revokeObjectURL(
            lien.href
        );
    }
);

// =========================
// Bouton nouvelle partie
// =========================

document
.getElementById(
    "btnNouvellePartie"
)
.addEventListener(
    "click",
    nouvellePartie
);