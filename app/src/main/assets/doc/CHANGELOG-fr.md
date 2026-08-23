******

### Historique des versions

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Note` Candidat alpha U1 de l'arbre courant postérieur à 0.1; l'entrée module, la sortie live, le input intégré au premier plan, le JSON structuré explicite et les artefacts bornés de U1-R2 ne sont couverts que jusqu'à E2; les lancements en arrière-plan et sys.stdin direct restent non interactifs, R2 E3 reste ouvert et ces résultats ne prouvent ni matrice d'appareils, ni livraison, ni publication
* `Fonction` Ajout d'un snapshot stdin fini et préfourni de 1 MiB au plus pour une entrée et une EOF déterministes avec `input()` et `sys.stdin`
* `Fonction` Finalisation des imports projet pour les modules workspace, les modules voisins et racine d'une entrée imbriquée, et les imports relatifs au package
* `Fonction` Ajout du protocole 1.2 avec `entryMode=file|module` explicite; l'exécution module emploie `runpy` avec `__package__`, `__spec__`, la racine du projet dans `sys.path[0]` et les imports relatifs corrects, tandis que le mode file reste inchangé
* `Fonction` Ajout avec le protocole 1.3 d'un prompt/réponse borné au premier plan après l'EOF du snapshot fini, avec saisie visible pour le `input()` intégré et masquée pour `getpass.getpass()`; les lancements en arrière-plan n'ouvrent jamais d'interface de saisie et `sys.stdin` direct reste fini
* `Fonction` Ajout avec le protocole 1.4 de résultats JSON stricts explicites et d'artefacts facultatifs bornés par nombre, chemin normalisé, taille par fichier/totale, références PFD exactes et SHA-256, sans jamais déduire un résultat de stdout
* `Correction` Décodage de la source en UTF-8 strict avant exécution afin qu'un encoding cookie non UTF-8 ne contourne plus le contrat
* `Amélioration` Accorder `INTERNET` afin que les scripts de confiance utilisent directement les clients réseau de la bibliothèque standard, tout en maintenant pip en ligne et le téléchargement automatique de code désactivés
* `Amélioration` Porter la limite d'exécution du Provider à 30 minutes et la sortie bornée à 16 MiB / 16384 chunks
* `Amélioration` Déplacement des chunks stdout/stderr bornés et de la contre-pression par crédits dans l'exécution du script, avec conservation de la sortie partielle ordonnée avant l'état terminal et interdiction après celui-ci
* `Amélioration` Utilisation d'un `__main__` indépendant par exécution et restauration de stdin/stdout/stderr, argv, cwd, `sys.path`, des modules et du cache d'importeurs
* `Amélioration` Application d'un lease de 5 secondes à une session ouverte mais jamais démarrée, puis libération des entrées, descriptors et de l'emplacement de session unique
* `Amélioration` Application du Host versionCode minimal 5275 à la frontière Binder du Provider au lieu de dépendre uniquement de la découverte côté Host

# v0.1.0

###### 2026/08/12

* `Note` La version 0.1.0 fixe l'identité source stable du Plugin et le lock Host exact 6.8.0/5275
* `Fonction` Protocole Python 1.0-1.1 associé à AutoJs6 6.8.0 / versionCode 5275, workspace projet borné et snapshots app/device/execution/project en lecture seule
* `Fonction` Hot-plug sans redémarrage hôte: installation ou réactivation permet à la prochaine exécution de redécouvrir et épingler l'identité, sans fallback si absent ou désactivé
* `Fonction` La mort Binder en cours termine l'exécution sans replay; les nouvelles exécutions redécouvrent le provider
* `Amélioration` Chaquopy est fixé comme runtime trusted-local et non-sandbox; SM003 est le signer à long terme et SuperMonster003 possède runtime, sécurité et release
* `Dépendance` Verrouillage de Chaquopy 17.0.0 et CPython 3.13.9; les APK stables sont liés à l'identité source finale et vérifiés comme artefacts exacts

# v0.1.0-alpha.1

###### 2026/08/09

* `Note` Sources de preuve de concept R2; Gradle, APK, Binder et appareil ne sont pas validés
* `Fonction` Scaffold provider Python V1 indépendant avec processus dédié, une session active et aucune file provider
* `Fonction` Exécution `__main__` d'une source, stdout/stderr bornés, exceptions structurées et annulation par redémarrage
* `Fonction` Génération ordonnée des README et journaux intégrés en 10 langues
* `Dépendance` Présélection de Chaquopy 17.0.0 et Python 3.13; versions et hashes restent à vérifier par construction
