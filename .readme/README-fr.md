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
protocol: 1.0-1.5
```

Le plug-in accepte une SOURCE indépendante, une archive workspace bornée facultative, un snapshot stdin fini et préfourni de 1 MiB au maximum, et le snapshot en lecture seule des capacités hôte du protocole 1.1. Le protocole 1.2 ajoute la négociation explicite de l'entrée file/module pour les projets admis. Le protocole 1.3 ajoute, après l'EOF du snapshot, un prompt/réponse détenu par l'hôte et réservé au premier plan pour le `input()` intégré; `getpass.getpass()` utilise une saisie masquée. Le protocole 1.4 ajoute un JSON strict explicite et des artefacts facultatifs manifestés par SHA-256; stdout reste un diagnostic et n'est jamais analysé comme résultat. Le protocole 1.5 ajoute un broker hôte de données pures lié à une exécution, à l'UID du plug-in, à l'ordre des appels et à un quota fini. Les dialogues Host exigent aussi une autorisation de premier plan soutenue par une Activity active; un lancement en arrière-plan renvoie `INTERACTIVE_NOT_ALLOWED` sans ouvrir d'UI. `sys.stdin` direct reste fini, les lancements en arrière-plan n'ouvrent jamais d'interface de saisie et les scripts ne reçoivent aucun Context, Binder brut, objet d'exécution hôte ou callback sink.

******

### État de l'intégration hôte

******

> La version 0.1.0 est associée uniquement à AutoJs6 6.8.0, avec le versionCode Host minimal 5275 gelé et imposé; la révision source Host finale et propre et le manifeste de distribution des trois AAR sont enregistrés dans le lock. Chaque nouvelle exécution redécouvre le provider; absent ou désactivé, il invite à installer ou activer sans fallback, et l'installation ou la réactivation ne demande aucun redémarrage de l'hôte. L'identité des APK stables est liée à cette source Plugin exacte et au lock Host.

```text
release target: 0.4.0-alpha.8
release state: 0.4.0-alpha.8 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time package evaluation is complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; no candidate dependency payload was added and no new device claim is made; later demand-driven M3 batches, M4 Path C, a complete device matrix, publication, and release evidence remain outside this claim
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
- Le délai maximal est 30 min, avec une session active et aucune file côté fournisseur.
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

Le chemin A de M4 est terminé; l'évaluation des paquets intégrés de M4 Path B conclut `NOT_ADMITTED`, donc le runtime intégré reste `stdlib-only`; l'évaluation native de M4 Path C continue selon la valeur utilisateur. L'automatisation M3 comprend les actions bornées, selector/arbre UI, la capture, la recherche de couleur, les modèles PNG/JPEG et l'OCR Host. Les outils de preuve historiques restent disponibles sans être des portes de publication automatiques.

- [Voir ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historique des versions

******

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
