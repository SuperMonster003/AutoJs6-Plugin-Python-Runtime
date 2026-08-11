<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>Runtime de Python independiente. Ejecuta scripts en un proceso de complemento dedicado</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Idiomas

******

El README.md actual está disponible en los siguientes idiomas:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- Español [es] # actual
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### Introducción

******

Python Runtime es un proveedor independiente del protocolo Python V1. El host entrega una instantánea de código Python a un proceso dedicado, que la ejecuta con CPython y devuelve salida acotada, excepciones estructuradas y un único estado terminal.

> La versión 0.1.0 está en preparación de publicación. Existen pruebas RC locales de compilación, APK, Binder y un dispositivo API 31 arm64-v8a, pero los cambios de gobierno exigen un nuevo congelado; aún no existen tag v0.1.0, GitHub Release ni production receipt.

******

### Funciones

******

- Ejecutar una instantánea UTF-8 como `__main__`.
- Conservar el orden de stdout y stderr y entregar chunks acotados mediante créditos.
- Informar `SystemExit`, errores de sintaxis y excepciones con traceback estructurado y acotado.
- Permitir una sesión activa por proceso sin cola del proveedor.
- No requerir reinicio del host: la siguiente ejecución nueva tras instalar o reactivar redescubre y fija el provider; una muerte Binder en curso termina esa ejecución y nunca la repite automáticamente.

******

### Runtime y formatos de datos

******

El protocolo V1 declara actualmente el siguiente alcance:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

La compilación solicita Python 3.13. Los artefactos RC locales congelados y la ejecución exacta en dispositivo registraron CPython 3.13.9; la versión y los hashes finales de 0.1.0 deben revisarse tras congelar el código.

******

### Interfaz del complemento

******

El host descubre e invoca el complemento con las siguientes identidades:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.1
```

El complemento acepta una SOURCE independiente, un workspace archive acotado opcional y el snapshot de capacidades host de solo lectura del protocolo 1.1; stdin snapshot sigue desactivado. No se inyectan Context, Binder, objetos del runtime host ni callback sinks.

******

### Estado de integración con el host

******

> La versión 0.1.0 se empareja solo con AutoJs6 6.8.0, cuya identidad final y límites de compatibilidad aún no están congelados. Cada ejecución nueva redescubre el provider; si falta o está desactivado pide instalar o activar sin fallback, y la instalación o reactivación no exige reiniciar el host. El índice oficial, el tag y la Release siguen pendientes.

```text
release target: 0.1.0
release state: release preparation; not tagged or published
paired host: AutoJs6 6.8.0
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### Seguridad y privacidad

******

El runtime Chaquopy es solo para scripts locales de confianza, no un sandbox de código hostil. El servicio exportado exige el permiso de firma host y comprueba UID, paquete y signer; UID Android separado, proceso dedicado y frontera Binder estrecha reducen la exposición sin aislar Python como sandbox. SM003 es el signer de publicación a largo plazo y SuperMonster003 es owner de runtime, seguridad y release.

******

### Límites operativos

******

- El código se limita a 4 MiB, la salida total a 4 MiB, cada chunk a 16 KiB y el total a 4096 chunks.
- El timeout máximo es 60 s, con una sesión activa y sin cola del proveedor.
- Se adopta la propiedad de los PFD completos recibidos por Binder y se cierran al terminar o cerrar la sesión.
- La salida se almacena primero con límites y después se envía con créditos; no se afirma backpressure durante la ejecución.
- La cancelación reinicia el proceso; las extensiones nativas y llamadas bloqueantes requieren validación Android posterior.
- La política stdlib-only prohíbe pip en línea y paquetes Python de terceros. Los permisos del APK combinado aún deben verificarse.

******

### Capacidades no declaradas

******

- No hay stdin snapshots, escritura de workspace, pip en línea ni descarga de wheels.
- No hay scripts UI, depurador, REPL ni acceso arbitrario a objetos Java del host.
- No hay broker AutoJs6 en tiempo real; las primeras API solo usan el snapshot app/device/execution/project congelado al iniciar y acceso de lectura acotado al workspace privado del complemento.
- No se garantiza Android de 32 bits ni wheels nativas de terceros.
- arm64-v8a tiene evidencia de dispositivo API 31; x86_64 solo tiene evidencia de empaquetado, no ejecución en dispositivo ni matriz completa.

******

### Hoja de ruta

******

La RC local y la evidencia concentrada de dispositivo de R6-P2/P3 ya son históricas. R6-P4 prepara 0.1.0; los blockers restantes son la identidad final AutoJs6 6.8.0, autenticación y repositorio GitHub, índice oficial, provenance del código actual y production receipt posterior a publicar. Una matriz API×ABI completa y un soak nuevo no son gates automáticos.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historial de versiones

******

# v0.1.0

###### 2026/08/11 (preparación de publicación; sin tag ni publicación)

* `Nota` 0.1.0 sigue en preparación; faltan identidad host final, repositorio y autenticación GitHub, índice oficial y production receipt
* `Función` Protocolo Python 1.0-1.1 emparejado con AutoJs6 6.8.0, workspace de proyecto acotado y snapshots app/device/execution/project de solo lectura
* `Función` Hot-plug sin reiniciar el host: instalar o reactivar permite que la siguiente ejecución redescubra y fije la identidad, sin fallback si falta o está desactivado
* `Función` La muerte Binder en curso termina la ejecución sin replay; nuevas ejecuciones redescubren el provider
* `Mejora` Chaquopy queda como runtime trusted-local y non-sandbox; SM003 es signer a largo plazo y SuperMonster003 es owner de runtime, seguridad y release
* `Dependencia` Bloqueo de Chaquopy 17.0.0 y CPython 3.13.9; los artefactos finales se verificarán tras congelar el código

# v0.1.0-alpha.1

###### 2026/08/09

* `Nota` Código de prueba de concepto R2; Gradle, APK, Binder y dispositivo no están validados
* `Función` Scaffold provider Python V1 independiente con proceso dedicado, una sesión activa y sin cola provider
* `Función` Ejecución `__main__` de una fuente, stdout/stderr acotados, excepciones estructuradas y cancelación por reinicio
* `Función` Generación ordenada de README y changelogs integrados en 10 idiomas
* `Dependencia` Preselección de Chaquopy 17.0.0 y Python 3.13; versiones y hashes requieren verificación de compilación

##### Más versiones

* [CHANGELOG-es.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-es.md)

******

### Verificación

******

Comprobación estática del sistema de archivos sin Gradle ni ADB:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

Pruebas semánticas portátiles del bootstrap con el CPython local:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Las comprobaciones estáticas y CPython local no sustituyen evidencia Android. Los resultados RC y de un dispositivo son históricos; tras congelar el código final solo se repiten las comprobaciones de compilación, APK, Binder y dispositivo representativo ligadas a la identidad de publicación.

******

### Compilación

******

Este corte documental no ejecuta compilación. La configuración release falla cerrada ante deriva de AAR, SHA-256, signer o runtime lock; 0.1.0 sigue en preparación, sin tag ni publicación.

Estos AAR release deben colocarse y bloquearse en `libs` antes de compilar:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

El runtime bloquea Chaquopy 17.0.0 y CPython 3.13.9 desde Maven y solo empaqueta stdlib. La publicación final debe revisar metadatos, bibliotecas nativas, páginas de 16 KB, NOTICE, signer SM003 y los tres APK distribuidos.

******

### Licencia

******

El código fuente usa MPL-2.0. Chaquopy, CPython y los demás componentes conservan sus licencias; atribuciones y acceso a fuentes upstream y del proyecto constan en `THIRD_PARTY_NOTICES.md`.

******

### Estructura de recursos

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` genera README y changelogs integrados en 10 idiomas desde JSON con orden fijo. Las cadenas Android se mantienen en sus directorios de recursos.

******

### Enlaces

******

- Documentación de AutoJs6: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
