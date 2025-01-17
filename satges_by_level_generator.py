import json

def load_json(filename):
    """Charge le contenu d'un fichier JSON."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def aggregate_tools(level_data):
    """
    Parcourt les niveaux de manière cumulative et agrège les outils.
    Retourne un dictionnaire dont la clé est le niveau (en tant que chaîne) et
    la valeur est un ensemble d'outils cumulés jusqu'à ce niveau.
    """
    cumulative_tools = {}  # dictionnaire {niveau: set(outils)}
    tools_set = set()

    # On trie les niveaux par ordre numérique croissant.
    niveaux = sorted(level_data.keys(), key=lambda x: int(x))
    
    for niveau in niveaux:
        activities = level_data[niveau]
        for activity in activities:
            # Pour chaque activité, récupère la liste des outils
            for tool in activity.get("Tools", []):
                # On ajoute le nom de l'outil dans l'ensemble cumulatif
                tools_set.add(tool.get("Name"))
        # On stocke une copie de l'ensemble pour ce niveau cumulatif
        cumulative_tools[niveau] = tools_set.copy()
    
    return cumulative_tools

def map_levels_to_stages(cumulative_tools, pipeline_data):
    """
    Pour chaque niveau (avec ses outils cumulés), vérifie pour chaque étape de la pipeline
    si l'un des outils de cette étape est présent dans l'ensemble des outils cumulés.
    Retourne un dictionnaire associant "Level X" à la liste des étapes trouvées.
    """
    mapping = {}
    # On s'appuie sur le même ordre que les niveaux utilisés
    niveaux = sorted(cumulative_tools.keys(), key=lambda x: int(x))
    
    for niveau in niveaux:
        outils_cumules = cumulative_tools[niveau]
        stages_included = []
        for stage_info in pipeline_data.get("pipeline", []):
            stage_name = stage_info.get("stage")
            # Pour l'étape, on récupère la liste des outils associés
            stage_tools = stage_info.get("tools", [])
            # Si au moins un outil de l'étape figure dans les outils cumulés, on ajoute l'étape.
            if any(tool in outils_cumules for tool in stage_tools):
                stages_included.append(stage_name)
        # On indexe le mapping avec "Level X" pour plus de clarté
        mapping[f"Level {niveau}"] = stages_included
    
    return mapping

def main():
    # Charger les deux fichiers JSON
    level_activities_file = "level_activities.json"
    pipeline_order_file = "pipeline_order.json"
    
    level_data = load_json(level_activities_file)
    pipeline_data = load_json(pipeline_order_file)
    
    # Etape 1 : Agrégation cumulative des outils pour chaque niveau.
    cumulative_tools = aggregate_tools(level_data)
    
    # Etape 2 : Mapping des niveaux aux étapes de la pipeline en fonction des outils.
    result_mapping = map_levels_to_stages(cumulative_tools, pipeline_data)
    
    # Etape 3 : Génération du fichier JSON de sortie
    output_file = "output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_mapping, f, indent=4, ensure_ascii=False)
    
    print(f"Le fichier '{output_file}' a été généré avec succès.")

if __name__ == "__main__":
    main()
