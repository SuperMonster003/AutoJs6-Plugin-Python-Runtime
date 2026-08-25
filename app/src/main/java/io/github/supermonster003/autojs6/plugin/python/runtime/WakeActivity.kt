package io.github.supermonster003.autojs6.plugin.python.runtime

import android.app.Activity
import android.os.Bundle

/** Clears OEM first-run restrictions, then immediately returns to AutoJs6. */
class WakeActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        finish()
    }
}
