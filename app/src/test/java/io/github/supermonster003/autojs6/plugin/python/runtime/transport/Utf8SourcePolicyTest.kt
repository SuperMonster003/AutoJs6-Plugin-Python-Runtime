package io.github.supermonster003.autojs6.plugin.python.runtime.transport

import org.junit.Assert.assertThrows
import org.junit.Test

class Utf8SourcePolicyTest {
    @Test
    fun acceptsUtf8BomAndUtf8Cookie() {
        Utf8SourcePolicy.requireValid("print('你好')\n".toByteArray(Charsets.UTF_8))
        Utf8SourcePolicy.requireValid(byteArrayOf(0xef.toByte(), 0xbb.toByte(), 0xbf.toByte()) + "print(1)\n".toByteArray())
        Utf8SourcePolicy.requireValid("# coding: utf_8\nprint(1)\n".toByteArray())
    }

    @Test
    fun rejectsMalformedUtf8NulAndNonUtf8Cookie() {
        assertThrows(Exception::class.java) {
            Utf8SourcePolicy.requireValid(byteArrayOf(0xc3.toByte(), 0x28))
        }
        assertThrows(IllegalArgumentException::class.java) {
            Utf8SourcePolicy.requireValid("print(1)\u0000\n".toByteArray())
        }
        assertThrows(IllegalArgumentException::class.java) {
            Utf8SourcePolicy.requireValid("# coding: latin-1\nprint(1)\n".toByteArray())
        }
    }
}
