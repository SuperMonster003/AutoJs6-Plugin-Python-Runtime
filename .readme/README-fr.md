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

> Il s'agit actuellement d'une preuve de concept R2. Les sources et les vérifications sémantiques locales du bootstrap sont présentes, mais la configuration Gradle, la compilation Android, l'inspection de l'APK, la validation Binder et les tests sur appareil n'ont pas été exécutés.

******

### Fonctions

******

- Exécuter un instantané de source Python UTF-8 en tant que `__main__`.
- Conserver l'ordre de stdout et stderr puis livrer des chunks bornés sous crédits.
- Signaler `SystemExit`, les erreurs de syntaxe et les exceptions avec une traceback structurée bornée.
- Autoriser une session active par processus sans file d'attente côté fournisseur.
- Retirer le processus après annulation, délai dépassé ou décès du callback sans rejouer le script.

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

La construction demande Python 3.13. 3.13.9 est la version empaquetée attendue d'après les informations Chaquopy actuelles; elle ne sera vérifiée qu'après inspection de l'APK et exécution sur appareil.

******

### Interface du plug-in

******

L'hôte découvre et appelle le plug-in avec les identités suivantes:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

Seul un descripteur SOURCE est accepté. Les limites de workspace archive et stdin snapshot sont nulles, et aucun Context, Binder, objet d'exécution hôte ou callback sink n'est injecté.

******

### État de l'intégration hôte

******

> Le protocole et le raccordement hôte progressent, mais les AAR release requis ne sont pas encore publiés et vérifiés. Installer ce scaffold ne fournit pas à lui seul un moteur Python utilisable de bout en bout.

******

### Sécurité et confidentialité

******

Le manifeste source ne demande aucune permission Android. Le service exporté exige la permission de signature de l'hôte et revérifie l'UID appelant, le paquet hôte installé et ses signatures. Le pont Java de Chaquopy reste accessible: l'isolation repose donc sur un UID Android distinct, un processus dédié et une frontière Binder étroite; CPython n'est pas présenté comme un bac à sable.

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

- Les archives de workspace, stdin snapshot, pip en ligne et téléchargements de wheel sont indisponibles.
- Aucun script UI, débogueur, REPL ou accès arbitraire aux objets Java de l'hôte.
- Aucun broker de capacités AutoJs6; les API hôte ne sont pas encore raccordées.
- Le support Android 32 bits et les wheels natives tierces ne sont pas garantis.
- Les tests CPython locaux ne constituent pas une preuve Chaquopy, Android, Binder ou appareil.

******

### Feuille de route

******

Le dépôt R2 indépendant, la frontière statique, les sources provider/bootstrap et les tests sémantiques locaux sont présents. Gradle et ADB sont différés pendant le soak protégé de QV710AF65F. Les AAR release, la résolution des dépendances, la compilation Android, les contrôles APK/16 KB, Binder/PFD et la matrice d'appareils restent incomplets.

- [Voir ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historique des versions

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

Tests sémantiques portables du bootstrap avec le CPython local:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Ces contrôles ne prouvent pas le fonctionnement Android. Gradle, APK, Binder et appareil devront être validés après le soak protégé.

******

### Construction

******

Aucune construction n'est lancée. La configuration release échoue fermée tant que les AAR ou leurs SHA-256 ne sont pas verrouillés.

Ces AAR release doivent être placés et verrouillés dans `libs` avant toute construction:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

Le moteur doit utiliser Chaquopy 17.0.0 depuis Maven et n'empaqueter que la stdlib. Métadonnées de vérification, bibliothèques natives, licences et compatibilité 16 KB restent à accepter.

******

### Licence

******

Le code source utilise MPL-2.0. Chaquopy, CPython et les autres composants gardent leurs licences respectives.

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
