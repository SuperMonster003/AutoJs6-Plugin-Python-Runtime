******

### Historial de versiones

******

# v0.1.0

###### 2026/08/12

* `Nota` La versión 0.1.0 fija la identidad fuente estable del Plugin y el lock Host exacto 6.8.0/5275
* `Función` Protocolo Python 1.0-1.1 emparejado con AutoJs6 6.8.0 / versionCode 5275, workspace de proyecto acotado y snapshots app/device/execution/project de solo lectura
* `Función` Hot-plug sin reiniciar el host: instalar o reactivar permite que la siguiente ejecución redescubra y fije la identidad, sin fallback si falta o está desactivado
* `Función` La muerte Binder en curso termina la ejecución sin replay; nuevas ejecuciones redescubren el provider
* `Mejora` Chaquopy queda como runtime trusted-local y non-sandbox; SM003 es signer a largo plazo y SuperMonster003 es owner de runtime, seguridad y release
* `Dependencia` Bloqueo de Chaquopy 17.0.0 y CPython 3.13.9; los APK estables están vinculados a la identidad fuente final y verificados como artefactos exactos

# v0.1.0-alpha.1

###### 2026/08/09

* `Nota` Código de prueba de concepto R2; Gradle, APK, Binder y dispositivo no están validados
* `Función` Scaffold provider Python V1 independiente con proceso dedicado, una sesión activa y sin cola provider
* `Función` Ejecución `__main__` de una fuente, stdout/stderr acotados, excepciones estructuradas y cancelación por reinicio
* `Función` Generación ordenada de README y changelogs integrados en 10 idiomas
* `Dependencia` Preselección de Chaquopy 17.0.0 y Python 3.13; versiones y hashes requieren verificación de compilación
