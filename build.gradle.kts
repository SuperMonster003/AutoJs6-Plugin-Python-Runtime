// Top-level build file where you can add configuration options common to all sub-projects/modules.

plugins {
    // @Hint: AGP is declared here as well, without being applied.
    //  ! The Chaquopy plugin is loaded from this script's classpath and needs AGP classes
    //  ! to be visible to it. Declaring both in the same block puts them in one classloader;
    //  ! leaving AGP out makes Chaquopy fail with "com/android/build/api/variant/Variant".
    //  ! zh-CN: 此处一并声明 AGP 但不应用. Chaquopy 插件由本脚本的 classpath 加载, 需要能看到
    //  ! AGP 的类; 两者写在同一个块中即处于同一 classloader. 若省略 AGP, Chaquopy 会以
    //  ! "com/android/build/api/variant/Variant" 失败.
    id("com.android.application") version System.getProperty("gradle.agp.version") apply false
    id("com.chaquo.python") version "17.0.0" apply false
}

allprojects {
    repositories {
        mavenCentral()
        google()
    }
}

tasks {
    register<Delete>("clean").configure {
        delete(rootProject.layout.buildDirectory)
    }
}
