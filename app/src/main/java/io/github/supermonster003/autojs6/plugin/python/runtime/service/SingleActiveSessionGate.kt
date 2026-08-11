package io.github.supermonster003.autojs6.plugin.python.runtime.service

import java.util.concurrent.atomic.AtomicReference

internal class SingleActiveSessionGate<T : Any> {
    private data class State<T>(val active: T?, val retiring: Boolean)

    private val state = AtomicReference(State<T>(active = null, retiring = false))

    fun tryAcquire(session: T): Boolean {
        while (true) {
            val current = state.get()
            if (current.retiring || current.active != null) return false
            if (state.compareAndSet(current, State(active = session, retiring = false))) return true
        }
    }

    fun release(session: T): Boolean {
        while (true) {
            val current = state.get()
            if (current.active !== session) return false
            if (state.compareAndSet(current, State(active = null, retiring = current.retiring))) return true
        }
    }

    fun markRetiring(): Boolean {
        while (true) {
            val current = state.get()
            if (current.retiring) return false
            if (state.compareAndSet(current, State(active = current.active, retiring = true))) return true
        }
    }

    fun isRetiring(): Boolean = state.get().retiring
}
