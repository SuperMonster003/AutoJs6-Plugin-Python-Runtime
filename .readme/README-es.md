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
protocol: 1.0-1.5
```

El complemento acepta una SOURCE independiente, un workspace archive acotado opcional, un snapshot stdin finito y preproporcionado de hasta 1 MiB y el snapshot de capacidades host de solo lectura del protocolo 1.1. El protocolo 1.2 añade negociación explícita de entrada file/module para proyectos admitidos. El protocolo 1.3 añade, tras el EOF del snapshot, prompt/respuesta propiedad del Host y solo en primer plano para el `input()` integrado; `getpass.getpass()` usa entrada oculta. El protocolo 1.4 añade JSON estricto explícito y artefactos opcionales manifestados con SHA-256; stdout sigue siendo diagnóstico y nunca se analiza como resultado. El protocolo 1.5 añade un broker Host de datos puros ligado a una ejecución, al UID del complemento, al orden de llamadas y a una cuota finita. Los diálogos Host también requieren autorización de primer plano respaldada por una Activity activa; los inicios en segundo plano reciben `INTERACTIVE_NOT_ALLOWED` sin abrir UI. `sys.stdin` directo sigue siendo finito, los inicios en segundo plano nunca abren UI de entrada y los scripts no reciben Context, Binder bruto, objetos del runtime host ni callback sinks.

******

### Estado de integración con el host

******

> La versión 0.1.0 se empareja solo con AutoJs6 6.8.0, con el versionCode mínimo del Host 5275 congelado y aplicado; la revisión final y limpia del código fuente del Host y el manifiesto de distribución de los tres AAR están registrados en el lock. Cada ejecución nueva redescubre el provider; si falta o está desactivado pide instalar o activar sin fallback, y la instalación o reactivación no exige reiniciar el Host. La identidad del APK estable está vinculada a ese código fuente exacto del Plugin y al lock Host.

```text
release target: 0.4.0-alpha.8
release state: 0.4.0-alpha.8 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time package evaluation is complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; no candidate dependency payload was added and no new device claim is made; later demand-driven M3 batches, M4 Path C, a complete device matrix, publication, and release evidence remain outside this claim
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
- El timeout máximo es 30 min, con una sesión activa y sin cola del proveedor.
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

La ruta A de M4 está terminada; la evaluación de paquetes integrados de M4 Path B concluyó `NOT_ADMITTED`, por lo que el runtime integrado sigue `stdlib-only`; la evaluación native de M4 Path C continúa según el valor para el usuario. La automatización M3 incluye acciones acotadas, selector/árbol UI, captura, búsqueda de color, plantillas PNG/JPEG y OCR del Host. Las herramientas históricas de evidencia siguen disponibles sin ser gates automáticos de publicación.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historial de versiones

******

# v0.4.0-alpha.8

###### 2026/08/24

* `Nota` Octavo candidato alpha del árbol actual; cerrar la evaluación de paquetes integrados M4 Path B como `NOT_ADMITTED`, mantener el runtime `stdlib-only`, no añadir `requests` ni ninguna dependencia candidata y no formular una nueva afirmación de aceptación en dispositivos
* `Mejora` ADR 0003 registra bases stdlib-only debug APK de 23,709,688 bytes para arm64-v8a, 23,726,048 bytes para x86_64 y 34,622,039 bytes para universal; no inventar una diferencia de tamaño sin un wheelhouse offline auditado, y exigir Gradle `--offline`, `--no-index`, `--require-hashes`, bloqueos de licencia/hash, diferencias de tres APK y aceptación pública dual ABI para una admisión futura

# v0.4.0-alpha.7

###### 2026/08/24

* `Nota` Séptimo candidato alfa current-tree de automatización M3; el flujo completo de Settings real pasó en el emulador API 37, mientras que la publicación, las rutas M4 B/C y la matriz completa de dispositivos quedan fuera de esta declaración
* `Función` Añade `m3_complete_automation`, un flujo acotado sobre Settings real que usa `app.launch`, `selector.find`, `selector.click` e `images.capture_screen`, con aserciones estrictas de PNG y contención del control de destino
* `Corrección` Normaliza antes de serializar a Python los límites de accesibilidad con `right < left` o `bottom < top` como ejes zero-area anclados, mientras las consultas selector exactas aíslan nodos no relacionados
* `Mejora` La ruta pública de proyecto exportada `RunIntentActivity` pasa en un emulador API 37 con PNG 1080x2424 y artefacto verificado por SHA-256; después restaura accesibilidad a 0/null y elimina todo staging exacto de prueba

# v0.4.0-alpha.6

###### 2026/08/24

* `Nota` Sexto candidato alpha current-tree de automatización M3; el reconocimiento OCR Host configurado pasó en un emulador API 37 con servicio elegible y falló de forma cerrada en un dispositivo físico API 31 sin cambiar sus servicios de accesibilidad; OCR más amplio, publicación y una matriz completa quedan fuera de esta afirmación
* `Función` Añadir `autojs6.ocr.recognize(image)` para bytes PNG/JPEG acotados y una tupla inmutable y ordenada de líneas del motor OCR Host configurado
* `Mejora` Reutilizar la carga PNG/JPEG de 1 MiB en bloques sin codificar de 24 KiB con verificación SHA-256, seleccionar solo un servicio OCR Host habilitado, autorizado y compatible, limitar el resultado a 256 líneas, 4 KiB de UTF-8 estricto por línea y 48 KiB en total, hacer siempre release y borrado de búferes, e informar `OCR_UNAVAILABLE` u `OCR_FAILED` de forma estable

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
