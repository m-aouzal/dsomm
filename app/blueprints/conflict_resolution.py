# file: app/blueprints/conflict_resolution.py

from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os

###############################################################################
# Définition du Blueprint
###############################################################################
conflict_resolution = Blueprint("conflict_resolution", __name__)

###############################################################################
# Emplacements des fichiers JSON
###############################################################################
DATA_FOLDER = "./data"
USER_RESPONSES_FILE = os.path.join(DATA_FOLDER, "user_responses.json")
LEVEL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "level_activities.json")
TOOL_ACTIVITIES_FILE = os.path.join(DATA_FOLDER, "tool_activities.json")
PIPELINE_ORDER_FILE   = os.path.join(DATA_FOLDER, "pipeline_order.json")

###############################################################################
# Fonctions utilitaires de chargement et sauvegarde JSON
###############################################################################
def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[DEBUG] Fichier introuvable : {path}. Retour d'un dict vide.")
        return {}

def save_json(path, data):
    print(f"[DEBUG] Sauvegarde des données dans {path} :\n", json.dumps(data, indent=2, ensure_ascii=False))
    with open(path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

###############################################################################
# ROUTE PRINCIPALE : RESOLUTION DES CONFLITS
###############################################################################
@conflict_resolution.route("/", methods=["GET", "POST"])
def resolve_conflict():
    """
    Processus global de détection et résolution de conflits (en français).
    
    (1) Lecture des données de la session.
    (2) Construction de la liste cumulative des activités pour les niveaux 1..selected_level.
    (3) Application des outils pour marquer couverture ou conflits.
    (4) Affichage du formulaire de résolution de conflit pour les activités dont le statut est "temporary".
    (5) Traitement POST : application des choix de l'utilisateur. Si plus aucun conflit n'est détecté,
        rediriger vers la page de résumé, sinon recharger la page de résolution pour résoudre les conflits restants.
    """
    # --- PHASE 1 : Lecture de la session
    chosen_level  = session.get("security_level", "1")
    chosen_stages = session.get("stages", [])
    stage_tools   = session.get("tools", {})  # { étape : {"standard": [], "custom": []} }

    print("[DEBUG] Lancement du resolve_conflict.")
    print("[DEBUG] Niveau choisi :", chosen_level)
    print("[DEBUG] Étapes choisies :", chosen_stages)
    print("[DEBUG] Outils choisis (par étape) :", json.dumps(stage_tools, indent=2, ensure_ascii=False))

    if not chosen_stages or not chosen_level:
        print("[DEBUG] Pas de level ou de stages dans la session. Redirection vers stages.")
        return redirect(url_for("stages.select_stages"))

    # --- PHASE 2 : Construction des activités 1..N
    level_acts_data = load_json(LEVEL_ACTIVITIES_FILE)
    activities = _build_activities_for_levels(chosen_level, level_acts_data)

    print("[DEBUG] Liste des activités initiales (status=unimplemented) :")
    for a in activities:
        print("    ", a)

    # On charge la mapping tool->activities et pipeline_order
    tool_acts_data = load_json(TOOL_ACTIVITIES_FILE)
    pipeline_order_data = load_json(PIPELINE_ORDER_FILE)

    # On applique la logique de couverture => détection de conflits
    _apply_tools_to_activities(activities, chosen_stages, stage_tools, tool_acts_data, pipeline_order_data)

    print("[DEBUG] Activités après application couverture / conflits :")
    for a in activities:
        print("    ", a)

    _debug_temporary_activities(activities)

    # --- PHASE 3 & 4 : Résolution des conflits par l'utilisateur
    if request.method == "POST":
        print("[DEBUG] Form POST reçu:", dict(request.form))
        for idx, act_item in enumerate(activities):
            chosen_list = request.form.getlist(f"choice_{idx}")
            new_custom_tool = request.form.get(f"new_custom_{idx}")
            print(f"[DEBUG] Activité Index={idx}, liste choix={chosen_list}, Nouvel outil custom={new_custom_tool}")

            if "none" in chosen_list:
                act_item["status"] = "unimplemented"
                act_item["tools"]  = {}
                act_item["custom"] = []
            else:
                if not chosen_list:
                    act_item["status"] = "unimplemented"
                    act_item["tools"]  = {}
                    act_item["custom"] = []
                else:
                    act_item["status"] = "implemented"
                    for t_name in list(act_item["tools"].keys()):
                        if t_name in chosen_list:
                            act_item["tools"][t_name] = "checked"
                        else:
                            del act_item["tools"][t_name]
                    for i in range(len(act_item["custom"]) - 1, -1, -1):
                        c_tool = act_item["custom"][i]
                        if c_tool not in chosen_list:
                            act_item["custom"].pop(i)
                    if new_custom_tool:
                        new_custom_tool = new_custom_tool.strip()
                        if new_custom_tool and new_custom_tool not in act_item["custom"]:
                            act_item["custom"].append(new_custom_tool)

        # PHASE 5 : Sauvegarde finale
        user_responses = {
            "selected_level": chosen_level,
            "stages": chosen_stages,
            "tools": stage_tools,
            "activities": activities
        }
        save_json(USER_RESPONSES_FILE, user_responses)

        print("[DEBUG] Conflits résolus / Sauvegarde terminée.")
        # Check s'il reste des conflits (status temporary)
        remaining_conflicts = [act for act in activities if act.get("status") == "temporary"]
        if remaining_conflicts:
            print("[DEBUG] Conflits restants :", remaining_conflicts)
            return redirect(url_for("conflict_resolution.resolve_conflict"))
        else:
            print("[DEBUG] Aucun conflit restant, redirection vers le résumé final.")
            return redirect(url_for("summary.display_summary"))

    # Pour GET : on filtre pour n'afficher que les activités avec status temporary
    temp_activities = [act for act in activities if act.get("status") == "temporary"]

    return render_template("conflict_resolution.html", activities=temp_activities)

###############################################################################
# FONCTIONS UTILITAIRES
###############################################################################
def _build_activities_for_levels(chosen_level_str, level_acts_data):
    """
    Construit la liste d'activités pour les niveaux 1..N (N=chosen_level_str).
    Chaque activité est un dict avec:
    { "activity": ..., "description": ..., "status": "unimplemented", "custom": [], "tools": {} }
    """
    try:
        max_lvl = int(chosen_level_str)
    except ValueError:
        max_lvl = 1

    results = []
    for lvl in range(1, max_lvl + 1):
        level_key = str(lvl)
        lvl_list = level_acts_data.get(level_key, [])
        print(f"[DEBUG] Niveau={lvl}, nb activités trouvées: {len(lvl_list)}")
        for act_obj in lvl_list:
            results.append({
                "activity": act_obj.get("Activity", f"ActivitéSansNom-L{lvl}"),
                "description": act_obj.get("Description", ""),
                "status": "unimplemented",
                "custom": [],
                "tools": {}
            })
    return results

def _apply_tools_to_activities(activities, chosen_stages, stage_tools, tool_acts_data, pipeline_order_data):
    """
    Pour chaque étape, on combine les outils standard et custom,
    on lit tool_acts_data pour obtenir la liste des activités couvertes par chaque outil.
    S'il y a déjà un outil "checked" et qu'un autre outil couvre la même activité, on marque tous
    en "temporary" pour signaler un conflit.
    Si l'outil est custom, on l'ajoute dans la liste "custom" de l'activité.
    """
    act_map = {a["activity"]: a for a in activities}

    for stage in chosen_stages:
        st_data = stage_tools.get(stage, {"standard": [], "custom": []})
        all_std_tools = st_data.get("standard", [])
        all_custom_tools = st_data.get("custom", [])
        all_tools = all_std_tools + all_custom_tools

        print(f"[DEBUG] Étape='{stage}', Outils totaux : {all_tools}")

        # Création de l'union des activités couvertes par les outils standards pour cette étape
        standard_union = set()
        for std_tool in all_std_tools:
            if std_tool == "none":
                continue
            std_info = tool_acts_data.get(std_tool, {})
            for act_obj in std_info.get("Activities", []):
                act_name = act_obj.get("Activity")
                if act_name:
                    standard_union.add(act_name)

        for tool_name in all_tools:
            if tool_name == "none":
                continue

            tool_info = tool_acts_data.get(tool_name)
            if not tool_info:
                print(f"[DEBUG] L'outil '{tool_name}' n'est pas trouvé dans tool_activities.json")
                continue

            # Obtenir la couverture via la liste "Activities"
            covered = set()
            for act_obj in tool_info.get("Activities", []):
                act_name = act_obj.get("Activity")
                if act_name:
                    covered.add(act_name)

            # Si l'outil est custom, on fusionne la couverture standard
            if tool_name in all_custom_tools:
                covered = covered.union(standard_union)

            print(f"[DEBUG] Outil='{tool_name}' couvre {len(covered)} activités : {covered}")

            for act_name in covered:
                if act_name not in act_map:
                    continue
                act_item = act_map[act_name]
                if not act_item["tools"]:
                    act_item["tools"][tool_name] = "checked"
                    act_item["status"] = "implemented"
                    print(f"[DEBUG] Activité '{act_name}' : 1er outil '{tool_name}' -> checked")
                else:
                    if tool_name not in act_item["tools"]:
                        act_item["tools"][tool_name] = "temporary"
                        print(f"[DEBUG] Activité '{act_name}' : ajout de '{tool_name}' en temporary (conflit)")
                    # Convertir tous les existants "checked" en "temporary"
                    for exist_tool in list(act_item["tools"].keys()):
                        if act_item["tools"][exist_tool] == "checked":
                            act_item["tools"][exist_tool] = "temporary"
                    act_item["status"] = "temporary"

                if tool_name in all_custom_tools and tool_name not in act_item["custom"]:
                    act_item["custom"].append(tool_name)

def _debug_temporary_activities(activities):
    """
    Affiche des messages de debug pour toutes les activités ayant status='temporary'
    et les outils associés.
    """
    print("[DEBUG] Vérification des activités en 'temporary' :")
    temporary_acts = [a for a in activities if a.get("status") == "temporary"]
    if not temporary_acts:
        print("    Aucune activité 'temporary' détectée.")
        return

    for act in temporary_acts:
        print(f"    [DEBUG] Activité TEMPORAIRE: {act['activity']}")
        print(f"           - Description: {act.get('description', 'N/A')}")
        print(f"           - Custom Tools: {act['custom']}")
        if act["tools"]:
            print("           - Outils dans 'tools':")
            for t_name, t_status in act["tools"].items():
                print(f"               * {t_name} : {t_status}")
        else:
            print("           - Aucune entrée dans 'tools'.")
