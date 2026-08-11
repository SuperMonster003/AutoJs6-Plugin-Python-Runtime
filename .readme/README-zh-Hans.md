<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>独立 Python 运行时插件. 在专用插件进程中执行 Python 脚本</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 语言

******

当前 README.md 支持以下语言:

- 简体中文 [zh-Hans] # 当前
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### 简介

******

Python Runtime 是独立的 Python 协议 V1 provider. 宿主把单个 Python 源码快照交给专用插件进程, 插件使用 CPython 执行并返回有界输出, 结构化异常和唯一终态.

> 当前仅为 R2 概念验证. 运行时源码与本机 bootstrap 语义检查已经落地, 但尚未执行 Gradle 配置, Android 编译, APK 检查, Binder 验证或设备验收.

******

### 功能

******

- 将一个 UTF-8 Python 源码快照作为 `__main__` 执行.
- 按原始顺序收集 stdout 和 stderr, 再通过有界 chunk 与 credit 传送.
- 返回 `SystemExit`, 语法错误和运行时异常, 包括有界结构化 traceback.
- 同一运行时进程只允许一个活动会话, provider 侧不排队.
- 取消, 超时, callback 死亡和需要隔离的关闭路径会淘汰专用进程, 且不会自动重放脚本.

******

### 运行时和数据格式

******

协议 V1 当前声明以下范围:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

构建请求 Python 3.13. 3.13.9 是根据当前 Chaquopy 发布信息记录的预期打包版本, 在 APK 解析和设备执行完成前不作为已验证事实.

******

### 插件接口

******

宿主通过以下标识发现并调用插件:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

插件只接收 SOURCE 描述符. workspace archive 与 stdin snapshot 的限制均为零, 也不向脚本注入 Context, Binder, 宿主运行时对象或 callback sink.

******

### 宿主集成状态

******

> 协议与宿主接线路线图正在推进, 但本仓库所需的 release AAR 尚未发布和校验. 仅安装当前 scaffold 不能建立可用的端到端 Python 引擎.

******

### 安全性和隐私

******

源码 manifest 不请求 Android 权限. Exported service 要求宿主签名权限, 并在 Binder 入口复核调用 UID, 已安装宿主包和当前签名集合. Python 通过 Chaquopy 仍可访问 Java bridge, 因此本插件依赖独立 Android UID, 专用进程和窄 Binder 能力边界. 明确边界为 `does not claim that Python code is sandboxed`.

******

### 运行限制

******

- 源码最大 4 MiB, 总输出最大 4 MiB, 单个输出 chunk 最大 16 KiB, 最多 4096 个 chunk.
- 请求超时最大 60 s, 同一进程最多一个活动会话, provider 侧不排队.
- SOURCE 描述符采用 Binder 接收端完整 PFD 所有权, 保留 reliable-pipe 错误通道, 并在终态或关闭时释放.
- 输出当前先在插件内有界缓冲, 再按 credit 发送; 尚不声明执行期间的流式背压.
- 取消模式为进程重启, 不是 CPython 级协作取消; 原生扩展或阻塞调用仍需后续 Android 验证.
- stdlib-only 策略禁止在线 pip 和第三方 Python 包, 合并后的 APK 权限仍须由构建门禁复核.

******

### 未声明的能力

******

- 不支持 workspace archive, stdin snapshot, 在线 pip 或运行时下载 wheel.
- 不提供 UI 脚本, 调试器, REPL 或任意宿主 Java 对象访问.
- 不提供 AutoJs6 能力 broker; console, 文件, 设备, 辅助功能, shell 等宿主 API 尚未接入.
- 不声明 32 位 Android 支持, 也不保证任意第三方 native wheel 可用.
- 不把本机 CPython 单元测试当作 Chaquopy, Android, Binder 或设备验收证据.

******

### 路线图

******

R2 的独立仓库, 静态边界, provider/bootstrap 源码和本机语义测试已落地. 因 QV710AF65F 正在进行受保护 soak, 所有 Gradle 与 ADB 工作暂缓. release AAR, 依赖解析, Android 编译, APK/16 KB page 检查, Binder/PFD 验证和设备矩阵仍未完成; 勾选状态以项目路线图为准.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本历史

******

# v0.1.0-alpha.1

###### 2026/08/09

* `提示` R2 概念验证源码. Gradle, APK, Binder 和设备验收尚未执行
* `新增` 独立 Python 协议 V1 provider scaffold, 专用运行时进程, 单活动会话和零 provider 队列
* `新增` 单源码 `__main__` 执行, 有界 stdout/stderr, 结构化异常以及进程重启式取消
* `新增` 固定顺序的 10 种语言 README 与应用内更新日志生成流程
* `依赖` 预选 Chaquopy 17.0.0 与 Python 3.13; 打包版本和依赖哈希仍待构建验证

##### 更多版本

* [CHANGELOG-zh-Hans.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hans.md)

******

### 验证

******

不调用 Gradle 或 ADB 的文件系统静态检查:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

使用本机 CPython 运行可移植 bootstrap 语义测试:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

这两项检查都不能证明 Android runtime 可用. Gradle, APK, Binder 与设备验证必须在受保护 soak 完成后单独补齐.

******

### 构建

******

当前不运行构建. Release 配置会在协议 AAR 缺失或 SHA-256 尚未锁定时 fail closed.

构建前必须在仓库 `libs` 目录暂存并锁定以下 release AAR:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

运行时计划通过 Maven 使用 Chaquopy 17.0.0, 仅打包 stdlib. 依赖校验元数据, native 库清单, 许可证义务和 16 KB page 兼容性仍是构建验收项.

******

### 许可证

******

项目源码使用 MPL-2.0. Chaquopy, CPython 和其他第三方组件继续适用各自的许可证.

******

### 资源布局

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` 从固定顺序的 JSON 源生成 10 种语言的 README 与应用内更新日志. Android 字符串由各自资源目录管理.

******

### 链接

******

- AutoJs6 文档: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
