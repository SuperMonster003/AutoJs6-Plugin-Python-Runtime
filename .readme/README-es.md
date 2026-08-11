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

> Actualmente es una prueba de concepto R2. Existen el código del runtime y las comprobaciones semánticas locales del bootstrap, pero no se han ejecutado la configuración Gradle, la compilación Android, la inspección del APK, la validación Binder ni las pruebas en dispositivo.

******

### Funciones

******

- Ejecutar una instantánea UTF-8 como `__main__`.
- Conservar el orden de stdout y stderr y entregar chunks acotados mediante créditos.
- Informar `SystemExit`, errores de sintaxis y excepciones con traceback estructurado y acotado.
- Permitir una sesión activa por proceso sin cola del proveedor.
- Retirar el proceso tras cancelación, timeout o muerte del callback sin repetir el script.

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

La compilación solicita Python 3.13. 3.13.9 es la versión empaquetada esperada según la información actual de Chaquopy; no se considera verificada hasta inspeccionar el APK y ejecutarlo en dispositivo.

******

### Interfaz del complemento

******

El host descubre e invoca el complemento con las siguientes identidades:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

Solo se acepta un descriptor SOURCE. Los límites de workspace archive y stdin snapshot son cero, y no se inyectan Context, Binder, objetos del runtime host ni callback sinks.

******

### Estado de integración con el host

******

> El protocolo y el cableado del host avanzan, pero los AAR release necesarios aún no se han publicado y verificado. Instalar este scaffold no crea por sí solo un motor Python funcional de extremo a extremo.

******

### Seguridad y privacidad

******

El manifest fuente no solicita permisos Android. El servicio exportado exige el permiso de firma del host y vuelve a comprobar el UID llamante, el paquete host instalado y sus firmas. Chaquopy mantiene accesible el puente Java, por lo que el aislamiento depende de un UID Android separado, un proceso dedicado y una frontera Binder estrecha; CPython no se declara sandbox.

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

- No hay workspace archives, stdin snapshots, pip en línea ni descarga de wheels.
- No hay scripts UI, depurador, REPL ni acceso arbitrario a objetos Java del host.
- Todavía no existe un broker de capacidades AutoJs6 ni conexión con las API del host.
- No se garantiza Android de 32 bits ni wheels nativas de terceros.
- Las pruebas CPython locales no son evidencia de Chaquopy, Android, Binder o dispositivo.

******

### Hoja de ruta

******

Están presentes el repositorio R2 independiente, el límite estático, el código provider/bootstrap y las pruebas semánticas locales. Gradle y ADB se aplazan durante el soak protegido de QV710AF65F. Quedan pendientes los AAR release, dependencias, compilación Android, controles APK/16 KB, Binder/PFD y la matriz de dispositivos.

- [Ver ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Historial de versiones

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

Pruebas semánticas portátiles del bootstrap con el CPython local:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Estas comprobaciones no demuestran que Android funcione. Gradle, APK, Binder y dispositivo deben validarse tras el soak protegido.

******

### Compilación

******

No se ejecuta ninguna compilación. La configuración release falla cerrada mientras falten los AAR o sus SHA-256.

Estos AAR release deben colocarse y bloquearse en `libs` antes de compilar:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

El runtime usará Chaquopy 17.0.0 desde Maven y solo empaquetará stdlib. Metadatos de verificación, bibliotecas nativas, licencias y compatibilidad con páginas de 16 KB siguen pendientes.

******

### Licencia

******

El código fuente usa MPL-2.0. Chaquopy, CPython y los demás componentes conservan sus licencias.

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
