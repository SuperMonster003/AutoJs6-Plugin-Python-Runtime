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
