# src/diagram_generator.py

from typing import List

def generate_diagram(pipeline_stages: List[str], selected_tools: List[str], filename: str = "devops_diagram.txt"):
    """
    Génère un diagramme de pipeline DevOps linéaire avec uniquement les noms des outils.
    
    Args:
        pipeline_stages (List[str]): Les étapes du pipeline dans l'ordre.
        selected_tools (List[str]): Les outils sélectionnés par l'utilisateur.
        filename (str): Nom du fichier de sortie sans extension.
    """
    # Créer une représentation linéaire des outils
    if selected_tools:
        pipeline_str = " -> ".join(selected_tools)
    else:
        pipeline_str = "Aucun outil sélectionné."

    # Écrire la représentation dans un fichier texte
    with open(filename, "w", encoding='utf-8') as f:
        f.write("Pipeline DevSecOps:\n")
        f.write(pipeline_str)
    
    print(f"Le diagramme a été généré avec succès : {filename}")
