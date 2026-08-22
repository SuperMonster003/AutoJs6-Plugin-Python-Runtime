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

> La identidad fuente 0.1.0 y el lock Host exacto están congelados. Las pruebas RC locales de compilación, APK, Binder y un dispositivo API 31 arm64-v8a siguen siendo históricas; la provenance APK/P3 estable se vincula a la identidad release exacta, mientras que un production receipt es un nivel de evidencia posterior e independiente.

******

### Funciones

******

- Ejecutar una instantánea UTF-8 como `__main__`.
- Aceptar un snapshot stdin finito y preproporcionado de hasta 1 MiB; tras su EOF, un inicio explícito en primer plano puede continuar el `input()` integrado mediante el prompt/respuesta acotado del protocolo 1.3.
- Seleccionar explícitamente `entryMode=file|module` para un proyecto admitido; el modo module usa metadatos estándar de `runpy`, la raíz del proyecto en `sys.path[0]` e imports relativos al package, mientras el modo file conserva la semántica de script ordinaria.
- Entregar durante la ejecución chunks acotados de stdout/stderr en su orden original; al agotarse los créditos se aplica contrapresión a la ejecución.
- Establecer un resultado JSON estricto explícito de hasta 64 KiB y transferir hasta 16 artefactos opcionales con límites de ruta, tamaño y SHA-256 del protocolo 1.4; nunca inferir un resultado desde stdout.
- Informar `SystemExit`, errores de sintaxis y excepciones con traceback estructurado y acotado.
- Permitir una sesión activa por proceso sin cola del proveedor.
- No requerir reinicio del host: la siguiente ejecución nueva tras instalar o reactivar redescubre y fija el provider; una muerte Binder en curso termina esa ejecución y nunca la repite automáticamente.

******

### Runtime y formatos de datos

******

El protocolo V1 declara actualmente el siguiente alcance:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
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
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.4
```

El complemento acepta una SOURCE independiente, un workspace archive acotado opcional, un snapshot stdin finito y preproporcionado de hasta 1 MiB y el snapshot de capacidades host de solo lectura del protocolo 1.1. El protocolo 1.2 añade negociación explícita de entrada file/module para proyectos admitidos. El protocolo 1.3 añade, tras el EOF del snapshot, prompt/respuesta propiedad del Host y solo en primer plano para el `input()` integrado. El protocolo 1.4 añade JSON estricto explícito y artefactos opcionales manifestados con SHA-256; stdout sigue siendo diagnóstico y nunca se analiza como resultado. `sys.stdin` directo sigue siendo finito, los inicios en segundo plano nunca abren UI de entrada y no se inyectan Context, Binder, objetos del runtime host ni callback sinks.

******

### Estado de integración con el host

******

> La versión 0.1.0 se empareja solo con AutoJs6 6.8.0, con el versionCode mínimo del Host 5275 congelado y aplicado; la revisión final y limpia del código fuente del Host y el manifiesto de distribución de los tres AAR están registrados en el lock. Cada ejecución nueva redescubre el provider; si falta o está desactivado pide instalar o activar sin fallback, y la instalación o reactivación no exige reiniciar el Host. La identidad del APK estable está vinculada a ese código fuente exacto del Plugin y al lock Host.

```text
release target: 0.2.0-alpha.1
release state: post-0.1 U1 current-tree alpha candidate; U1-R2 module entry, live output, foreground built-in input, explicit structured JSON and bounded output artifacts are implemented through E2 only; background launches and direct sys.stdin remain finite and non-interactive, R2 E3 is still open, and prior 0.1.0 artifacts do not cover U1 or establish device-matrix, release, or public evidence
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- El código se limita a 4 MiB, la salida total a 16 MiB, cada chunk a 16 KiB y el total a 16384 chunks.
- El timeout máximo es 30 min, con una sesión activa y sin cola del proveedor.
- Se adopta la propiedad de los PFD completos recibidos por Binder y se cierran al terminar o cerrar la sesión.
- La salida se entrega chunk a chunk con créditos durante la ejecución; al agotarse se pausa el script, la salida aceptada precede al único terminal y se prohíbe toda salida posterior.
- El JSON estructurado se limita a 64 KiB; se admiten hasta 16 artefactos con rutas de 1024 UTF-8 bytes, 4 MiB por archivo, 8 MiB en total y verificación Host de longitud exacta, EOF y SHA-256.
- La cancelación reinicia el proceso; las extensiones nativas y llamadas bloqueantes requieren validación Android posterior.
- El permiso `INTERNET` permite que los scripts usen directamente los clientes de red de la biblioteca estándar; pip en línea, la descarga automática de código y la instalación de paquetes de terceros en ejecución siguen sin admitirse.

******

### Capacidades no declaradas

******

- No hay stdin general en vivo ni streaming callback de `sys.stdin` directo. La interacción en primer plano solo se aplica al `input()` integrado después del EOF del snapshot finito de hasta 1 MiB. La escritura de workspace, pip en línea y descarga de wheels siguen sin soporte.
- No hay scripts UI, depurador, REPL ni acceso arbitrario a objetos Java del host.
- No hay broker AutoJs6 en tiempo real; las primeras API solo usan el snapshot app/device/execution/project congelado al iniciar y acceso de lectura acotado al workspace privado del complemento.
- No se garantiza Android de 32 bits ni wheels nativas de terceros.
- arm64-v8a tiene evidencia de dispositivo API 31; x86_64 solo tiene evidencia de empaquetado, no ejecución en dispositivo ni matriz completa.

******

### Hoja de ruta

******

La RC local y la evidencia concentrada de dispositivo de R6-P2/P3 permanecen históricas. Este clean VERSION_BUILD=11 freeze commit fija la identidad fuente estable del Plugin y el lock Host exacto 6.8.0/5275; la provenance del APK estable se evalúa contra esas identidades exactas y cualquier production receipt debe usar la misma base. Una matriz API×ABI completa y un soak nuevo no son gates automáticos.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historial de versiones

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Nota` Candidato alpha U1 del árbol actual posterior a 0.1; la entrada module, salida live, input integrado en primer plano, JSON estructurado explícito y artefactos acotados de U1-R2 solo están cubiertos hasta E2; los inicios en segundo plano y sys.stdin directo siguen sin interacción, R2 E3 continúa abierto y estos resultados no prueban matriz de dispositivos, lanzamiento ni publicación
* `Función` Añade un snapshot stdin finito y preproporcionado de hasta 1 MiB para entrada y EOF deterministas mediante `input()` y `sys.stdin`
* `Función` Completa los imports de proyecto para módulos workspace, módulos hermanos y raíz de una entrada anidada e imports relativos al package
* `Función` Añade el protocolo 1.2 con `entryMode=file|module` explícito; la ejecución module usa `runpy` con `__package__`, `__spec__`, la raíz del proyecto en `sys.path[0]` e imports relativos correctos, mientras el modo file no cambia
* `Función` Añade con el protocolo 1.3 prompt/respuesta acotado y solo en primer plano para el `input()` integrado tras el EOF del snapshot finito; los inicios en segundo plano nunca abren UI de entrada y `sys.stdin` directo sigue finito
* `Función` Añade con el protocolo 1.4 resultados JSON estrictos explícitos y artefactos opcionales acotados por cantidad, ruta normalizada, tamaño por archivo/total, referencias PFD exactas y SHA-256, sin inferir nunca un resultado desde stdout
* `Corrección` Decodifica el código como UTF-8 estricto antes de ejecutarlo para que un encoding cookie no UTF-8 no eluda el contrato
* `Mejora` Conceder `INTERNET` para que los scripts de confianza usen directamente los clientes de red de la biblioteca estándar, manteniendo desactivados pip en línea y la descarga automática de código
* `Mejora` Elevar el límite de ejecución del Provider a 30 minutos y la salida acotada a 16 MiB / 16384 chunks
* `Mejora` Traslada los chunks acotados de stdout/stderr y la contrapresión por créditos a la ejecución del script, conservando la salida parcial ordenada antes del terminal y prohibiéndola después
* `Mejora` Usa un `__main__` independiente por ejecución y restaura stdin/stdout/stderr, argv, cwd, `sys.path`, módulos y caché de importadores
* `Mejora` Aplica un lease de 5 segundos a una sesión abierta que nunca inicia y luego libera entradas, descriptors y el único slot de sesión
* `Mejora` Impone el Host versionCode mínimo 5275 en el límite Binder del Provider en vez de depender solo del descubrimiento del Host

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

Las comprobaciones estáticas y CPython local no sustituyen evidencia Android. Los resultados RC y de un dispositivo son históricos; la aceptación release usa comprobaciones de compilación, APK, Binder y dispositivo representativo ligadas a la identidad exacta.

******

### Compilación

******

La generación documental no ejecuta compilación. La configuración release falla cerrada ante deriva de AAR, SHA-256, signer o runtime lock; los artefactos estables solo se aceptan vinculados a la identidad release exacta.

Estos AAR release deben colocarse y bloquearse en `libs` antes de compilar:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

El runtime bloquea Chaquopy 17.0.0 y CPython 3.13.9 desde Maven y solo empaqueta stdlib. El gate release comprueba metadatos, bibliotecas nativas, NOTICE, signer SM003 y los tres APK distribuidos contra la identidad exacta; la compatibilidad con páginas de 16 KB aún no tiene un gate dedicado y no se declara verificada.

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
