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
- Livrer pendant l'exécution des chunks stdout/stderr bornés dans leur ordre d'origine; l'épuisement des crédits applique une contre-pression à l'exécution.
- Définir un résultat JSON strict explicite de 64 KiB au maximum et transférer jusqu'à 16 artefacts facultatifs sous les limites de chemin, taille et SHA-256 du protocole 1.4; ne jamais déduire un résultat de stdout.
- Appeler en direct `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, `notice` sensible aux autorisations, `files.read_text/write_text/exists/is_file/is_dir/list` borné, `dialogs.alert/confirm/prompt/select` réservé au premier plan et `engines.current/run/stop_self` via le broker de données pures du protocole 1.5 lié à l'exécution, révoqué à l'état terminal.
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
release target: 0.3.0-alpha.5
release state: 0.3.0-alpha.5 current-tree candidate; M1 and M2, the complete first low-risk protocol 1.5 Host capability slice, and the bounded Host-files, foreground-dialog, and engines portions of the second slice passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3 batches, a complete device matrix, publication, and release evidence remain outside this claim
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
- Les PFD complets reçus par Binder sont possédés puis fermés à l'état terminal ou à la fermeture.
- La sortie est livrée chunk par chunk sous crédits pendant l'exécution; l'épuisement des crédits suspend le script, toute sortie acceptée précède l'unique état terminal et aucune sortie n'est permise après celui-ci.
- Le JSON structuré est limité à 64 KiB; au plus 16 artefacts sont admis avec des chemins de 1024 UTF-8 bytes, 4 MiB par fichier, 8 MiB au total et une vérification hôte de la longueur exacte, de l'EOF et du SHA-256.
- Le protocole 1.5 admet au plus 1024 appels hôte par exécution, limite chaque requête/réponse à 64 KiB, le texte à 32 KiB et l'attente d'une action ordinaire du thread principal Host à 5 s. Host files utilise des chemins relatifs de 4 KiB, du texte UTF-8 de 32 KiB et des listes d'au plus 128 noms de 255 UTF-8 bytes chacun. Les dialogues de premier plan limitent le titre à 256 UTF-8 bytes, le contenu à 4 KiB, les valeurs/réponses prompt à 32 KiB et les listes select à 64 éléments de 1 KiB chacun et 32 KiB au total; une réponse utilisateur peut attendre 5 min. Une exécution peut lancer avec succès au plus 16 scripts enfants Host non-Python asynchrones et bornés; Python imbriqué renvoie `NESTED_PYTHON_NOT_ALLOWED` et `stop_self` annule par redémarrage du processus.
- L'annulation redémarre le processus; les extensions natives et appels bloquants restent à valider sur Android.
- L'autorisation `INTERNET` permet aux scripts d'utiliser directement les clients réseau de la bibliothèque standard; pip en ligne, le téléchargement automatique de code et l'installation de paquets tiers à l'exécution restent non pris en charge.

******

### Capacités non déclarées

******

- Le stdin général en direct et le streaming callback de `sys.stdin` direct sont indisponibles. L'interaction au premier plan s'applique uniquement au `input()` intégré et à `getpass.getpass()` après l'EOF du snapshot fini de 1 MiB au maximum. L'écriture dans le workspace, pip en ligne et les téléchargements de wheel restent indisponibles.
- Aucun script UI, débogueur, REPL ou accès arbitraire aux objets Java de l'hôte.
- Le broker temps réel couvre le premier lot complet à faible risque, Host files borné, les dialogues de premier plan et engines borné; accessibilité, capture d'écran et OCR restent non déclarés.
- Le support Android 32 bits et les wheels natives tierces ne sont pas garantis.
- L'arbre courant dispose d'un smoke sur appareil API 31 arm64-v8a et d'un smoke sur émulateur API 37 x86_64 à pages de 16 KB; aucun ne constitue une matrice complète d'appareils ni une qualification de release.

******

### Feuille de route

******

Les preuves RC locales et appareil concentrées de R6-P2/P3 restent historiques. Ce clean VERSION_BUILD=11 freeze commit fixe l'identité source stable du Plugin et le lock Host exact 6.8.0/5275; la provenance des APK stables est évaluée par rapport à ces identités exactes et tout production receipt doit utiliser la même base. Une matrice API×ABI complète et un nouveau soak ne sont pas des portes automatiques.

- [Voir ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historique des versions

******

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
