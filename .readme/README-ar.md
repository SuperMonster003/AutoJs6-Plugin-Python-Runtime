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

> جمدت source identity للإصدار 0.1.0 وHost lock الدقيقة. تبقى أدلة RC المحلية للبناء وAPK وBinder وجهاز API 31 arm64-v8a واحد تاريخية؛ لم تكتمل بعد APK/P3 provenance النهائية وtag ‏v0.1.0 وGitHub Release وproduction receipt.

******

### الميزات

******

- تنفيذ لقطة مصدر Python بترميز UTF-8 كـ `__main__`.
- حفظ ترتيب stdout وstderr ثم إرسال chunks محدودة باستخدام credits.
- إرجاع `SystemExit` وأخطاء الصياغة والتنفيذ مع traceback منظم ومحدود.
- السماح بجلسة نشطة واحدة لكل عملية دون طابور لدى provider.
- لا حاجة لإعادة تشغيل المضيف: يعيد التنفيذ الجديد التالي بعد التثبيت أو إعادة التفعيل اكتشاف provider وتثبيت هويته، بينما ينهي Binder death أثناء التشغيل ذلك التنفيذ دون إعادة تلقائية.

******

### بيئة التشغيل وتنسيقات البيانات

******

يعلن البروتوكول V1 حاليا النطاق التالي:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
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
protocol: 1.0-1.1
```

تقبل الإضافة SOURCE مستقلا وworkspace archive اختياريا محدودا وsnapshot للقدرات المضيفة للقراءة فقط في البروتوكول 1.1؛ يظل stdin snapshot معطلا ولا يتم حقن Context أو Binder أو كائنات المضيف أو callback sink.

******

### حالة تكامل المضيف

******

> يرتبط 0.1.0 فقط بـ AutoJs6 6.8.0، وقد جمد وفرض الحد الأدنى Host versionCode 5275. سجلت clean Host source revision النهائية وmanifest توزيع AAR الثلاثة في lock. يعيد كل تنفيذ جديد اكتشاف provider؛ عند فقده أو تعطيله يطلب التثبيت أو التفعيل دون fallback، ولا يحتاج Host إلى إعادة تشغيل بعد التثبيت أو التفعيل. ما زالت APK/P3 provenance النهائية والفهرسة الرسمية وtag وRelease معلقة.

```text
release target: 0.1.0
release state: stable source identity frozen by the clean VERSION_BUILD=9 commit with the final Host lock; not tagged or published
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- حد المصدر 4 MiB والخرج الكلي 4 MiB وكل chunk ‏16 KiB وعددها 4096.
- أقصى timeout هو 60 s مع جلسة واحدة ودون طابور provider.
- تتملك العملية نسخ PFD الكاملة المستلمة عبر Binder وتغلقها عند النهاية أو close.
- يخزن الخرج أولا بحدود ثم يرسل بالـ credits؛ لا يدعى وجود backpressure أثناء التنفيذ.
- يعيد الإلغاء تشغيل العملية؛ تتطلب native extensions والاستدعاءات الحاجبة تحقق Android لاحقا.
- تحظر سياسة stdlib-only استخدام pip عبر الإنترنت وحزم Python الخارجية. ما زالت أذونات APK المدمج بحاجة للفحص.

******

### قدرات غير معلنة

******

- لا تدعم stdin snapshot أو الكتابة إلى workspace أو pip عبر الإنترنت أو تنزيل wheels.
- لا توجد نصوص UI أو debugger أو REPL أو صلاحية عشوائية لكائنات Java في المضيف.
- لا يوجد AutoJs6 capability broker آني؛ تستخدم أول API فقط snapshot ‏app/device/execution/project المجمد عند بدء التنفيذ وقراءة محدودة من workspace الخاص بالإضافة.
- لا يضمن Android ‏32-bit أو أي native wheel خارجي.
- يوجد دليل جهاز API 31 لـ arm64-v8a؛ أما x86_64 فلديه دليل packaging فقط وليس تنفيذا على جهاز أو مصفوفة كاملة.

******

### خارطة الطريق

******

أصبحت أدلة RC المحلية والجهاز المركزة في R6-P2/P3 تاريخية. يثبت clean VERSION_BUILD=9 freeze commit هذا stable Plugin source identity وexact Host 6.8.0/5275 lock؛ العوائق المتبقية فقط هي APK/P3 provenance للـ artifacts الدقيقة والفهرس الرسمي وtag/Release وproduction receipt بعد النشر. ليست مصفوفة API×ABI الكاملة أو soak جديد بوابات تلقائية.

- [عرض ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### سجل الإصدارات

******

# v0.1.0

###### 2026/08/12 (جمد المصدر؛ دون tag أو نشر)

* `ملاحظة` جمدت source identity للإصدار 0.1.0 وHost lock الدقيقة؛ تبقى APK/P3 provenance النهائية والفهرس الرسمي وtag/Release وproduction receipt
* `إضافة` بروتوكول Python ‏1.0-1.1 مقترن بـ AutoJs6 6.8.0 / versionCode 5275 وproject workspace محدود وsnapshots ‏app/device/execution/project للقراءة فقط
* `إضافة` Hot-plug دون إعادة تشغيل المضيف: يسمح التثبيت أو إعادة التفعيل للتنفيذ الجديد التالي بإعادة اكتشاف الهوية وpin دون fallback عند الفقد أو التعطيل
* `إضافة` ينهي Binder death أثناء التشغيل التنفيذ الحالي دون replay؛ تعيد عمليات التنفيذ الجديدة اكتشاف provider
* `تحسين` تثبيت Chaquopy كبيئة trusted-local وnon-sandbox؛ ‏SM003 هو signer طويل الأجل وSuperMonster003 هو owner لـ runtime/security/release
* `اعتماد` قفل Chaquopy 17.0.0 وCPython 3.13.9؛ تعاد مراجعة artifacts النهائية بعد تجميد المصدر

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

لا تستبدل الفحوص الثابتة وCPython المحلي أدلة Android. نتائج RC والجهاز الواحد الحالية تاريخية؛ بعد تجميد المصدر النهائي تعاد فقط فحوص البناء وAPK وBinder والجهاز التمثيلي المرتبطة بهوية النشر.

******

### البناء

******

لا يشغل هذا التعديل الوثائقي البناء. تفشل إعدادات release بشكل مغلق عند تغير AAR أو SHA-256 أو signer أو runtime lock؛ ما زال 0.1.0 قيد التحضير بلا tag أو نشر.

يجب وضع ملفات release AAR التالية وتثبيتها في `libs` قبل البناء:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

تقفل البيئة Chaquopy 17.0.0 وCPython 3.13.9 من Maven وتحزم stdlib فقط. يجب أن يعيد الإصدار النهائي فحص metadata والمكتبات الأصلية وصفحات 16 KB وNOTICE وsigner ‏SM003 وملفات APK الثلاثة.

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
