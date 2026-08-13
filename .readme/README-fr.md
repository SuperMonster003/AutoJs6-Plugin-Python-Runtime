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
- Accepter pour `input()` un instantané stdin fini et préfourni de 1 MiB au maximum; aucune interaction prompt/réponse en temps réel n'est fournie.
- Conserver l'ordre de stdout et stderr puis livrer des chunks bornés sous crédits.
- Signaler `SystemExit`, les erreurs de syntaxe et les exceptions avec une traceback structurée bornée.
- Autoriser une session active par processus sans file d'attente côté fournisseur.
- Ne pas redémarrer l'hôte: la prochaine nouvelle exécution après installation ou réactivation redécouvre et épingle le provider; une mort Binder en cours termine cette exécution sans jamais la rejouer.

******

### Moteur et formats de données

******

Le protocole V1 déclare actuellement le périmètre suivant:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
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
protocol: 1.0-1.1
```

Le plug-in accepte une SOURCE indépendante, une archive workspace bornée facultative, un snapshot stdin fini et préfourni de 1 MiB au maximum, et le snapshot en lecture seule des capacités hôte du protocole 1.1. Stdin n'est pas un canal interactif en temps réel; aucun Context, Binder, objet d'exécution hôte ou callback sink n'est injecté.

******

### État de l'intégration hôte

******

> La version 0.1.0 est associée uniquement à AutoJs6 6.8.0, avec le versionCode Host minimal 5275 gelé et imposé; la révision source Host finale et propre et le manifeste de distribution des trois AAR sont enregistrés dans le lock. Chaque nouvelle exécution redécouvre le provider; absent ou désactivé, il invite à installer ou activer sans fallback, et l'installation ou la réactivation ne demande aucun redémarrage de l'hôte. L'identité des APK stables est liée à cette source Plugin exacte et au lock Host.

```text
release target: 0.2.0-alpha.1
release state: post-0.1 U1 alpha source candidate; not published, E3 device acceptance pending, and prior 0.1.0 artifacts do not cover the current source
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- La source est limitée à 4 MiB, la sortie totale à 4 MiB, chaque chunk à 16 KiB et le nombre de chunks à 4096.
- Le délai maximal est 60 s, avec une session active et aucune file côté fournisseur.
- Les PFD complets reçus par Binder sont possédés puis fermés à l'état terminal ou à la fermeture.
- La sortie est d'abord mise en mémoire de façon bornée puis envoyée sous crédits; aucune contre-pression pendant l'exécution n'est revendiquée.
- L'annulation redémarre le processus; les extensions natives et appels bloquants restent à valider sur Android.
- La politique stdlib-only interdit pip en ligne et les paquets Python tiers. Les permissions de l'APK fusionné restent à vérifier.

******

### Capacités non déclarées

******

- Stdin interactif en temps réel est indisponible; seul un snapshot fini et préfourni de 1 MiB au maximum est pris en charge. L'écriture dans le workspace, pip en ligne et les téléchargements de wheel restent indisponibles.
- Aucun script UI, débogueur, REPL ou accès arbitraire aux objets Java de l'hôte.
- Aucun broker AutoJs6 temps réel; les premières API utilisent seulement le snapshot app/device/execution/project gelé au démarrage et un accès borné en lecture seule au workspace privé du plug-in.
- Le support Android 32 bits et les wheels natives tierces ne sont pas garantis.
- arm64-v8a dispose d'une preuve appareil API 31; x86_64 n'a actuellement qu'une preuve d'empaquetage, ni exécution appareil ni matrice complète.

******

### Feuille de route

******

Les preuves RC locales et appareil concentrées de R6-P2/P3 restent historiques. Ce clean VERSION_BUILD=11 freeze commit fixe l'identité source stable du Plugin et le lock Host exact 6.8.0/5275; la provenance des APK stables est évaluée par rapport à ces identités exactes et tout production receipt doit utiliser la même base. Une matrice API×ABI complète et un nouveau soak ne sont pas des portes automatiques.

- [Voir ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historique des versions

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Note` Alpha source U1 postérieure à 0.1; aucune interaction stdin en direct et acceptation appareil E3 encore en attente
* `Fonction` Ajout d'un snapshot stdin fini et préfourni de 1 MiB au plus pour une entrée et une EOF déterministes avec `input()` et `sys.stdin`
* `Fonction` Finalisation des imports projet pour les modules workspace, les modules voisins et racine d'une entrée imbriquée, et les imports relatifs au package
* `Correction` Décodage de la source en UTF-8 strict avant exécution afin qu'un encoding cookie non UTF-8 ne contourne plus le contrat
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

Le runtime verrouille Chaquopy 17.0.0 et CPython 3.13.9 depuis Maven et n'empaquette que la stdlib. Le gate release vérifie métadonnées, bibliothèques natives, NOTICE, signer SM003 et les trois APK distribués par rapport à l'identité exacte; la compatibilité des pages 16 KB n'a actuellement aucun gate dédié et n'est pas déclarée vérifiée.

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
