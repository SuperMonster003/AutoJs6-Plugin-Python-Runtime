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
- Для `input()` принимается конечный заранее переданный stdin snapshot размером до 1 MiB; интерактивного prompt/reply в реальном времени нет.
- Сохранение порядка stdout и stderr с передачей ограниченных chunks по credits.
- Возврат `SystemExit`, синтаксических и runtime ошибок с ограниченным структурированным traceback.
- Один активный сеанс на процесс без очереди provider.
- Перезапуск хоста не нужен: следующая новая сессия после установки или повторного включения заново обнаруживает и фиксирует provider, а Binder death во время выполнения завершает его без автоматического повтора.

******

### Среда и форматы данных

******

Протокол V1 сейчас объявляет следующий диапазон:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
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
protocol: 1.0-1.1
```

Принимаются отдельный SOURCE, необязательный ограниченный workspace archive, конечный заранее переданный stdin snapshot размером до 1 MiB и read-only snapshot возможностей хоста протокола 1.1. Stdin не является интерактивным каналом реального времени; Context, Binder, объекты хоста и callback sink не внедряются.

******

### Состояние интеграции с хостом

******

> Версия 0.1.0 предназначена только для AutoJs6 6.8.0; минимальный Host versionCode 5275 зафиксирован и принудительно проверяется. Финальная clean Host source revision и manifest дистрибутива из трех AAR записаны в lock. Каждый новый запуск заново обнаруживает provider; при отсутствии или отключении предлагается установка или включение без fallback, а после установки или включения Host перезапускать не нужно. Stable APK identity привязана к этой exact Plugin source и Host lock.

```text
release target: 0.2.0-alpha.1
release state: post-0.1 U1 alpha source candidate; not published, E3 device acceptance pending, and prior 0.1.0 artifacts do not cover the current source
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- Источник ограничен 4 MiB, весь вывод 4 MiB, chunk 16 KiB, число chunks 4096.
- Максимальный timeout 60 s, один активный сеанс и без очереди provider.
- Полные PFD на стороне получателя Binder принимаются во владение и закрываются при завершении или close.
- Вывод сначала ограниченно буферизуется, затем передается по credits; backpressure во время выполнения не заявлен.
- Отмена перезапускает процесс; native extensions и блокирующие вызовы требуют Android-проверки.
- Политика stdlib-only запрещает online pip и сторонние пакеты. Разрешения объединенного APK еще нужно проверить.

******

### Необъявленные возможности

******

- Нет интерактивного stdin в реальном времени; поддерживается только конечный заранее переданный snapshot до 1 MiB. Запись в workspace, online pip и загрузка wheels по-прежнему не поддерживаются.
- Нет UI-сценариев, debugger, REPL и произвольного доступа к Java-объектам хоста.
- Нет realtime AutoJs6 capability broker; первые API используют только замороженный при запуске snapshot app/device/execution/project и ограниченное read-only чтение private workspace плагина.
- 32-разрядный Android и произвольные native wheels не гарантируются.
- Для arm64-v8a есть свидетельство устройства API 31; для x86_64 пока только packaging, не запуск на устройстве и не полная матрица.

******

### План

******

Локальные RC- и концентрированные device-свидетельства R6-P2/P3 сохраняются как история. Этот clean VERSION_BUILD=11 freeze commit фиксирует stable Plugin source identity и exact Host 6.8.0/5275 lock; provenance стабильных APK оценивается относительно этих exact identities, и любой production receipt должен использовать ту же основу. Полная API×ABI matrix и новый soak не являются автоматическими gates.

- [Открыть ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### История версий

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Примечание` Alpha исходников U1 после 0.1; интерактивный stdin в реальном времени недоступен, приемка E3 на устройстве еще не выполнена
* `Добавлено` Добавлен конечный заранее предоставленный snapshot stdin до 1 MiB для детерминированного ввода и EOF через `input()` и `sys.stdin`
* `Добавлено` Завершена семантика project import для модулей workspace, соседних и корневых модулей вложенной точки входа и package-relative imports
* `Исправлено` Исходник декодируется как strict UTF-8 до выполнения, поэтому encoding cookie с иной кодировкой больше не обходит контракт
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

# v0.1.0-alpha.1

###### 2026/08/09

* `Примечание` Исходники прототипа R2; Gradle, APK, Binder и устройство не проверены
* `Добавлено` Независимый scaffold provider Python V1 с отдельным процессом, одним сеансом и без очереди
* `Добавлено` Выполнение одной исходной программы как `__main__`, ограниченный stdout/stderr, структурированные исключения и отмена перезапуском
* `Добавлено` Упорядоченная генерация README и встроенных журналов на 10 языках
* `Зависимость` Предварительно выбраны Chaquopy 17.0.0 и Python 3.13; версии и hashes требуют проверки сборкой

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

Runtime фиксирует Chaquopy 17.0.0 и CPython 3.13.9 из Maven и включает только stdlib. Release gate проверяет metadata, native libraries, NOTICE, signer SM003 и три распространяемых APK относительно exact identity; для совместимости с 16 KB page сейчас нет отдельного gate, поэтому она не заявляется как проверенная.

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
