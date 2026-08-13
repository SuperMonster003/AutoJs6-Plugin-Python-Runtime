******

### Historique des versions

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Note` Candidat alpha U1 à sources propres postérieur à 0.1; aucune interaction stdin en direct, et l'acceptation U1-R1 E3 n'est représentée que par un rapport canonical PASS concordant pour les artefacts Host/Plugin exacts sur QV710AF65F/API 31/arm64; ceci ne constitue pas une preuve de matrice d'appareils, de livraison ou de publication
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
