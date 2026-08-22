# The Binder interfaces and codecs are a separately versioned public ABI.
-keep class org.autojs.plugin.python.runtime.api.** { *; }
-keep interface org.autojs.plugin.python.runtime.api.** { *; }

# Runtime service entry points are instantiated by Android from the manifest.
-keep class io.github.supermonster003.autojs6.plugin.python.runtime.** extends android.app.Service { *; }

# The packaged bootstrap calls this one narrow Plugin-private bridge by name.
-keep class io.github.supermonster003.autojs6.plugin.python.runtime.execution.ChaquopyOutputSink {
    public boolean emit(java.lang.String, byte[]);
}

-keep class io.github.supermonster003.autojs6.plugin.python.runtime.execution.ChaquopyInputBridge {
    public java.lang.String request(java.lang.String, java.lang.String);
}
