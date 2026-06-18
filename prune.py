import argparse
import json
import os

from ete3 import Tree, TreeStyle

# =========================
# Arguments
# =========================

parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--input",
    required=True
)

parser.add_argument(
    "-o",
    "--output",
    required=True
)

parser.add_argument(
    "-s",
    "--session",
    required=True
)

parser.add_argument(
    "-t",
    "--taxa",
    nargs="+",
    required=True
)

args = parser.parse_args()

# =========================
# Chargement arbre
# =========================

tree = Tree(
    args.input,
    format=1
)

existing = set(
    tree.get_leaf_names()
)

keep = [
    x for x in args.taxa
    if x in existing
]

if len(keep) == 0:

    raise ValueError(
        "Aucun taxon valide trouvé dans l'arbre"
    )

# =========================
# Prune
# =========================

tree.prune(
    keep,
    preserve_branch_length=True
)

# Copie avant renommage

solution_tree = tree.copy()

# =========================
# Equivalences + Clades
# =========================

equivalents = {}
clades = []

for node in tree.traverse():

    if node.is_leaf():
        continue

    enfants = node.get_children()

    if len(enfants) != 2:
        continue

    # feuilles soeurs

    if (
        enfants[0].is_leaf()
        and
        enfants[1].is_leaf()
    ):

        a = enfants[0].name
        b = enfants[1].name

        equivalents.setdefault(
            a,
            []
        ).append(b)

        equivalents.setdefault(
            b,
            []
        ).append(a)

    # clade complet

    feuilles = sorted(
        node.get_leaf_names()
    )

    if len(feuilles) > 1:

        clades.append(feuilles)

# =========================
# Mapping numéro -> taxid
# =========================

mapping = {}

for i, leaf in enumerate(
    tree.iter_leaves(),
    start=1
):

    mapping[str(i)] = leaf.name

    leaf.name = str(i)

# =========================
# Sauvegarde mapping
# =========================

with open(
    os.path.join(
        args.session,
        "mapping.json"
    ),
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        mapping,
        f,
        ensure_ascii=False,
        indent=4
    )

# =========================
# Sauvegarde équivalences
# =========================

with open(
    os.path.join(
        args.session,
        "equivalents.json"
    ),
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        equivalents,
        f,
        ensure_ascii=False,
        indent=4
    )

# =========================
# Sauvegarde clades
# =========================

with open(
    os.path.join(
        args.session,
        "clades.json"
    ),
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        clades,
        f,
        ensure_ascii=False,
        indent=4
    )
# =========================
# Chargement noms espèces
# =========================

try:

    with open(
        "static/especes.json",
        "r",
        encoding="utf-8"
    ) as f:

        noms = json.load(f)

except Exception:

    noms = {}

# =========================
# Remplacement TaxID -> Nom
# =========================

for leaf in solution_tree.iter_leaves():

    taxid = leaf.name

    if taxid in noms:

        leaf.name = noms[taxid]

# =========================
# Uniformisation branches
# =========================

for node in tree.traverse():

    node.dist = 1

for node in solution_tree.traverse():

    node.dist = 1

# =========================
# Sauvegarde NWK
# =========================

tree.write(
    outfile=args.output,
    format=1
)

# =========================
# Style
# =========================

ts = TreeStyle()

ts.show_leaf_name = True
ts.scale = 50

# =========================
# Taille dynamique
# =========================

nb_especes = len(keep)

largeur = 1200

hauteur = max(
    500,
    nb_especes * 80
)

# =========================
# Arbre quiz
# =========================

tree.render(
    os.path.join(
        args.session,
        "tree.png"
    ),
    w=largeur,
    h=hauteur,
    units="px",
    tree_style=ts
)

# =========================
# Arbre solution
# =========================

solution_tree.render(
    os.path.join(
        args.session,
        "solution.png"
    ),
    w=largeur,
    h=hauteur,
    units="px",
    tree_style=ts
)