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
- Вызов live-операций `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, учитывающего разрешения `notice`, ограниченного `files.read_text/write_text/exists/is_file/is_dir/list`, доступного только на переднем плане `dialogs.alert/confirm/prompt/select` и `engines.current/run/stop_self` через привязанный к выполнению pure-data broker протокола 1.5, который отзывается при завершении.
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

Принимаются отдельный SOURCE, необязательный ограниченный workspace archive, конечный заранее переданный stdin snapshot размером до 1 MiB и read-only snapshot возможностей хоста протокола 1.1. Протокол 1.2 добавляет явное согласование входа file/module для допущенных проектов. Протокол 1.3 добавляет после EOF snapshot принадлежащий Host prompt/reply только для встроенного `input()` на переднем плане, а стандартный `getpass.getpass()` использует скрытый ввод. Протокол 1.4 добавляет явный строгий JSON и необязательные output artifacts с манифестом SHA-256; stdout остается диагностикой и никогда не разбирается как результат. Протокол 1.5 добавляет pure-data Host broker, привязанный к одному выполнению, UID плагина, порядку вызовов и конечной квоте. Диалоги Host также требуют foreground-разрешения с активной Activity; фоновый запуск не открывает UI и возвращает `INTERACTIVE_NOT_ALLOWED`. Прямой `sys.stdin` остается конечным, фоновые запуски не открывают UI ввода, а скрипты не получают Context, raw Binder, объекты Host runtime или callback sink.

******

### Состояние интеграции с хостом

******

> Версия 0.1.0 предназначена только для AutoJs6 6.8.0; минимальный Host versionCode 5275 зафиксирован и принудительно проверяется. Финальная clean Host source revision и manifest дистрибутива из трех AAR записаны в lock. Каждый новый запуск заново обнаруживает provider; при отсутствии или отключении предлагается установка или включение без fallback, а после установки или включения Host перезапускать не нужно. Stable APK identity привязана к этой exact Plugin source и Host lock.

```text
release target: 0.3.0-alpha.6
release state: 0.3.0-alpha.6 current-tree candidate; M1 and M2, the implemented protocol 1.5 Host capability slices, and M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3/M4 batches, a complete device matrix, publication, and release evidence remain outside this claim
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
- Workspace проекта ограничен 64 MiB в сжатом виде, 8192 файлами и 128 MiB после извлечения; до dispatch выбор Provider должен удовлетворять всем трем фактическим измерениям snapshot.
- Полные PFD на стороне получателя Binder принимаются во владение и закрываются при завершении или close.
- Вывод передаётся по chunks и credits во время выполнения; при исчерпании credits скрипт приостанавливается, принятый вывод предшествует единственному terminal, а вывод после terminal запрещён.
- Структурированный JSON ограничен 64 KiB; допускается до 16 artifacts с путем до 1024 UTF-8 bytes, 4 MiB на файл, 8 MiB суммарно и проверкой Host точной длины, EOF и SHA-256.
- Протокол 1.5 допускает до 1024 Host-вызовов на выполнение, ограничивает request/response значением 64 KiB, текст — 32 KiB, а ожидание обычного действия главного потока Host — 5 s. Host files использует относительные пути до 4 KiB, UTF-8 текст до 32 KiB и списки до 128 имён размером до 255 UTF-8 bytes каждое. Foreground-диалоги ограничивают заголовок 256 UTF-8 bytes, содержимое 4 KiB, default/reply prompt 32 KiB, а select — 64 элементами по 1 KiB и 32 KiB суммарно; ответ пользователя ожидается до 5 min. Одно выполнение может успешно асинхронно запустить до 16 ограниченных корнем дочерних Host-скриптов не на Python; вложенный Python возвращает `NESTED_PYTHON_NOT_ALLOWED`, а `stop_self` отменяет выполнение перезапуском процесса.
- Отмена перезапускает процесс; native extensions и блокирующие вызовы требуют Android-проверки.
- Разрешение `INTERNET` позволяет скриптам напрямую использовать сетевые клиенты стандартной библиотеки; online pip, автоматическая загрузка кода и установка сторонних пакетов во время выполнения по-прежнему не поддерживаются.

******

### Необъявленные возможности

******

- Общий live stdin и callback streaming прямого `sys.stdin` недоступны. Интерактивность на переднем плане применяется только к встроенному `input()` и стандартному `getpass.getpass()` после EOF конечного snapshot до 1 MiB. Запись в workspace, online pip и загрузка wheels по-прежнему не поддерживаются.
- Нет UI-сценариев, debugger, REPL и произвольного доступа к Java-объектам хоста.
- Live broker охватывает полный первый низкорисковый набор, ограниченный Host files, foreground dialogs и ограниченный engines; accessibility, screenshot и OCR пока не заявлены.
- 32-разрядный Android и произвольные native wheels не гарантируются.
- Для текущего дерева есть smoke evidence на устройстве API 31 arm64-v8a и эмуляторе API 37 x86_64 со страницами 16 KB; это не выдается за полную матрицу устройств или release qualification.

******

### План

******

Путь A этапа M4 завершен: допущенные проекты могут включать pure-Python зависимости, а расширенный трехмерный профиль workspace и реальный HTTPS-сценарий requests прошли приемку на двух устройствах. Дальнейшие возможности автоматизации M3 и пути M4 для встроенных/native пакетов развиваются по пользовательской ценности; исторические инструменты доказательств остаются доступными, но не служат автоматическими воротами выпуска.

- [Открыть ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### История версий

******

# v0.3.0-alpha.6

###### 2026/08/23

* `Примечание` Первый alpha-кандидат M4 текущего дерева; локальные pure-Python зависимости проекта прошли целевую приемку на двух устройствах, а последующие этапы M3/M4, публикация и полная матрица устройств остаются вне этого заявления
* `Добавлено` Поддержка локальных pure-Python пакетов проекта и метаданных `.dist-info` из допущенного корня с воспроизводимым примером `requests` на фиксированных версиях и без установщика во время выполнения
* `Улучшено` Пределы workspace увеличены до 64 MiB в сжатом виде, 8192 файлов и 128 MiB после извлечения; перед dispatch три фактических измерения snapshot сопоставляются с возможностями Provider, а отсутствующий import остается `ModuleNotFoundError` без online pip или отката к другому движку

# v0.3.0-alpha.5

###### 2026/08/23

* `Примечание` Пятый M3 current-tree alpha candidate: ограниченная часть Host engines второго набора прошла фокусную приёмку на двух устройствах; последующие возможности, публикация и полная матрица устройств не входят в это заявление
* `Добавлено` Добавлены live API `autojs6.engines.current/run/stop_self` для метаданных текущего движка без путей, асинхронного запуска дочерних Host-скриптов не на Python и детерминированной самоостановки
* `Улучшено` Принимаются только нормализованные пути относительно корня выполнения и до 16 успешных запусков за выполнение; вложенный Python завершается с `NESTED_PYTHON_NOT_ALLOWED`, а `stop_self` отменяет выполнение перезапуском процесса provider

# v0.3.0-alpha.4

###### 2026/08/23

* `Примечание` Четвёртый M3 current-tree alpha candidate: foreground-диалоги Host прошли фокусную приёмку на двух устройствах; engines, последующие возможности, публикация и полная матрица устройств не входят в это заявление
* `Добавлено` Добавлены доступные только на переднем плане API `autojs6.dialogs.alert/confirm/prompt/select` с типизированными результатами подтверждения, boolean, nullable text и nullable индекса с нуля
* `Улучшено` Ограничены заголовки, содержимое, ответы и элементы, диалоги Host сериализуются по одному, а фоновые запуски отклоняются стабильным `INTERACTIVE_NOT_ALLOWED` без открытия UI

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
