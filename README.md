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
- 从已准入项目根目录 import 项目本地纯 Python 包与 `.dist-info` 元数据, 无需在线 pip 或运行时安装.
- 在脚本执行期间按 stdout/stderr 原始顺序通过有界 chunk 与 credit 传送; credit 耗尽会对执行施加背压.
- 通过协议 1.4 显式设置最大 64 KiB 的严格 JSON 结果, 并传送最多 16 个具有路径、大小与 SHA-256 限制的可选输出 artifact; 绝不从 stdout 推断结果.
- 通过协议 1.5 的执行级纯数据 broker 实时调用 `toast`、`clip.get/set`、`app.launch/launch_app/open_url`、`device.info`、`console.log/warn/error`、权限感知 `notice`、有界 `files.read_text/write_text/exists/is_file/is_dir/list`、仅限前台的 `dialogs.alert/confirm/prompt/select`、`engines.current/run/stop_self` 与有界 `automator.click/long_click/press/swipe/back/home`, 终态后自动撤销.
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

插件接收独立 SOURCE, 可选的有界 workspace archive, 最大 1 MiB 的有限预置 stdin snapshot, 以及协议 1.1 的只读宿主能力快照. 协议 1.2 为已准入项目增加显式 file/module 入口协商. 协议 1.3 在快照 EOF 后为内置 `input()` 增加由 Host 持有且仅限前台的 prompt/reply; 标准库 `getpass.getpass()` 使用隐藏回显. 协议 1.4 增加显式严格 JSON 结果与可选的 SHA-256 manifest 输出 artifact, stdout 仅用于诊断且绝不被解析为结果. 协议 1.5 增加绑定单次执行、插件 UID、调用序号与配额的纯数据 Host capability broker. Host 对话框还要求由存活 Activity 支撑的前台授权; 后台启动不会打开 UI, 而是稳定返回 `INTERACTIVE_NOT_ALLOWED`. 直接 `sys.stdin` 始终有限, 后台启动绝不打开输入 UI, 用户脚本也不会得到 Context、原始 Binder、宿主运行时对象或 callback sink.

******

### 宿主集成状态

******

> 0.1.0 仅与 AutoJs6 6.8.0 配对, 最低 Host versionCode 已冻结并强制为 5275; 最终 clean Host 源码修订和三件 AAR distribution manifest 已写入 lock. 每次新执行都会重新发现 provider; 缺失或禁用时提示安装或启用且绝不 fallback, 安装或重新启用后无需重启 Host. 稳定 APK 身份与该精确 Plugin 源码和 Host lock 绑定.

```text
release target: 0.4.0-alpha.1
release state: 0.4.0-alpha.1 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator coordinate/global actions passed on the accessibility-enabled emulator, and physical-device fail-closed acceptance passed without changing its accessibility services; later M3/M4 batches, a complete device matrix, publication, and release evidence remain outside this claim
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
- 项目 workspace 上限为压缩后 64 MiB、8192 个文件条目及解压后 128 MiB; 分发前 Provider 选择必须同时满足快照的实际三维需求.
- SOURCE 描述符采用 Binder 接收端完整 PFD 所有权, 保留 reliable-pipe 错误通道, 并在终态或关闭时释放.
- 输出在执行期间按 credit 逐 chunk 发送; credit 耗尽会暂停脚本, 已接受的输出先于唯一终态, 终态后禁止输出.
- 结构化 JSON 最大 64 KiB; 输出 artifact 最多 16 个, 路径最大 1024 UTF-8 bytes, 单个最大 4 MiB, 合计最大 8 MiB, Host 必须核对精确长度、EOF 与 SHA-256.
- 协议 1.5 每次执行最多 1024 次 Host 调用, 单个请求/响应最大 64 KiB, 文本最大 32 KiB, 普通 Host 主线程动作等待最多 5 s. Host files 使用最大 4 KiB 的相对路径、最大 32 KiB 的 UTF-8 文本, 每次最多枚举 128 个名称, 每个最大 255 UTF-8 bytes. 前台对话框标题最大 256 UTF-8 bytes, 正文最大 4 KiB, prompt 默认值/回复最大 32 KiB, select 最多 64 项、每项最大 1 KiB、合计最大 32 KiB, 单次用户响应最多等待 5 min. 每次执行最多成功异步启动 16 个限定根目录内的非 Python Host 子脚本; 嵌套 Python 返回 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self` 通过进程重启取消自身.
- Automator 坐标仅接受 0 到 1000000 的严格整数, press 与 swipe 持续时间为 1 ms 到 4 s; 宿主无障碍不可用时抛 `CapabilityUnavailableError`, 不打开设置.
- 取消模式为进程重启, 不是 CPython 级协作取消; 原生扩展或阻塞调用仍需后续 Android 验证.
- 插件已授予 `INTERNET` 以支持脚本通过标准库直接联网; 仍不支持在线 pip、自动下载代码或运行时安装第三方包.

******

### 未声明的能力

******

- 不提供通用实时 stdin 或直接 `sys.stdin` callback streaming. 前台交互仅适用于最大 1 MiB 的有限 snapshot 到达 EOF 后的内置 `input()` 与标准库 `getpass.getpass()`. 仍不支持 workspace 写回, 在线 pip 或运行时下载 wheel.
- 不提供 UI 脚本, 调试器, REPL 或任意宿主 Java 对象访问.
- 实时 broker 已覆盖完整首批低风险能力、有界 Host files、前台对话框、有界 engines 及显式坐标/全局 automator 动作; selector/UI 树、截图及 OCR 仍未声明.
- 不声明 32 位 Android 支持, 也不保证任意第三方 native wheel 可用.
- 当前树已有 API 31 arm64-v8a 真机冒烟证据与 API 37 x86_64 16 KB page 模拟器冒烟证据; 两者都不冒充完整设备矩阵或发布资质.

******

### 路线图

******

M4 路径 A 已完成, M3 自动化已通过宿主无障碍接通有界坐标手势及返回/主页动作. selector/UI 树、截图、OCR 与 M4 构建期/native 包路径继续按用户价值推进; 历史证据工具保留但不作为自动发布门禁.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本历史

******

# v0.4.0-alpha.1

###### 2026/08/23

* `提示` 首个 M3 自动化 current-tree alpha 候选; 有界坐标/全局动作已在启用无障碍的 API 37 模拟器通过聚焦验收, API 31 物理机在不改变既有无障碍服务的前提下通过 fail-closed, selector/UI 树、截图、OCR、发布与完整设备矩阵不在本次声明范围
* `新增` 新增经宿主无障碍执行的实时 `autojs6.automator.click/long_click/press/swipe/back/home` API, 返回动作实际分发结果布尔值
* `优化` 坐标只接受 0 到 1000000 的非布尔严格整数, press/swipe 持续时间只接受 1 到 4000 ms; 宿主无障碍不可用时抛 `CapabilityUnavailableError`, 不打开设置

# v0.3.0-alpha.6

###### 2026/08/23

* `提示` 首个 M4 current-tree alpha 候选; 项目本地纯 Python 依赖路径已通过双设备聚焦验收, 后续 M3/M4 批次、发布及完整设备矩阵不在本次声明范围
* `新增` 支持从已准入项目根目录导入项目本地纯 Python 包与 `.dist-info` 元数据, 提供锁定版本的 `requests` 可复现示例, 且不引入运行时安装器
* `优化` 将项目 workspace 上限提高到压缩 64 MiB、8192 个文件条目与解压 128 MiB, 分发前按快照实际三维需求匹配 Provider 能力; 缺失 import 仍抛 `ModuleNotFoundError`, 不触发在线 pip 或引擎回落

# v0.3.0-alpha.5

###### 2026/08/23

* `提示` M3 第五个 current-tree alpha 候选; 第二批有界 Host engines 能力已通过双设备聚焦验收, 后续能力、公开发布和完整设备矩阵仍不在本条声明范围内
* `新增` 新增实时 `autojs6.engines.current/run/stop_self` API, 提供不含绝对路径的当前引擎信息、非 Python Host 子脚本异步启动及确定性停止自身
* `优化` 子脚本仅接受执行根目录内的规范化相对路径且每次执行最多成功启动 16 个; 嵌套 Python 稳定返回 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self` 通过 provider 进程重启取消当前执行

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
