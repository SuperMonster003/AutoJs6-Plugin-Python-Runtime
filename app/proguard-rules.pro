# The Binder interfaces and codecs are a separately versioned public ABI.
-keep class org.autojs.plugin.python.runtime.api.** { *; }
-keep interface org.autojs.plugin.python.runtime.api.** { *; }

# Runtime service entry points are instantiated by Android from the manifest.
-keep class io.github.supermonster003.autojs6.plugin.python.runtime.** extends android.app.Service { *; }
