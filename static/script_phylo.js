// =========================
// Varibale global
// =========================

let contenuFichier = "";
let listeTaxIds = [];

const especes = {};

let mappingCourant = {};
let equivalences = {};
let solutionURL = "";

let clades = [];
let cladesFile = "";
let ordreUtilisateur = {};

let solutionImage = "";
let mappingFile = "";
let equivalentsFile = "";

const DEBUG = true;

function handleIconOrderError(img, safe) {
    const attempt = Number(img.dataset.iconAttempt || 0);
    if (attempt === 0) {
        img.dataset.iconAttempt = 1;
        img.src = '/static/icons/' + safe + '.png';
    } else if (attempt === 1) {
        img.dataset.iconAttempt = 2;
        img.src = '/static/icons/' + safe + '.jpg';
    } else if (attempt === 2) {
        img.dataset.iconAttempt = 3;
        img.src = '/static/icons/' + safe + '.webp';
    } else if (attempt === 3) {
        img.dataset.iconAttempt = 4;
        img.src = '/static/icons/' + safe + '.svg';
    } else {
        img.src = '/static/icons/generic.svg';
    }
}

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

const GROUP_ICON_SAFE_NAMES = {
    "Marsupiaux": "marsupiaux",
    "Mammifères": "mammiferes",
    "Oiseaux": "oiseaux",
    "Reptiles": "reptiles",
    "Poisson": "poisson",
    "Invertébrés": "invertebres",
    "Plantes": "plantes",
    "Champignons": "champignons"
};

function getGroupNameForEspece(e) {
    for (const nom in GROUPES) {
        if (GROUPES[nom](e)) {
            return nom;
        }
    }
    return null;
}

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

function getSelectedGroupes() {
    return [...document.querySelectorAll('input[name="groupes"]:checked')]
        .map(input => input.value);
}

function getModeDifficulte() {
    const radio = document.querySelector('input[name="difficulte"]:checked');
    return radio ? radio.value : "facile";
}

function formatEspeceLabel(e, mode) {
    const label = `${e.commonName} (${e.latinName})`;
    if (mode === "facile") {
        return `${label}<span class="espece-details">${e.reign} / ${e.clas} / ${e.order}</span>`;
    }
    return label;
}

function getGroupIconHtml(groupName) {
    const safe = GROUP_ICON_SAFE_NAMES[groupName] || groupName.toLowerCase().replace(/[^a-z0-9]/g, '_');
    return "<img class='icon-order' src='/static/icons/" + safe + ".svg' " +
        "onerror=\"handleIconOrderError(this, '" + safe + "')\">";
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

    console.clear();

    console.log("=================================");
    console.log("NOUVEAU TIRAGE");
    console.log("=================================");

    document.getElementById(
        "score"
    ).innerHTML = "";

    document.getElementById(
        "solution"
    ).innerHTML = "";

    document.getElementById(
        "zoneConfiguration"
    ).style.display = "none";

    listeTaxIds =
        tirage.map(e => e.id);

    contenuFichier =
        listeTaxIds.join(",");

    console.log(
        "TaxIds envoyés à Flask :"
    );

    console.table(
        tirage.map(e => ({
            TaxID: e.id,
            Nom: e.commonName,
            Latin: e.latinName
        }))
    );

    document.getElementById(
        "btnDownload"
    ).style.display =
        "inline-block";
    document.getElementById(
        "btnCorrection"
    ).style.display =
        "inline-block";
    document.getElementById(
        "btnSolution"
    ).style.display =
        "inline-block";
    // hide any test-mode buttons during a draw
    document.querySelectorAll('.test-mode').forEach(b => b.style.display = 'none');

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

    .then(response => {

        console.log(
            "Réponse Flask :",
            response.status
        );

        if (!response.ok) {

            throw new Error(
                "Erreur Flask : " +
                response.status
            );
        }

        return response.json();
    })

    .then(data => {

        console.log(
            "Fichiers générés :"
        );

        console.table(data);

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

        cladesFile =
            data.clades;

        return fetch(
            mappingFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => {

        console.log(
            "Chargement mapping.json :",
            r.status
        );

        return r.json();
    })

    .then(mapping => {

        mappingCourant =
            mapping;

        console.log(
            "Mapping reçu :"
        );

        console.table(mapping);

        return fetch(
            equivalentsFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => {

        console.log(
            "Chargement equivalents.json :",
            r.status
        );

        return r.json();
    })

    .then(eq => {

        equivalences =
            eq;

        console.log(
            "Equivalences :"
        );

        console.log(eq);

        return fetch(
            cladesFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => {

        console.log(
            "Chargement clades.json :",
            r.status
        );

        return r.json();
    })

    .then(c => {

        clades =
            c;

        console.log(
            "Clades :"
        );

        console.log(c);

        console.log(
            "================================="
        );

        console.log(
            "SOLUTION DU QUIZ"
        );

        console.log(
            "================================="
        );

        Object.keys(mappingCourant)
            .sort((a, b) => a - b)
            .forEach(numero => {

                const taxid =
                    mappingCourant[numero];

                const e =
                    especes[taxid];

                if (e) {

                    console.log(
                        numero +
                        " -> " +
                        e.commonName +
                        " (" +
                        e.latinName +
                        ") [" +
                        taxid +
                        "]"
                    );
                }
            });

        console.log(
            "================================="
        );

        genererQuiz(
            mappingCourant
        );
    })

    .catch(error => {

        console.error(
            "ERREUR :",
            error
        );

        document.getElementById(
            "resultats"
        ).innerHTML +=

            "<br><br><b>Erreur Flask</b>";
    });
}
// =========================
// Génération du quiz Drag & Drop
// =========================

function genererQuiz(mapping) {

    mappingCourant = mapping;

    ordreUtilisateur = {};

    const quiz =
        document.getElementById("quiz");

    quiz.innerHTML = "";

    const listeEspeces =
        Object.values(mapping);

    const modeDifficulte = getModeDifficulte();

    const especesTriees =
        [...listeEspeces]
        .sort((a, b) => {

            const ea = especes[a];
            const eb = especes[b];

            const nameA = ea ? ea.commonName : a;
            const nameB = eb ? eb.commonName : b;

            return nameA.localeCompare(
                nameB
            );
        });

    let dragged = null;

    let index = 0;

    for (const numero in mapping) {

        const taxid =
            especesTriees[index];

        ordreUtilisateur[numero] =
            taxid;

        const e =
            especes[taxid];

        const ligne =
            document.createElement("div");

        ligne.className =
            "ligne-quiz";

        ligne.dataset.numero =
            numero;

        ligne.dataset.taxid =
            taxid;

        ligne.draggable = true;

        const label = e
            ? `${e.commonName} (${e.latinName})`
            : `TaxID ${taxid}`;

        // determine icon based on group (one icon per selected group)
        let iconHtml = "";
        let labelText = label;

        if (e) {
            const groupName = getGroupNameForEspece(e);
            if (groupName) {
                iconHtml = getGroupIconHtml(groupName);
            } else {
                iconHtml = "<img class='icon-order' src='/static/icons/generic.svg'>";
            }
            labelText = formatEspeceLabel(e, modeDifficulte);
            if (groupName) {
                labelText = `${groupName} — ${labelText}`;
            }
        } else {
            iconHtml = "<img class='icon-order' src='/static/icons/generic.svg'>";
        }

        ligne.innerHTML =
            "<span class='numero'>" +
            numero +
            " → </span>" +
            "<span class='nom'>" +
            iconHtml +
            labelText +
            "</span>";

        ligne.addEventListener(
            "dragstart",
            () => {

                dragged = ligne;
            }
        );

        ligne.addEventListener(
            "dragover",
            (e) => {

                e.preventDefault();
            }
        );

        ligne.addEventListener(
            "drop",
            () => {

                if (
                    !dragged ||
                    dragged === ligne
                ) {
                    return;
                }

                const nom1 =
                    dragged.querySelector(
                        ".nom"
                    ).innerHTML;

                const nom2 =
                    ligne.querySelector(
                        ".nom"
                    ).innerHTML;

                dragged.querySelector(
                    ".nom"
                ).innerHTML = nom2;

                ligne.querySelector(
                    ".nom"
                ).innerHTML = nom1;

                const tax1 =
                    dragged.dataset.taxid;

                const tax2 =
                    ligne.dataset.taxid;

                dragged.dataset.taxid =
                    tax2;

                ligne.dataset.taxid =
                    tax1;

                ordreUtilisateur[
                    dragged.dataset.numero
                ] = tax2;

                ordreUtilisateur[
                    ligne.dataset.numero
                ] = tax1;
            }
        );

        quiz.appendChild(ligne);

        index++;
    }
}

// =========================
// Correction
// =========================

function corrigerQuiz() {

    const lignes =
        document.querySelectorAll(
            ".ligne-quiz"
        );

    let score = 0;

    const dejaValide = new Set();

    const reponsesUtilisateur = {};

    lignes.forEach(ligne => {

        reponsesUtilisateur[
            ligne.dataset.numero
        ] =
            ligne.dataset.taxid;
    });

    lignes.forEach(ligne => {

        ligne.style.backgroundColor = "";

        const numero =
            ligne.dataset.numero;

        const bonneReponse =
            mappingCourant[numero];

        const valeur =
            ligne.dataset.taxid;

        let correct = false;

        if (
            valeur === bonneReponse
        ) {

            correct = true;
        }

        else {

            const soeurs =
                equivalences[
                    bonneReponse
                ] || [];

            if (
                soeurs.includes(
                    valeur
                )
            ) {

                correct = true;
            }
        }

        if (correct) {

            ligne.style.backgroundColor =
                "#90EE90";

            dejaValide.add(numero);

            score++;
        }

        else {

            ligne.style.backgroundColor =
                "#FFB6B6";
        }
    });

    const positionParTaxid = {};

    for (const numero in reponsesUtilisateur) {

        positionParTaxid[
            reponsesUtilisateur[numero]
        ] = parseInt(numero, 10);
    }

    const toutesLesCladesContigues =
        clades.every(clade => {

            const positions = clade
                .map(taxid =>
                    positionParTaxid[taxid]
                )
                .filter(p => p !== undefined)
                .sort((a, b) => a - b);

            if (positions.length === 0) {
                return true;
            }

            return (
                positions[positions.length - 1] -
                positions[0] + 1 ===
                positions.length
            );
        });

    if (toutesLesCladesContigues) {

        score = Object.keys(mappingCourant).length;

        lignes.forEach(ligne => {

            ligne.style.backgroundColor =
                "#90EE90";
        });

        document.getElementById(
            "score"
        ).innerHTML =
            "<h3>Score : " +
            score +
            " / " +
            score +
            "</h3>" +
            "<b>Ordre valide selon la topologie de l'arbre.</b>";

        document.getElementById(
            "btnNouvellePartie"
        ).style.display =
            "inline-block";

        return;
    }

    // =====================
    // Validation clades + équivalences
    // =====================

    clades.forEach(clade => {

        const numerosDuClade = [];

        for (const numero in mappingCourant) {

            if (
                clade.includes(
                    mappingCourant[numero]
                )
            ) {

                numerosDuClade.push(
                    numero
                );
            }
        }

        let cladeValide = true;

        numerosDuClade.forEach(numero => {

            const attendu =
                mappingCourant[numero];

            const obtenu =
                reponsesUtilisateur[numero];

            if (!obtenu) {

                cladeValide = false;
                return;
            }

            const equivalentes =
                equivalences[attendu] || [];

            if (
                obtenu !== attendu &&
                !equivalentes.includes(obtenu)
            ) {

                cladeValide = false;
            }
        });

        if (cladeValide) {

            numerosDuClade.forEach(numero => {

                if (
                    !dejaValide.has(
                        numero
                    )
                ) {

                    dejaValide.add(
                        numero
                    );

                    score++;

                    const ligne =
                        document.querySelector(
                            ".ligne-quiz[data-numero='" +
                            numero +
                            "']"
                        );

                    if (ligne) {

                        ligne.style.backgroundColor =
                            "#90EE90";
                    }
                }
            });
        }
    });

    const total =
        Object.keys(
            mappingCourant
        ).length;

    if (
        score > total
    ) {

        score = total;
    }

    const pourcentage =
        Math.round(
            score /
            total *
            100
        );

    let message = "";

    if (
        pourcentage === 100
    ) {

        message =
            total +
            "/" +
            total +
            " !";

        document.getElementById(
            "btnNouvellePartie"
        ).style.display =
            "inline-block";
    }

    else if (
        pourcentage >= 75
    ) {

        message =
            "Presque parfait";
    }

    else if (
        pourcentage >= 50
    ) {

        message =
            "Pas mal";
    }

    else {

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

        if (e) {
            html +=
                "<b>" +
                numero +
                "</b> → " +
                e.commonName +
                " (" +
                e.latinName +
                ")" +
                "<span class='espece-details'>" +
                e.reign +
                " / " +
                e.clas +
                " / " +
                e.order +
                "</span><br>";
        }
        else {
            html +=
                "<b>" +
                numero +
                "</b> → TaxID " +
                taxid +
                "<br>";
        }
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
    document.getElementById(
        "btnCorrection"
    ).style.display = "none";
    document.getElementById(
        "btnSolution"
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

    // show any test-mode buttons when starting a new game
    document.querySelectorAll('.test-mode').forEach(b => b.style.display = 'inline-block');
    document.getElementById(
        "btnCorrection"
    ).style.display = "none";
    document.getElementById(
        "btnSolution"
    ).style.display = "none";
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

            const choisis =
                getSelectedGroupes();

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

            if (
                tirage.length === 0
            ) {
                alert(
                    "Aucune espèce trouvée dans les groupes sélectionnés."
                );
                return;
            }

            afficherResultats(
                tirage
            );
        }
    );
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

// =========================
// Mode test
// =========================

function lancerTestLineaire() {

    const taxIdsTest = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8"
    ];

    const tirage = taxIdsTest.map(id => ({
        id,
        commonName: `Feuille ${id}`,
        latinName: `Leaf ${id}`,
        toString() {
            return `${this.commonName} (${this.latinName}) [${this.id}]`;
        }
    }));

    console.log(
        "MODE TEST ARBRE LINEAIRE"
    );

    document.getElementById(
        "zoneConfiguration"
    ).style.display = "none";

    listeTaxIds = taxIdsTest;
    contenuFichier = listeTaxIds.join(",");

    document.getElementById(
        "btnDownload"
    ).style.display = "inline-block";

    document.getElementById(
        "resultats"
    ).innerHTML =
        "<h3>Espèces tirées :</h3>" +
        tirage.map(e => e.toString()).join("<br>") +
        "<br><br><h3>Tax IDs :</h3>" +
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
                tax_ids: listeTaxIds,
                input_tree: "linear_test.nwk"
            })
        }
    )

    .then(response => {

        console.log(
            "Réponse Flask :",
            response.status
        );

        if (!response.ok) {

            throw new Error(
                "Erreur Flask : " +
                response.status
            );
        }

        return response.json();
    })

    .then(data => {

        console.log(
            "Fichiers générés :"
        );

        console.table(data);

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

        cladesFile =
            data.clades;

        return fetch(
            mappingFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => {

        console.log(
            "Chargement mapping.json :",
            r.status
        );

        return r.json();
    })

    .then(mapping => {

        mappingCourant =
            mapping;

        console.log(
            "Mapping reçu :"
        );

        console.table(mapping);

        return fetch(
            equivalentsFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => {

        console.log(
            "Chargement equivalents.json :",
            r.status
        );

        return r.json();
    })

    .then(eq => {

        equivalences =
            eq;

        console.log(
            "Equivalences :"
        );

        console.log(eq);

        return fetch(
            cladesFile +
            "?t=" +
            Date.now()
        );
    })

    .then(r => {

        console.log(
            "Chargement clades.json :",
            r.status
        );

        return r.json();
    })

    .then(c => {

        clades =
            c;

        console.log(
            "Clades :"
        );

        console.log(c);

        console.log(
            "================================="
        );

        console.log(
            "SOLUTION DU QUIZ"
        );

        console.log(
            "================================="
        );

        Object.keys(mappingCourant)
            .sort((a, b) => a - b)
            .forEach(numero => {

                const taxid =
                    mappingCourant[numero];

                const e =
                    especes[taxid];

                if (e) {

                    console.log(
                        numero +
                        " -> " +
                        e.commonName +
                        " (" +
                        e.latinName +
                        ") [" +
                        taxid +
                        "]"
                    );
                }
                else {
                    console.log(
                        numero +
                        " -> " +
                        taxid
                    );
                }
            });

        console.log(
            "================================="
        );

        genererQuiz(
            mappingCourant
        );
    })

    .catch(error => {

        console.error(
            "ERREUR :",
            error
        );

        document.getElementById(
            "resultats"
        ).innerHTML +=

            "<br><br><b>Erreur Flask</b>";
    });
}

function lancerTirageAll() {

    loadCSV(function(rows) {

        buildEspeceTable(rows);

        let choisis = getSelectedGroupes();

        // If no groups selected, use all available groups
        if (choisis.length === 0) {
            choisis = Object.keys(GROUPES);
        }

        const groups =
            buildGroups();

        // Collect all species from selected groups
        let toutesEspeces = [];
        choisis.forEach(groupe => {
            if (groups[groupe]) {
                toutesEspeces = toutesEspeces.concat(
                    groups[groupe]
                );
            }
        });

        // Get the number of species to draw
        const nombre = getNombreTirage();

        // Draw random species
        const tirage = tirageAleatoire(
            toutesEspeces,
            nombre
        );

        console.log(
            "MODE TIRAGE TOUTES ESPECES",
            tirage.length
        );

        afficherResultats(
            tirage
        );
    });
}
