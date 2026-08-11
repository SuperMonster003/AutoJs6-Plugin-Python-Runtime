// Top-level build file where you can add configuration options common to all sub-projects/modules.

plugins {
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
