import sys

def parse_newick(s):
    s = s.strip()
    if s.endswith(';'):
        s = s[:-1]
    i = 0

    def parse_node():
        nonlocal i
        if i >= len(s):
            return None
        if s[i] == '(':
            i += 1
            children = []
            while True:
                child = parse_node()
                children.append(child)
                if i >= len(s):
                    break
                if s[i] == ',':
                    i += 1
                    continue
                if s[i] == ')':
                    i += 1
                    # skip possible node label or branch length until comma or closing
                    while i < len(s) and s[i] not in ',()':
                        i += 1
                    break
            return children
        else:
            start = i
            while i < len(s) and s[i] not in ',()':
                i += 1
            label = s[start:i].strip()
            return label

    tree = parse_node()
    return tree


def collect_clades(node):
    """Return (leaves_list, clades_list) where clades_list is list of lists of leaves for each internal node"""
    if isinstance(node, str) or node is None:
        return [node] if node not in (None, "") else [], []
    leaves = []
    clades = []
    for child in node:
        child_leaves, child_clades = collect_clades(child)
        leaves.extend(child_leaves)
        clades.extend(child_clades)
    if len(leaves) > 1:
        clades.append(list(leaves))
    return leaves, clades


def check_contiguity(clades, permutation):
    # permutation: list of labels in order (strings)
    pos = {str(label): idx+1 for idx, label in enumerate(permutation)}
    for clade in clades:
        # map clade labels to positions if present
        positions = [pos.get(str(l)) for l in clade if pos.get(str(l)) is not None]
        if not positions:
            continue
        positions.sort()
        if positions[-1] - positions[0] + 1 != len(positions):
            return False
    return True


def run_tests(nwk_path):
    with open(nwk_path, 'r', encoding='utf-8') as f:
        nwk = f.read().strip()

    tree = parse_newick(nwk)
    all_leaves, clades = collect_clades(tree)

    print('Leaves:', all_leaves)
    print('Clades:', clades)

    tests = [
        [3,4,1,2,7,8,5,6],
        [5,6,7,8,4,3,1,2],
        [3,4,1,2,5,6,7,8],
        [5,6,3,4,1,2,7,8],
        [1,2,3,4,5,6,7,8],
        [5,6,7,8,4,3,1,2],
    ]

    for perm in tests:
        ok = check_contiguity(clades, perm)
        print(f'Permutation {perm} ->', 'VALID' if ok else 'INVALID')

    # random swaps: generate some random permutations by swapping subtree blocks
    print('\nRandomized checks:')
    import random
    for _ in range(10):
        p = list(range(1, len(all_leaves)+1))
        random.shuffle(p)
        ok = check_contiguity(clades, p)
        print(f'{p} ->', 'VALID' if ok else 'INVALID')


if __name__ == '__main__':
    nwk = 'linear_test.nwk'
    if len(sys.argv) > 1:
        nwk = sys.argv[1]
    run_tests(nwk)
