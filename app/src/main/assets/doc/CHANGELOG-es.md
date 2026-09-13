******

### Historial de versiones

******

# v0.5.2

###### 2026/09/13

* `Nota` Candidato de código estable 0.5.2; la aceptación final en dispositivos y la publicación siguen separadas de los resultados beta históricos
* `Corrección` Corregir la lectura de archivos de salida en Android 7 conservando la protección de descriptores y enlaces simbólicos
* `Corrección` Informar solo de las ABI nativas presentes en el APK instalado

# v0.5.1

###### 2026/09/13

* `Nota` Candidato de código estable 0.5.1; la aceptación final en dispositivos y la publicación siguen separadas de los resultados beta históricos
* `Corrección` Fallo de compilación Release después de clean cuando falta el archivo de reglas ProGuard generado por Chaquopy
* `Mejora` Verificación de compilación de la alineación de páginas de 16 KB en bibliotecas nativas de 64 bits, con controles del contrato manifest e informes JSON
* `Mejora` Activación del host, metadatos, documentación traducida y recopilación de APK firmados conforme a las convenciones comunes

# v0.5.0

###### 2026/08/25

* `Nota` 0.5.0 es el candidato de código estable acumulativo; el candidato beta exacto firmado con SM003 superó las 10 pruebas Android, sin declarar un APK estable, tag ni publicación completada
* `Función` M6 consolida las capacidades M1-M5 y los materiales reutilizables de los puntos 2/3/4, y fija los límites ligeros alpha → beta → stable y de publicación
* `Mejora` El APK arm64 0.5.0-beta.1 extraído de QV710AF65F fue idéntico byte a byte al candidato formal; la segunda ejecución completa terminó con 10/10 PASS

# v0.5.0-beta.1

###### 2026/08/25

* `Nota` 0.5.0-beta.1 es un candidato de código con funciones congeladas; el candidato alpha exacto firmado con SM003 superó las 10 pruebas Android, sin declarar un APK beta, versión estable ni publicación completada
* `Función` M6 añade proyectos reutilizables para los puntos 2/3/4 y un verificador artifact independiente para validar de forma repetible imports, stdin/entrada interactiva y resultados estructurados
* `Mejora` El APK arm64 0.5.0-alpha.6 extraído de QV710AF65F fue idéntico byte a byte al candidato formal; la lista completa terminó con 10/10 PASS

# v0.5.0-alpha.6

###### 2026/08/25

* `Nota` Sexto candidato alpha current-tree; completar el contrato AutoJs6 WakeActivity para la primera activación del Plugin en OnePlus OPD2413 y OEM similares, sin afirmar un production signed candidate, beta ni publicación
* `Corrección` Declarar `org.autojs.plugin.WAKE_ACTIVITY` y `org.autojs.plugin.action.WAKE` con una Activity NoDisplay protegida por permiso de firma y de finalización inmediata; `ACTIVATE` en Plugin Center puede limpiar `stopped/notLaunched` y reintentar la activación automáticamente
* `Mejora` Reproducir y recuperar el fallo original con el Host debug `afca7b14c` y un Plugin de diagnóstico con el mismo signer, devolviendo el resultado startup probe a `277 ms`; confirmar por separado que un signer distinto falla de forma cerrada como `PYTHON_RUNTIME_PROVIDER_UNTRUSTED`

# v0.5.0-alpha.5

###### 2026/08/25

* `Nota` Quinto candidato alpha current-tree; reconstruir los tres AAR release de la Host API desde el commit clean exacto `afca7b14c` con bytes idénticos y actualizar el provenance lock a ese origen, sin declarar un signed APK, el smoke Android de diez puntos, beta ni publication
* `Mejora` Ejecutar Host `verifyPythonReleaseApiDistributionGate` en un worktree aislado y fijar AutoJs6 6.8.0/versionCode 5276, el protocolo 1.6, el source fingerprint y el SHA-256 del distribution manifest con `dirty=false`

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

# v0.5.0-alpha.1

###### 2026/08/24

* `Nota` Primer candidato alpha M5 del árbol actual; el modo long-running foreground del protocolo 1.6 y las pruebas JVM Host/Plugin offline y portables pasan, pero no se ejecutó smoke Android M5 ni se afirman publicación, concurrencia o precalentamiento
* `Función` Añadir `executionMode=long-running` por proyecto sin fecha límite, propiedad de un servicio Host `specialUse` en primer plano, notificación persistente y acción Stop; los inicios programados, background/Intent y de desarrollador se rechazan sin degradación
* `Mejora` Emitir heartbeats Provider ordenados cada 15 s y aplicar leases Host de 2 min para inicio, 45 s para heartbeat y uno independiente del servicio foreground; la pérdida de vida y Stop fallan cerrados mediante reinicio de proceso mientras el protocolo acotado 1.0-1.5 conserva compatibilidad

# v0.4.0-alpha.9

###### 2026/08/24

* `Nota` Noveno candidato alpha del árbol actual; cerrar M4 Path C native como `NOT_ADMITTED`, mantener el runtime `stdlib-only`, no añadir payload de Pillow, NumPy, OpenCV ni native transitivo y no formular una nueva afirmación de aceptación en dispositivos
* `Mejora` ADR 0004 registra debug builds offline dual ABI con `--no-index --find-links`: Pillow 11.0.0 añade 2,054,483 bytes a cada APK, NumPy 1.26.2 añade 21,931,164 bytes y las seis salidas pasan `zipalign -c -P 16 4`
* `Mejora` La auditoría ELF NDK 29 del cierre completo rechaza FreeType a `0x1000` en ambos ABI y OpenBLAS/libgfortran a `0x1000` en x86_64; OpenCV no tiene wheel Android `cp313` oficial y reabrir exige wheels NDK r28+ reproducibles y aceptación pública de 16 KiB

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

# v0.4.0-alpha.5

###### 2026/08/24

* `Nota` Quinto candidato alpha de automatización M3 del árbol actual; la búsqueda acotada por plantilla pasó en un emulador API 37 con accesibilidad y falló de forma cerrada en un dispositivo físico API 31 sin cambiar sus servicios de accesibilidad; OCR, publicación y una matriz completa quedan fuera de esta afirmación
* `Función` Añadir `autojs6.images.find_image(template, *, region=None, threshold=0)` para bytes PNG/JPEG, una región acotada opcional y un resultado de coordenada superior izquierda o `None`
* `Mejora` Subir una plantilla por ejecución de hasta 1 MiB en bloques brutos de 24 KiB con verificación SHA-256, decodificar como máximo 2048 píxeles por lado, recorrer de forma determinista en row-major bajo `autojs6-python-image-match-v1`, usar píxeles totalmente opacos como participantes y los demás como comodines, no requerir OpenCV, siempre hacer release y borrar los búferes, y reintentar solo el límite Android de 333 ms tras una espera acotada de 350 ms

# v0.4.0-alpha.4

###### 2026/08/24

* `Nota` Cuarto candidato alpha de automatización M3 del árbol actual; la búsqueda acotada de color pasó en un emulador API 37 con accesibilidad y falló de forma cerrada en un dispositivo físico API 31 sin cambiar sus servicios; búsqueda por plantilla, OCR, publicación y matriz completa quedan fuera de esta declaración
* `Función` Añadir `autojs6.images.find_color(color, *, region=None, threshold=0)` para enteros RGB estrictos o texto `#RRGGBB`, región acotada opcional y resultado coordenada o `None`
* `Mejora` Capturar una nueva pantalla de accesibilidad Android 11+ por llamada, recorrerla en orden row-major determinista con umbral por canal de 0 a 255, validar `autojs6-python-color-match-v1` exacto y no transferir bytes ni handles de imagen a Python

# v0.4.0-alpha.3

###### 2026/08/24

* `Nota` Tercer candidato alpha M3 de automatización del árbol actual; la ruta completa de captura de pantalla acotada para Android 11+ superó la aceptación focalizada en un emulador API 37 con accesibilidad habilitada, y el cierre seguro superó la prueba en un dispositivo físico API 31 sin cambiar sus servicios de accesibilidad; búsqueda de imagen/color, OCR, publicación y una matriz completa quedan fuera de esta declaración
* `Función` Añade `autojs6.images.capture_screen`, que devuelve bytes PNG/JPEG verificados o escribe y publica atómicamente un artefacto de salida de ejecución
* `Mejora` Conserva como máximo 1 captura por ejecución, transfiere bloques sin codificar de 32 KiB y limita los datos codificados a 4 MiB; Python verifica orden, EOF, SHA-256 y firmas de formato y siempre ejecuta release, mientras Host borra al reemplazar/release/terminar y comunica errores estables sin habilitar servicios ni abrir ajustes

# v0.4.0-alpha.2

###### 2026/08/24

* `Nota` Segundo candidato alpha M3 de automatización del árbol actual; la ruta completa y acotada de selector/árbol UI superó la aceptación focalizada en un emulador API 37 con accesibilidad habilitada, y el cierre seguro superó la prueba en un dispositivo físico API 31 sin cambiar sus servicios de accesibilidad; capturas, OCR, publicación y una matriz completa quedan fuera de esta declaración
* `Función` Añadir las API en vivo `autojs6.selector.snapshot/find/click/set_text` para datos separados del árbol de accesibilidad, consultas de primera coincidencia compuestas con AND y acciones explícitas mediante referencias opacas de nodo ligadas a la ejecución
* `Mejora` Limitar nodos, profundidad, carga y texto de snapshot, tamaño de búsqueda, texto de consulta/asignación y nodos retenidos; informar búsquedas incompletas como `SELECTOR_SCAN_LIMIT_EXCEEDED`, referencias obsoletas como `STALE_NODE` y accesibilidad no disponible como `CapabilityUnavailableError` sin abrir ajustes

# v0.4.0-alpha.1

###### 2026/08/23

* `Nota` Primer candidato alpha M3 de automatización del árbol actual; las acciones acotadas por coordenadas/globales pasaron la aceptación focalizada en un emulador API 37 con accesibilidad habilitada y fail-closed pasó en un dispositivo físico API 31 sin cambiar sus servicios de accesibilidad, mientras selector/árbol UI, capturas, OCR, publicación y una matriz completa quedan fuera de esta declaración
* `Función` Añadir las API en vivo `autojs6.automator.click/long_click/press/swipe/back/home` mediante la accesibilidad Host, devolviendo el resultado booleano real del envío
* `Mejora` Exigir coordenadas enteras estrictas no booleanas de 0 a 1000000 y duraciones press/swipe de 1 a 4000 ms; una accesibilidad Host no disponible lanza `CapabilityUnavailableError` sin abrir ajustes

# v0.3.0-alpha.6

###### 2026/08/23

* `Nota` Primer candidato alpha M4 del árbol actual; la ruta de dependencias Python puras locales al proyecto pasó la aceptación focalizada en dos dispositivos, mientras los siguientes lotes M3/M4, la publicación y una matriz completa quedan fuera de esta declaración
* `Función` Admitir paquetes Python puros locales al proyecto y metadatos `.dist-info` desde raíces admitidas, con un ejemplo `requests` reproducible y fijado, sin instalador en ejecución
* `Mejora` Elevar los límites del workspace a 64 MiB comprimidos, 8192 archivos y 128 MiB extraídos, y comparar antes del envío las tres dimensiones reales del snapshot con las capacidades del Provider; un import ausente sigue siendo `ModuleNotFoundError`, sin pip en línea ni respaldo de motor

# v0.3.0-alpha.5

###### 2026/08/23

* `Nota` Quinto candidato alpha M3 del árbol actual; la parte acotada de Host engines de la segunda entrega superó la aceptación focalizada en dos dispositivos, sin afirmar capacidades posteriores, publicación ni una matriz completa de dispositivos
* `Función` Añadir las API en vivo `autojs6.engines.current/run/stop_self` para metadatos del motor actual sin rutas, lanzamiento asíncrono de scripts Host secundarios no Python y detención propia determinista
* `Mejora` Aceptar solo rutas secundarias normalizadas relativas a la raíz de ejecución y hasta 16 lanzamientos exitosos por ejecución; Python anidado falla con `NESTED_PYTHON_NOT_ALLOWED`, mientras `stop_self` cancela reiniciando el proceso provider

# v0.3.0-alpha.4

###### 2026/08/23

* `Nota` Cuarto candidato alpha M3 del árbol actual; los diálogos Host en primer plano superaron la aceptación focalizada en dos dispositivos, sin afirmar engines, capacidades posteriores, publicación ni una matriz completa de dispositivos
* `Función` Añadir las API solo en primer plano `autojs6.dialogs.alert/confirm/prompt/select`, con resultados tipados de acuse, confirmación, texto anulable e índice anulable desde cero
* `Mejora` Limitar títulos, contenido, respuestas y elementos, serializar un diálogo propiedad del Host a la vez y rechazar inicios en segundo plano con `INTERACTIVE_NOT_ALLOWED` sin abrir UI

# v0.3.0-alpha.3

###### 2026/08/23

* `Nota` Tercer candidato alpha M3 del árbol actual; la parte acotada de Host files de la segunda entrega superó la aceptación focalizada en dos dispositivos, sin afirmar diálogos, engines, capacidades posteriores, publicación ni una matriz completa de dispositivos
* `Función` Añadir las API en vivo `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` para acceso acotado a texto UTF-8 dentro de la raíz del proyecto actual o el directorio del script independiente
* `Mejora` Rechazar rutas inseguras o fuera de la raíz, limitar texto y listados directos, devolver errores de archivo estables y separar la raíz Host en vivo de la instantánea workspace congelada del Plugin

# v0.3.0-alpha.2

###### 2026/08/23

* `Nota` Segundo candidato alpha M3 del árbol actual; se implementó la primera entrega completa de capacidades Host de bajo riesgo, sin afirmar entregas posteriores, publicación ni una matriz completa de dispositivos
* `Función` Añadir datos en vivo de batería/pantalla/brillo/volumen con `autojs6.device.info()`, niveles de consola Host `autojs6.console.log/warn/error` y notificaciones `autojs6.notice`
* `Mejora` Validar estrictamente el esquema de device y devolver `PERMISSION_DENIED` estable sin abrir ajustes ni cambiar permisos del dispositivo

# v0.3.0-alpha.1

###### 2026/08/23

* `Nota` Primer candidato alpha M3 del árbol actual; el protocolo 1.5 y el subconjunto de capacidades Host de bajo riesgo están implementados, sin afirmar capacidades posteriores, publicación ni una matriz completa de dispositivos
* `Función` Añadir el broker de capacidades Host del protocolo 1.5 ligado a la ejecución mediante JSON de datos puros, UUID de solicitud, UID del complemento, IDs de llamada monótonos, cuota de 1024 llamadas, mensajes de 64 KiB y límite de dispatch Host de 5 segundos
* `Función` Añadir las API Host en vivo `autojs6.toast`, `autojs6.clip.get/set` y `autojs6.app.launch/launch_app/open_url`
* `Mejora` Revocar el broker de forma uniforme al terminar, cancelar, morir Binder o limpiar, con errores Python estables

# v0.2.0-alpha.1

###### 2026/08/13

* `Nota` Candidato alpha U1 del árbol actual posterior a 0.1; la entrada module, salida live, input integrado en primer plano, JSON estructurado explícito y artefactos acotados de U1-R2 solo están cubiertos hasta E2; los inicios en segundo plano y sys.stdin directo siguen sin interacción, R2 E3 continúa abierto y estos resultados no prueban matriz de dispositivos, lanzamiento ni publicación
* `Función` Añade un snapshot stdin finito y preproporcionado de hasta 1 MiB para entrada y EOF deterministas mediante `input()` y `sys.stdin`
* `Función` Completa los imports de proyecto para módulos workspace, módulos hermanos y raíz de una entrada anidada e imports relativos al package
* `Función` Añade el protocolo 1.2 con `entryMode=file|module` explícito; la ejecución module usa `runpy` con `__package__`, `__spec__`, la raíz del proyecto en `sys.path[0]` e imports relativos correctos, mientras el modo file no cambia
* `Función` Añade con el protocolo 1.3 prompt/respuesta acotado y solo en primer plano tras el EOF del snapshot finito, con entrada visible para `input()` y oculta para `getpass.getpass()`; los inicios en segundo plano nunca abren UI de entrada y `sys.stdin` directo sigue finito
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
