import sys
"""
Converts a newick tree to a SVG drawing
"""

class NWK2SVG:
  """
  The Main class
  """
  DEFAULT_WIDTH = 600
  DEFAULT_SPECIES_HEIGHT = 138

  @staticmethod
  def main(args):
    """
    Command line entrry point
    """
    width = NWK2SVG.DEFAULT_WIDTH
    species_height = NWK2SVG.DEFAULT_SPECIES_HEIGHT

    if len(args) != 2 and len(args) != 4:
      print("Usage: python nwk2svg.py <input.nwk> <output.svg> [width speciesHeight]", file=sys.stderr)
      sys.exit(1)

    input_path = args[0]
    output_path = args[1]

    if len(args) > 2:
      width = float(args[2])
      species_height = float(args[3])

    NWK2SVG.run(input_path, output_path, width, species_height)

  @staticmethod
  def run(input_path, output_path, width, species_height):
    """
    Main entry point (as a function)
    """
    try:
      with open(input_path, "r") as f:
        newick = f.read().strip()

      root = NWK2SVG.Parser(newick).parse()
      svg = NWK2SVG.SVGExporter.convert(root, width, species_height)

      with open(output_path, "w") as f:
        f.write(svg)

    except IOError as e:
      print("Error reading/writing file: " + str(e), file=sys.stderr)
      sys.exit(1)
    except ValueError as e:
      print("Error parsing Newick: " + str(e), file=sys.stderr)
      sys.exit(1)

  class Parser:
    """
    Class in charge of the parsing
    """
    def __init__(self, newick):
      self.s = newick
      self.pos = 0

    def parse(self):
      """
      Class constructor, builds the root node
      """
      root = self.parse_subtree(None)
      self.skip_whitespace()
      if self.pos < len(self.s) and self.s[self.pos] == ';':
        self.pos += 1
      return root

    def parse_subtree(self, parent):
      """
      Builds the subtree from a node
      """
      self.skip_whitespace()
      node = NWK2SVG.Node(parent)
      if self.pos < len(self.s) and self.s[self.pos] == '(':
        self.pos += 1  # consume '('
        node.children.append(self.parse_subtree(node))
        self.skip_whitespace()
        while self.pos < len(self.s) and self.s[self.pos] == ',':
          self.pos += 1  # consume ','
          node.children.append(self.parse_subtree(node))
          self.skip_whitespace()
        if self.pos < len(self.s) and self.s[self.pos] == ')':
          self.pos += 1  # consume ')'
        else:
          raise ValueError("Malformed Newick: expected ')' at position " + str(self.pos))

      self.parse_name_if_present()  # name is parsed but intentionally discarded (no text output)
      self.skip_whitespace()
      if self.pos < len(self.s) and self.s[self.pos] == ':':
        self.pos += 1  # consume ':'
        node.branch_length = self.parse_number()
      return node

    def parse_name_if_present(self):
      """
      name parser
      """
      self.skip_whitespace()
      if self.pos < len(self.s) and self.s[self.pos] == '\'':
        # quoted label: consume until closing quote
        self.pos += 1
        while self.pos < len(self.s) and self.s[self.pos] != '\'':
          self.pos += 1

        if self.pos < len(self.s):
          self.pos += 1  # consume closing quote
        return

      while self.pos < len(self.s):
        c = self.s[self.pos]
        if c in (':', ',', ')', '(', ';'):
          break
        self.pos += 1

    def parse_number(self):
      """
      number parser
      """
      self.skip_whitespace()
      start = self.pos
      while self.pos < len(self.s):
        c = self.s[self.pos]
        if c.isdigit() or c in ('.', '-', '+', 'e', 'E'):
          self.pos += 1
        else:
          break
      num = self.s[start:self.pos]
      if num == "":
        raise ValueError("Malformed Newick: expected number at position " + str(start))

      return float(num)

    def skip_whitespace(self):
      while self.pos < len(self.s) and self.s[self.pos].isspace():
        self.pos += 1

  class Node:
    """
    Class representing a tree node
    """
    def __init__(self, parent):
      """
      Construction, builds a node from it's parent
      """
      self.parent = parent
      self.children = []
      self.depth = 0 if parent is None else parent.depth + 1

      self.branch_length = 1.0
      self.x = 0.0
      self.y = 0.0

    def is_leaf(self):
      """
      is this node a leaf ?
      """
      return len(self.children) == 0

    def is_root(self):
      """
      is this node the root
      """
      return self.parent is None

    def count_leaves(self):
      """
      counts the leaves from this node
      """
      if self.is_leaf():
        return 1
      count = 0
      for child in self.children:
        count += child.count_leaves()
      return count

  class SVGExporter:
    """
    the class in charge of the actual drawing of the SVG
    """
    WIDTH = 600  # set to NWK2SVG.DEFAULT_WIDTH below, once Main exists
    HEIGHT = 138  # set to NWK2SVG.DEFAULT_SPECIES_HEIGHT below, once Main exists

    leaf_counter = 0

    MIN = 10
    MAX = 240

    @staticmethod
    def convert(root, width, species_height):
      """
      The main entry point
      root: the root node of the tree
      width: the SVG width
      species_height: the height take by a species
      """
      stroke = species_height / 8
      leaf_count = max(root.count_leaves(), 1)

      NWK2SVG.SVGExporter.leaf_counter = 0
      NWK2SVG.SVGExporter.compute_x(root, -1.0)
      NWK2SVG.SVGExporter.to_the_max(root, NWK2SVG.SVGExporter.get_max_x(root))
      NWK2SVG.SVGExporter.to_the_max2(root)

      min_x = NWK2SVG.SVGExporter.get_min_x(root)
      max_x = NWK2SVG.SVGExporter.get_max_x(root)
      NWK2SVG.SVGExporter.scale(root, min_x, max_x, width)

      NWK2SVG.SVGExporter.compute_y(root, species_height)

      tree_depth = NWK2SVG.SVGExporter.get_max_x(root)
      scale_x = (width - (2 * stroke)) / tree_depth if tree_depth > 0 else 1.0

      height = 2 * species_height / 2 + ((leaf_count - 1) * species_height if leaf_count > 1 else 0)
      NWK2SVG.SVGExporter.WIDTH = width
      NWK2SVG.SVGExporter.HEIGHT = height

      sb = []
      sb.append(NWK2SVG.SVGExporter.get_canvas())
      NWK2SVG.SVGExporter.draw_lines(root, scale_x, stroke / 2, species_height / 2, stroke, sb)
      sb.append("</svg>\n")

      return "".join(sb)

    @staticmethod
    def get_canvas():
      """
      creates the main canvas
      """
      width = NWK2SVG.SVGExporter.WIDTH
      height = NWK2SVG.SVGExporter.HEIGHT
      min_ = NWK2SVG.SVGExporter.MIN
      max_ = NWK2SVG.SVGExporter.MAX
      return (
          "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 " + str(width) + " " + str(height) +
          "\" width=\"" + str(width) + "\" height=\"" + str(height) + "\">\n" +
          "<defs>\n" +
          "    <linearGradient id=\"lineGradient\" x1=\"0\" y1=\"0\" x2=\"" + str(width) + "\" y2=\"" + str(height) + "\" gradientUnits=\"userSpaceOnUse\">\n" +
          "      <stop offset=\"0%\" stop-color=\"rgb(" + str(max_) + "," + str(min_) + "," + str(max_) + ")\" />\n" +
          "      <stop offset=\"100%\" stop-color=\"rgb(" + str(min_) + "," + str(max_) + "," + str(max_) + ")\" />\n" +
          "    </linearGradient>\n" +
          "    <linearGradient id=\"horiz\" x1=\"0\" y1=\"" + str(height / 2) + "\" x2=\"" + str(width) + "\" y2=\"" + str(height / 2) + "\" gradientUnits=\"userSpaceOnUse\">\n" +
          "      <stop offset=\"0%\" stop-color=\"rgb(" + str(min_) + "," + str(min_) + "," + str(max_) + ")\" />\n" +
          "      <stop offset=\"100%\" stop-color=\"rgb(" + str(min_) + "," + str(min_) + "," + str(min_) + ")\" />\n" +
          "    </linearGradient>\n" +
          "    <linearGradient id=\"vert\" x1=\"" + str(width / 2) + "\" y1=\"0\" x2=\"" + str(width / 2) + "\" y2=\"" + str(height) + "\" gradientUnits=\"userSpaceOnUse\">\n" +
          "      <stop offset=\"0%\" stop-color=\"rgb(" + str(max_) + "," + str(min_) + "," + str(min_) + ")\" />\n" +
          "      <stop offset=\"100%\" stop-color=\"rgb(" + str(min_) + "," + str(max_) + "," + str(min_) + ")\" />\n" +
          "    </linearGradient>\n" +
          "  </defs>"
      )

    @staticmethod
    def compute_x(node, parent_x):
      """
      Compute the X (level) for a node
      node: the node
      parent_x: the X (level) of the node's parent
      """
      node.x = parent_x + node.branch_length
      for child in node.children:
        NWK2SVG.SVGExporter.compute_x(child, node.x)

    @staticmethod
    def get_min_x(node):
      """
      Returns the min X for a node (and its descendent)
      """
      m = node.x
      for child in node.children:
        m = min(m, NWK2SVG.SVGExporter.get_max_x(child))
      return m

    @staticmethod
    def get_max_x(node):
      """
      Returns the max X for a node (and its descendent)
      """
      m = node.x
      for child in node.children:
        m = max(m, NWK2SVG.SVGExporter.get_max_x(child))
      return m

    @staticmethod
    def scale(node, min_x, max_x, width):
      """
      scales the whole tree horizontally
      """
      node.x = NWK2SVG.SVGExporter.scale_value(node.x, min_x, max_x, width)
      for child in node.children:
        NWK2SVG.SVGExporter.scale(child, min_x, max_x, width)

    @staticmethod
    def scale_value(x, min_, max_, width):
      """
      scale sub computation
      """
      ratio = (x - min_) / (max_ - min_)
      return ratio * width

    @staticmethod
    def to_the_max(node, max_):
      """
      First step to bring all Xs to the max available value
      """
      for child in node.children:
        NWK2SVG.SVGExporter.to_the_max(child, max_)
      if node.is_leaf():
        node.x = max_
      else:
        min_ = max_
        for child in node.children:
          min_ = min(min_, child.x)
        node.x = min_ - 1

    @staticmethod
    def to_the_max2(node):
      """
      Second step to bring all Xs to the max available value
      """
      for child in node.children:
        NWK2SVG.SVGExporter.to_the_max2(child)

      if node.is_leaf() or node.is_root():
        return

      min_ = node.children[0].x
      for child in node.children:
        min_ = min(min_, child.x)
      nx = (node.parent.x + min_) * 0.5

      node.x = nx

    @staticmethod
    def compute_y(node, leaf_spacing):
      """
      Computes the y coordinates for a node
      """
      if node.is_leaf():
        node.y = NWK2SVG.SVGExporter.leaf_counter * leaf_spacing
        NWK2SVG.SVGExporter.leaf_counter += 1
        return node.y
      total = 0
      for child in node.children:
        total += NWK2SVG.SVGExporter.compute_y(child, leaf_spacing)
      node.y = total / len(node.children)
      return node.y

    # ---------- SVG rendering ----------

    @staticmethod
    def draw_lines(node, scale_x, offset_x, offset_y, stroke, sb):
      """
      Draw all the lines from 1 node to its children
      """
      for child in node.children:
        sb.append(NWK2SVG.SVGExporter.get_lines(node, child, scale_x, offset_x, offset_y, stroke))
        NWK2SVG.SVGExporter.draw_lines(child, scale_x, offset_x, offset_y, stroke, sb)

    @staticmethod
    def get_lines(node, child, scale_x, offset_x, offset_y, stroke):
      """
      Get all the lines between 1 parent and 1 child
      """
      x1 = node.x * scale_x + offset_x
      y1 = node.y + offset_y
      x2 = child.x * scale_x + offset_x
      y2 = child.y + offset_y

      if y1 == y2:
        return NWK2SVG.SVGExporter.get_line(x1, y1, x2, y2, stroke)
      else:
        return (NWK2SVG.SVGExporter.get_line(x1, y1, x1, y2, stroke) +
                NWK2SVG.SVGExporter.get_line(x1, y2, x2, y2, stroke))

    @staticmethod
    def get_line(x1, y1, x2, y2, stroke):
      """
      Gets the actual SVG lines
      """
      return (
          "  <line" +
          " x1=\"" + str(x1) + "\"" +
          " y1=\"" + str(y1) + "\"" +
          " x2=\"" + str(x2) + "\"" +
          " y2=\"" + str(y2) + "\"" +
          " stroke=\"url(#horiz)\"" +
          " stroke-width=\"" + str(stroke) + "\"" +
          " stroke-linecap=\"round\" " +
          " />" +
          "  <line" +
          " x1=\"" + str(x1) + "\"" +
          " y1=\"" + str(y1) + "\"" +
          " x2=\"" + str(x2) + "\"" +
          " y2=\"" + str(y2) + "\"" +
          " stroke=\"url(#vert)\"" +
          " stroke-width=\"" + str(stroke) + "\"" +
          " stroke-linecap=\"round\" " +
          " style=\"mix-blend-mode: screen\"" +
          " />"
      )


# Now that Main is fully defined, mirror the Java static-field initialization
# (SVGExporter.WIDTH = NWK2SVG.DEFAULT_WIDTH, SVGExporter.HEIGHT = NWK2SVG.DEFAULT_SPECIES_HEIGHT)
NWK2SVG.SVGExporter.WIDTH = NWK2SVG.DEFAULT_WIDTH
NWK2SVG.SVGExporter.HEIGHT = NWK2SVG.DEFAULT_SPECIES_HEIGHT


if __name__ == "__main__":
    NWK2SVG.main(sys.argv[1:])