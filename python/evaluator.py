"""
Automorphism-aware evaluator for the "guess the species positions" game.

Built entirely on ete3's own Tree API:
  - Tree(newick, format=1)   -> parsing (no custom parser needed)
  - node.is_leaf()           -> leaf test
  - node.children            -> child TreeNode list
  - node.name                -> leaf label (built-in, no custom Node class)
  - node.iter_leaves()       -> left-to-right leaf traversal
  - node.add_feature(k, v)   -> attach custom data (slot index, shape signature)
"""

import os

from ete3 import Tree
from scipy.optimize import linear_sum_assignment


def solve(session):
  """
  session: sessions id
  """
  input=os.path.join("sessions", session, "tree.nwk")
  tree = Tree(input, format=1)
  return prepare(tree)

def evaluate(session, query):
  """
  session: sessions id
  query: query string as "sp1,sp2,sp3...,spN"
  """
  #return "false,true,true,true,false,false,true,false"
  input=os.path.join("sessions", session, "tree.nwk")
  tree = Tree(input, format=1)
  guess = query.split(",")
  evaluation = doEvaluate(tree, guess)
  return ",".join(str(b).lower() for b in evaluation)

def doEvaluate(tree, guess):
  """
  tree:  an ete3.Tree (the secret reference tree)
  guess: species names, in the same order as tree.iter_leaves()

  Returns (well_placed, truth) where well_placed[i] is True iff slot i's
  guess is justified by *some* valid tree automorphism, chosen to
  maximize the total number of True's.
  """

  truth = prepare(tree)
  assert sorted(guess) == sorted(truth), "guess must be a permutation of the true species set"
  memo = {}
  _, pi = g(tree, tree, guess, truth, memo)
  well_placed = [guess[i] == truth[pi[i]] for i in range(len(guess))]
  return well_placed#, truth

def prepare(tree):
  """
  Attach two features to every node:
    - slot  (leaves only): fixed left-to-right index — the positional
                            convention your guess vector must use
    - shape (all nodes):   structural signature, ignores species names;
                            two subtrees share .shape iff they're
                            topologically interchangeable
  Returns `truth`: true species name at each slot index.
  """
  for i, leaf in enumerate(tree.iter_leaves()):
    leaf.add_feature("slot", i)

  compute_shape(tree)

  truth = [None] * sum(1 for _ in tree.iter_leaves())
  for leaf in tree.iter_leaves():
    truth[leaf.slot] = leaf.name
  return truth

def compute_shape(node):
  """
  Computes the shape of the node
  """  
  if node.is_leaf():
    node.add_feature("shape", "L")
  else:
    for child in node.children:
      compute_shape(child)
    node.add_feature(
        "shape",
        "(" + ",".join(sorted(c.shape for c in node.children)) + ")"
    )

def g(u, v, guess, truth, memo):
  """Max matches from realigning guessed content under u onto v's slots
  (u, v must share .shape). Returns (score, {guess_slot: truth_slot})."""
  key = (id(u), id(v))
  if key in memo:
    return memo[key]

  if u.is_leaf():
    score = 1 if guess[u.slot] == truth[v.slot] else 0
    mapping = {u.slot: v.slot}
    memo[key] = (score, mapping)
    return score, mapping

  groups_u, groups_v = {}, {}
  for c in u.children:
    groups_u.setdefault(c.shape, []).append(c)
  for c in v.children:
    groups_v.setdefault(c.shape, []).append(c)

  total, mapping = 0, {}
  for shape, us in groups_u.items():
    vs = groups_v[shape]
    k = len(us)
    scores = [[0] * k for _ in range(k)]
    submaps = [[None] * k for _ in range(k)]
    for i, ui in enumerate(us):
      for j, vj in enumerate(vs):
        sc, mp = g(ui, vj, guess, truth, memo)
        scores[i][j], submaps[i][j] = sc, mp
    cost = [[-scores[i][j] for j in range(k)] for i in range(k)]
    row, col = linear_sum_assignment(cost)
    for i, j in zip(row, col):
      total += scores[i][j]
      mapping.update(submaps[i][j])

  memo[key] = (total, mapping)
  return total, mapping
