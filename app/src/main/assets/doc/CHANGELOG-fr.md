******

### Historique des versions

******

# v0.5.3

###### 2026/09/15

* `Amélioration` compileSdk passe à 37 (Android 17) ; targetSdk reste à 36 jusqu'à la vérification du comportement dépendant de la cible

# v0.5.2

###### 2026/09/13

* `Note` Candidat source stable 0.5.2; la validation finale sur appareil et la publication restent distinctes des résultats beta historiques
* `Correction` Corriger la lecture des fichiers de sortie sur Android 7 en conservant les protections des descripteurs et liens symboliques
* `Correction` Indiquer uniquement les ABI natives présentes dans l’APK installé
* `Correction` Utiliser des dates de compilation en anglais indépendamment de la langue de la machine

# v0.5.1

###### 2026/09/13

* `Note` Candidat source stable 0.5.1; la validation finale sur appareil et la publication restent distinctes des résultats beta historiques
* `Correction` Échec de la compilation Release après clean lorsque le fichier de règles ProGuard généré par Chaquopy est absent
* `Amélioration` Vérification à la compilation de l'alignement des pages de 16 KB des bibliothèques natives 64 bits, avec contrôle du contrat manifest et rapports JSON
* `Amélioration` Harmonisation de l'activation, des métadonnées, de la documentation traduite et de la collecte des APK signés

# v0.5.0

###### 2026/08/25

* `Note` 0.5.0 est le candidat source stable cumulatif ; le candidat beta exact signé SM003 a réussi les 10 tests Android, sans déclarer un APK stable, un tag ou une publication terminée
* `Fonction` M6 regroupe les capacités M1-M5 et les supports réutilisables des points 2/3/4, tout en fixant les limites légères alpha → beta → stable et de publication
* `Amélioration` L’APK arm64 0.5.0-beta.1 extrait de QV710AF65F est identique octet par octet au candidat officiel ; la seconde exécution complète donne 10/10 PASS

# v0.5.0-beta.1

###### 2026/08/25

* `Note` 0.5.0-beta.1 est un candidat source avec fonctionnalités gelées ; le candidat alpha exact signé SM003 a réussi les 10 tests Android, sans déclarer un APK beta, une version stable ou une publication terminée
* `Fonction` M6 ajoute des projets réutilisables pour les points 2/3/4 et un vérificateur artifact indépendant afin de valider de façon répétable les imports, stdin/saisie interactive et résultats structurés
* `Amélioration` L’APK arm64 0.5.0-alpha.6 extrait de QV710AF65F est identique octet par octet au candidat officiel ; la liste complète donne 10/10 PASS

# v0.5.0-alpha.6

###### 2026/08/25

* `Note` Sixième candidat alpha current-tree; compléter le contrat AutoJs6 WakeActivity pour la première activation du Plugin sur OnePlus OPD2413 et des OEM similaires, sans revendiquer de production signed candidate, de beta ni de publication
* `Correction` Déclarer `org.autojs.plugin.WAKE_ACTIVITY` et `org.autojs.plugin.action.WAKE` avec une Activity NoDisplay protégée par permission de signature et immédiatement terminée; `ACTIVATE` dans Plugin Center peut ainsi effacer `stopped/notLaunched` et retenter automatiquement l'activation
* `Amélioration` Reproduire puis corriger l'échec initial avec le Host debug `afca7b14c` et un Plugin de diagnostic au même signer, avec un résultat startup probe à `277 ms`; confirmer séparément qu'un signer différent échoue de façon fermée avec `PYTHON_RUNTIME_PROVIDER_UNTRUSTED`

# v0.5.0-alpha.5

###### 2026/08/25

* `Note` Cinquième candidat alpha current-tree; reconstruire les trois AAR release de la Host API depuis le commit clean exact `afca7b14c` avec des octets identiques et actualiser le provenance lock vers cette source, sans déclarer de signed APK, de smoke Android en dix points, de beta ni de publication
* `Amélioration` Exécuter Host `verifyPythonReleaseApiDistributionGate` dans un worktree isolé et figer AutoJs6 6.8.0/versionCode 5276, le protocole 1.6, le source fingerprint et le SHA-256 du distribution manifest avec `dirty=false`

# v0.5.0-alpha.4

###### 2026/08/25

* `Note` Quatrième candidat alpha current-tree ; M6 regroupe les étapes 0.2/0.3/0.4 non publiées dans un train cumulatif 0.5.0 sans revendiquer beta, version stable, signing ni publication
* `Fonction` Ajouter `tools/verify-m6-candidate.py` avec les profils explicites `--source-only` et `--full` pour contrôler clean Git, version, Changelog, documents générés et AAR lock, puis les tests portables, la porte R2 statique et un offline debug build
* `Amélioration` Définir une liste de smoke Android en 10 points et la promotion alpha → beta → 0.5.0 ; la porte locale n'exécute aucune opération ADB, signing, tag, push ou publication

# v0.5.0-alpha.3

###### 2026/08/24

* `Note` Troisième candidat alpha M5 current-tree ; les smokes Android ciblés long-running et FIFO Host passent sur QV710AF65F, et la mesure du démarrage écarte la rétention de processus sans revendiquer publication ni release
* `Amélioration` Mesurer cinq lancements fresh-process à 441/447/429/427/428 ms avec cinq PID Plugin distincts ; la médiane de tous les échantillons est 429 ms, celle sans le premier lancement 428.5 ms, et le maximum 447 ms
* `Amélioration` Clore l'évaluation du préchauffage sous le seuil de 1000 ms : conserver la retraite per-execution et ses sémantiques d'isolation/annulation au lieu d'ajouter une option keep-process

# v0.5.0-alpha.2

###### 2026/08/24

* `Note` Deuxième candidat alpha M5 current-tree ; la FIFO Host et les portes JVM/portables hors ligne passent, sans revendiquer de smoke Android concurrent, CPython réellement parallèle, préchauffage, publication ni release
* `Fonction` Admettre les lancements Python concurrents par une FIFO Host équitable avec un propriétaire actif et au plus 32 attentes avant la découverte du Provider ; Stop en file est interruptible sans liaison Plugin, consommation du timeout ni notification long-task anticipée
* `Amélioration` Conserver la liaison Provider jusqu'à 3 secondes après la fermeture d'une session dispatchée pour confirmer la retraite de génération avant la relève FIFO ; le protocole 1.6, les trois AAR et la limite Plugin mono-session sans file restent inchangés

# v0.5.0-alpha.1

###### 2026/08/24

* `Note` Premier candidat alpha M5 current-tree; le mode long-running foreground du protocole 1.6 et les gates JVM Host/Plugin hors ligne et portables passent, mais aucun smoke Android M5 n'a été exécuté et la publication, la concurrence et le préchauffage ne sont pas revendiqués
* `Fonction` Ajouter `executionMode=long-running` au niveau projet sans échéance, détenu par un service Host `specialUse` au premier plan, une notification persistante et l'action Stop; les lancements planifiés, background/Intent et développeur sont rejetés sans rétrogradation
* `Amélioration` Émettre des heartbeats Provider ordonnés toutes les 15 s et imposer des baux Host de 2 min au démarrage, 45 s entre heartbeats et un bail indépendant du service foreground; toute perte de vie et Stop échouent fermés par redémarrage du processus, tandis que le protocole borné 1.0-1.5 reste compatible

# v0.4.0-alpha.9

###### 2026/08/24

* `Note` Neuvième candidat alpha de l'arbre courant; clore M4 Path C native avec `NOT_ADMITTED`, conserver le runtime `stdlib-only`, n'ajouter aucun payload Pillow, NumPy, OpenCV ou native transitif et ne faire aucune nouvelle déclaration d'acceptation sur appareil
* `Amélioration` ADR 0004 consigne les debug builds offline dual ABI avec `--no-index --find-links`: Pillow 11.0.0 ajoute 2,054,483 bytes à chaque APK, NumPy 1.26.2 ajoute 21,931,164 bytes, et les six sorties passent `zipalign -c -P 16 4`
* `Amélioration` L'audit ELF NDK 29 de la clôture complète refuse FreeType à `0x1000` sur les deux ABI et OpenBLAS/libgfortran à `0x1000` sur x86_64; OpenCV n'a pas de wheel Android `cp313` officiel, et la réouverture exige des wheels NDK r28+ reproductibles et une acceptation publique 16 KiB

# v0.4.0-alpha.8

###### 2026/08/24

* `Note` Huitième candidat alpha de l'arbre courant; clore l'évaluation des paquets intégrés M4 Path B avec `NOT_ADMITTED`, conserver le runtime `stdlib-only`, n'ajouter ni `requests` ni aucune dépendance candidate et ne faire aucune nouvelle déclaration d'acceptation sur appareil
* `Amélioration` ADR 0003 fixe les bases stdlib-only debug APK à 23,709,688 bytes pour arm64-v8a, 23,726,048 bytes pour x86_64 et 34,622,039 bytes pour universal; aucun faux écart de taille sans wheelhouse hors ligne audité, et toute admission future exige Gradle `--offline`, `--no-index`, `--require-hashes`, les verrous licence/hash, les écarts des trois APK et une acceptation publique dual ABI

# v0.4.0-alpha.7

###### 2026/08/24

* `Note` Septième candidat alpha current-tree de l’automatisation M3 ; le flux Settings réel complet a réussi sur l’émulateur API 37, tandis que la publication, les chemins M4 B/C et la matrice complète des appareils restent hors de cette déclaration
* `Fonction` Ajout de `m3_complete_automation`, un flux Settings réel et borné utilisant `app.launch`, `selector.find`, `selector.click` et `images.capture_screen`, avec validation stricte du PNG et de l’inclusion du contrôle cible
* `Correction` Normalisation avant sérialisation Python des limites d’accessibilité avec `right < left` ou `bottom < top` en axes zero-area ancrés, tandis que les requêtes selector exactes isolent les nœuds sans rapport
* `Amélioration` Le chemin de projet public `RunIntentActivity` exporté réussit sur un émulateur API 37 avec un PNG 1080x2424 et un artefact vérifié par SHA-256, puis l’accessibilité est restaurée à 0/null et tous les staging de test exacts sont supprimés

# v0.4.0-alpha.6

###### 2026/08/24

* `Note` Sixième candidat alpha current-tree de l'automatisation M3; la reconnaissance OCR Host configurée a réussi sur un émulateur API 37 doté d'un service éligible et a échoué de façon fermée sur un appareil physique API 31 sans modifier ses services d'accessibilité; l'OCR enrichi, la publication et une matrice complète restent hors de cette déclaration
* `Fonction` Ajouter `autojs6.ocr.recognize(image)` pour des octets PNG/JPEG bornés et un tuple immuable et ordonné de lignes issu du moteur OCR Host configuré
* `Amélioration` Réutiliser l'upload PNG/JPEG de 1 MiB en blocs bruts de 24 KiB avec vérification SHA-256, ne sélectionner qu'un service OCR Host activé, autorisé et compatible, limiter le résultat à 256 lignes, 4 KiB d'UTF-8 strict par ligne et 48 KiB au total, toujours release et effacer les tampons, et signaler de façon stable `OCR_UNAVAILABLE` ou `OCR_FAILED`

# v0.4.0-alpha.5

###### 2026/08/24

* `Note` Cinquième candidat alpha d'automatisation M3 de l'arbre courant; la recherche bornée par modèle a réussi sur un émulateur API 37 avec accessibilité et a échoué de façon fermée sur un appareil physique API 31 sans modifier ses services d'accessibilité; OCR, publication et matrice complète restent hors de cette affirmation
* `Fonction` Ajouter `autojs6.images.find_image(template, *, region=None, threshold=0)` pour des octets PNG/JPEG, une région bornée facultative et un résultat coordonnée supérieure gauche ou `None`
* `Amélioration` Charger un modèle par exécution jusqu'à 1 MiB en blocs bruts de 24 KiB avec vérification SHA-256, décoder au plus 2048 pixels par côté, parcourir de façon déterministe en row-major sous `autojs6-python-image-match-v1`, faire participer les pixels totalement opaques et traiter les autres comme jokers, ne pas dépendre d'OpenCV, toujours release puis effacer les tampons, et ne réessayer que la limite Android de 333 ms après une attente bornée de 350 ms

# v0.4.0-alpha.4

###### 2026/08/24

* `Note` Quatrième candidat alpha d'automatisation M3 de l'arbre actuel; la recherche de couleur bornée a réussi sur un émulateur API 37 avec accessibilité et échoué de façon fermée sur un appareil API 31 sans modifier ses services; recherche par modèle, OCR, publication et matrice complète restent hors de cette déclaration
* `Fonction` Ajouter `autojs6.images.find_color(color, *, region=None, threshold=0)` pour un entier RGB strict ou un texte `#RRGGBB`, une région bornée facultative et un résultat coordonnée ou `None`
* `Amélioration` Capturer un nouvel écran d'accessibilité Android 11+ par appel, le parcourir dans un ordre row-major déterministe avec un seuil par canal de 0 à 255, valider exactement `autojs6-python-color-match-v1` et ne transférer aucun octet ni handle d'image vers Python

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
