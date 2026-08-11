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

> هذا حاليا نموذج R2 أولي. توجد مصادر بيئة التشغيل واختبارات دلالة bootstrap المحلية، لكن لم يتم تشغيل إعداد Gradle أو تجميع Android أو فحص APK أو تحقق Binder أو اختبارات الأجهزة.

******

### الميزات

******

- تنفيذ لقطة مصدر Python بترميز UTF-8 كـ `__main__`.
- حفظ ترتيب stdout وstderr ثم إرسال chunks محدودة باستخدام credits.
- إرجاع `SystemExit` وأخطاء الصياغة والتنفيذ مع traceback منظم ومحدود.
- السماح بجلسة نشطة واحدة لكل عملية دون طابور لدى provider.
- إنهاء العملية المخصصة بعد الإلغاء أو timeout أو callback death دون إعادة تشغيل النص.

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

يطلب البناء Python 3.13. الإصدار 3.13.9 هو الإصدار المتوقع وفق معلومات Chaquopy الحالية ولا يعد متحققا حتى فحص APK وتشغيله على جهاز.

******

### واجهة الإضافة

******

يكتشف المضيف الإضافة ويستدعيها بالمعرفات التالية:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

تقبل الإضافة descriptor من نوع SOURCE فقط. حدود workspace archive وstdin snapshot تساوي صفرا ولا يتم حقن Context أو Binder أو كائنات المضيف أو callback sink.

******

### حالة تكامل المضيف

******

> يتقدم البروتوكول وربط المضيف، لكن ملفات release AAR المطلوبة لم تنشر أو تتحقق بعد. تثبيت هذا scaffold وحده لا ينشئ محرك Python صالحا للاستخدام.

******

### الأمان والخصوصية

******

لا يطلب manifest المصدر أذونات Android. تتطلب exported service إذن توقيع المضيف وتعيد التحقق من UID والحزمة المثبتة والتوقيعات عند مداخل Binder. يظل Java bridge في Chaquopy متاحا، لذلك يعتمد العزل على Android UID مستقل وعملية مخصصة وحد Binder ضيق ولا يدعي أن CPython sandbox آمن.

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

- لا تدعم workspace archive أو stdin snapshot أو pip عبر الإنترنت أو تنزيل wheels.
- لا توجد نصوص UI أو debugger أو REPL أو صلاحية عشوائية لكائنات Java في المضيف.
- لا يوجد بعد AutoJs6 capability broker أو ربط مع API المضيف.
- لا يضمن Android ‏32-bit أو أي native wheel خارجي.
- اختبارات CPython المحلية ليست دليلا على Chaquopy أو Android أو Binder أو الأجهزة.

******

### خارطة الطريق

******

يتوفر مستودع R2 المستقل والحد الثابت ومصادر provider/bootstrap والاختبارات المحلية. تم تأجيل Gradle وADB أثناء soak المحمي للجهاز QV710AF65F. ما زالت release AAR والتبعيات وتجميع Android وفحوص APK/16 KB وBinder/PFD ومصفوفة الأجهزة غير مكتملة.

- [عرض ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### سجل الإصدارات

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

اختبارات دلالة bootstrap المحمولة باستخدام CPython المحلي:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

لا تثبت هذه الفحوص عمل Android. يجب التحقق من Gradle وAPK وBinder والأجهزة بعد انتهاء soak المحمي.

******

### البناء

******

لا يتم البناء الآن. تفشل إعدادات release بشكل مغلق ما دامت AAR أو قيم SHA-256 غير مثبتة.

يجب وضع ملفات release AAR التالية وتثبيتها في `libs` قبل البناء:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

يخطط لاستخدام Chaquopy 17.0.0 من Maven مع stdlib فقط. ما زالت بيانات تحقق التبعيات والمكتبات الأصلية والتراخيص وتوافق 16 KB page بحاجة للقبول.

******

### الترخيص

******

يستخدم مصدر المشروع MPL-2.0. تبقى Chaquopy وCPython والمكونات الأخرى تحت تراخيصها.

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
