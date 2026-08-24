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
- Aceptar un snapshot stdin finito y preproporcionado de hasta 1 MiB; tras su EOF, un inicio explícito en primer plano puede continuar el `input()` integrado mediante el prompt/respuesta acotado del protocolo 1.3, mientras `getpass.getpass()` usa entrada oculta.
- Seleccionar explícitamente `entryMode=file|module` para un proyecto admitido; el modo module usa metadatos estándar de `runpy`, la raíz del proyecto en `sys.path[0]` e imports relativos al package, mientras el modo file conserva la semántica de script ordinaria.
- Importar desde la raíz admitida paquetes Python puros locales al proyecto y sus metadatos `.dist-info`, sin pip en línea ni instalación en ejecución.
- Entregar durante la ejecución chunks acotados de stdout/stderr en su orden original; al agotarse los créditos se aplica contrapresión a la ejecución.
- Establecer un resultado JSON estricto explícito de hasta 64 KiB y transferir hasta 16 artefactos opcionales con límites de ruta, tamaño y SHA-256 del protocolo 1.4; nunca inferir un resultado desde stdout.
- Invocar en vivo `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, `notice` sensible a permisos, `files.read_text/write_text/exists/is_file/is_dir/list` acotado, `dialogs.alert/confirm/prompt/select` solo en primer plano, `engines.current/run/stop_self`, `automator.click/long_click/press/swipe/back/home` acotado, `selector.snapshot/find/click/set_text` acotado, `images.capture_screen`, `images.find_color`, `images.find_image` y `ocr.recognize` mediante el broker de datos puros del protocolo 1.5 ligado a la ejecución y revocado al terminar.
- El protocolo 1.6 añade proyectos explícitos `executionMode=long-running` sin fecha límite de ejecución, con notificación Host en primer plano, acción Stop y heartbeats Provider ordenados cada 15 s; los inicios en segundo plano fallan de forma cerrada sin degradarse.
- El Host emparejado admite lanzamientos Python concurrentes mediante una FIFO justa antes de descubrir el Provider: un propietario activo y hasta 32 esperas; Stop en cola es interrumpible y una generación despachada espera hasta 3 s la salida Binder antes del relevo, mientras el Provider sigue con una sola sesión y sin cola.
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
protocol: 1.0-1.6
```

El complemento acepta una SOURCE independiente, un workspace archive acotado opcional, un snapshot stdin finito y preproporcionado de hasta 1 MiB y el snapshot de capacidades host de solo lectura del protocolo 1.1. El protocolo 1.2 añade negociación explícita de entrada file/module para proyectos admitidos. El protocolo 1.3 añade, tras el EOF del snapshot, prompt/respuesta propiedad del Host y solo en primer plano para el `input()` integrado; `getpass.getpass()` usa entrada oculta. El protocolo 1.4 añade JSON estricto explícito y artefactos opcionales manifestados con SHA-256; stdout sigue siendo diagnóstico y nunca se analiza como resultado. El protocolo 1.5 añade un broker Host de datos puros ligado a una ejecución, al UID del complemento, al orden de llamadas y a una cuota finita. Los diálogos Host también requieren autorización de primer plano respaldada por una Activity activa; los inicios en segundo plano reciben `INTERACTIVE_NOT_ALLOWED` sin abrir UI. `sys.stdin` directo sigue siendo finito, los inicios en segundo plano nunca abren UI de entrada y los scripts no reciben Context, Binder bruto, objetos del runtime host ni callback sinks.

******

### Estado de integración con el host

******

> La versión 0.1.0 se empareja solo con AutoJs6 6.8.0, con el versionCode mínimo del Host 5275 congelado y aplicado; la revisión final y limpia del código fuente del Host y el manifiesto de distribución de los tres AAR están registrados en el lock. Cada ejecución nueva redescubre el provider; si falta o está desactivado pide instalar o activar sin fallback, y la instalación o reactivación no exige reiniciar el Host. La identidad del APK estable está vinculada a ese código fuente exacto del Plugin y al lock Host.

```text
release target: 0.5.0-alpha.4
release state: 0.5.0-alpha.4 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time pure-Python and M4 Path C native-package evaluations are complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; Path C built the official Pillow 11.0.0 and NumPy 1.26.2 dual-ABI closures offline, but transitive 4 KiB ELF LOAD segments failed the 16 KiB gate, and the official OpenCV index had no cp313 Android wheel; no candidate dependency payload was added; protocol 1.6 adds an explicit foreground-only long-running mode with a Host specialUse foreground notification, manual Stop, and 15-second Provider heartbeats under fail-closed leases; on QV710AF65F with Host versionCode 5276 and Plugin versionCode 81, notification Stop ended the script, the project rebound cleanly, and a subsequent run remained healthy through tick=70 (about 350 seconds), so the focused long-running Android smoke passes; the paired Host now admits concurrent Python launches through one fair FIFO owner plus 32 bounded waiters before Provider binding, supports interruptible queued Stop, and waits up to 3 seconds for dispatched process-generation retirement before handoff while the Plugin remains single-session with no provider queue; the first concurrency attempt on that device reached Provider BUSY/SESSION_OPEN because the installed Host did not yet contain FIFO integration; after installing the exact afca7b14c arm64 Host APK, the user confirmed the full documented FIFO order, fresh-PID generation handoff, queued Stop isolation, and later rerun checklist matched expectations with no issue, so the focused concurrency Android smoke passes; the no-runtime-change startup probe on QV710AF65F measured 441/447/429/427/428 ms with five distinct Plugin PIDs; the all-sample median is 429 ms, the median excluding the first run is 428.5 ms, and the maximum is 447 ms; every sample is below the 1000 ms threshold, so process retention is not justified and per-execution retirement remains; M6 consolidates the unpublished 0.2/0.3/0.4 implementation waypoints into one cumulative 0.5.0 release train and adds a read-only source profile plus a full local candidate gate with a ten-item manual Android smoke checklist; neither profile uses ADB, signing, network, tagging, pushing, or publication; M4 Path D, the exact signed-candidate smoke, beta/stable promotion, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
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
- El timeout de solicitudes acotadas se limita a 30 min. Los proyectos long-running explícitos no tienen fecha límite, pero requieren la vida Host en primer plano, un lease de inicio de 2 min y un lease de heartbeat de 45 s; sigue habiendo una sesión activa sin cola del proveedor.
- Un workspace de proyecto se limita a 64 MiB comprimidos, 8192 archivos y 128 MiB extraídos; antes del envío, la selección del Provider debe satisfacer las tres dimensiones reales del snapshot.
- Se adopta la propiedad de los PFD completos recibidos por Binder y se cierran al terminar o cerrar la sesión.
- La salida se entrega chunk a chunk con créditos durante la ejecución; al agotarse se pausa el script, la salida aceptada precede al único terminal y se prohíbe toda salida posterior.
- El JSON estructurado se limita a 64 KiB; se admiten hasta 16 artefactos con rutas de 1024 UTF-8 bytes, 4 MiB por archivo, 8 MiB en total y verificación Host de longitud exacta, EOF y SHA-256.
- El protocolo 1.5 admite hasta 1024 llamadas Host por ejecución, limita cada solicitud/respuesta a 64 KiB, el texto a 32 KiB y la espera de una acción ordinaria del hilo principal Host a 5 s. Host files usa rutas relativas de 4 KiB, texto UTF-8 de 32 KiB y listados de hasta 128 nombres de 255 UTF-8 bytes cada uno. Los diálogos de primer plano limitan el título a 256 UTF-8 bytes, el contenido a 4 KiB, los valores/respuestas prompt a 32 KiB y las listas select a 64 elementos de 1 KiB cada uno y 32 KiB en total; una respuesta puede esperar 5 min. Una ejecución puede iniciar con éxito hasta 16 scripts Host secundarios no Python, asíncronos y acotados; Python anidado devuelve `NESTED_PYTHON_NOT_ALLOWED` y `stop_self` cancela mediante reinicio del proceso.
- Las coordenadas de automator son enteros estrictos de 0 a 1000000, mientras que las duraciones de press y swipe van de 1 ms a 4 s; una accesibilidad Host no disponible lanza `CapabilityUnavailableError` sin abrir ajustes.
- Los snapshots de selector admiten como máximo 128 nodos, profundidad 32 y 48 KiB de JSON; find examina hasta 1024 nodos, el texto de nodo se limita a 256 Unicode code points, el texto de consulta a 1024 UTF-8 bytes, set_text a 4 KiB y cada ejecución conserva hasta 128 referencias de nodo. Un examen incompleto devuelve `SELECTOR_SCAN_LIMIT_EXCEEDED` y una referencia obsoleta devuelve `STALE_NODE`.
- La captura de pantalla conserva como máximo 1 imagen por ejecución, limita los datos codificados a 4 MiB, los bloques sin codificar a 32 KiB, cada dimensión a 8192 píxeles y el área total a 16777216 píxeles. Python verifica longitud, orden, EOF, SHA-256 y firma de formato antes de devolver; una accesibilidad/API no disponible lanza `CapabilityUnavailableError`, y los errores estables incluyen `SCREEN_CAPTURE_FAILED`, `RESULT_LIMIT_EXCEEDED` y `STALE_IMAGE`. La búsqueda de color recorre una captura nueva por filas con región acotada opcional y umbral por canal de hasta 255, devolviendo solo coordenada o ausencia sin transferir bytes de imagen. La búsqueda por plantilla conserva como máximo 1 plantilla PNG/JPEG, la limita a 1 MiB, transfiere bloques sin codificar de 24 KiB y limita cada dimensión a 2048, el área a 1048576, la región a 4194304 y las comparaciones a 16777216; solo participan píxeles totalmente opacos, los demás son comodines, el recorrido row-major es determinista y los búferes se liberan y borran al terminar.
- `ocr.recognize` reutiliza el contenedor PNG/JPEG de 1 MiB, bloques sin codificar de 24 KiB, 2048 píxeles por lado y 1048576 píxeles decodificados. El motor OCR configurado del Host devuelve como máximo 256 líneas, 4 KiB de UTF-8 estricto por línea y 48 KiB en total dentro del presupuesto de admisión/llamada de 60 s; un motor no disponible o fallido informa `OCR_UNAVAILABLE` o `OCR_FAILED`, y las cargas siempre se liberan y borran.
- La cancelación reinicia el proceso; las extensiones nativas y llamadas bloqueantes requieren validación Android posterior.
- El permiso `INTERNET` permite que los scripts usen directamente los clientes de red de la biblioteca estándar; pip en línea, la descarga automática de código y la instalación de paquetes de terceros en ejecución siguen sin admitirse.

******

### Capacidades no declaradas

******

- No hay stdin general en vivo ni streaming callback de `sys.stdin` directo. La interacción en primer plano solo se aplica al `input()` integrado y a `getpass.getpass()` después del EOF del snapshot finito de hasta 1 MiB. La escritura de workspace, pip en línea y descarga de wheels siguen sin soporte.
- No hay scripts UI, depurador, REPL ni acceso arbitrario a objetos Java del host.
- El broker en vivo cubre la primera entrega completa de bajo riesgo, Host files acotado, diálogos de primer plano, engines acotado, acciones automator explícitas por coordenadas/globales, snapshots/acciones acotados de selector/árbol UI, captura de pantalla, `find_color`, `find_image` y OCR por líneas. Los cuadros/confianza/opciones de OCR, el procesamiento mutable de imágenes y la coincidencia multiescala siguen sin declararse.
- No se garantiza Android de 32 bits ni wheels nativas de terceros.
- El árbol actual tiene evidencia smoke en un dispositivo API 31 arm64-v8a y en un emulador API 37 x86_64 con páginas de 16 KB; ninguna se presenta como matriz completa de dispositivos ni como calificación de release.

******

### Hoja de ruta

******

La ruta A de M4 está terminada; las evaluaciones M4 Paths B y C concluyeron `NOT_ADMITTED`, por lo que el runtime integrado sigue `stdlib-only`. Path C compiló Pillow y NumPy sin conexión, pero sus cierres native fallaron el gate ELF dual ABI de 16 KiB y OpenCV no tenía wheel Android `cp313`; Path D queda sujeto a demanda. La automatización M3 incluye acciones acotadas, selector/árbol UI, captura, búsqueda de color, plantillas PNG/JPEG y OCR del Host. Las herramientas históricas de evidencia no son gates automáticos de publicación.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historial de versiones

******

# v0.5.0-alpha.4

###### 2026/08/25

* `Nota` Cuarto candidato alpha current-tree; M6 acumula los hitos 0.2/0.3/0.4 no publicados en un solo tren 0.5.0 sin afirmar beta, versión estable, signing ni publication
* `Función` Añadir `tools/verify-m6-candidate.py` con perfiles explícitos `--source-only` y `--full` para comprobar clean Git, versión, Changelog, documentos generados y AAR lock, además de pruebas portables, puerta estática R2 y offline debug build
* `Mejora` Definir una lista Android smoke de 10 puntos y la promoción alpha → beta → 0.5.0; la puerta local no ejecuta ADB, signing, tag, push ni publication

# v0.5.0-alpha.3

###### 2026/08/24

* `Nota` Tercer candidato alpha M5 current-tree; pasan los smokes Android focalizados de long-running y FIFO Host en QV710AF65F, y la medición de arranque deja fuera la retención de proceso sin afirmar publicación ni release
* `Mejora` Medir cinco arranques fresh-process en 441/447/429/427/428 ms con cinco PID Plugin distintos; la mediana de todas las muestras es 429 ms, sin la primera ejecución 428.5 ms, y el máximo 447 ms
* `Mejora` Cerrar la evaluación de precalentamiento por debajo del umbral de 1000 ms: conservar el retiro per-execution y su aislamiento/cancelación en lugar de añadir una opción keep-process

# v0.5.0-alpha.2

###### 2026/08/24

* `Nota` Segundo candidato alpha M5 current-tree; pasan la FIFO Host y las puertas JVM/portables sin conexión, sin afirmar smoke Android concurrente, CPython paralelo real, precalentamiento, publicación ni release
* `Función` Admitir lanzamientos Python concurrentes mediante una FIFO Host justa con un propietario activo y hasta 32 esperas antes de descubrir el Provider; Stop en cola es interrumpible sin enlazar el Plugin, consumir timeout ni crear antes la notificación long-task
* `Mejora` Mantener el binding Provider hasta 3 segundos tras cerrar una sesión despachada para confirmar el retiro de generación antes del relevo FIFO; el protocolo 1.6, los tres AAR y el límite Plugin de sesión única sin cola no cambian

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

El runtime bloquea Chaquopy 17.0.0 y CPython 3.13.9 desde Maven y solo empaqueta stdlib. El gate release comprueba metadatos, bibliotecas nativas, NOTICE, signer SM003 y los tres APK distribuidos contra la identidad exacta. Pasó un smoke focalizado del árbol actual en un emulador API 37 x86_64 con páginas de 16 KB; no equivale a un gate integral de compatibilidad ni a una matriz de dispositivos.

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
