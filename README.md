Résumé : Application DSOMM COMPASS - Guide pour la Sélection d'Outils DevSecOps

L'application DSOMM COMPASSest un outil web interactif conçu pour accompagner les organisations dans la mise en place d'une chaîne d'outillage DevSecOps alignée sur le modèle de maturité DSOMM (DevSecOps Maturity Model). Elle propose une approche structurée et personnalisable pour la sélection d'outils, en guidant les utilisateurs à travers plusieurs phases clés :

Définition du Périmètre : L'utilisateur commence par définir ses besoins en sélectionnant un niveau de sécurité (de 1 à 5) et les étapes pertinentes de son cycle de vie de développement logiciel (SDLC) parmi une liste prédéfinie de 26 stages.

Sélection d'Outils : Pour chaque étape choisie, l'application propose une liste d'outils standards issus d'une base de données enrichie, basée sur le modèle DSOMM. L'utilisateur peut sélectionner un ou plusieurs outils, ou ajouter des outils personnalisés. Un fichier stage_defaults.json associe des activités par défaut à chaque étape, facilitant l'intégration des outils personnalisés.

Résolution des Conflits : L'application détecte automatiquement les conflits potentiels, où plusieurs outils sont capables d'implémenter une même activité. Une interface dédiée permet à l'utilisateur de résoudre ces conflits en choisissant un outil préféré, en validant l'utilisation de plusieurs outils, ou en ajoutant un nouvel outil personnalisé.

Analyse des Écarts (Gap Analysis) : Cette phase vise à identifier les activités non encore couvertes par des outils ("unimplemented"). L'application présente ces activités une par une, suggère des outils standards pertinents et offre une section "Mes Outils" regroupant les outils déjà sélectionnés par l'utilisateur ainsi que ses outils personnalisés. L'utilisateur peut alors choisir un outil, ajouter un nouvel outil personnalisé, ou confirmer que l'activité ne sera pas implémentée ("unimplemented_confirmed"). Les conflits potentiels générés durant cette phase sont résolus après coup.

Confirmation des Activités "Checked" : Une étape de validation finale permet à l'utilisateur de revoir et de confirmer les activités marquées comme "checked" (c'est-à-dire celles pour lesquelles des outils ont été sélectionnés, mais qui n'ont pas encore été confirmées comme étant implémentées). L'utilisateur peut ici valider ses choix, les modifier, ou marquer une activité comme "unimplemented_confirmed".

Génération de Rapports : L'application génère un résumé synthétique des choix de l'utilisateur, incluant le niveau de sécurité, les étapes sélectionnées, les outils choisis et le statut final de chaque activité ("implemented", "unimplemented_confirmed", "policy"). Un rapport complet, enrichi d'informations issues du modèle DSOMM, est également disponible sur demande.

Points forts de l'application:

Guidage structuré et alignement DSOMM : L'application suit une méthodologie claire basée sur le modèle de maturité DSOMM.
Flexibilité et personnalisation : L'utilisateur peut adapter le processus à ses besoins spécifiques en sélectionnant son niveau de sécurité, les étapes de son SDLC, et en ajoutant des outils personnalisés.
Gestion des conflits : Les conflits potentiels entre outils sont identifiés et résolus de manière interactive.
Analyse des écarts (Gap Analysis) : Une phase dédiée permet d'identifier et de combler les lacunes dans la couverture DevSecOps.
Liste "Mes Outils" : Un accès rapide aux outils déjà sélectionnés, y compris les outils personnalisés, facilite les choix ultérieurs.
Confirmation finale : Une étape de validation permet de s'assurer que les choix finaux correspondent aux intentions de l'utilisateur.
Rapports détaillés : Des rapports clairs et complets facilitent la compréhension et la mise en œuvre des choix effectués.
En somme, l'application DSOMM se présente comme un outil précieux pour les organisations souhaitant améliorer leur maturité DevSecOps en sélectionnant et en intégrant des outils de manière cohérente et alignée sur leurs besoins spécifiques.

TO RUN THE APP :

1. Clone the repository
2. Install the dependencies
3. Run the app with the command : cd app && flask run
