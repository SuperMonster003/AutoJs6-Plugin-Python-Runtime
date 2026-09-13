******

### سجل الإصدارات

******

# v0.5.1

###### 2026/09/13

* `ملاحظة` مرشح مصدر مستقر 0.5.1; يبقى قبول الجهاز النهائي والنشر منفصلين عن نتائج beta التاريخية
* `إصلاح` فشل بناء Release بعد clean بسبب غياب ملف قواعد ProGuard الذي ينشئه Chaquopy
* `تحسين` التحقق أثناء البناء من محاذاة صفحات 16 KB للمكتبات الأصلية ذات 64 بت, مع فحص عقد manifest وتقارير JSON
* `تحسين` توحيد تنشيط المضيف وبيانات الإضافة والوثائق المترجمة وتجميع إصدارات APK الموقعة وفق قواعد الإضافات المشتركة

# v0.5.0

###### 2026/08/25

* `ملاحظة` 0.5.0 مرشح المصدر المستقر التراكمي؛ اجتاز مرشح beta المطابق والموقّع بـ SM003 اختبارات Android العشرة 10، من دون إعلان اكتمال APK المستقر أو tag أو publication
* `إضافة` يجمع M6 قدرات M1-M5 ومواد الاختبار القابلة لإعادة الاستخدام للبنود 2/3/4، ويثبت حدود مرشحي alpha → beta → stable والنشر الخفيفة
* `تحسين` تطابق APK arm64 للإصدار 0.5.0-beta.1 المسحوب من QV710AF65F بايتاً ببايت مع المرشح الرسمي، واكتملت الجولة الكاملة الثانية بنتيجة 10/10 PASS

# v0.5.0-beta.1

###### 2026/08/25

* `ملاحظة` 0.5.0-beta.1 مرشح مصدر مع تجميد الميزات؛ اجتاز مرشح alpha المطابق والموقّع بـ SM003 اختبارات Android العشرة 10، من دون إعلان اكتمال beta APK أو الإصدار المستقر أو publication
* `إضافة` يضيف M6 مشاريع قابلة لإعادة الاستخدام للبنود 2/3/4 ومدقق artifact مستقلاً كي يمكن قبول الاستيراد وstdin/الإدخال التفاعلي والنتائج المنظمة بصورة قابلة للتكرار
* `تحسين` تطابق APK arm64 للإصدار 0.5.0-alpha.6 المسحوب من QV710AF65F بايتاً ببايت مع المرشح الرسمي، واكتملت القائمة ذات البنود العشرة بنتيجة 10/10 PASS

# v0.5.0-alpha.6

###### 2026/08/25

* `ملاحظة` مرشح current-tree alpha السادس؛ استكمال عقد AutoJs6 WakeActivity لأول تفعيل للـ Plugin على OnePlus OPD2413 وأجهزة OEM المشابهة دون ادعاء production signed candidate أو beta أو publication
* `إصلاح` إعلان `org.autojs.plugin.WAKE_ACTIVITY` و`org.autojs.plugin.action.WAKE` عبر Activity من نوع NoDisplay محمية بـ signature permission وتنتهي فورا؛ يتيح ذلك لـ `ACTIVATE` في Plugin Center مسح `stopped/notLaunched` وإعادة محاولة التفعيل تلقائيا
* `تحسين` إعادة إنتاج الفشل الأصلي ومعالجته باستخدام debug Host عند `afca7b14c` وPlugin تشخيصي له نفس signer، مع إرجاع نتيجة startup probe خلال `277 ms`؛ والتأكد بشكل مستقل من أن اختلاف signer يفشل مغلقا باسم `PYTHON_RUNTIME_PROVIDER_UNTRUSTED`

# v0.5.0-alpha.5

###### 2026/08/25

* `ملاحظة` مرشح alpha خامس من current-tree; إعادة بناء ملفات AAR release الثلاثة لواجهة Host API من المصدر clean الدقيق `afca7b14c` مع تطابق البايتات وتحديث provenance lock إلى هذا المصدر, دون إعلان signed APK أو smoke Android ذي البنود العشرة أو beta أو publication
* `تحسين` تشغيل Host `verifyPythonReleaseApiDistributionGate` في worktree معزول وتثبيت AutoJs6 6.8.0/versionCode 5276 و protocol 1.6 و source fingerprint و SHA-256 الخاص بـ distribution manifest مع `dirty=false`

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

# v0.5.0-alpha.1

###### 2026/08/24

* `ملاحظة` أول مرشح alpha لـ M5 في الشجرة الحالية؛ ينجح مصدر foreground long-running للبروتوكول 1.6 واختبارات JVM غير المتصلة لـ Host/Plugin والبوابات المحمولة، لكن لم ينفذ smoke Android لـ M5 ولا يدعى النشر أو concurrency أو prewarm للعملية
* `إضافة` إضافة `executionMode=long-running` على مستوى المشروع دون deadline، تملكه خدمة Host `specialUse` في foreground وإشعار دائم وإجراء Stop؛ ترفض أسطح schedule وbackground/Intent وdeveloper دون downgrade
* `تحسين` يرسل Provider heartbeats مرتبة كل 15 s ويفرض Host lease بدء 2 min وlease heartbeat ‏45 s وlease مستقل لخدمة foreground؛ يفشل فقدان liveness وStop بشكل مغلق عبر إعادة تشغيل العملية بينما يبقى البروتوكول المحدود 1.0-1.5 متوافقا

# v0.4.0-alpha.9

###### 2026/08/24

* `ملاحظة` مرشح alpha التاسع للشجرة الحالية؛ يُغلق تقييم حزم native في M4 Path C بقرار `NOT_ADMITTED`، ويبقى runtime المضمّن `stdlib-only`، ولا تُضاف حمولات Pillow أو NumPy أو OpenCV أو تبعيات native الانتقالية ولا يُقدّم ادعاء قبول جديد على الأجهزة
* `تحسين` يسجل ADR 0004 debug builds ثنائية ABI وoffline باستخدام `--no-index --find-links`: يضيف Pillow 11.0.0 مقدار 2,054,483 bytes لكل APK، ويضيف NumPy 1.26.2 مقدار 21,931,164 bytes، وتجتاز المخرجات الستة `zipalign -c -P 16 4`
* `تحسين` يرفض تدقيق ELF الكامل عبر NDK 29 مكتبة FreeType بمحاذاة `0x1000` على كلا ABI وOpenBLAS/libgfortran بمحاذاة `0x1000` على x86_64؛ ولا يملك OpenCV wheel Android رسميًا من نوع `cp313`، وتتطلب إعادة الفتح wheels قابلة للتكرار عبر NDK r28+ وقبولًا عامًا بحجم 16 KiB

# v0.4.0-alpha.8

###### 2026/08/24

* `ملاحظة` مرشح alpha الثامن للشجرة الحالية؛ يُغلق تقييم حزم build-time في M4 Path B بقرار `NOT_ADMITTED`، ويبقى runtime المضمّن `stdlib-only`، ولا تُضاف `requests` أو أي تبعية مرشحة ولا يُقدّم ادعاء قبول جديد على الأجهزة
* `تحسين` يسجل ADR 0003 خطوط stdlib-only debug APK الأساسية: 23,709,688 bytes لـ arm64-v8a و23,726,048 bytes لـ x86_64 و34,622,039 bytes لـ universal؛ لا يُختلق فرق حجم دون wheelhouse offline مدقق، ويتطلب القبول المستقبلي Gradle `--offline` و`--no-index` و`--require-hashes` وأقفال license/hash وفروق أحجام ثلاثة APK وقبول المسار العام dual ABI

# v0.4.0-alpha.7

###### 2026/08/24

* `ملاحظة` مرشح alpha السابع من current-tree لأتمتة M3؛ نجح مسار Settings الحقيقي الكامل على محاكي API 37، بينما يبقى النشر ومسارا M4 B/C ومصفوفة الأجهزة الكاملة خارج نطاق هذا الإقرار
* `إضافة` إضافة `m3_complete_automation`، وهو مسار محدود على Settings الحقيقي يستخدم `app.launch` و`selector.find` و`selector.click` و`images.capture_screen` مع تحقق صارم من PNG واحتواء عنصر الوجهة
* `إصلاح` تطبيع حدود إمكانية الوصول ذات `right < left` أو `bottom < top` قبل تسلسل Python إلى محاور zero-area مرتبطة بنقطة الأصل، مع عزل عقد الشجرة غير المرتبطة عبر استعلامات selector الدقيقة
* `تحسين` نجح مسار المشروع العام المصدّر `RunIntentActivity` على محاكي API 37 مع PNG بدقة 1080x2424 وأثر متحقق منه عبر SHA-256، ثم أُعيدت إمكانية الوصول إلى 0/null وأزيل كل staging اختباري محدد

# v0.4.0-alpha.6

###### 2026/08/24

* `ملاحظة` مرشح alpha السادس لشجرة M3 automation الحالية؛ نجح Host OCR recognition المضبوط على API 37 emulator بخدمة مؤهلة وفشل مغلقا على جهاز API 31 فعلي من دون تغيير accessibility services؛ تبقى OCR الأوسع والنشر ومصفوفة الأجهزة الكاملة خارج هذا الادعاء
* `إضافة` إضافة `autojs6.ocr.recognize(image)` لبايتات PNG/JPEG محدودة وtuple ثابت ومرتب من أسطر النص يعيده Host OCR engine المضبوط
* `تحسين` إعادة استخدام PNG/JPEG upload بحجم 1 MiB وraw chunks بحجم 24 KiB والتحقق SHA-256، واختيار Host OCR service مفعلة ومصرحا بها ومتوافقة فقط، وتحديد النتيجة عند 256 سطرا و4 KiB من strict UTF-8 لكل سطر و48 KiB إجمالا، ودائما release وتصفير buffers، والإبلاغ الثابت بـ `OCR_UNAVAILABLE` أو `OCR_FAILED`

# v0.4.0-alpha.5

###### 2026/08/24

* `ملاحظة` مرشح alpha الخامس لأتمتة M3 في الشجرة الحالية؛ نجحت مطابقة القالب المحدودة على محاكي API 37 مع accessibility مفعلة وفشلت بشكل مغلق على جهاز فعلي API 31 من دون تغيير خدمات accessibility؛ ولا تشمل هذه المطالبة OCR أو النشر أو مصفوفة أجهزة كاملة
* `إضافة` إضافة `autojs6.images.find_image(template, *, region=None, threshold=0)` لبايتات PNG/JPEG ومنطقة محدودة اختيارية ونتيجة إحداثي الزاوية العليا اليسرى أو `None`
* `تحسين` رفع template واحد لكل تنفيذ حتى 1 MiB في raw chunks بحجم 24 KiB مع تحقق SHA-256، وفك ترميز لا يتجاوز 2048 بكسل لكل جانب، ومسح deterministic بترتيب row-major وفق `autojs6-python-image-match-v1`؛ تشارك البكسلات المعتمة بالكامل فقط والبقية wildcard، ولا حاجة إلى OpenCV، مع تنفيذ release وتصفير buffers دائمًا، وإعادة محاولة حد Android البالغ 333 ms فقط بعد انتظار محدود قدره 350 ms

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

# v0.4.0-alpha.1

###### 2026/08/23

* `ملاحظة` اول مرشح alpha للشجرة الحالية لأتمتة M3؛ اجتازت إجراءات الإحداثيات/global المحدودة القبول المركز على محاكي API 37 مع accessibility مفعلة، واجتاز fail-closed جهازا فعليا API 31 دون تغيير accessibility services الحالية، بينما تبقى selector/UI tree وscreenshot وOCR والنشر ومصفوفة الأجهزة الكاملة خارج هذا الادعاء
* `إضافة` إضافة واجهات live `autojs6.automator.click/long_click/press/swipe/back/home` عبر Host accessibility مع إرجاع نتيجة dispatch المنطقية الفعلية
* `تحسين` قبول إحداثيات صحيحة صارمة غير boolean من 0 إلى 1000000 ومدد press/swipe من 1 إلى 4000 ms فقط؛ يؤدي غياب Host accessibility إلى `CapabilityUnavailableError` دون فتح الإعدادات

# v0.3.0-alpha.6

###### 2026/08/23

* `ملاحظة` اول مرشح alpha من M4 للشجرة الحالية؛ اجتاز مسار تبعيات pure-Python المحلية للمشروع قبولا مركزا على جهازين، بينما تبقى دفعات M3/M4 اللاحقة والنشر ومصفوفة الاجهزة الكاملة خارج هذا الادعاء
* `إضافة` دعم حزم pure-Python المحلية للمشروع وبيانات `.dist-info` من جذور المشاريع المقبولة، مع مثال `requests` قابل لاعادة الانتاج باصدارات مثبتة ودون مثبت وقت التشغيل
* `تحسين` رفع حدود workspace إلى 64 MiB مضغوطة و8192 ملفا و128 MiB بعد الاستخراج، ومطابقة الابعاد الفعلية الثلاثة للـ snapshot مع قدرات Provider قبل dispatch؛ يبقى import المفقود `ModuleNotFoundError` دون pip عبر الانترنت او رجوع إلى محرك اخر

# v0.3.0-alpha.5

###### 2026/08/23

* `ملاحظة` مرشح alpha خامس من M3 للشجرة الحالية؛ اجتاز جزء Host engines المحدود من المجموعة الثانية قبولاً مركزاً على جهازين، ولا يشمل ذلك القدرات اللاحقة أو النشر أو مصفوفة أجهزة كاملة
* `إضافة` إضافة واجهات live `autojs6.engines.current/run/stop_self` لبيانات المحرك الحالي من دون مسارات وتشغيل نصوص Host فرعية غير مكتوبة بلغة Python بشكل غير متزامن والإيقاف الذاتي الحتمي
* `تحسين` قبول المسارات الفرعية النسبية المطبعة داخل جذر التنفيذ فقط وبحد أقصى 16 تشغيلاً ناجحاً لكل تنفيذ؛ تفشل Python المتداخلة بالرمز `NESTED_PYTHON_NOT_ALLOWED` ويلغي `stop_self` التنفيذ بإعادة تشغيل عملية provider

# v0.3.0-alpha.4

###### 2026/08/23

* `ملاحظة` مرشح alpha رابع من M3 للشجرة الحالية؛ اجتازت حوارات Host في foreground قبولاً مركزاً على جهازين، ولا يشمل ذلك engines أو القدرات اللاحقة أو النشر أو مصفوفة أجهزة كاملة
* `إضافة` إضافة API المقصورة على foreground وهي `autojs6.dialogs.alert/confirm/prompt/select` مع نتائج typed للإقرار والتأكيد والنص nullable وفهرس nullable يبدأ من الصفر
* `تحسين` تقييد العناوين والمحتوى والردود والعناصر، وتسلسل حوار واحد تملكه Host في كل مرة، ورفض تشغيل background بالرمز المستقر `INTERACTIVE_NOT_ALLOWED` من دون فتح UI

# v0.3.0-alpha.3

###### 2026/08/23

* `ملاحظة` مرشح alpha ثالث من M3 للشجرة الحالية؛ اجتاز الجزء المحدود من Host files في المجموعة الثانية قبولاً مركزاً على جهازين، ولا يشمل ذلك الحوارات أو engines أو القدرات اللاحقة أو النشر أو مصفوفة أجهزة كاملة
* `إضافة` إضافة API مباشرة `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` للوصول المحدود إلى نص UTF-8 داخل جذر المشروع الحالي أو مجلد السكربت المستقل
* `تحسين` رفض المسارات غير الآمنة أو الخارجة من الجذر، وتقييد النص والقوائم المباشرة، وإرجاع أخطاء ملفات مستقرة، وفصل جذر Host المباشر عن workspace snapshot المجمدة في Plugin

# v0.3.0-alpha.2

###### 2026/08/23

* `ملاحظة` ثاني مرشح alpha من M3 للشجرة الحالية؛ اكتملت أول مجموعة قدرات Host منخفضة المخاطر، ولا يشمل هذا الادعاء الدفعات اللاحقة أو النشر أو مصفوفة أجهزة كاملة
* `إضافة` إضافة بيانات البطارية/الشاشة/السطوع/الصوت المباشرة عبر `autojs6.device.info()` ومستويات وحدة تحكم Host عبر `autojs6.console.log/warn/error` وإشعارات `autojs6.notice`
* `تحسين` التحقق الصارم من مخطط نتيجة device وإرجاع `PERMISSION_DENIED` ثابت عند نقص إذن الإشعارات من دون فتح الإعدادات أو تغيير أذونات الجهاز

# v0.3.0-alpha.1

###### 2026/08/23

* `ملاحظة` أول مرشح alpha من M3 للشجرة الحالية؛ نُفذ البروتوكول 1.5 ومجموعة قدرات Host منخفضة المخاطر، ولا يشمل هذا الادعاء القدرات اللاحقة أو النشر أو مصفوفة أجهزة كاملة
* `إضافة` إضافة Host capability broker خاص بالتنفيذ في البروتوكول 1.5 عبر JSON ببيانات خالصة مرتبط بـ request UUID وUID الإضافة ومعرفات call متزايدة وحصة 1024 استدعاء ورسائل 64 KiB وحد dispatch للمضيف قدره 5 ثوان
* `إضافة` إضافة Host API مباشرة: `autojs6.toast` و`autojs6.clip.get/set` و`autojs6.app.launch/launch_app/open_url`
* `تحسين` إلغاء broker بشكل موحد عند terminal والإلغاء وBinder death والتنظيف، مع أخطاء Python ثابتة للقدرات غير المتاحة وأخطاء Host أو protocol

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
