import csv
import os
import random

from python import treehandler


def prepare(sessionID, wd, parameters):
  """
  Entry point to prepare a session
  """
  output = os.path.join(wd, "game.html")
  mode = parameters.get("gamemode")
  nbspecies = int(parameters.get("nbspecies"))

  workSpecies = None

  allspecies = load_species("data/species.tsv")  

  if parameters.get("speciesset") == "australie":
    workSpecies = createAustralia(allspecies, nbspecies)
  else :      
    filteredspecies = filter_rows(allspecies, getColumnNames(parameters))
    #getnbspecies
    nbspecies = min(nbspecies, len(filteredspecies))
    workSpecies = select_rows(filteredspecies, random_integers(nbspecies, len(filteredspecies)))

  treehandler.generate(wd, workSpecies)
  with open(output, "w", encoding="utf-8") as f:
    createGameHTML(f, sessionID, workSpecies, mode)

def createAustralia(all, nb):
  """
  Creates a subtree for australia game
  """
  australia = []
  with open("data/austral.tsv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")  # uses header row as keys
    for row in reader:
      australia.append(row)

  pool = select_rows(australia, random_integers(nb/2, len(australia)))
  valid_ids = {row["sp1"] for row in pool} | {row["sp2"] for row in pool}

  # Filter source
  extract = [row for row in all if row["latin"] in valid_ids]
  return extract
  
def createGameHTML(f, sessionID, table, mode):
  """
  Writes the HTML code the session/game.html
  """
  printTree(f, sessionID)
  printList(f, table, mode)

def printTree(f, sessionID):
  """
  Writes the HTML for the tree div
  """
  f.write(f"<div id=\"{sessionID}\" class=\"tree\">")
  f.write(f" <img src=\"sessions/{sessionID}/tree.svg\" alt=\"thetree\" class=\"tile\"/>")
  f.write("</div>")

def printList(f, table, mode):
  """
  Writes the HTML for the swap div
  """
  f.write("<div class=\"swap\">")
  f.write(" <ul class=\"sortable-list\">")
  for row in table:
    french=row.get("french")
    latin=row.get("latin")
    full=row.get("full")
    img=getImage(latin)
    f.write(f"<li class=\"sortable-item\" draggable=\"true\" id=\"YY{latin}YY\"><div id=\"XX{latin}XX\" class=\"select neutral\">")
    f.write(f"<img src=\"{img}\" alt=\"{latin}\" class=\"avatar\"/>")
    f.write("<div class=\"right\">")
    f.write(f"  <div class=\"locale\">{french}</div>")
    f.write(f"  <div class=\"latin\">{latin}</div>")
    if mode == "1" :
      f.write(f"  <div class=\"details\">{full}</div>")
    f.write("</div>")
    f.write("</div></li>")
  f.write(" </ul>\n")
  f.write("</div>\n")

def getImage(latin):
  """
  Gets the image path for a species
  """
  jpg = getImagePath(latin, "jpg")
  if os.path.exists(jpg):
    return jpg
  png = getImagePath(latin, "png")
  if os.path.exists(png):
    return png
  svg = getImagePath(latin, "svg")
  if os.path.exists(svg):
    return svg
  return "html/images/missing.svg"

def getImagePath(latin, ext):
  """
  Gets a plausible image path for a species and an extension
  """
  return f"html/images/{'_'.join(latin.split())}.{ext}"

def load_species(path):
  """
  Loads the original species.tsv files
  """
  species = []
  with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")  # uses header row as keys
    for row in reader:
      species.append(row)
  return species

def listAllSpecies():
  """
  Loads all the species, to display them
  """
  allspecies = load_species("data/species.tsv")
  output = "data/allSpecies.html"
  with open(output, "w", encoding="utf-8") as f:
    f.write("<div class=\tree\">Nothing</div>")
    printList(f, allspecies, "1")
  return "ok"

def getColumnNames(parameters):
  """
  List columns to consider depending on selected parameters
  """
  if parameters.get("speciesset") == "fruits":
      return ["Fruits"] 
  if parameters.get("speciesset") == "australie":
      return ["Mam", "Mars"]
  if parameters.get("speciesset") == "ferme":
      return ["Ferme"] 
  if parameters.get("speciesset") == "foret":
      return ["Foret"] 
  if parameters.get("speciesset") == "beach":
      return ["mer"] 
  if parameters.get("speciesset") == "primate":
      return ["primate"] 
  if parameters.get("speciesset") == "cute":
      return ["cute"] 
  if parameters.get("speciesset") == "ugly":
      return ["ugly"] 
  if parameters.get("speciesset") == "dino":
      return ["Dino"] 
  if parameters.get("speciesset") == "maladie":
      return ["Maladie"] 
  ret = []
  if parameters.get("mam") == True:
    ret.append("Mam")
  if parameters.get("mars") == True:
    ret.append("Mars")
  if parameters.get("bird") == True:
    ret.append("Bird")
  if parameters.get("rep") == True:
    ret.append("Rep")
  if parameters.get("fish") == True:
    ret.append("Fish")
  if parameters.get("dino") == True:
    ret.append("Dino")
  if parameters.get("inv") == True:
    ret.append("Inv")
  if parameters.get("plan") == True:
    ret.append("Plan")
  if parameters.get("fung") == True:
    ret.append("Fung")
  if parameters.get("bact") == True:
    ret.append("Bact")    
  return ret

def filter_rows(table, columns):
  """
  Applies a filter on the original table, from a list of columns
  """
  return [
    row for row in table
    if any(row.get(col) == "1" for col in columns)
  ]

def random_integers(n, x):
  """
  Generates n distinct integer in [1;x]
  """
  #print(f"range nb:{n} from size:{x}")
  return random.sample(range(1, x + 1), int(n))

def select_rows(table, indices):
  """
  Keeps only the selected rows from a table
  """
  return [table[i - 1] for i in indices]