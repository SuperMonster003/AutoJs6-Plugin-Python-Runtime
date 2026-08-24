<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>Независимая среда Python. Запуск сценариев в отдельном процессе плагина</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Языки

******

Текущий README.md доступен на следующих языках:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- Русский [ru] # текущий
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### Введение

******

Python Runtime — независимый provider протокола Python V1. Хост передает один снимок исходного кода в отдельный процесс, который выполняет его в CPython и возвращает ограниченный вывод, структурированные исключения и одно терминальное состояние.

> Идентичность исходников 0.1.0 и точный Host lock заморожены. Существующие локальные RC-свидетельства build, APK, Binder и одного устройства API 31 arm64-v8a остаются историческими; stable APK/P3 provenance привязана к exact release identity, а production receipt является отдельным уровнем доказательства после публикации.

******

### Возможности

******

- Выполнение одного UTF-8 снимка Python как `__main__`.
- Принимается конечный заранее переданный stdin snapshot размером до 1 MiB; после его EOF явный запуск на переднем плане может продолжить встроенный `input()` через ограниченный prompt/reply протокола 1.3, а стандартный `getpass.getpass()` использует скрытый ввод.
- Явный выбор `entryMode=file|module` для допущенного проекта: режим module использует стандартные метаданные `runpy`, корень проекта в `sys.path[0]` и относительные импорты пакета, а режим file сохраняет обычную семантику скрипта.
- Импорт локальных для проекта pure-Python пакетов и метаданных `.dist-info` из допущенного корня без online pip и установки во время выполнения.
- Передача ограниченных chunks stdout/stderr в исходном порядке во время выполнения; исчерпание credits создаёт backpressure для выполнения.
- Явное задание строгого JSON-результата до 64 KiB и передача до 16 необязательных output artifacts с ограничениями пути, размера и SHA-256 протокола 1.4; результат никогда не выводится из stdout.
- Вызов live-операций `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, учитывающего разрешения `notice`, ограниченного `files.read_text/write_text/exists/is_file/is_dir/list`, доступного только на переднем плане `dialogs.alert/confirm/prompt/select`, `engines.current/run/stop_self`, ограниченного `automator.click/long_click/press/swipe/back/home`, ограниченного `selector.snapshot/find/click/set_text`, `images.capture_screen`, `images.find_color`, `images.find_image` и `ocr.recognize` через привязанный к выполнению pure-data broker протокола 1.5, который отзывается при завершении.
- Протокол 1.6 добавляет явные проекты `executionMode=long-running` без deadline выполнения, с foreground-уведомлением Host, действием Stop и упорядоченными heartbeat Provider каждые 15 s; фоновые поверхности завершаются fail closed без downgrade.
- Возврат `SystemExit`, синтаксических и runtime ошибок с ограниченным структурированным traceback.
- Один активный сеанс на процесс без очереди provider.
- Перезапуск хоста не нужен: следующая новая сессия после установки или повторного включения заново обнаруживает и фиксирует provider, а Binder death во время выполнения завершает его без автоматического повтора.

******

### Среда и форматы данных

******

Протокол V1 сейчас объявляет следующий диапазон:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

Сборка запрашивает Python 3.13. Замороженные локальные RC-артефакты и точный запуск на устройстве зафиксировали CPython 3.13.9; версию и hashes финальной 0.1.0 нужно проверить заново после заморозки исходников.

******

### Интерфейс плагина

******

Хост находит и вызывает плагин по следующим идентификаторам:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.6
```

Принимаются отдельный SOURCE, необязательный ограниченный workspace archive, конечный заранее переданный stdin snapshot размером до 1 MiB и read-only snapshot возможностей хоста протокола 1.1. Протокол 1.2 добавляет явное согласование входа file/module для допущенных проектов. Протокол 1.3 добавляет после EOF snapshot принадлежащий Host prompt/reply только для встроенного `input()` на переднем плане, а стандартный `getpass.getpass()` использует скрытый ввод. Протокол 1.4 добавляет явный строгий JSON и необязательные output artifacts с манифестом SHA-256; stdout остается диагностикой и никогда не разбирается как результат. Протокол 1.5 добавляет pure-data Host broker, привязанный к одному выполнению, UID плагина, порядку вызовов и конечной квоте. Диалоги Host также требуют foreground-разрешения с активной Activity; фоновый запуск не открывает UI и возвращает `INTERACTIVE_NOT_ALLOWED`. Прямой `sys.stdin` остается конечным, фоновые запуски не открывают UI ввода, а скрипты не получают Context, raw Binder, объекты Host runtime или callback sink.

******

### Состояние интеграции с хостом

******

> Версия 0.1.0 предназначена только для AutoJs6 6.8.0; минимальный Host versionCode 5275 зафиксирован и принудительно проверяется. Финальная clean Host source revision и manifest дистрибутива из трех AAR записаны в lock. Каждый новый запуск заново обнаруживает provider; при отсутствии или отключении предлагается установка или включение без fallback, а после установки или включения Host перезапускать не нужно. Stable APK identity привязана к этой exact Plugin source и Host lock.

```text
release target: 0.5.0-alpha.1
release state: 0.5.0-alpha.1 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time pure-Python and M4 Path C native-package evaluations are complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; Path C built the official Pillow 11.0.0 and NumPy 1.26.2 dual-ABI closures offline, but transitive 4 KiB ELF LOAD segments failed the 16 KiB gate, and the official OpenCV index had no cp313 Android wheel; no candidate dependency payload was added; protocol 1.6 adds an explicit foreground-only long-running mode with a Host specialUse foreground notification, manual Stop, and 15-second Provider heartbeats under fail-closed leases; Host and Plugin offline JVM plus portable source gates passed, but no M5 Android device smoke has run and no new device claim is made; concurrency, prewarm, later demand-driven M3 batches, M4 Path D, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### Безопасность и конфиденциальность

******

Runtime Chaquopy предназначен только для доверенных локальных сценариев, а не как hostile-code sandbox. Exported service требует signature permission хоста и проверяет UID, package и signer; отдельный Android UID, процесс и узкая граница Binder уменьшают воздействие, но не делают Python sandbox. Долгосрочный release signer — SM003, а SuperMonster003 отвечает за runtime, security и release.

******

### Ограничения

******

- Источник ограничен 4 MiB, весь вывод 16 MiB, chunk 16 KiB, число chunks 16384.
- Timeout ограниченного запроса не превышает 30 min. Явные long-running проекты не имеют deadline, но требуют foreground lifetime Host, стартовую аренду 2 min и heartbeat-аренду 45 s; по-прежнему активен один сеанс без очереди provider.
- Workspace проекта ограничен 64 MiB в сжатом виде, 8192 файлами и 128 MiB после извлечения; до dispatch выбор Provider должен удовлетворять всем трем фактическим измерениям snapshot.
- Полные PFD на стороне получателя Binder принимаются во владение и закрываются при завершении или close.
- Вывод передаётся по chunks и credits во время выполнения; при исчерпании credits скрипт приостанавливается, принятый вывод предшествует единственному terminal, а вывод после terminal запрещён.
- Структурированный JSON ограничен 64 KiB; допускается до 16 artifacts с путем до 1024 UTF-8 bytes, 4 MiB на файл, 8 MiB суммарно и проверкой Host точной длины, EOF и SHA-256.
- Протокол 1.5 допускает до 1024 Host-вызовов на выполнение, ограничивает request/response значением 64 KiB, текст — 32 KiB, а ожидание обычного действия главного потока Host — 5 s. Host files использует относительные пути до 4 KiB, UTF-8 текст до 32 KiB и списки до 128 имён размером до 255 UTF-8 bytes каждое. Foreground-диалоги ограничивают заголовок 256 UTF-8 bytes, содержимое 4 KiB, default/reply prompt 32 KiB, а select — 64 элементами по 1 KiB и 32 KiB суммарно; ответ пользователя ожидается до 5 min. Одно выполнение может успешно асинхронно запустить до 16 ограниченных корнем дочерних Host-скриптов не на Python; вложенный Python возвращает `NESTED_PYTHON_NOT_ALLOWED`, а `stop_self` отменяет выполнение перезапуском процесса.
- Координаты automator принимают только строгие целые числа от 0 до 1000000, а длительность press и swipe — от 1 ms до 4 s; при недоступной Host accessibility возникает `CapabilityUnavailableError` без открытия настроек.
- Snapshot selector допускает не более 128 узлов, глубину 32 и 48 KiB JSON; find сканирует не более 1024 узлов, текст узла ограничен 256 Unicode code points, текст запроса — 1024 UTF-8 bytes, set_text — 4 KiB, а одно выполнение сохраняет не более 128 ссылок на узлы. Неполное сканирование возвращает `SELECTOR_SCAN_LIMIT_EXCEEDED`, устаревшая ссылка — `STALE_NODE`.
- Screen capture сохраняет не более 1 изображения на выполнение, ограничивает encoded data до 4 MiB, raw chunk до 32 KiB, каждую сторону до 8192 пикселей и общую площадь до 16777216 пикселей. Python проверяет длину, порядок, EOF, SHA-256 и сигнатуру формата перед возвратом; недоступность accessibility/API вызывает `CapabilityUnavailableError`, остальные стабильные ошибки включают `SCREEN_CAPTURE_FAILED`, `RESULT_LIMIT_EXCEEDED` и `STALE_IMAGE`. Color search сканирует новый снимок по строкам с необязательной ограниченной областью и порогом каждого канала до 255, возвращая только координату или отсутствие без передачи байтов изображения. Template search сохраняет не более 1 PNG/JPEG template, ограничивает его до 1 MiB, передаёт raw chunk по 24 KiB и ограничивает сторону до 2048, площадь до 1048576, search region до 4194304 и comparisons до 16777216; участвуют только полностью непрозрачные pixels, остальные служат wildcard, сканирование deterministic row-major, а buffers освобождаются и обнуляются при завершении.
- `ocr.recognize` повторно использует PNG/JPEG envelope размером 1 MiB, raw chunks по 24 KiB, до 2048 pixels на сторону и 1048576 декодированных pixels. Настроенный Host OCR engine в существующем admission/call budget 60 s возвращает не более 256 строк, 4 KiB strict UTF-8 на строку и 48 KiB суммарно; недоступность и сбой обозначаются `OCR_UNAVAILABLE` и `OCR_FAILED`, а upload всегда освобождается и обнуляется.
- Отмена перезапускает процесс; native extensions и блокирующие вызовы требуют Android-проверки.
- Разрешение `INTERNET` позволяет скриптам напрямую использовать сетевые клиенты стандартной библиотеки; online pip, автоматическая загрузка кода и установка сторонних пакетов во время выполнения по-прежнему не поддерживаются.

******

### Необъявленные возможности

******

- Общий live stdin и callback streaming прямого `sys.stdin` недоступны. Интерактивность на переднем плане применяется только к встроенному `input()` и стандартному `getpass.getpass()` после EOF конечного snapshot до 1 MiB. Запись в workspace, online pip и загрузка wheels по-прежнему не поддерживаются.
- Нет UI-сценариев, debugger, REPL и произвольного доступа к Java-объектам хоста.
- Live broker охватывает полный первый низкорисковый набор, ограниченный Host files, foreground dialogs, ограниченный engines, явные координатные/global automator actions, ограниченные snapshot/actions selector/UI tree, screen capture, `find_color`, `find_image` и построчный OCR. OCR boxes/confidence/options, изменяемая обработка изображений и multi-scale matching пока не заявлены.
- 32-разрядный Android и произвольные native wheels не гарантируются.
- Для текущего дерева есть smoke evidence на устройстве API 31 arm64-v8a и эмуляторе API 37 x86_64 со страницами 16 KB; это не выдается за полную матрицу устройств или release qualification.

******

### План

******

M4 Path A завершен; оценки M4 Paths B и C обе завершились решением `NOT_ADMITTED`, поэтому встроенный runtime остается `stdlib-only`. В Path C Pillow и NumPy собраны offline, но полные native-замыкания не прошли dual ABI ELF gate 16 KiB, а для OpenCV нет Android wheel `cp313`; Path D остается по запросу. Автоматизация M3 включает ограниченные actions, selector/UI tree, screen capture, color search, PNG/JPEG template matching и Host OCR. Исторические инструменты доказательств не являются автоматическими воротами выпуска.

- [Открыть ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### История версий

******

# v0.5.0-alpha.1

###### 2026/08/24

* `Примечание` Первый M5 current-tree alpha-кандидат; foreground long-running протокола 1.6 и offline JVM-тесты Host/Plugin с portable gate проходят, но M5 Android smoke не запускался и публикация, concurrency и prewarm процесса не заявляются
* `Добавлено` Добавлен проектный `executionMode=long-running` без deadline, которым владеют Host `specialUse` foreground service, постоянное уведомление и действие Stop; плановые, background/Intent и developer-запуски отклоняются без downgrade
* `Улучшено` Provider отправляет упорядоченные heartbeat каждые 15 s, Host проверяет start lease 2 min, heartbeat lease 45 s и независимую аренду foreground service; потеря liveness и Stop fail closed через перезапуск процесса, а bounded protocol 1.0-1.5 остается совместимым

# v0.4.0-alpha.9

###### 2026/08/24

* `Примечание` Девятый alpha-кандидат текущего дерева; оценка native-пакетов M4 Path C закрыта решением `NOT_ADMITTED`, встроенный runtime остается `stdlib-only`, payload Pillow, NumPy, OpenCV и транзитивных native-зависимостей не добавлен, новые заявления о приемке на устройствах не делаются
* `Улучшено` ADR 0004 фиксирует dual ABI offline debug builds с `--no-index --find-links`: Pillow 11.0.0 добавляет 2,054,483 bytes к каждому APK, NumPy 1.26.2 добавляет 21,931,164 bytes, все шесть выходов проходят `zipalign -c -P 16 4`
* `Улучшено` Полный ELF-аудит NDK 29 отклоняет FreeType с `0x1000` на обеих ABI и OpenBLAS/libgfortran с `0x1000` на x86_64; для OpenCV нет официального Android wheel `cp313`, а повторное открытие требует воспроизводимых wheels NDK r28+ и публичной приемки 16 KiB

# v0.4.0-alpha.8

###### 2026/08/24

* `Примечание` Восьмой alpha-кандидат текущего дерева; оценка встроенных пакетов M4 Path B закрыта решением `NOT_ADMITTED`, встроенный runtime остается `stdlib-only`, `requests` и другие кандидаты не добавлены, новые заявления о приемке на устройствах не делаются
* `Улучшено` ADR 0003 фиксирует stdlib-only debug APK базы: 23,709,688 bytes для arm64-v8a, 23,726,048 bytes для x86_64 и 34,622,039 bytes для universal; без проверенного offline wheelhouse ложная разница размеров не публикуется, а будущий допуск требует Gradle `--offline`, `--no-index`, `--require-hashes`, license/hash locks, разницы трех APK и приемки публичного пути dual ABI

##### Другие версии

* [CHANGELOG-ru.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-ru.md)

******

### Проверка

******

Статическая проверка файлов без Gradle и ADB:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

Переносимые семантические тесты bootstrap в локальном CPython:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Статические проверки и локальный CPython не заменяют Android-свидетельства. Существующие RC и результат одного устройства исторические; release acceptance использует build, APK, Binder и representative-device проверки, связанные с exact identity.

******

### Сборка

******

Генерация документации сама не запускает сборку. Release-конфигурация fail closed при drift AAR, SHA-256, signer или runtime lock; stable artifacts принимаются только при связи с exact release identity.

Перед сборкой следующие release AAR нужно разместить и зафиксировать в `libs`:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

Runtime фиксирует Chaquopy 17.0.0 и CPython 3.13.9 из Maven и включает только stdlib. Release gate проверяет metadata, native libraries, NOTICE, signer SM003 и три распространяемых APK относительно exact identity. Сфокусированный smoke текущего дерева на эмуляторе API 37 x86_64 со страницами 16 KB пройден; это не комплексный compatibility gate и не полная матрица устройств.

******

### Лицензия

******

Исходный код распространяется по MPL-2.0. Chaquopy, CPython и другие компоненты сохраняют свои лицензии; атрибуция и доступ к upstream/project source описаны в `THIRD_PARTY_NOTICES.md`.

******

### Структура ресурсов

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` создает README и встроенные журналы на 10 языках из JSON с фиксированным порядком. Строки Android хранятся в каталогах ресурсов.

******

### Ссылки

******

- Документация AutoJs6: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
