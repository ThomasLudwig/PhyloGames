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
  unclean = os.path.join(wd, "unclean.nwk")
  output = os.path.join(wd, "tree.nwk")
  map = os.path.join(wd, "order.json")
  svg = os.path.join(wd, "tree.svg")

  #Load ete Tree
  tree = Tree(input, format=1)
  #Prune to selected species
  prune(tree, taxa)
  #Remove unary nodes
  save(tree, unclean)
  remove_unary_nodes(tree, False)

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

def remove_unary_nodes(tree, preserve_distances=False):
  """
  Remove unary nodes while preserving the Tree root object.

  Unary internal nodes are collapsed.
  A unary root is replaced by its only child in place.
  """

  # Collapse unary non-root nodes
  changed = True

  while changed:
    changed = False
    for node in list(tree.traverse("postorder")):
      if node.is_root() or len(node.children) != 1:
        continue
      child = node.children[0]
      if preserve_distances:
        child.dist += node.dist
      node.delete(prevent_nondicotomic=False)
      changed = True
      break

  # Collapse unary root nodes without replacing the Tree object
  while len(tree.children) == 1:
    child = tree.children[0]

    if preserve_distances:
      tree.dist += child.dist

    # Copy the child's properties into the existing root
    tree.name = child.name
    tree.dist = child.dist
    tree.support = child.support

    # Detach the child's children
    grandchildren = child.children[:]
    child.detach()

    # Attach grandchildren directly to the existing root
    for grandchild in grandchildren:
      tree.add_child(grandchild)

  return tree

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

