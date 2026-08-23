******

### Historique des versions

******

# v0.4.0-alpha.3

###### 2026/08/24

* `Note` Troisième candidat alpha M3 d'automatisation de l'arbre courant; le parcours complet de capture d'écran bornée Android 11+ a réussi l'acceptation ciblée sur un émulateur API 37 avec accessibilité activée, et le fail-closed a réussi sur un appareil physique API 31 sans modifier ses services d'accessibilité; recherche d'image/couleur, OCR, publication et matrice complète restent hors de cette déclaration
* `Fonction` Ajout de `autojs6.images.capture_screen`, qui renvoie des octets PNG/JPEG vérifiés ou écrit et publie atomiquement un artefact de sortie d'exécution
* `Amélioration` Conserver au plus 1 capture par exécution, transférer des blocs bruts de 32 KiB et limiter les données encodées à 4 MiB; Python vérifie ordre, EOF, SHA-256 et signatures de format puis effectue toujours release, tandis que Host efface au remplacement/release/terminal et signale des erreurs stables sans activer de service ni ouvrir les paramètres

# v0.4.0-alpha.2

###### 2026/08/24

* `Note` Deuxième candidat alpha M3 d'automatisation de l'arbre courant; le parcours selector/arbre UI borné complet a réussi l'acceptation ciblée sur un émulateur API 37 avec accessibilité activée, et le fail-closed a réussi sur un appareil physique API 31 sans modifier ses services d'accessibilité; captures, OCR, publication et matrice complète restent hors de cette déclaration
* `Fonction` Ajouter les API live `autojs6.selector.snapshot/find/click/set_text` pour les données détachées de l'arbre d'accessibilité, les requêtes de première correspondance composées avec AND et les actions explicites via des références de node opaques liées à l'exécution
* `Amélioration` Borner les nodes, la profondeur, la charge et le texte des snapshots, la taille du parcours, le texte de requête/définition et les nodes conservés; signaler les parcours incomplets par `SELECTOR_SCAN_LIMIT_EXCEEDED`, les références obsolètes par `STALE_NODE` et l'accessibilité indisponible par `CapabilityUnavailableError` sans ouvrir les paramètres

# v0.4.0-alpha.1

###### 2026/08/23

* `Note` Premier candidat alpha M3 d'automatisation de l'arbre courant; les actions bornées par coordonnées/globales ont réussi l'acceptation ciblée sur un émulateur API 37 avec accessibilité activée et fail-closed a réussi sur un appareil physique API 31 sans modifier ses services d'accessibilité, tandis que selector/arbre UI, captures, OCR, publication et matrice complète restent hors de cette déclaration
* `Fonction` Ajouter les API temps réel `autojs6.automator.click/long_click/press/swipe/back/home` via l'accessibilité Host, avec retour du résultat booléen réel de l'envoi
* `Amélioration` Exiger des coordonnées entières strictes non booléennes de 0 à 1000000 et des durées press/swipe de 1 à 4000 ms; une accessibilité Host indisponible lève `CapabilityUnavailableError` sans ouvrir les paramètres

# v0.3.0-alpha.6

###### 2026/08/23

* `Note` Premier candidat alpha M4 de l'arbre courant; le chemin des dépendances Python pures locales au projet a réussi l'acceptation ciblée sur deux appareils, tandis que les lots M3/M4 suivants, la publication et une matrice complète restent hors de cette déclaration
* `Fonction` Prendre en charge les paquets Python purs locaux au projet et les métadonnées `.dist-info` depuis les racines admises, avec un exemple `requests` reproductible et verrouillé, sans installateur à l'exécution
* `Amélioration` Porter les limites du workspace à 64 MiB compressés, 8192 fichiers et 128 MiB extraits, puis comparer avant l'envoi les trois dimensions réelles du snapshot aux capacités du Provider; un import absent reste `ModuleNotFoundError`, sans pip en ligne ni repli de moteur

# v0.3.0-alpha.5

###### 2026/08/23

* `Note` Cinquième candidat alpha M3 de l'arbre courant; la partie Host engines bornée du deuxième lot a passé l'acceptation ciblée sur deux appareils, sans revendiquer les capacités suivantes, la publication ni une matrice complète d'appareils
* `Fonction` Ajout des API live `autojs6.engines.current/run/stop_self` pour les métadonnées du moteur courant sans chemin, le lancement asynchrone de scripts enfants Host non-Python et l'auto-arrêt déterministe
* `Amélioration` Accepter uniquement les chemins enfants normalisés relatifs à la racine d'exécution et au plus 16 lancements réussis par exécution; Python imbriqué échoue avec `NESTED_PYTHON_NOT_ALLOWED`, tandis que `stop_self` annule par redémarrage du processus provider

# v0.3.0-alpha.4

###### 2026/08/23

* `Note` Quatrième candidat alpha M3 de l'arbre courant; les dialogues Host au premier plan ont passé l'acceptation ciblée sur deux appareils, sans revendiquer engines, capacités suivantes, publication ni matrice complète d'appareils
* `Fonction` Ajouter les API réservées au premier plan `autojs6.dialogs.alert/confirm/prompt/select`, avec résultats typés pour acquittement, confirmation, texte nullable et index nullable à partir de zéro
* `Amélioration` Borner titres, contenus, réponses et éléments, sérialiser un dialogue détenu par Host à la fois et refuser les lancements en arrière-plan avec `INTERACTIVE_NOT_ALLOWED` sans ouvrir d'UI

# v0.3.0-alpha.3

###### 2026/08/23

* `Note` Troisième candidat alpha M3 de l'arbre courant; la partie Host files bornée du deuxième lot a passé l'acceptation ciblée sur deux appareils, sans revendiquer dialogues, engines, capacités suivantes, publication ni matrice complète d'appareils
* `Fonction` Ajouter les API en direct `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` pour l'accès borné au texte UTF-8 dans la racine du projet courant ou le dossier du script autonome
* `Amélioration` Refuser les chemins dangereux ou sortant de la racine, borner le texte et les listes directes, renvoyer des erreurs de fichier stables et distinguer la racine Host active du snapshot workspace Plugin figé

# v0.3.0-alpha.2

###### 2026/08/23

* `Note` Deuxième candidat alpha M3 de l'arbre courant; le premier lot complet de capacités Host à faible risque est implémenté, sans revendiquer les lots suivants, la publication ni une matrice complète d'appareils
* `Fonction` Ajouter les données batterie/écran/luminosité/volume en direct de `autojs6.device.info()`, les niveaux de console Host `autojs6.console.log/warn/error` et les notifications `autojs6.notice`
* `Amélioration` Valider strictement le schéma device et renvoyer un `PERMISSION_DENIED` stable sans ouvrir les réglages ni modifier les autorisations de l'appareil

# v0.3.0-alpha.1

###### 2026/08/23

* `Note` Premier candidat alpha M3 de l'arbre courant; le protocole 1.5 et le sous-ensemble de capacités Host à faible risque sont implémentés, sans revendiquer les capacités suivantes, la publication ni une matrice complète d'appareils
* `Fonction` Ajouter le broker de capacités Host du protocole 1.5, lié à l'exécution par JSON de données pures, UUID de requête, UID du plug-in, identifiants d'appel monotones, quota de 1024 appels, messages de 64 KiB et plafond de dispatch Host de 5 secondes
* `Fonction` Ajouter les API Host en direct `autojs6.toast`, `autojs6.clip.get/set` et `autojs6.app.launch/launch_app/open_url`
* `Amélioration` Révoquer le broker de façon uniforme à l'état terminal, à l'annulation, à la mort Binder et au nettoyage, avec des erreurs Python stables

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
