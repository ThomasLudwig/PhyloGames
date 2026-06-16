from flask import (
    Flask,
    render_template,
    request,
    send_file
)

import subprocess
import os
import time
import random
import string

app = Flask(__name__)
# =========================
# Fichiers de session
# =========================

@app.route(
    "/sessions/<session_id>/<filename>"
)
def session_files(
    session_id,
    filename
):

    return send_file(
        os.path.join(
            "sessions",
            session_id,
            filename
        )
    )
# =========================
# Génération session
# =========================

def get_session_id():

    epoch = str(int(time.time()))

    rnd = "".join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=4
        )
    )

    return epoch + rnd


# =========================
# CSV
# =========================

@app.route("/especes")
def especes():

    return send_file(
        "species_taxonomy_with_ott.csv"
    )


# =========================
# Accueil
# =========================

@app.route("/")
def accueil():

    return render_template(
        "Phylo.html"
    )


# =========================
# Prune
# =========================

@app.route(
    "/prune",
    methods=["POST"]
)
def prune():

    tax_ids = request.json.get(
        "tax_ids",
        []
    )

    session_id = get_session_id()

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    session_dir = os.path.join(
        base_dir,
        "sessions",
        session_id
    )

    os.makedirs(
        session_dir,
        exist_ok=True
    )

    cmd = [
        "py",
        "-3.11",
        "prune.py",

        "-i",
        "taxid.nwk",

        "-o",
        os.path.join(
            session_dir,
            "extract.nwk"
        ),

        "-s",
        session_dir,

        "-t"
    ] + tax_ids

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=base_dir
    )

    if result.returncode != 0:

        return {
            "error": result.stderr
        }, 500

    return {
        "session": session_id,

        "tree":
        f"/sessions/{session_id}/tree.png",

        "solution":
        f"/sessions/{session_id}/solution.png",

        "mapping":
        f"/sessions/{session_id}/mapping.json",

        "equivalents":
        f"/sessions/{session_id}/equivalents.json"
    }


if __name__ == "__main__":

    app.run(
        host=0000,
        port=5000,
        debug=True
    )