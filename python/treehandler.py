import json
import os

from ete3 import Tree
from python import nwk2svg


## Creates a subtree for the selected species
def generate(wd, table):
  taxa = [row["latin"] for row in table]
  input = "data/phyliptree.phy"
  output = os.path.join(wd, "tree.nwk")
  map = os.path.join(wd, "order.json")
  clades = os.path.join(wd, "clades.json")
  equivs = os.path.join(wd, "equivs.json")
  svg = os.path.join(wd, "tree.svg")
  print(f"Input: {input}")
  print(f"WD: {wd}")
  print(f"Output: {output}")
  print(f"taxa: {len(taxa)}")
  for tax in taxa:
    print(f" -{tax}")

  #Load ete Tree
  tree = Tree(input, format=1)
  #Prune to selected species
  prune(tree, taxa)
  #Save pruned tree
  save(tree, output)
  #Save species order
  mapping(tree, map)
  #Save clades and equivs
  cladesAndEquiv(tree, clades, equivs)
  #Draw SVG
  #draw(tree, svg)
  draw(output, svg)

def prune(tree, taxa)  :
  #existing leaves
  existing = set(tree.get_leaf_names())
  i = 0
  for ex in existing:
    print(f"* {ex}")
    if i > 9:
      break
    i = i+1
  #kept leaves
  keep_set = [x for x in taxa if x in existing]
  if len(keep_set) != len(taxa):
    raise ValueError(f"Waiting for {len(taxa)} species, tree only has {len(keep_set)} (total={len(existing)})")

  # Prune
  # Instead of using tree.prune() which can have issues with ambiguous node names,
  # we build a new tree keeping only the desired leaves
  
  # Get all leaves to prune
  to_delete = []
  for leaf in tree.iter_leaves():
    if leaf.name not in keep_set:
      to_delete.append(leaf)

  # Delete leaves not in keep list
  for leaf in to_delete:
    leaf.delete()

  # Clean up: remove nodes with no leaves
  for node in tree.traverse():
    if not node.is_leaf() and not node.get_leaves():
      node.delete()

# Writes Tree to nwk file
def save(tree, output):
  tree.write(outfile=output,format=1)

# Save Species order
def mapping(tree, map):
  mapping = {}
  for i, leaf in enumerate(tree.iter_leaves(), start=1):
    mapping[str(i)] = leaf.name
    leaf.name = str(i)
  with open(map, "w", encoding="utf-8") as f:
    json.dump( mapping, f, ensure_ascii=False, indent=4)

def cladesAndEquiv(tree, cladesFile, equivsFile):
  equivs = {}
  clades = []

  for node in tree.traverse():

    #Not processing leaves
    if node.is_leaf():
      continue

    #Not processing node that are not bi-branch (ie exclude singles)
    children = node.get_children()
    if len(children) != 2:
      continue

    # sister leaves
    if (children[0].is_leaf() and children[1].is_leaf()):
      a = children[0].name
      b = children[1].name
      equivs.setdefault(a, []).append(b)
      equivs.setdefault(b, []).append(a)

    # complet clade
    feuilles = sorted(node.get_leaf_names())
    if len(feuilles) > 1:
      clades.append(feuilles)

  # Save equivs
  with open(equivsFile,"w",encoding="utf-8") as f:
    json.dump(equivs, f, ensure_ascii=False, indent=4)

  # Saves clades
  with open(cladesFile,"w",encoding="utf-8") as f:
    json.dump(clades,f,ensure_ascii=False,indent=4)

# Draws the subtree
def draw(nck, svg):
  nwk2svg.NWK2SVG.run(nck, svg, 600, 138)

