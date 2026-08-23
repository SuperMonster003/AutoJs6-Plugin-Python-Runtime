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
- استدعاء `toast` و`clip.get/set` و`app.launch/launch_app/open_url` و`device.info` و`console.log/warn/error` و`notice` المراعي للأذونات و`files.read_text/write_text/exists/is_file/is_dir/list` المحدود و`dialogs.alert/confirm/prompt/select` المقصور على foreground و`engines.current/run/stop_self` و`automator.click/long_click/press/swipe/back/home` المحدود و`selector.snapshot/find/click/set_text` المحدود و`images.capture_screen` و`images.find_color` مباشرة عبر broker بيانات خالصة مرتبط بالتنفيذ في البروتوكول 1.5 ويُلغى عند النهاية.
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
protocol: 1.0-1.5
```

تقبل الإضافة SOURCE مستقلا وworkspace archive اختياريا محدودا وstdin snapshot محدودا ومقدما مسبقا بحجم أقصاه 1 MiB وsnapshot للقدرات المضيفة للقراءة فقط في البروتوكول 1.1. يضيف البروتوكول 1.2 تفاوضا صريحا على مدخل file/module للمشاريع المقبولة. يضيف البروتوكول 1.3 بعد EOF للـ snapshot تفاعل prompt/reply تملكه Host ومقصورا على `input()` المضمنة في foreground، بينما تستخدم `getpass.getpass()` إدخالا مخفيا. يضيف البروتوكول 1.4 JSON صارما وصريحا وoutput artifacts اختيارية موصوفة بـ SHA-256؛ يبقى stdout للتشخيص ولا يحلل كنتيجة. يضيف البروتوكول 1.5 broker Host ببيانات خالصة مرتبطا بتنفيذ واحد وUID الإضافة وترتيب الاستدعاءات وحصة محدودة. تتطلب حوارات Host أيضا تفويضا foreground مدعوما بـ Activity نشطة؛ يعيد تشغيل background الرمز `INTERACTIVE_NOT_ALLOWED` من دون فتح UI. يظل `sys.stdin` المباشر محدودا ولا تفتح عمليات background واجهة إدخال ولا تتلقى النصوص Context أو Binder خاما أو كائنات Host runtime أو callback sink.

******

### حالة تكامل المضيف

******

> يرتبط 0.1.0 فقط بـ AutoJs6 6.8.0، وقد جمد وفرض الحد الأدنى Host versionCode 5275. سجلت clean Host source revision النهائية وmanifest توزيع AAR الثلاثة في lock. يعيد كل تنفيذ جديد اكتشاف provider؛ عند فقده أو تعطيله يطلب التثبيت أو التفعيل دون fallback، ولا يحتاج Host إلى إعادة تشغيل بعد التثبيت أو التفعيل. ترتبط stable APK identity بهذه exact Plugin source وHost lock.

```text
release target: 0.4.0-alpha.4
release state: 0.4.0-alpha.4 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, and one-shot RGB find_color passed their enabled-service paths on the emulator and fail-closed on the physical device without changing its accessibility services; template image matching, OCR, later M3/M4 batches, a complete device matrix, publication, and release evidence remain outside this claim
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
- أقصى timeout هو 30 min مع جلسة واحدة ودون طابور provider.
- يحد workspace المشروع عند 64 MiB مضغوطا و8192 ملفا و128 MiB بعد الاستخراج؛ وقبل dispatch يجب أن يلبي اختيار Provider الأبعاد الفعلية الثلاثة للـ snapshot.
- تتملك العملية نسخ PFD الكاملة المستلمة عبر Binder وتغلقها عند النهاية أو close.
- يرسل الخرج chunk بعد chunk بالـ credits أثناء التنفيذ؛ يوقف نفاد credits السكربت مؤقتا، ويسبق الخرج المقبول الحالة terminal الوحيدة، ويمنع الخرج بعدها.
- يحد JSON المنظم عند 64 KiB وتقبل حتى 16 artifacts بمسار 1024 UTF-8 bytes و4 MiB لكل ملف و8 MiB إجمالا مع تحقق Host من الطول الدقيق وEOF وSHA-256.
- يسمح البروتوكول 1.5 بحد أقصى 1024 من استدعاءات Host لكل تنفيذ، ويحد كل request/response عند 64 KiB والنص عند 32 KiB وانتظار إجراء عادي على main thread عند 5 s. تستخدم Host files مسارات نسبية بحد 4 KiB ونص UTF-8 بحد 32 KiB وقوائم من 128 اسماً بحد 255 UTF-8 bytes لكل اسم. تحد حوارات foreground العنوان عند 256 UTF-8 bytes والمحتوى عند 4 KiB وdefault/reply لـ prompt عند 32 KiB وselect عند 64 عناصر، كل منها 1 KiB وبمجموع 32 KiB؛ ويمكن انتظار رد المستخدم حتى 5 min. يمكن لكل تنفيذ تشغيل ما يصل إلى 16 من نصوص Host الفرعية غير المكتوبة بلغة Python بشكل غير متزامن وضمن النطاق؛ تعيد Python المتداخلة `NESTED_PYTHON_NOT_ALLOWED` ويلغي `stop_self` التنفيذ بإعادة تشغيل العملية.
- لا تقبل إحداثيات automator إلا أعدادا صحيحة من 0 إلى 1000000، وتتراوح مدة press وswipe من 1 ms إلى 4 s؛ يؤدي عدم توفر Host accessibility إلى `CapabilityUnavailableError` دون فتح الإعدادات.
- يقبل snapshot الخاص بـ selector حتى 128 عقدة وعمقا 32 و48 KiB من JSON؛ ويفحص find حتى 1024 عقدة، ويحد نص العقدة عند 256 Unicode code points ونص الاستعلام عند 1024 UTF-8 bytes وset_text عند 4 KiB، ويحتفظ كل تنفيذ بما يصل إلى 128 مرجعا للعقد. يعيد الفحص غير المكتمل `SELECTOR_SCAN_LIMIT_EXCEEDED` والمرجع القديم `STALE_NODE`.
- تحتفظ screen capture بما يصل إلى 1 صورة لكل تنفيذ، وتحد البيانات المشفرة عند 4 MiB والكتلة الخام عند 32 KiB وكل بُعد عند 8192 بكسل والمساحة الكلية عند 16777216 بكسل. يتحقق Python من الطول والترتيب وEOF وSHA-256 وتوقيع التنسيق قبل الإرجاع؛ يؤدي عدم توفر accessibility/API إلى `CapabilityUnavailableError`، وتشمل الأخطاء الثابتة `SCREEN_CAPTURE_FAILED` و`RESULT_LIMIT_EXCEEDED` و`STALE_IMAGE`. يبحث color search في لقطة جديدة بترتيب الصفوف مع منطقة محدودة اختيارية وحد لكل قناة حتى 255، ولا يعيد إلا إحداثيا أو عدم تطابق من دون نقل بايتات الصورة.
- يعيد الإلغاء تشغيل العملية؛ تتطلب native extensions والاستدعاءات الحاجبة تحقق Android لاحقا.
- يسمح إذن `INTERNET` للنصوص باستخدام عملاء الشبكة في المكتبة القياسية مباشرة؛ ولا يزال pip عبر الإنترنت والتنزيل التلقائي للكود وتثبيت حزم الجهات الخارجية وقت التشغيل غير مدعوم.

******

### قدرات غير معلنة

******

- لا يتوفر live stdin عام ولا callback streaming مباشر لـ `sys.stdin`. يقتصر تفاعل foreground على `input()` المضمنة و`getpass.getpass()` بعد EOF للـ snapshot المحدود حتى 1 MiB. تظل الكتابة إلى workspace وpip عبر الإنترنت وتنزيل wheels غير مدعومة.
- لا توجد نصوص UI أو debugger أو REPL أو صلاحية عشوائية لكائنات Java في المضيف.
- يغطي broker المباشر أول مجموعة كاملة منخفضة المخاطر وHost files المحدودة وحوارات foreground وengines المحدودة وإجراءات automator الصريحة بالإحداثيات/global وsnapshot/actions المحدودة لـ selector/UI tree وscreen capture و`find_color` المحدودين؛ ولا تزال `find_image` ورفع القالب وOCR غير معلنة.
- لا يضمن Android ‏32-bit أو أي native wheel خارجي.
- تتوفر للشجرة الحالية أدلة smoke على جهاز API 31 ‏arm64-v8a وعلى محاكي API 37 ‏x86_64 بصفحات 16 KB؛ ولا يقدم أي منهما كمصفوفة أجهزة كاملة أو كتأهيل release.

******

### خارطة الطريق

******

اكتمل المسار A من M4، وتشمل automation في M3 الآن إجراءات إحداثيات/global محدودة وطبقة بيانات selector/UI tree وscreen capture وبحث RGB لمرة واحدة عبر Host accessibility. يستمر البحث بالقالب وOCR ومسارات الحزم build-time/native في M4 حسب قيمة المستخدم؛ تبقى أدوات الأدلة التاريخية متاحة لكنها ليست بوابات إصدار تلقائية.

- [عرض ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### سجل الإصدارات

******

# v0.4.0-alpha.4

###### 2026/08/24

* `ملاحظة` مرشح alpha رابع لأتمتة M3 في الشجرة الحالية؛ نجح بحث اللون المحدود على محاكي API 37 مع accessibility وفشل بشكل مغلق على جهاز API 31 من دون تغيير خدماته؛ يظل بحث القالب وOCR والنشر ومصفوفة الأجهزة الكاملة خارج هذا الادعاء
* `إضافة` إضافة `autojs6.images.find_color(color, *, region=None, threshold=0)` لعدد RGB صحيح صارم أو نص `#RRGGBB` ومنطقة محدودة اختيارية ونتيجة إحداثي أو `None`
* `تحسين` التقاط شاشة accessibility جديدة واحدة على Android 11+ لكل استدعاء ومسحها بترتيب row-major حتمي وحد لكل قناة من 0 إلى 255 والتحقق من `autojs6-python-color-match-v1` الدقيق وعدم نقل بايتات الصورة أو مقابضها إلى Python

# v0.4.0-alpha.3

###### 2026/08/24

* `ملاحظة` مرشح alpha ثالث لأتمتة M3 في الشجرة الحالية؛ اجتاز مسار screen capture المحدود الكامل لنظام Android 11+ قبولاً مركزاً على محاكي API 37 مع تفعيل accessibility service، واجتاز fail-closed على جهاز فعلي API 31 من دون تغيير accessibility services فيه؛ يبقى البحث عن image/color وOCR والنشر ومصفوفة الأجهزة الكاملة خارج هذا الادعاء
* `إضافة` إضافة `autojs6.images.capture_screen` لإرجاع encoded bytes موثقة بصيغة PNG/JPEG أو كتابة ونشر output artifact للتنفيذ بصورة ذرية
* `تحسين` الاحتفاظ بما يصل إلى 1 capture لكل تنفيذ ونقل raw chunks بحجم 32 KiB وحد encoded data عند 4 MiB؛ يتحقق Python من الترتيب وEOF وSHA-256 وتواقيع التنسيق ويجري release دائماً، ويمسح Host البيانات عند الاستبدال/release/terminal ويعيد أخطاء ثابتة من دون تفعيل service أو فتح الإعدادات

# v0.4.0-alpha.2

###### 2026/08/24

* `ملاحظة` مرشح alpha ثان لأتمتة M3 في الشجرة الحالية؛ اجتاز مسار selector/UI tree المحدود الكامل قبولاً مركزاً على محاكي API 37 مع تفعيل خدمة إمكانية الوصول، واجتاز fail-closed على جهاز فعلي API 31 من دون تغيير خدمات إمكانية الوصول فيه؛ تبقى screenshot وOCR والنشر ومصفوفة الأجهزة الكاملة خارج هذا الادعاء
* `إضافة` إضافة واجهات live `autojs6.selector.snapshot/find/click/set_text` لبيانات accessibility tree المنفصلة واستعلامات أول تطابق المركبة بعلاقة AND والإجراءات الصريحة عبر مراجع node مبهمة مرتبطة بالتنفيذ
* `تحسين` تقييد nodes وعمق snapshot وحجمه ونصه وحجم selector scan ونص query/set والعقد المحتفظ بها؛ يعاد `SELECTOR_SCAN_LIMIT_EXCEEDED` للمسح غير المكتمل و`STALE_NODE` للمرجع القديم، وتؤدي accessibility غير المتاحة إلى `CapabilityUnavailableError` دون فتح الإعدادات

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
