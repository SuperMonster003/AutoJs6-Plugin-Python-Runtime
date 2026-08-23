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
- إرسال chunks محدودة من stdout/stderr بترتيبها الأصلي أثناء التنفيذ؛ يفرض نفاد credits ضغطا عكسيا على التنفيذ.
- تعيين نتيجة JSON صارمة وصريحة بحجم أقصاه 64 KiB ونقل ما يصل إلى 16 من output artifacts الاختيارية ضمن حدود المسار والحجم وSHA-256 في البروتوكول 1.4؛ ولا تستنتج النتيجة من stdout.
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
protocol: 1.0-1.4
```

تقبل الإضافة SOURCE مستقلا وworkspace archive اختياريا محدودا وstdin snapshot محدودا ومقدما مسبقا بحجم أقصاه 1 MiB وsnapshot للقدرات المضيفة للقراءة فقط في البروتوكول 1.1. يضيف البروتوكول 1.2 تفاوضا صريحا على مدخل file/module للمشاريع المقبولة. يضيف البروتوكول 1.3 بعد EOF للـ snapshot تفاعل prompt/reply تملكه Host ومقصورا على `input()` المضمنة في foreground، بينما تستخدم `getpass.getpass()` إدخالا مخفيا. يضيف البروتوكول 1.4 JSON صارما وصريحا وoutput artifacts اختيارية موصوفة بـ SHA-256؛ يبقى stdout للتشخيص ولا يحلل كنتيجة. يظل `sys.stdin` المباشر محدودا ولا تفتح عمليات background واجهة إدخال ولا يتم حقن Context أو Binder أو كائنات المضيف أو callback sink.

******

### حالة تكامل المضيف

******

> يرتبط 0.1.0 فقط بـ AutoJs6 6.8.0، وقد جمد وفرض الحد الأدنى Host versionCode 5275. سجلت clean Host source revision النهائية وmanifest توزيع AAR الثلاثة في lock. يعيد كل تنفيذ جديد اكتشاف provider؛ عند فقده أو تعطيله يطلب التثبيت أو التفعيل دون fallback، ولا يحتاج Host إلى إعادة تشغيل بعد التثبيت أو التفعيل. ترتبط stable APK identity بهذه exact Plugin source وHost lock.

```text
release target: 0.2.0-alpha.1
release state: 0.2.0 current-tree candidate; M1 and M2 are implemented and smoke-tested on an API 31 arm64 device plus an API 37 x86_64 16 KiB-page emulator; background direct sys.stdin remains finite, and no complete device-matrix, publication, or release evidence is claimed
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
- تتملك العملية نسخ PFD الكاملة المستلمة عبر Binder وتغلقها عند النهاية أو close.
- يرسل الخرج chunk بعد chunk بالـ credits أثناء التنفيذ؛ يوقف نفاد credits السكربت مؤقتا، ويسبق الخرج المقبول الحالة terminal الوحيدة، ويمنع الخرج بعدها.
- يحد JSON المنظم عند 64 KiB وتقبل حتى 16 artifacts بمسار 1024 UTF-8 bytes و4 MiB لكل ملف و8 MiB إجمالا مع تحقق Host من الطول الدقيق وEOF وSHA-256.
- يعيد الإلغاء تشغيل العملية؛ تتطلب native extensions والاستدعاءات الحاجبة تحقق Android لاحقا.
- يسمح إذن `INTERNET` للنصوص باستخدام عملاء الشبكة في المكتبة القياسية مباشرة؛ ولا يزال pip عبر الإنترنت والتنزيل التلقائي للكود وتثبيت حزم الجهات الخارجية وقت التشغيل غير مدعوم.

******

### قدرات غير معلنة

******

- لا يتوفر live stdin عام ولا callback streaming مباشر لـ `sys.stdin`. يقتصر تفاعل foreground على `input()` المضمنة و`getpass.getpass()` بعد EOF للـ snapshot المحدود حتى 1 MiB. تظل الكتابة إلى workspace وpip عبر الإنترنت وتنزيل wheels غير مدعومة.
- لا توجد نصوص UI أو debugger أو REPL أو صلاحية عشوائية لكائنات Java في المضيف.
- لا يوجد AutoJs6 capability broker آني؛ تستخدم أول API فقط snapshot ‏app/device/execution/project المجمد عند بدء التنفيذ وقراءة محدودة من workspace الخاص بالإضافة.
- لا يضمن Android ‏32-bit أو أي native wheel خارجي.
- تتوفر للشجرة الحالية أدلة smoke على جهاز API 31 ‏arm64-v8a وعلى محاكي API 37 ‏x86_64 بصفحات 16 KB؛ ولا يقدم أي منهما كمصفوفة أجهزة كاملة أو كتأهيل release.

******

### خارطة الطريق

******

تبقى أدلة RC المحلية والجهاز المركزة في R6-P2/P3 تاريخية. يثبت clean VERSION_BUILD=11 freeze commit هذا stable Plugin source identity وexact Host 6.8.0/5275 lock؛ تقيم stable APK provenance مقابل هذه exact identities ويجب أن يستخدم أي production receipt الأساس نفسه. ليست مصفوفة API×ABI الكاملة أو soak جديد بوابات تلقائية.

- [عرض ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### سجل الإصدارات

******

# v0.2.0-alpha.1

###### 2026/08/13

* `ملاحظة` مرشح alpha لشجرة U1 الحالية بعد 0.1؛ تغطى module entry وlive output وinput المضمن في foreground وstructured JSON الصريح وoutput artifacts المحدودة في U1-R2 حتى E2 فقط؛ تظل عمليات background وsys.stdin المباشر غير تفاعلية ويبقى R2 E3 مفتوحا ولا تثبت نتائج الشجرة الحالية مصفوفة اجهزة او اصدارا او نشرا عاما
* `إضافة` إضافة snapshot محدود ومقدم مسبقا لـ stdin بحجم أقصى 1 MiB لتوفير input وEOF حتميين عبر `input()` و`sys.stdin`
* `إضافة` إكمال دلالات project import لوحدات workspace ووحدات sibling/root لنقطة دخول متداخلة وعمليات package-relative import
* `إضافة` إضافة البروتوكول 1.2 مع `entryMode=file|module` الصريح؛ يستخدم تنفيذ module أداة `runpy` مع `__package__` و`__spec__` الصحيحين وجذر المشروع في `sys.path[0]` وعمليات الاستيراد النسبية، بينما يبقى وضع file دون تغيير
* `إضافة` إضافة prompt/reply محدود في البروتوكول 1.3 ومقصور على foreground بعد EOF للـ snapshot المحدود، بإدخال ظاهر للدالة `input()` ومخفي للدالة `getpass.getpass()`؛ لا تفتح عمليات background واجهة إدخال ويظل `sys.stdin` المباشر محدودا
* `إضافة` إضافة نتائج JSON صارمة وصريحة وoutput artifacts اختيارية في البروتوكول 1.4 ضمن حدود العدد والمسار المنظم وحجم الملف/الإجمالي ومراجع PFD الدقيقة وSHA-256 دون استنتاج نتيجة من stdout
* `إصلاح` فك source بترميز strict UTF-8 قبل التنفيذ لمنع encoding cookie بترميز آخر من تجاوز العقد
* `تحسين` منح `INTERNET` كي تستخدم النصوص الموثوقة عملاء شبكة المكتبة القياسية مباشرة مع إبقاء pip عبر الإنترنت والتنزيل التلقائي للكود معطلين
* `تحسين` رفع حد تنفيذ Provider إلى 30 دقيقة والإخراج المحدود إلى 16 MiB / 16384 chunks
* `تحسين` نقل chunks المحدودة من stdout/stderr والضغط العكسي بالـ credits إلى أثناء تنفيذ السكربت، مع حفظ الخرج الجزئي المرتب قبل terminal ومنعه بعدها
* `تحسين` استخدام `__main__` مستقل لكل تنفيذ واستعادة حالات stdin/stdout/stderr وargv وcwd و`sys.path` وmodule وimporter cache
* `تحسين` تطبيق lease مدته 5 ثوان على session مفتوحة لم تبدأ ثم تحرير inputs وdescriptors وموضع session الوحيد
* `تحسين` فرض الحد الأدنى Host versionCode 5275 عند حد Binder الخاص بـ Provider بدلا من الاعتماد فقط على discovery من Host

# v0.1.0

###### 2026/08/12

* `ملاحظة` يثبت الإصدار 0.1.0 stable Plugin source identity وexact Host 6.8.0/5275 lock
* `إضافة` بروتوكول Python ‏1.0-1.1 مقترن بـ AutoJs6 6.8.0 / versionCode 5275 وproject workspace محدود وsnapshots ‏app/device/execution/project للقراءة فقط
* `إضافة` Hot-plug دون إعادة تشغيل المضيف: يسمح التثبيت أو إعادة التفعيل للتنفيذ الجديد التالي بإعادة اكتشاف الهوية وpin دون fallback عند الفقد أو التعطيل
* `إضافة` ينهي Binder death أثناء التشغيل التنفيذ الحالي دون replay؛ تعيد عمليات التنفيذ الجديدة اكتشاف provider
* `تحسين` تثبيت Chaquopy كبيئة trusted-local وnon-sandbox؛ ‏SM003 هو signer طويل الأجل وSuperMonster003 هو owner لـ runtime/security/release
* `اعتماد` قفل Chaquopy 17.0.0 وCPython 3.13.9؛ ترتبط stable APKs بهوية المصدر النهائية وتتحقق كـ exact artifacts

# v0.1.0-alpha.1

###### 2026/08/09

* `ملاحظة` مصادر نموذج R2 أولي؛ لم يتم التحقق من Gradle أو APK أو Binder أو الأجهزة
* `إضافة` scaffold مستقل لـ provider Python V1 بعملية مخصصة وجلسة واحدة ودون طابور
* `إضافة` تنفيذ مصدر واحد كـ `__main__` مع stdout/stderr محدودين واستثناءات منظمة وإلغاء بإعادة العملية
* `إضافة` إنشاء README وسجلات مدمجة بعشر لغات وفق ترتيب ثابت
* `اعتماد` اختيار أولي لـ Chaquopy 17.0.0 وPython 3.13؛ الإصدارات وhashes تحتاج تحقق البناء

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
