<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>Moteur Python indépendant. Exécute les scripts dans un processus de plug-in dédié</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Langues

******

Le fichier README.md actuel est disponible dans les langues suivantes:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- Français [fr] # actuel
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### Introduction

******

Python Runtime est un fournisseur indépendant du protocole Python V1. L'hôte transmet un instantané de source Python à un processus dédié, qui l'exécute avec CPython et renvoie une sortie bornée, des exceptions structurées et un seul état terminal.

> L'identité source 0.1.0 et le lock Host exact sont gelés. Les preuves RC locales de construction, APK, Binder et d'un appareil API 31 arm64-v8a restent historiques; la provenance APK/P3 stable est liée à l'identité release exacte, tandis qu'un production receipt constitue un niveau de preuve post-publication distinct.

******

### Fonctions

******

- Exécuter un instantané de source Python UTF-8 en tant que `__main__`.
- Accepter un snapshot stdin fini et préfourni de 1 MiB au maximum; après son EOF, un lancement explicite au premier plan peut poursuivre le `input()` intégré par le prompt/réponse borné du protocole 1.3, tandis que `getpass.getpass()` utilise une saisie masquée.
- Sélectionner explicitement `entryMode=file|module` pour un projet admis; le mode module emploie les métadonnées standard de `runpy`, la racine du projet dans `sys.path[0]` et les imports relatifs au package, tandis que le mode file conserve la sémantique d'un script ordinaire.
- Importer depuis la racine admise des paquets Python purs locaux au projet et leurs métadonnées `.dist-info`, sans pip en ligne ni installation à l'exécution.
- Livrer pendant l'exécution des chunks stdout/stderr bornés dans leur ordre d'origine; l'épuisement des crédits applique une contre-pression à l'exécution.
- Définir un résultat JSON strict explicite de 64 KiB au maximum et transférer jusqu'à 16 artefacts facultatifs sous les limites de chemin, taille et SHA-256 du protocole 1.4; ne jamais déduire un résultat de stdout.
- Appeler en direct `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, `notice` sensible aux autorisations, `files.read_text/write_text/exists/is_file/is_dir/list` borné, `dialogs.alert/confirm/prompt/select` réservé au premier plan, `engines.current/run/stop_self`, `automator.click/long_click/press/swipe/back/home` borné, `selector.snapshot/find/click/set_text` borné, `images.capture_screen`, `images.find_color`, `images.find_image` et `ocr.recognize` via le broker de données pures du protocole 1.5 lié à l'exécution, révoqué à l'état terminal.
- Le protocole 1.6 ajoute les projets explicites `executionMode=long-running` sans échéance d'exécution, avec notification Host de premier plan, action Stop et heartbeats Provider ordonnés toutes les 15 s; les surfaces d'arrière-plan échouent de façon fermée sans rétrogradation.
- Le Host associé admet les lancements Python concurrents par une FIFO équitable avant la découverte du Provider : un propriétaire actif et au plus 32 attentes; l'arrêt en file est interruptible et une génération dispatchée attend jusqu'à 3 s la sortie Binder avant la relève, tandis que le Provider reste mono-session sans file.
- Signaler `SystemExit`, les erreurs de syntaxe et les exceptions avec une traceback structurée bornée.
- Autoriser une session active par processus sans file d'attente côté fournisseur.
- Ne pas redémarrer l'hôte: la prochaine nouvelle exécution après installation ou réactivation redécouvre et épingle le provider; une mort Binder en cours termine cette exécution sans jamais la rejouer.

******

### Moteur et formats de données

******

Le protocole V1 déclare actuellement le périmètre suivant:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

La construction demande Python 3.13. Les artefacts RC locaux gelés et l'exécution exacte sur appareil ont enregistré CPython 3.13.9; la version et les hashes finaux de 0.1.0 devront être revérifiés après le gel des sources.

******

### Interface du plug-in

******

L'hôte découvre et appelle le plug-in avec les identités suivantes:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.6
```

Le plug-in accepte une SOURCE indépendante, une archive workspace bornée facultative, un snapshot stdin fini et préfourni de 1 MiB au maximum, et le snapshot en lecture seule des capacités hôte du protocole 1.1. Le protocole 1.2 ajoute la négociation explicite de l'entrée file/module pour les projets admis. Le protocole 1.3 ajoute, après l'EOF du snapshot, un prompt/réponse détenu par l'hôte et réservé au premier plan pour le `input()` intégré; `getpass.getpass()` utilise une saisie masquée. Le protocole 1.4 ajoute un JSON strict explicite et des artefacts facultatifs manifestés par SHA-256; stdout reste un diagnostic et n'est jamais analysé comme résultat. Le protocole 1.5 ajoute un broker hôte de données pures lié à une exécution, à l'UID du plug-in, à l'ordre des appels et à un quota fini. Les dialogues Host exigent aussi une autorisation de premier plan soutenue par une Activity active; un lancement en arrière-plan renvoie `INTERACTIVE_NOT_ALLOWED` sans ouvrir d'UI. `sys.stdin` direct reste fini, les lancements en arrière-plan n'ouvrent jamais d'interface de saisie et les scripts ne reçoivent aucun Context, Binder brut, objet d'exécution hôte ou callback sink.

******

### État de l'intégration hôte

******

> La version 0.1.0 est associée uniquement à AutoJs6 6.8.0, avec le versionCode Host minimal 5275 gelé et imposé; la révision source Host finale et propre et le manifeste de distribution des trois AAR sont enregistrés dans le lock. Chaque nouvelle exécution redécouvre le provider; absent ou désactivé, il invite à installer ou activer sans fallback, et l'installation ou la réactivation ne demande aucun redémarrage de l'hôte. L'identité des APK stables est liée à cette source Plugin exacte et au lock Host.

```text
release target: 0.5.0-alpha.4
release state: 0.5.0-alpha.4 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time pure-Python and M4 Path C native-package evaluations are complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; Path C built the official Pillow 11.0.0 and NumPy 1.26.2 dual-ABI closures offline, but transitive 4 KiB ELF LOAD segments failed the 16 KiB gate, and the official OpenCV index had no cp313 Android wheel; no candidate dependency payload was added; protocol 1.6 adds an explicit foreground-only long-running mode with a Host specialUse foreground notification, manual Stop, and 15-second Provider heartbeats under fail-closed leases; on QV710AF65F with Host versionCode 5276 and Plugin versionCode 81, notification Stop ended the script, the project rebound cleanly, and a subsequent run remained healthy through tick=70 (about 350 seconds), so the focused long-running Android smoke passes; the paired Host now admits concurrent Python launches through one fair FIFO owner plus 32 bounded waiters before Provider binding, supports interruptible queued Stop, and waits up to 3 seconds for dispatched process-generation retirement before handoff while the Plugin remains single-session with no provider queue; the first concurrency attempt on that device reached Provider BUSY/SESSION_OPEN because the installed Host did not yet contain FIFO integration; after installing the exact afca7b14c arm64 Host APK, the user confirmed the full documented FIFO order, fresh-PID generation handoff, queued Stop isolation, and later rerun checklist matched expectations with no issue, so the focused concurrency Android smoke passes; the no-runtime-change startup probe on QV710AF65F measured 441/447/429/427/428 ms with five distinct Plugin PIDs; the all-sample median is 429 ms, the median excluding the first run is 428.5 ms, and the maximum is 447 ms; every sample is below the 1000 ms threshold, so process retention is not justified and per-execution retirement remains; M6 consolidates the unpublished 0.2/0.3/0.4 implementation waypoints into one cumulative 0.5.0 release train and adds a read-only source profile plus a full local candidate gate with a ten-item manual Android smoke checklist; neither profile uses ADB, signing, network, tagging, pushing, or publication; M4 Path D, the exact signed-candidate smoke, beta/stable promotion, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### Sécurité et confidentialité

******

Le runtime Chaquopy est réservé aux scripts locaux de confiance, pas à un sandbox de code hostile. Le service exporté exige la permission de signature hôte et revérifie UID, paquet et signer; UID Android distinct, processus dédié et frontière Binder étroite réduisent l'exposition sans isoler Python comme sandbox. SM003 est le signer de publication à long terme et SuperMonster003 possède les rôles runtime, sécurité et release.

******

### Limites d'exécution

******

- La source est limitée à 4 MiB, la sortie totale à 16 MiB, chaque chunk à 16 KiB et le nombre de chunks à 16384.
- Le délai des requêtes bornées est limité à 30 min. Les projets long-running explicites n'ont pas d'échéance, mais exigent la durée de vie Host au premier plan, un bail de démarrage de 2 min et un bail heartbeat de 45 s; une seule session reste active sans file provider.
- Un workspace de projet est limité à 64 MiB compressés, 8192 fichiers et 128 MiB extraits; avant l'envoi, la sélection du Provider doit satisfaire les trois dimensions réelles du snapshot.
- Les PFD complets reçus par Binder sont possédés puis fermés à l'état terminal ou à la fermeture.
- La sortie est livrée chunk par chunk sous crédits pendant l'exécution; l'épuisement des crédits suspend le script, toute sortie acceptée précède l'unique état terminal et aucune sortie n'est permise après celui-ci.
- Le JSON structuré est limité à 64 KiB; au plus 16 artefacts sont admis avec des chemins de 1024 UTF-8 bytes, 4 MiB par fichier, 8 MiB au total et une vérification hôte de la longueur exacte, de l'EOF et du SHA-256.
- Le protocole 1.5 admet au plus 1024 appels hôte par exécution, limite chaque requête/réponse à 64 KiB, le texte à 32 KiB et l'attente d'une action ordinaire du thread principal Host à 5 s. Host files utilise des chemins relatifs de 4 KiB, du texte UTF-8 de 32 KiB et des listes d'au plus 128 noms de 255 UTF-8 bytes chacun. Les dialogues de premier plan limitent le titre à 256 UTF-8 bytes, le contenu à 4 KiB, les valeurs/réponses prompt à 32 KiB et les listes select à 64 éléments de 1 KiB chacun et 32 KiB au total; une réponse utilisateur peut attendre 5 min. Une exécution peut lancer avec succès au plus 16 scripts enfants Host non-Python asynchrones et bornés; Python imbriqué renvoie `NESTED_PYTHON_NOT_ALLOWED` et `stop_self` annule par redémarrage du processus.
- Les coordonnées automator sont des entiers stricts de 0 à 1000000, tandis que les durées de press et swipe vont de 1 ms à 4 s; une accessibilité Host indisponible lève `CapabilityUnavailableError` sans ouvrir les paramètres.
- Les snapshots selector acceptent au plus 128 nœuds, une profondeur de 32 et 48 KiB de JSON; find parcourt au plus 1024 nœuds, le texte d'un nœud est limité à 256 Unicode code points, le texte de requête à 1024 UTF-8 bytes, set_text à 4 KiB et chaque exécution conserve au plus 128 références de nœud. Un parcours incomplet renvoie `SELECTOR_SCAN_LIMIT_EXCEEDED` et une référence périmée renvoie `STALE_NODE`.
- La capture d'écran conserve au plus 1 image par exécution, limite les données encodées à 4 MiB, les blocs bruts à 32 KiB, chaque dimension à 8192 pixels et la surface totale à 16777216 pixels. Python vérifie longueur, ordre, EOF, SHA-256 et signature de format avant le retour; une accessibilité/API indisponible lève `CapabilityUnavailableError`, et les erreurs stables incluent `SCREEN_CAPTURE_FAILED`, `RESULT_LIMIT_EXCEEDED` et `STALE_IMAGE`. La recherche de couleur parcourt une nouvelle capture par lignes, avec région bornée facultative et seuil par canal jusqu'à 255, puis renvoie seulement une coordonnée ou une absence sans transférer les octets de l'image. La recherche par modèle conserve au plus 1 modèle PNG/JPEG, le limite à 1 MiB, transfère des blocs bruts de 24 KiB et limite chaque dimension à 2048, la surface à 1048576, la région à 4194304 et les comparaisons à 16777216; seuls les pixels totalement opaques participent, les autres sont des jokers, le parcours row-major est déterministe et les tampons sont libérés et effacés à l'état terminal.
- `ocr.recognize` réutilise l'enveloppe PNG/JPEG de 1 MiB, des blocs bruts de 24 KiB, 2048 pixels par côté et 1048576 pixels décodés. Le moteur OCR Host configuré renvoie au plus 256 lignes, 4 KiB d'UTF-8 strict par ligne et 48 KiB au total dans le budget d'admission/appel de 60 s; un moteur indisponible ou défaillant signale `OCR_UNAVAILABLE` ou `OCR_FAILED`, et les données chargées sont toujours libérées et effacées.
- L'annulation redémarre le processus; les extensions natives et appels bloquants restent à valider sur Android.
- L'autorisation `INTERNET` permet aux scripts d'utiliser directement les clients réseau de la bibliothèque standard; pip en ligne, le téléchargement automatique de code et l'installation de paquets tiers à l'exécution restent non pris en charge.

******

### Capacités non déclarées

******

- Le stdin général en direct et le streaming callback de `sys.stdin` direct sont indisponibles. L'interaction au premier plan s'applique uniquement au `input()` intégré et à `getpass.getpass()` après l'EOF du snapshot fini de 1 MiB au maximum. L'écriture dans le workspace, pip en ligne et les téléchargements de wheel restent indisponibles.
- Aucun script UI, débogueur, REPL ou accès arbitraire aux objets Java de l'hôte.
- Le broker temps réel couvre le premier lot complet à faible risque, Host files borné, les dialogues de premier plan, engines borné, les actions automator explicites par coordonnées/globales, les snapshots/actions selector/arbre UI, la capture d'écran, `find_color`, `find_image` et l'OCR par lignes. Les boîtes/confiance/options OCR, le traitement d'image mutable et la recherche multi-échelle restent non déclarés.
- Le support Android 32 bits et les wheels natives tierces ne sont pas garantis.
- L'arbre courant dispose d'un smoke sur appareil API 31 arm64-v8a et d'un smoke sur émulateur API 37 x86_64 à pages de 16 KB; aucun ne constitue une matrice complète d'appareils ni une qualification de release.

******

### Feuille de route

******

Le chemin A de M4 est terminé; les évaluations M4 Paths B et C concluent toutes deux `NOT_ADMITTED`, donc le runtime intégré reste `stdlib-only`. Path C construit Pillow et NumPy hors ligne, mais leurs clôtures native échouent au contrôle ELF 16 KiB dual ABI, et OpenCV n'a pas de wheel Android `cp313`; Path D reste piloté par la demande. L'automatisation M3 comprend les actions bornées, selector/arbre UI, la capture, la recherche de couleur, les modèles PNG/JPEG et l'OCR Host. Les outils de preuve historiques ne sont pas des portes de publication automatiques.

- [Voir ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historique des versions

******

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

##### Autres versions

* [CHANGELOG-fr.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-fr.md)

******

### Vérification

******

Vérification statique du système de fichiers sans Gradle ni ADB:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

Tests sémantiques portables du bootstrap avec le CPython local:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Les contrôles statiques et CPython local ne remplacent pas les preuves Android. Les résultats RC et mono-appareil existants sont historiques; l'acceptation release utilise les contrôles construction, APK, Binder et appareil représentatif liés à l'identité exacte.

******

### Construction

******

La génération documentaire ne lance aucune construction. La configuration release échoue fermée sur toute dérive AAR, SHA-256, signer ou runtime lock; les artefacts stables ne sont acceptés que s'ils sont liés à l'identité release exacte.

Ces AAR release doivent être placés et verrouillés dans `libs` avant toute construction:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

Le runtime verrouille Chaquopy 17.0.0 et CPython 3.13.9 depuis Maven et n'empaquette que la stdlib. Le gate release vérifie métadonnées, bibliothèques natives, NOTICE, signer SM003 et les trois APK distribués par rapport à l'identité exacte. Un smoke ciblé de l'arbre courant a réussi sur un émulateur API 37 x86_64 à pages de 16 KB; ce n'est ni un gate complet de compatibilité ni une matrice d'appareils.

******

### Licence

******

Le code source utilise MPL-2.0. Chaquopy, CPython et les autres composants gardent leurs licences; les attributions et accès aux sources amont et du projet figurent dans `THIRD_PARTY_NOTICES.md`.

******

### Organisation des ressources

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` génère les README et journaux intégrés en 10 langues depuis des sources JSON ordonnées. Les chaînes Android restent dans leurs répertoires de ressources.

******

### Liens

******

- Documentation AutoJs6: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
