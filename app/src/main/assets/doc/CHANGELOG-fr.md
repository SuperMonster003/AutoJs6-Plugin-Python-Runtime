******

### Historique des versions

******

# v0.1.0

###### 2026/08/11 (préparation de publication; ni tag ni publication)

* `Note` 0.1.0 reste en préparation; l'identité hôte finale, le dépôt et l'authentification GitHub, l'index officiel et le production receipt sont en attente
* `Fonction` Protocole Python 1.0-1.1 associé à AutoJs6 6.8.0, workspace projet borné et snapshots app/device/execution/project en lecture seule
* `Fonction` Hot-plug sans redémarrage hôte: installation ou réactivation permet à la prochaine exécution de redécouvrir et épingler l'identité, sans fallback si absent ou désactivé
* `Fonction` La mort Binder en cours termine l'exécution sans replay; les nouvelles exécutions redécouvrent le provider
* `Amélioration` Chaquopy est fixé comme runtime trusted-local et non-sandbox; SM003 est le signer à long terme et SuperMonster003 possède runtime, sécurité et release
* `Dépendance` Verrouillage de Chaquopy 17.0.0 et CPython 3.13.9; les artefacts finaux seront revérifiés après le gel des sources

# v0.1.0-alpha.1

###### 2026/08/09

* `Note` Sources de preuve de concept R2; Gradle, APK, Binder et appareil ne sont pas validés
* `Fonction` Scaffold provider Python V1 indépendant avec processus dédié, une session active et aucune file provider
* `Fonction` Exécution `__main__` d'une source, stdout/stderr bornés, exceptions structurées et annulation par redémarrage
* `Fonction` Génération ordonnée des README et journaux intégrés en 10 langues
* `Dépendance` Présélection de Chaquopy 17.0.0 et Python 3.13; versions et hashes restent à vérifier par construction
