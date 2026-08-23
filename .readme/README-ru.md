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
- Передача ограниченных chunks stdout/stderr в исходном порядке во время выполнения; исчерпание credits создаёт backpressure для выполнения.
- Явное задание строгого JSON-результата до 64 KiB и передача до 16 необязательных output artifacts с ограничениями пути, размера и SHA-256 протокола 1.4; результат никогда не выводится из stdout.
- Вызов live-операций `toast`, `clip.get/set` и `app.launch/launch_app/open_url` через привязанный к выполнению pure-data broker протокола 1.5, который отзывается при завершении.
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
protocol: 1.0-1.5
```

Принимаются отдельный SOURCE, необязательный ограниченный workspace archive, конечный заранее переданный stdin snapshot размером до 1 MiB и read-only snapshot возможностей хоста протокола 1.1. Протокол 1.2 добавляет явное согласование входа file/module для допущенных проектов. Протокол 1.3 добавляет после EOF snapshot принадлежащий Host prompt/reply только для встроенного `input()` на переднем плане, а стандартный `getpass.getpass()` использует скрытый ввод. Протокол 1.4 добавляет явный строгий JSON и необязательные output artifacts с манифестом SHA-256; stdout остается диагностикой и никогда не разбирается как результат. Протокол 1.5 добавляет pure-data Host broker, привязанный к одному выполнению, UID плагина, порядку вызовов и конечной квоте. Прямой `sys.stdin` остается конечным, фоновые запуски не открывают UI ввода, а скрипты не получают Context, raw Binder, объекты Host runtime или callback sink.

******

### Состояние интеграции с хостом

******

> Версия 0.1.0 предназначена только для AutoJs6 6.8.0; минимальный Host versionCode 5275 зафиксирован и принудительно проверяется. Финальная clean Host source revision и manifest дистрибутива из трех AAR записаны в lock. Каждый новый запуск заново обнаруживает provider; при отсутствии или отключении предлагается установка или включение без fallback, а после установки или включения Host перезапускать не нужно. Stable APK identity привязана к этой exact Plugin source и Host lock.

```text
release target: 0.3.0-alpha.1
release state: 0.3.0 current-tree candidate; M1 and M2 are complete, and protocol 1.5 plus the first toast/clipboard/app Host capability slice passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3 capabilities, a complete device matrix, publication, and release evidence remain outside this claim
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
- Максимальный timeout 30 min, один активный сеанс и без очереди provider.
- Полные PFD на стороне получателя Binder принимаются во владение и закрываются при завершении или close.
- Вывод передаётся по chunks и credits во время выполнения; при исчерпании credits скрипт приостанавливается, принятый вывод предшествует единственному terminal, а вывод после terminal запрещён.
- Структурированный JSON ограничен 64 KiB; допускается до 16 artifacts с путем до 1024 UTF-8 bytes, 4 MiB на файл, 8 MiB суммарно и проверкой Host точной длины, EOF и SHA-256.
- Протокол 1.5 допускает до 1024 Host-вызовов на выполнение, ограничивает request/response значением 64 KiB, текст — 32 KiB, а ожидание dispatch — 5 s.
- Отмена перезапускает процесс; native extensions и блокирующие вызовы требуют Android-проверки.
- Разрешение `INTERNET` позволяет скриптам напрямую использовать сетевые клиенты стандартной библиотеки; online pip, автоматическая загрузка кода и установка сторонних пакетов во время выполнения по-прежнему не поддерживаются.

******

### Необъявленные возможности

******

- Общий live stdin и callback streaming прямого `sys.stdin` недоступны. Интерактивность на переднем плане применяется только к встроенному `input()` и стандартному `getpass.getpass()` после EOF конечного snapshot до 1 MiB. Запись в workspace, online pip и загрузка wheels по-прежнему не поддерживаются.
- Нет UI-сценариев, debugger, REPL и произвольного доступа к Java-объектам хоста.
- Live broker сейчас охватывает только toast, clipboard и запуск приложений/HTTP(S) URL; dynamic device, Host console, notifications, files, dialogs, accessibility, screenshot и OCR пока не заявлены.
- 32-разрядный Android и произвольные native wheels не гарантируются.
- Для текущего дерева есть smoke evidence на устройстве API 31 arm64-v8a и эмуляторе API 37 x86_64 со страницами 16 KB; это не выдается за полную матрицу устройств или release qualification.

******

### План

******

Локальные RC- и концентрированные device-свидетельства R6-P2/P3 сохраняются как история. Этот clean VERSION_BUILD=11 freeze commit фиксирует stable Plugin source identity и exact Host 6.8.0/5275 lock; provenance стабильных APK оценивается относительно этих exact identities, и любой production receipt должен использовать ту же основу. Полная API×ABI matrix и новый soak не являются автоматическими gates.

- [Открыть ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### История версий

******

# v0.3.0-alpha.1

###### 2026/08/23

* `Примечание` Первый M3 current-tree alpha candidate: протокол 1.5 и низкорисковый набор Host capabilities реализованы; последующие возможности, публикация и полная матрица устройств не входят в это заявление
* `Добавлено` Добавлен execution-scoped Host capability broker протокола 1.5 с pure-data JSON, привязкой к request UUID и UID плагина, монотонными call ID, квотой 1024 вызова, сообщениями 64 KiB и лимитом Host dispatch 5 секунд
* `Добавлено` Добавлены live Host API `autojs6.toast`, `autojs6.clip.get/set` и `autojs6.app.launch/launch_app/open_url`
* `Улучшено` Broker единообразно отзывается при terminal, cancel, Binder death и cleanup; ошибки unavailable capabilities и Host/protocol стабильно отображаются в Python

# v0.2.0-alpha.1

###### 2026/08/13

* `Примечание` Alpha-кандидат U1 текущего дерева после 0.1; module entry, live output, встроенный input на переднем плане, явный structured JSON и ограниченные output artifacts U1-R2 покрыты только до E2; фоновые запуски и прямой sys.stdin остаются неинтерактивными, R2 E3 остается открытым, а результаты текущего дерева не доказывают матрицу устройств, выпуск или публикацию
* `Добавлено` Добавлен конечный заранее предоставленный snapshot stdin до 1 MiB для детерминированного ввода и EOF через `input()` и `sys.stdin`
* `Добавлено` Завершена семантика project import для модулей workspace, соседних и корневых модулей вложенной точки входа и package-relative imports
* `Добавлено` Добавлен протокол 1.2 с явным `entryMode=file|module`; выполнение module использует `runpy` с корректными `__package__`, `__spec__`, корнем проекта в `sys.path[0]` и относительными импортами, а режим file не изменён
* `Добавлено` В протокол 1.3 добавлен ограниченный prompt/reply только на переднем плане после EOF конечного snapshot: видимый ввод для встроенного `input()` и скрытый для `getpass.getpass()`; фоновые запуски не открывают UI ввода, а прямой `sys.stdin` остается конечным
* `Добавлено` В протокол 1.4 добавлены явные строгие JSON-результаты и необязательные output artifacts с ограничениями количества, нормализованного пути, размера файла/суммы, точных PFD-ссылок и SHA-256 без вывода результата из stdout
* `Исправлено` Исходник декодируется как strict UTF-8 до выполнения, поэтому encoding cookie с иной кодировкой больше не обходит контракт
* `Улучшено` Предоставить `INTERNET`, чтобы доверенные скрипты напрямую использовали сетевые клиенты стандартной библиотеки, оставив online pip и автоматическую загрузку кода отключёнными
* `Улучшено` Увеличить предел выполнения Provider до 30 минут, а ограниченный вывод — до 16 MiB / 16384 chunks
* `Улучшено` Перенос ограниченных chunks stdout/stderr и backpressure по credits внутрь выполнения скрипта с сохранением упорядоченного частичного вывода до terminal и запретом после него
* `Улучшено` Каждый запуск получает отдельный `__main__` с восстановлением stdin/stdout/stderr, argv, cwd, `sys.path`, состояния modules и importer cache
* `Улучшено` Для открытого, но не запущенного session действует lease 5 секунд, после чего освобождаются inputs, descriptors и единственный session slot
* `Улучшено` Минимальный Host versionCode 5275 проверяется на Binder-границе Provider, а не только при discovery со стороны Host

# v0.1.0

###### 2026/08/12

* `Примечание` Версия 0.1.0 фиксирует stable Plugin source identity и exact Host 6.8.0/5275 lock
* `Добавлено` Протокол Python 1.0-1.1 для AutoJs6 6.8.0 / versionCode 5275, ограниченный project workspace и read-only snapshots app/device/execution/project
* `Добавлено` Hot-plug без перезапуска хоста: install или повторное включение позволяет следующему запуску заново найти и pin ID, без fallback при отсутствии или отключении
* `Добавлено` Binder death во время работы завершает текущий запуск без replay; новые запуски заново обнаруживают provider
* `Улучшено` Chaquopy закреплен как trusted-local, non-sandbox runtime; долгосрочный signer — SM003, owner runtime/security/release — SuperMonster003
* `Зависимость` Зафиксированы Chaquopy 17.0.0 и CPython 3.13.9; стабильные APK привязаны к финальной идентичности исходников и проверены как точные artifacts

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
