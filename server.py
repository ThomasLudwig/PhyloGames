from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def accueil():
    return render_template("Phylo.html")

@app.route("/prune", methods=["POST"])
def prune():

    tax_ids = request.json.get("tax_ids", [])

    cmd = [
        "py", "-3.11",
        "prune.py",
        "-i", "taxid.nwk",
        "-o", "extract.nwk",
        "-t"
    ] + tax_ids

    subprocess.run(cmd, capture_output=True, text=True)

    return {"image": "/static/tree.png"}

if __name__ == "__main__":
    app.run(port=5000, debug=True)