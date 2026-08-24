<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>بيئة تشغيل Python مستقلة. تنفذ النصوص في عملية إضافة مخصصة</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### اللغات

******

يتوفر README.md الحالي باللغات التالية:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- العربية [ar] # الحالية

******

### مقدمة

******

Python Runtime هو provider مستقل للإصدار V1 من بروتوكول Python. يرسل المضيف لقطة مصدر واحدة إلى عملية مخصصة تنفذها عبر CPython وتعيد خرجا محدودا واستثناءات منظمة وحالة نهائية واحدة.

> جمدت source identity للإصدار 0.1.0 وHost lock الدقيقة. تبقى أدلة RC المحلية للبناء وAPK وBinder وجهاز API 31 arm64-v8a واحد تاريخية؛ ترتبط stable APK/P3 provenance بهوية release الدقيقة ويعد production receipt مستوى أدلة مستقلا بعد النشر.

******

### الميزات

******

- تنفيذ لقطة مصدر Python بترميز UTF-8 كـ `__main__`.
- قبول stdin snapshot محدود ومقدم مسبقا بحجم أقصاه 1 MiB؛ وبعد وصوله إلى EOF يمكن لتشغيل صريح في foreground متابعة `input()` المضمنة عبر prompt/reply محدود في البروتوكول 1.3، بينما تستخدم `getpass.getpass()` إدخالا مخفيا.
- اختيار `entryMode=file|module` صراحة لمشروع مقبول؛ يستخدم وضع module بيانات `runpy` القياسية وجذر المشروع في `sys.path[0]` وعمليات الاستيراد النسبية للحزمة، بينما يحافظ وضع file على دلالات السكربت العادية.
- استيراد حزم pure-Python المحلية للمشروع وبيانات `.dist-info` من جذر المشروع المقبول دون pip عبر الإنترنت أو تثبيت وقت التشغيل.
- إرسال chunks محدودة من stdout/stderr بترتيبها الأصلي أثناء التنفيذ؛ يفرض نفاد credits ضغطا عكسيا على التنفيذ.
- تعيين نتيجة JSON صارمة وصريحة بحجم أقصاه 64 KiB ونقل ما يصل إلى 16 من output artifacts الاختيارية ضمن حدود المسار والحجم وSHA-256 في البروتوكول 1.4؛ ولا تستنتج النتيجة من stdout.
- استدعاء `toast` و`clip.get/set` و`app.launch/launch_app/open_url` و`device.info` و`console.log/warn/error` و`notice` المراعي للأذونات و`files.read_text/write_text/exists/is_file/is_dir/list` المحدود و`dialogs.alert/confirm/prompt/select` المقصور على foreground و`engines.current/run/stop_self` و`automator.click/long_click/press/swipe/back/home` المحدود و`selector.snapshot/find/click/set_text` المحدود و`images.capture_screen` و`images.find_color` و`images.find_image` و`ocr.recognize` مباشرة عبر broker بيانات خالصة مرتبط بالتنفيذ في البروتوكول 1.5 ويُلغى عند النهاية.
- يضيف البروتوكول 1.6 مشاريع صريحة `executionMode=long-running` دون deadline للتنفيذ، مع إشعار Host في foreground وإجراء Stop وheartbeats مرتبة من Provider كل 15 s؛ تفشل أسطح background بشكل مغلق دون downgrade.
- يقبل Host المقترن تشغيلات Python المتزامنة عبر FIFO عادلة قبل اكتشاف Provider: مالك active واحد وحتى 32 منتظرًا؛ يمكن مقاطعة queued Stop وتنتظر generation المرسلة حتى 3 s خروج Binder قبل التسليم، بينما يبقى Provider بجلسة واحدة ومن دون طابور.
- إرجاع `SystemExit` وأخطاء الصياغة والتنفيذ مع traceback منظم ومحدود.
- السماح بجلسة نشطة واحدة لكل عملية دون طابور لدى provider.
- لا حاجة لإعادة تشغيل المضيف: يعيد التنفيذ الجديد التالي بعد التثبيت أو إعادة التفعيل اكتشاف provider وتثبيت هويته، بينما ينهي Binder death أثناء التشغيل ذلك التنفيذ دون إعادة تلقائية.

******

### بيئة التشغيل وتنسيقات البيانات

******

يعلن البروتوكول V1 حاليا النطاق التالي:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

يطلب البناء Python 3.13. سجلت عناصر RC المحلية المجمدة والتنفيذ الدقيق على الجهاز CPython 3.13.9؛ يجب إعادة فحص الإصدار وhashes النهائية لـ 0.1.0 بعد تجميد المصدر.

******

### واجهة الإضافة

******

يكتشف المضيف الإضافة ويستدعيها بالمعرفات التالية:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.6
```

تقبل الإضافة SOURCE مستقلا وworkspace archive اختياريا محدودا وstdin snapshot محدودا ومقدما مسبقا بحجم أقصاه 1 MiB وsnapshot للقدرات المضيفة للقراءة فقط في البروتوكول 1.1. يضيف البروتوكول 1.2 تفاوضا صريحا على مدخل file/module للمشاريع المقبولة. يضيف البروتوكول 1.3 بعد EOF للـ snapshot تفاعل prompt/reply تملكه Host ومقصورا على `input()` المضمنة في foreground، بينما تستخدم `getpass.getpass()` إدخالا مخفيا. يضيف البروتوكول 1.4 JSON صارما وصريحا وoutput artifacts اختيارية موصوفة بـ SHA-256؛ يبقى stdout للتشخيص ولا يحلل كنتيجة. يضيف البروتوكول 1.5 broker Host ببيانات خالصة مرتبطا بتنفيذ واحد وUID الإضافة وترتيب الاستدعاءات وحصة محدودة. تتطلب حوارات Host أيضا تفويضا foreground مدعوما بـ Activity نشطة؛ يعيد تشغيل background الرمز `INTERACTIVE_NOT_ALLOWED` من دون فتح UI. يظل `sys.stdin` المباشر محدودا ولا تفتح عمليات background واجهة إدخال ولا تتلقى النصوص Context أو Binder خاما أو كائنات Host runtime أو callback sink.

******

### حالة تكامل المضيف

******

> يرتبط 0.1.0 فقط بـ AutoJs6 6.8.0، وقد جمد وفرض الحد الأدنى Host versionCode 5275. سجلت clean Host source revision النهائية وmanifest توزيع AAR الثلاثة في lock. يعيد كل تنفيذ جديد اكتشاف provider؛ عند فقده أو تعطيله يطلب التثبيت أو التفعيل دون fallback، ولا يحتاج Host إلى إعادة تشغيل بعد التثبيت أو التفعيل. ترتبط stable APK identity بهذه exact Plugin source وHost lock.

```text
release target: 0.5.0-alpha.4
release state: 0.5.0-alpha.4 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time pure-Python and M4 Path C native-package evaluations are complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; Path C built the official Pillow 11.0.0 and NumPy 1.26.2 dual-ABI closures offline, but transitive 4 KiB ELF LOAD segments failed the 16 KiB gate, and the official OpenCV index had no cp313 Android wheel; no candidate dependency payload was added; protocol 1.6 adds an explicit foreground-only long-running mode with a Host specialUse foreground notification, manual Stop, and 15-second Provider heartbeats under fail-closed leases; on QV710AF65F with Host versionCode 5276 and Plugin versionCode 81, notification Stop ended the script, the project rebound cleanly, and a subsequent run remained healthy through tick=70 (about 350 seconds), so the focused long-running Android smoke passes; the paired Host now admits concurrent Python launches through one fair FIFO owner plus 32 bounded waiters before Provider binding, supports interruptible queued Stop, and waits up to 3 seconds for dispatched process-generation retirement before handoff while the Plugin remains single-session with no provider queue; the first concurrency attempt on that device reached Provider BUSY/SESSION_OPEN because the installed Host did not yet contain FIFO integration; after installing the exact afca7b14c arm64 Host APK, the user confirmed the full documented FIFO order, fresh-PID generation handoff, queued Stop isolation, and later rerun checklist matched expectations with no issue, so the focused concurrency Android smoke passes; the no-runtime-change startup probe on QV710AF65F measured 441/447/429/427/428 ms with five distinct Plugin PIDs; the all-sample median is 429 ms, the median excluding the first run is 428.5 ms, and the maximum is 447 ms; every sample is below the 1000 ms threshold, so process retention is not justified and per-execution retirement remains; M6 consolidates the unpublished 0.2/0.3/0.4 implementation waypoints into one cumulative 0.5.0 release train and adds a read-only source profile plus a full local candidate gate with a ten-item manual Android smoke checklist; neither profile uses ADB, signing, network, tagging, pushing, or publication; M4 Path D, the exact signed-candidate smoke, beta/stable promotion, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### الأمان والخصوصية

******

بيئة Chaquopy مخصصة للنصوص المحلية الموثوقة وليست hostile-code sandbox. تتطلب exported service إذن توقيع المضيف وتتحقق من UID والحزمة وsigner؛ يقلل Android UID المستقل والعملية المخصصة وحد Binder الضيق تعرض المضيف لكنه لا يجعل Python sandbox. ‏SM003 هو signer طويل الأجل ويتولى SuperMonster003 ملكية runtime وsecurity وrelease.

******

### حدود التشغيل

******

- حد المصدر 4 MiB والخرج الكلي 16 MiB وكل chunk ‏16 KiB وعددها 16384.
- يقتصر timeout للطلبات المحدودة على 30 min. لا تملك مشاريع long-running الصريحة deadline، لكنها تتطلب عمر Host في foreground وlease بدء 2 min وlease heartbeat ‏45 s؛ وتبقى جلسة نشطة واحدة دون طابور provider.
- يحد workspace المشروع عند 64 MiB مضغوطا و8192 ملفا و128 MiB بعد الاستخراج؛ وقبل dispatch يجب أن يلبي اختيار Provider الأبعاد الفعلية الثلاثة للـ snapshot.
- تتملك العملية نسخ PFD الكاملة المستلمة عبر Binder وتغلقها عند النهاية أو close.
- يرسل الخرج chunk بعد chunk بالـ credits أثناء التنفيذ؛ يوقف نفاد credits السكربت مؤقتا، ويسبق الخرج المقبول الحالة terminal الوحيدة، ويمنع الخرج بعدها.
- يحد JSON المنظم عند 64 KiB وتقبل حتى 16 artifacts بمسار 1024 UTF-8 bytes و4 MiB لكل ملف و8 MiB إجمالا مع تحقق Host من الطول الدقيق وEOF وSHA-256.
- يسمح البروتوكول 1.5 بحد أقصى 1024 من استدعاءات Host لكل تنفيذ، ويحد كل request/response عند 64 KiB والنص عند 32 KiB وانتظار إجراء عادي على main thread عند 5 s. تستخدم Host files مسارات نسبية بحد 4 KiB ونص UTF-8 بحد 32 KiB وقوائم من 128 اسماً بحد 255 UTF-8 bytes لكل اسم. تحد حوارات foreground العنوان عند 256 UTF-8 bytes والمحتوى عند 4 KiB وdefault/reply لـ prompt عند 32 KiB وselect عند 64 عناصر، كل منها 1 KiB وبمجموع 32 KiB؛ ويمكن انتظار رد المستخدم حتى 5 min. يمكن لكل تنفيذ تشغيل ما يصل إلى 16 من نصوص Host الفرعية غير المكتوبة بلغة Python بشكل غير متزامن وضمن النطاق؛ تعيد Python المتداخلة `NESTED_PYTHON_NOT_ALLOWED` ويلغي `stop_self` التنفيذ بإعادة تشغيل العملية.
- لا تقبل إحداثيات automator إلا أعدادا صحيحة من 0 إلى 1000000، وتتراوح مدة press وswipe من 1 ms إلى 4 s؛ يؤدي عدم توفر Host accessibility إلى `CapabilityUnavailableError` دون فتح الإعدادات.
- يقبل snapshot الخاص بـ selector حتى 128 عقدة وعمقا 32 و48 KiB من JSON؛ ويفحص find حتى 1024 عقدة، ويحد نص العقدة عند 256 Unicode code points ونص الاستعلام عند 1024 UTF-8 bytes وset_text عند 4 KiB، ويحتفظ كل تنفيذ بما يصل إلى 128 مرجعا للعقد. يعيد الفحص غير المكتمل `SELECTOR_SCAN_LIMIT_EXCEEDED` والمرجع القديم `STALE_NODE`.
- تحتفظ screen capture بما يصل إلى 1 صورة لكل تنفيذ، وتحد البيانات المشفرة عند 4 MiB والكتلة الخام عند 32 KiB وكل بُعد عند 8192 بكسل والمساحة الكلية عند 16777216 بكسل. يتحقق Python من الطول والترتيب وEOF وSHA-256 وتوقيع التنسيق قبل الإرجاع؛ يؤدي عدم توفر accessibility/API إلى `CapabilityUnavailableError`، وتشمل الأخطاء الثابتة `SCREEN_CAPTURE_FAILED` و`RESULT_LIMIT_EXCEEDED` و`STALE_IMAGE`. يبحث color search في لقطة جديدة بترتيب الصفوف مع منطقة محدودة اختيارية وحد لكل قناة حتى 255، ولا يعيد إلا إحداثيا أو عدم تطابق من دون نقل بايتات الصورة. يحتفظ template search بما يصل إلى 1 قالب PNG/JPEG، ويحده عند 1 MiB وينقل raw chunks بحجم 24 KiB، مع حد البعد 2048 والمساحة 1048576 ومنطقة البحث 4194304 والمقارنات 16777216؛ تشارك pixels المعتمة بالكامل فقط والبقية wildcards، ويكون المسح deterministic row-major، وتُحرر buffers وتُصفّر عند النهاية.
- يعيد `ocr.recognize` استخدام غلاف PNG/JPEG بحجم 1 MiB وraw chunks بحجم 24 KiB وحد 2048 pixels لكل ضلع و1048576 pixels بعد decode. يعيد Host OCR engine المضبوط بحد أقصى 256 سطرا و4 KiB من strict UTF-8 لكل سطر و48 KiB إجمالا ضمن admission/call budget الحالي 60 s؛ يبلغ عدم التوفر والفشل بـ `OCR_UNAVAILABLE` و`OCR_FAILED`، ويُحرر upload ويُصفّر دائما.
- يعيد الإلغاء تشغيل العملية؛ تتطلب native extensions والاستدعاءات الحاجبة تحقق Android لاحقا.
- يسمح إذن `INTERNET` للنصوص باستخدام عملاء الشبكة في المكتبة القياسية مباشرة؛ ولا يزال pip عبر الإنترنت والتنزيل التلقائي للكود وتثبيت حزم الجهات الخارجية وقت التشغيل غير مدعوم.

******

### قدرات غير معلنة

******

- لا يتوفر live stdin عام ولا callback streaming مباشر لـ `sys.stdin`. يقتصر تفاعل foreground على `input()` المضمنة و`getpass.getpass()` بعد EOF للـ snapshot المحدود حتى 1 MiB. تظل الكتابة إلى workspace وpip عبر الإنترنت وتنزيل wheels غير مدعومة.
- لا توجد نصوص UI أو debugger أو REPL أو صلاحية عشوائية لكائنات Java في المضيف.
- يغطي broker المباشر أول مجموعة كاملة منخفضة المخاطر وHost files المحدودة وحوارات foreground وengines المحدودة وإجراءات automator الصريحة بالإحداثيات/global وsnapshot/actions المحدودة لـ selector/UI tree وscreen capture و`find_color` و`find_image` وOCR سطرية؛ ولا تزال OCR boxes/confidence/options ومعالجة الصور القابلة للتغيير والمطابقة multi-scale غير معلنة.
- لا يضمن Android ‏32-bit أو أي native wheel خارجي.
- تتوفر للشجرة الحالية أدلة smoke على جهاز API 31 ‏arm64-v8a وعلى محاكي API 37 ‏x86_64 بصفحات 16 KB؛ ولا يقدم أي منهما كمصفوفة أجهزة كاملة أو كتأهيل release.

******

### خارطة الطريق

******

اكتمل M4 Path A؛ وانتهى تقييما M4 Paths B وC بقرار `NOT_ADMITTED`، لذلك يبقى runtime المضمّن `stdlib-only`. نجح Path C في بناء Pillow وNumPy دون اتصال، لكن إغلاقاتهما native الكاملة فشلت في بوابة ELF ثنائية ABI بحجم 16 KiB، ولا يملك OpenCV wheel Android من نوع `cp313`؛ ويبقى Path D حسب الطلب. تشمل automation في M3 الإجراءات المحدودة وselector/UI tree وscreen capture والبحث اللوني وقوالب PNG/JPEG وHost OCR. لا تُعد أدوات الأدلة التاريخية بوابات إصدار تلقائية.

- [عرض ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### سجل الإصدارات

******

# v0.5.0-alpha.4

###### 2026/08/25

* `ملاحظة` مرشح alpha رابع من current-tree؛ يجمع M6 محطات 0.2/0.3/0.4 غير المنشورة في مسار تراكمي واحد 0.5.0 دون ادعاء beta أو إصدار مستقر أو signing أو publication
* `إضافة` إضافة `tools/verify-m6-candidate.py` بملفي تعريف صريحين `--source-only` و`--full` لفحص clean Git والإصدار وChangelog والمستندات المولدة وAAR lock، ثم الاختبارات المحمولة وبوابة R2 الثابتة وoffline debug build
* `تحسين` تثبيت Android smoke checklist من 10 عناصر وتسلسل الترقية alpha → beta → 0.5.0؛ لا تنفذ البوابة المحلية أي ADB أو signing أو tag أو push أو publication

# v0.5.0-alpha.3

###### 2026/08/24

* `ملاحظة` مرشح alpha ثالث لـ M5 current-tree؛ تنجح اختبارات Android المركزة لوضع long-running وFIFO في Host على QV710AF65F، ويستبعد قياس بدء التشغيل الاحتفاظ بالعملية من النطاق دون ادعاء النشر أو release
* `تحسين` قياس خمس عمليات fresh-process عند 441/447/429/427/428 ms مع خمسة معرّفات PID مختلفة لـ Plugin؛ وسيط جميع العينات 429 ms، والوسيط دون التشغيل الأول 428.5 ms، والحد الأقصى 447 ms
* `تحسين` إغلاق تقييم prewarm دون عتبة 1000 ms: الاحتفاظ بتقاعد العملية per-execution ودلالات العزل/الإلغاء بدلاً من إضافة خيار keep-process

# v0.5.0-alpha.2

###### 2026/08/24

* `ملاحظة` مرشح alpha ثانٍ من M5 current-tree؛ تنجح FIFO في Host وبوابات JVM/portable دون اتصال، من دون ادعاء Android concurrency smoke أو CPython متوازٍ فعلي أو prewarm أو نشر أو release
* `إضافة` قبول تشغيلات Python المتزامنة عبر FIFO عادلة في Host بمالك active واحد وحتى 32 منتظرًا قبل اكتشاف Provider؛ يمكن مقاطعة queued Stop من دون ربط Plugin أو استهلاك request timeout أو إنشاء إشعار long-task مبكرًا
* `تحسين` الاحتفاظ بـ Provider binding حتى 3 ثوانٍ بعد إغلاق dispatched session لتأكيد retirement للجيل قبل FIFO handoff؛ يبقى البروتوكول 1.6 وملفات AAR الثلاثة وحد Plugin single-session/no-provider-queue دون تغيير

##### المزيد من الإصدارات

* [CHANGELOG-ar.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-ar.md)

******

### التحقق

******

فحص ثابت للملفات دون Gradle أو ADB:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

اختبارات دلالة bootstrap المحمولة باستخدام CPython المحلي:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

لا تستبدل الفحوص الثابتة وCPython المحلي أدلة Android. نتائج RC والجهاز الواحد الحالية تاريخية؛ يستخدم release acceptance فحوص البناء وAPK وBinder والجهاز التمثيلي المرتبطة بالهوية الدقيقة.

******

### البناء

******

لا يشغل توليد الوثائق البناء بذاته. تفشل إعدادات release بشكل مغلق عند تغير AAR أو SHA-256 أو signer أو runtime lock؛ لا تقبل stable artifacts إلا عند ربطها بهوية release الدقيقة.

يجب وضع ملفات release AAR التالية وتثبيتها في `libs` قبل البناء:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

تقفل البيئة Chaquopy 17.0.0 وCPython 3.13.9 من Maven وتحزم stdlib فقط. يفحص release gate ‏metadata والمكتبات الأصلية وNOTICE وsigner ‏SM003 وملفات APK الثلاثة مقابل الهوية الدقيقة. نجح smoke مركز للشجرة الحالية على محاكي API 37 ‏x86_64 بصفحات 16 KB؛ ولا يعادل ذلك compatibility gate شاملا أو مصفوفة أجهزة كاملة.

******

### الترخيص

******

يستخدم مصدر المشروع MPL-2.0 وتبقى Chaquopy وCPython والمكونات الأخرى تحت تراخيصها؛ توثق `THIRD_PARTY_NOTICES.md` النسب والوصول إلى upstream/project source.

******

### بنية الموارد

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

ينشئ `.python/generate_markdown.py` ملفات README وسجلات مدمجة بعشر لغات من JSON ثابت الترتيب. تدار سلاسل Android في مجلدات الموارد الخاصة بها.

******

### الروابط

******

- توثيق AutoJs6: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
