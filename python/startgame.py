import os
import csv
import random
from python import treehandler

##Entry point to prepare a session
def prepare(sessionID, wd, parameters):
  print(f"SessionID: {sessionID}")
  print(f"Working Dir: {wd}")
  for key, value in parameters.items():
    print(f"Param {key} ==> {value}")

  allspecies = load_species("data/species.tsv")  
  print(f"Loaded {len(allspecies)} species")

  output = os.path.join(wd, "game.html")

  filteredspecies = filter_rows(allspecies, getColumnNames(parameters))
  print(f"Filtered {len(filteredspecies)} species")

  #getnbspecies
  mode = parameters.get("gamemode")
  nbspecies = parameters.get("nbspecies")
  nbspecies = min(nbspecies, len(filteredspecies))

  workSpecies = select_rows(filteredspecies, random_integers(nbspecies, len(filteredspecies)))
  print(f"working {len(workSpecies)} species")

  treehandler.generate(wd, workSpecies)
  
  with open(output, "w", encoding="utf-8") as f:
    createGameHTML(f, sessionID, workSpecies, mode)

def listAllSpecies():
  allspecies = load_species("data/species.tsv")
  output = "data/allSpecies.html"
  with open(output, "w", encoding="utf-8") as f:
    f.write("<div class=\tree\">Nothing</div>")
    printList(f, allspecies, "1")
  return "ok"
  
##Writes the HTML code the session/game.html
def createGameHTML(f, sessionID, table, mode):
  printTree(f, sessionID)
  printList(f, table, mode)

def printTree(f, sessionID):
  f.write(f"<div id=\"{sessionID}\" class=\"tree\">")
  f.write(f" <img src=\"sessions/{sessionID}/tree.svg\" alt=\"thetree\" class=\"tile\"/>")
  f.write("</div>")

def printList(f, table, mode):
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

## Gets the image path for a species
def getImage(latin):
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

## Gets a plausible image path for a species and an extension
def getImagePath(latin, ext):
  return f"html/images/{'_'.join(latin.split())}.{ext}"

## Loads the original species.tsv files
def load_species(path):
  species = []
  with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")  # uses header row as keys
    for row in reader:
      species.append(row)
  return species

## List columns to consider depending on selected parameters
def getColumnNames(parameters):
  if parameters.get("speciesset") == "fruits":
      return ["Fruits"] 
  if parameters.get("speciesset") == "australie":
      return ["Mam", "Mars"]
  if parameters.get("speciesset") == "ferme":
      return ["Ferme"] 
  if parameters.get("speciesset") == "foret":
      return ["Foret"] 
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

# Applies a filter on the original table, from a list of columns
def filter_rows(table, columns):
  return [
    row for row in table
    if any(row.get(col) == "1" for col in columns)
  ]

# Generates n distinct integer in [1;x]
def random_integers(n, x):
  return random.sample(range(1, x + 1), n)

# Keep only the selected rows from a table
def select_rows(table, indices):
  return [table[i - 1] for i in indices]