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
import sys

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

    try:

        tax_ids = request.json.get(
            "tax_ids",
            []
        )

        print("\n" + "=" * 60)
        print("NOUVEAU TIRAGE")
        print("=" * 60)

        print(
            f"Nombre de taxons reçus : {len(tax_ids)}"
        )

        print(
            "Taxons :"
        )

        for t in tax_ids:
            print("  -", t)

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

        input_tree = request.json.get(
            "input_tree",
            "taxid.nwk"
        )

        allowed_trees = {
            "taxid.nwk",
            "linear_test.nwk"
        }

        if input_tree not in allowed_trees:
            input_tree = "taxid.nwk"

        cmd = [
            sys.executable,
            "prune.py",

            "-i",
            input_tree,

            "-o",
            os.path.join(
                session_dir,
                "extract.nwk"
            ),

            "-s",
            session_dir,

            "-t"
        ] + tax_ids

        print("\nCommande exécutée :")
        print(" ".join(cmd))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=base_dir
        )

        print("\nCode retour :")
        print(result.returncode)

        if result.stdout:

            print("\nSTDOUT :")
            print(result.stdout)

        if result.stderr:

            print("\nSTDERR :")
            print(result.stderr)

        if result.returncode != 0:

            print(
                "\nERREUR prune.py"
            )

            return {
                "error":
                result.stderr
            }, 500

        print(
            "\nFichiers générés :"
        )

        fichiers = [
            "tree.png",
            "solution.png",
            "mapping.json",
            "equivalents.json",
            "clades.json"
        ]

        for fichier in fichiers:

            path = os.path.join(
                session_dir,
                fichier
            )

            print(
                fichier,
                "->",
                os.path.exists(path)
            )

        mapping_path = os.path.join(
            session_dir,
            "mapping.json"
        )

        if os.path.exists(mapping_path):

            import json

            with open(
                mapping_path,
                encoding="utf-8"
            ) as f:

                mapping = json.load(f)

            print("\nRÉPONSES DU QUIZ :")

            for numero, taxid in mapping.items():

                print(
                    f"{numero} -> {taxid}"
                )

        print(
            "\nSession :",
            session_id
        )

        print("=" * 60)

        return {

            "session":
            session_id,

            "tree":
            f"/sessions/{session_id}/tree.png",

            "solution":
            f"/sessions/{session_id}/solution.png",

            "mapping":
            f"/sessions/{session_id}/mapping.json",

            "equivalents":
            f"/sessions/{session_id}/equivalents.json",

            "clades":
            f"/sessions/{session_id}/clades.json"
        }

    except Exception as e:

        import traceback

        print("\nERREUR FLASK")
        print(traceback.format_exc())

        return {
            "error": str(e)
        }, 500
    
# =========================
# Gestion erreurs Flask
# =========================

@app.errorhandler(404)
def error404(e):

    print(
        "\n[404] Ressource introuvable :",
        request.url
    )

    return {
        "error": "404 Not Found"
    }, 404


@app.errorhandler(500)
def error500(e):

    print(
        "\n[500] Erreur interne serveur"
    )

    return {
        "error":
        "500 Internal Server Error"
    }, 500


@app.errorhandler(Exception)
def error_generique(e):

    import traceback

    print(
        "\n[EXCEPTION NON GÉRÉE]"
    )

    print(
        traceback.format_exc()
    )

    return {
        "error": str(e)
    }, 500
# =========================
# Lancement Flask
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

# =========================
# Erreurs Flask globales
# =========================

@app.errorhandler(404)
def erreur404(e):

    print(
        "\nERREUR 404 :",
        request.path
    )

    return {
        "error":
        "404 Not Found",
        "path":
        request.path
    }, 404


@app.errorhandler(500)
def erreur500(e):

    print(
        "\nERREUR 500"
    )

    import traceback
    traceback.print_exc()

    return {
        "error":
        "500 Internal Server Error"
    }, 500