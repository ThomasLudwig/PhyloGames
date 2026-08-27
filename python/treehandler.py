import json
import os

from ete3 import Tree

from python import nwk2svg


def generate(wd, table):
  """
  Creates a subtree for the selected species
  """
  taxa = [row["latin"] for row in table]
  input = "data/phyliptree.nwk"
  output = os.path.join(wd, "tree.nwk")
  map = os.path.join(wd, "order.json")
  svg = os.path.join(wd, "tree.svg")

  #Load ete Tree
  tree = Tree(input, format=1)
  #Prune to selected species
  prune(tree, taxa)
  #Save pruned tree
  save(tree, output)
  #Save species order
  mapping(tree, map)
  #Draw SVG
  draw(output, svg)

def prune(tree, taxa)  :
  """
  Kee only the listed taxa in the tree
  """
  #existing leaves
  existing = set(tree.get_leaf_names())
  i = 0
  for ex in existing:
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

def save(tree, output):
  """
  Writes Tree to nwk file
  """
  tree.write(outfile=output,format=1)

def mapping(tree, map):
  """
  Saves the Species order
  """
  mapping = {}
  for i, leaf in enumerate(tree.iter_leaves(), start=1):
    mapping[str(i)] = leaf.name
    leaf.name = str(i)
  with open(map, "w", encoding="utf-8") as f:
    json.dump( mapping, f, ensure_ascii=False, indent=4)

def draw(nck, svg):
  """
  Draws the pruned tree
  """  
  nwk2svg.NWK2SVG.run(nck, svg, 600, 138)

