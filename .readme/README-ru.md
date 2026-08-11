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

> Сейчас это прототип R2. Исходники среды и локальные семантические проверки bootstrap готовы, но конфигурация Gradle, компиляция Android, проверка APK, Binder и испытания на устройстве не выполнялись.

******

### Возможности

******

- Выполнение одного UTF-8 снимка Python как `__main__`.
- Сохранение порядка stdout и stderr с передачей ограниченных chunks по credits.
- Возврат `SystemExit`, синтаксических и runtime ошибок с ограниченным структурированным traceback.
- Один активный сеанс на процесс без очереди provider.
- Завершение отдельного процесса после отмены, timeout или callback death без повтора сценария.

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

Сборка запрашивает Python 3.13. 3.13.9 — ожидаемая версия пакета по текущим данным Chaquopy, но она не подтверждена до анализа APK и запуска на устройстве.

******

### Интерфейс плагина

******

Хост находит и вызывает плагин по следующим идентификаторам:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

Принимается только descriptor SOURCE. Лимиты workspace archive и stdin snapshot равны нулю; Context, Binder, объекты хоста и callback sink в сценарий не внедряются.

******

### Состояние интеграции с хостом

******

> Протокол и подключение хоста развиваются, но требуемые release AAR еще не опубликованы и не проверены. Установка этого scaffold сама по себе не создает рабочий Python engine.

******

### Безопасность и конфиденциальность

******

Исходный manifest не запрашивает разрешений Android. Exported service требует signature permission хоста и повторно проверяет UID, установленный пакет хоста и текущие подписи. Java bridge Chaquopy остается доступным, поэтому изоляция основана на отдельном Android UID, выделенном процессе и узкой границе Binder; CPython не считается безопасной sandbox.

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

- Нет workspace archive, stdin snapshot, online pip и загрузки wheels.
- Нет UI-сценариев, debugger, REPL и произвольного доступа к Java-объектам хоста.
- Пока нет AutoJs6 capability broker и подключения host API.
- 32-разрядный Android и произвольные native wheels не гарантируются.
- Локальные тесты CPython не являются доказательством Chaquopy, Android, Binder или устройства.

******

### План

******

Независимый репозиторий R2, статическая граница, исходники provider/bootstrap и локальные тесты готовы. Gradle и ADB отложены на время защищенного soak QV710AF65F. Release AAR, зависимости, компиляция Android, проверки APK/16 KB, Binder/PFD и матрица устройств не завершены.

- [Открыть ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### История версий

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

Переносимые семантические тесты bootstrap в локальном CPython:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Эти проверки не доказывают работу Android. Gradle, APK, Binder и устройство нужно проверить после защищенного soak.

******

### Сборка

******

Сборка сейчас не выполняется. Release-конфигурация fail closed, пока AAR или SHA-256 не зафиксированы.

Перед сборкой следующие release AAR нужно разместить и зафиксировать в `libs`:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

Планируется Chaquopy 17.0.0 из Maven только со stdlib. Метаданные зависимостей, native-библиотеки, лицензии и 16 KB page еще требуют проверки.

******

### Лицензия

******

Исходный код распространяется по MPL-2.0. Chaquopy, CPython и другие компоненты сохраняют свои лицензии.

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
