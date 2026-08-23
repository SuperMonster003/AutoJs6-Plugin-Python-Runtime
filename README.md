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

> 0.1.0 源码身份和精确 Host lock 已冻结. 既有本地 RC 的构建, APK, Binder 和一台 API 31 arm64-v8a 设备证据仍是历史证据; 稳定 APK/P3 provenance 与精确 release identity 绑定, production receipt 是发布后的独立证据层级.

******

### 功能

******

- 将一个 UTF-8 Python 源码快照作为 `__main__` 执行.
- 接收最大 1 MiB 的有限预置 stdin snapshot; 快照到达 EOF 后, 显式前台启动可通过协议 1.3 的有界 prompt/reply 继续内置 `input()`, 且标准库 `getpass.getpass()` 使用隐藏回显.
- 为已准入项目显式选择 `entryMode=file|module`; module 模式使用标准 `runpy` 元数据、项目根目录 `sys.path[0]` 与包相对导入, file 模式保持普通脚本语义.
- 在脚本执行期间按 stdout/stderr 原始顺序通过有界 chunk 与 credit 传送; credit 耗尽会对执行施加背压.
- 通过协议 1.4 显式设置最大 64 KiB 的严格 JSON 结果, 并传送最多 16 个具有路径、大小与 SHA-256 限制的可选输出 artifact; 绝不从 stdout 推断结果.
- 通过协议 1.5 的执行级纯数据 broker 实时调用 `toast`、`clip.get/set`、`app.launch/launch_app/open_url`、`device.info`、`console.log/warn/error` 与权限感知 `notice`, 终态后自动撤销.
- 返回 `SystemExit`, 语法错误和运行时异常, 包括有界结构化 traceback.
- 同一运行时进程只允许一个活动会话, provider 侧不排队.
- Host 无需重启; 安装或重新启用插件后下一次新执行会重新发现并 pin provider 身份, 在途 Binder death 会终止该执行且绝不自动重放.

******

### 运行时和数据格式

******

协议 V1 当前声明以下范围:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

构建请求 Python 3.13. 已冻结的本地 RC 产物与精确设备执行记录为 CPython 3.13.9; 最终 0.1.0 在源码冻结后仍须重新核验版本和哈希.

******

### 插件接口

******

宿主通过以下标识发现并调用插件:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.5
```

插件接收独立 SOURCE, 可选的有界 workspace archive, 最大 1 MiB 的有限预置 stdin snapshot, 以及协议 1.1 的只读宿主能力快照. 协议 1.2 为已准入项目增加显式 file/module 入口协商. 协议 1.3 在快照 EOF 后为内置 `input()` 增加由 Host 持有且仅限前台的 prompt/reply; 标准库 `getpass.getpass()` 使用隐藏回显. 协议 1.4 增加显式严格 JSON 结果与可选的 SHA-256 manifest 输出 artifact, stdout 仅用于诊断且绝不被解析为结果. 协议 1.5 增加绑定单次执行、插件 UID、调用序号与配额的纯数据 Host capability broker. 直接 `sys.stdin` 始终有限, 后台启动绝不打开输入 UI, 用户脚本也不会得到 Context、原始 Binder、宿主运行时对象或 callback sink.

******

### 宿主集成状态

******

> 0.1.0 仅与 AutoJs6 6.8.0 配对, 最低 Host versionCode 已冻结并强制为 5275; 最终 clean Host 源码修订和三件 AAR distribution manifest 已写入 lock. 每次新执行都会重新发现 provider; 缺失或禁用时提示安装或启用且绝不 fallback, 安装或重新启用后无需重启 Host. 稳定 APK 身份与该精确 Plugin 源码和 Host lock 绑定.

```text
release target: 0.3.0-alpha.2
release state: 0.3.0-alpha.2 current-tree candidate; M1 and M2 are complete, and the complete first low-risk protocol 1.5 Host capability slice passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3 batches, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### 安全性和隐私

******

Chaquopy 运行时只面向可信本地脚本, 不是 hostile-code sandbox. Exported service 要求宿主签名权限并复核 UID, 包和 signer; 独立 Android UID, 专用进程和窄 Binder 边界降低宿主暴露, 但不让 Python 成为沙箱. SM003 是长期发行 signer, SuperMonster003 承担 runtime, security 与 release owner.

******

### 运行限制

******

- 源码最大 4 MiB, 总输出最大 16 MiB, 单个输出 chunk 最大 16 KiB, 最多 16384 个 chunk.
- 请求超时最大 30 min, 同一进程最多一个活动会话, provider 侧不排队.
- SOURCE 描述符采用 Binder 接收端完整 PFD 所有权, 保留 reliable-pipe 错误通道, 并在终态或关闭时释放.
- 输出在执行期间按 credit 逐 chunk 发送; credit 耗尽会暂停脚本, 已接受的输出先于唯一终态, 终态后禁止输出.
- 结构化 JSON 最大 64 KiB; 输出 artifact 最多 16 个, 路径最大 1024 UTF-8 bytes, 单个最大 4 MiB, 合计最大 8 MiB, Host 必须核对精确长度、EOF 与 SHA-256.
- 协议 1.5 每次执行最多 1024 次 Host 调用, 单个请求/响应最大 64 KiB, 文本最大 32 KiB, 单次 Host 调度等待最多 5 s.
- 取消模式为进程重启, 不是 CPython 级协作取消; 原生扩展或阻塞调用仍需后续 Android 验证.
- 插件已授予 `INTERNET` 以支持脚本通过标准库直接联网; 仍不支持在线 pip、自动下载代码或运行时安装第三方包.

******

### 未声明的能力

******

- 不提供通用实时 stdin 或直接 `sys.stdin` callback streaming. 前台交互仅适用于最大 1 MiB 的有限 snapshot 到达 EOF 后的内置 `input()` 与标准库 `getpass.getpass()`. 仍不支持 workspace 写回, 在线 pip 或运行时下载 wheel.
- 不提供 UI 脚本, 调试器, REPL 或任意宿主 Java 对象访问.
- 实时 broker 已覆盖完整首批低风险能力; 文件、对话框、无障碍、截图及 OCR 仍未声明.
- 不声明 32 位 Android 支持, 也不保证任意第三方 native wheel 可用.
- 当前树已有 API 31 arm64-v8a 真机冒烟证据与 API 37 x86_64 16 KB page 模拟器冒烟证据; 两者都不冒充完整设备矩阵或发布资质.

******

### 路线图

******

R6-P2/P3 的本地 RC 与集中设备证据保留为历史记录. 本次 clean VERSION_BUILD=11 freeze commit 固定了稳定 Plugin 源码身份和精确 Host 6.8.0/5275 lock; 稳定 APK provenance 按这些精确身份核验, 任何 production receipt 也必须使用相同依据. 完整 API×ABI 矩阵和新 soak 不作为自动门禁.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本历史

******

# v0.3.0-alpha.2

###### 2026/08/23

* `提示` M3 第二个 current-tree alpha 候选; 完整首批低风险 Host 能力已实现, 后续能力批次、公开发布和完整设备矩阵仍不在本条声明范围内
* `新增` 新增实时 `autojs6.device.info()` 电量/屏幕/亮度/音量数据、`autojs6.console.log/warn/error` 宿主控制台级别及 `autojs6.notice` 通知
* `优化` 严格校验 device 结果结构, 通知权限不足时稳定返回 `PERMISSION_DENIED`, 不打开设置或更改设备权限状态

# v0.3.0-alpha.1

###### 2026/08/23

* `提示` M3 首个 current-tree alpha 候选; 协议 1.5 与低风险 Host 能力子集已实现, 后续能力、发布和完整设备矩阵仍不在本条声明范围内
* `新增` 新增协议 1.5 执行级 Host capability broker, 以纯数据 JSON 绑定 request UUID、插件 UID、单调调用序号、1024 次配额、64 KiB 消息及 5 秒 Host 调度上限
* `新增` 新增 `autojs6.toast`, `autojs6.clip.get/set` 与 `autojs6.app.launch/launch_app/open_url` 实时 Host API
* `优化` 终态、取消、Binder death 与清理路径统一撤销 broker, Python 侧稳定映射 capability unavailable、Host 与协议错误

# v0.2.0-alpha.1

###### 2026/08/13

* `提示` 0.1 后的 U1 current-tree alpha 候选; U1-R2 module entry、live output、前台内置 input、显式结构化 JSON 与有界输出 artifact 仅完成到 E2, 后台启动与直接 sys.stdin 仍非交互, R2 E3 仍未完成, 且这些当前树结果不属于设备矩阵/发布/公开证据
* `新增` 新增最大 1 MiB 的有限预置 stdin snapshot, 为 `input()` 与 `sys.stdin` 提供确定性输入和 EOF
* `新增` 完善项目导入语义, 支持 workspace 模块, 嵌套入口同级与根模块以及 package-relative import
* `新增` 新增协议 1.2 显式 `entryMode=file|module`; module 执行通过 `runpy` 提供正确的 `__package__`、`__spec__`、项目根目录 `sys.path[0]` 与相对导入, file 模式保持不变
* `新增` 新增协议 1.3: 有限 snapshot 到达 EOF 后, 仅前台内置 `input()` 使用可见回显、标准库 `getpass.getpass()` 使用隐藏回显的有界 prompt/reply; 后台启动绝不打开输入 UI, 直接 `sys.stdin` 始终有限
* `新增` 新增协议 1.4 显式严格 JSON 结果与可选输出 artifact, 对数量、规范化路径、单个/合计大小、精确 PFD 引用及 SHA-256 设限, 且绝不从 stdout 推断结果
* `修复` 执行前按 strict UTF-8 解码源码, 非 UTF-8 encoding cookie 不再绕过契约
* `优化` 授予 `INTERNET`, 让可信脚本可直接使用标准库网络客户端, 同时仍禁用在线 pip 与自动代码下载
* `优化` 将 Provider 执行上限提高到 30 分钟, 有界输出提高到 16 MiB / 16384 个 chunk
* `优化` 将 stdout/stderr 的有界 chunk 与 credit 背压前移到脚本执行期间, 保留终态前的有序部分输出并禁止终态后输出
* `优化` 每次执行使用独立 `__main__`, 并恢复 stdin/stdout/stderr, argv, cwd, `sys.path`, module 与 importer cache 状态
* `优化` 为已打开但未 start 的 session 增加 5 秒 lease, 到期释放输入, descriptor 与单会话占位
* `优化` Provider 在 Binder 入站强制最低 Host versionCode 5275, 不再只依赖 Host 侧发现检查

##### 更多版本

* [CHANGELOG-zh-Hans.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hans.md)

******

### 验证

******

不调用 Gradle 或 ADB 的文件系统静态检查:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

使用本机 CPython 运行可移植 bootstrap 语义测试:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

静态和本机 CPython 检查不能替代 Android 证据. 既有本地 RC 与单设备结果是历史证据; release acceptance 使用与精确身份直接绑定的构建, APK, Binder 和代表性设备验证.

******

### 构建

******

文档生成本身不运行构建. Release 配置在协议 AAR, SHA-256, signer 或运行时锁漂移时 fail closed; 稳定产物仅在绑定精确 release identity 时被接受.

构建前必须在仓库 `libs` 目录暂存并锁定以下 release AAR:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

运行时通过 Maven 锁定 Chaquopy 17.0.0 与 CPython 3.13.9, 仅打包 stdlib. Release gate 按精确身份核对依赖校验元数据, native 库, NOTICE, SM003 signer 和三种发行 APK. 当前树已通过 API 37 x86_64 16 KB page 模拟器的聚焦冒烟; 这不等同于完整兼容性 gate 或设备矩阵声明.

******

### 许可证

******

项目源码使用 MPL-2.0. Chaquopy, CPython 和其他第三方组件继续适用各自许可证; 归属, 上游源码与本项目源码获取说明见 `THIRD_PARTY_NOTICES.md`.

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
