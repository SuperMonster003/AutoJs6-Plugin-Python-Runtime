******

### Historial de versiones

******

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
