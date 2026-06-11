import argparse
import json

from ete3 import Tree, TreeStyle

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", required=True)
parser.add_argument("-o", "--output", required=True)
parser.add_argument("-t", "--taxa", nargs="+", required=True)

args = parser.parse_args()
# On charge l'arbre
tree = Tree(args.input, format=1)

existing = set(tree.get_leaf_names())
# On transorme "A,B,C,D" en "A","B","C","D"
keep = [x for x in args.taxa if x in existing]

if len(keep) == 0:
    raise ValueError(
        "Aucun taxon valide trouvé dans l'arbre"
    )
# On coupe
tree.prune(
    keep,
    preserve_branch_length=True
)

equivalents = {}

for node in tree.traverse():

    if node.is_leaf():
        continue

    enfants = node.get_children()

    if len(enfants) != 2:
        continue

    if (
        enfants[0].is_leaf()
        and
        enfants[1].is_leaf()
    ):

        a = enfants[0].name
        b = enfants[1].name

        equivalents.setdefault(a, []).append(b)
        equivalents.setdefault(b, []).append(a)

mapping = {}

for i, leaf in enumerate(
    tree.iter_leaves(),
    start=1
):

    mapping[str(i)] = leaf.name

    leaf.name = str(i)

with open(
    "static/mapping.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        mapping,
        f,
        ensure_ascii=False,
        indent=4
    )


with open(
    "static/equivalents.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        equivalents,
        f,
        ensure_ascii=False,
        indent=4
    )
# On sauvegarde
tree.write(
    outfile=args.output,
    format=1
)

ts = TreeStyle()

ts.show_leaf_name = True

tree.render(
    "static/tree.png",
    w=1200,
    units="px",
    tree_style=ts
)