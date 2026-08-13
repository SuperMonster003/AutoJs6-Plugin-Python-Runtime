******

### سجل الإصدارات

******

# v0.2.0-alpha.1

###### 2026/08/13

* `ملاحظة` مرشح alpha لمصادر U1 النظيفة بعد 0.1؛ لا يتوفر تفاعل stdin مباشر, ولا يمثل قبول U1-R1 E3 الا تقرير canonical PASS مطابقا لقطع Host/Plugin الدقيقة على QV710AF65F/API 31/arm64؛ وهذا ليس دليلا لمصفوفة اجهزة او اصدار او نشر عام
* `إضافة` إضافة snapshot محدود ومقدم مسبقا لـ stdin بحجم أقصى 1 MiB لتوفير input وEOF حتميين عبر `input()` و`sys.stdin`
* `إضافة` إكمال دلالات project import لوحدات workspace ووحدات sibling/root لنقطة دخول متداخلة وعمليات package-relative import
* `إصلاح` فك source بترميز strict UTF-8 قبل التنفيذ لمنع encoding cookie بترميز آخر من تجاوز العقد
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
