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
- 为 `input()` 接收最大 1 MiB 的有限预置 stdin snapshot; 不提供实时交互式 prompt/reply.
- 按原始顺序收集 stdout 和 stderr, 再通过有界 chunk 与 credit 传送.
- 返回 `SystemExit`, 语法错误和运行时异常, 包括有界结构化 traceback.
- 同一运行时进程只允许一个活动会话, provider 侧不排队.
- Host 无需重启; 安装或重新启用插件后下一次新执行会重新发现并 pin provider 身份, 在途 Binder death 会终止该执行且绝不自动重放.

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
protocol: 1.0-1.1
```

插件接收独立 SOURCE, 可选的有界 workspace archive, 最大 1 MiB 的有限预置 stdin snapshot, 以及协议 1.1 的只读宿主能力快照. stdin 不是实时交互通道; 插件不会向脚本注入 Context, Binder, 宿主运行时对象或 callback sink.

******

### 宿主集成状态

******

> 0.1.0 仅与 AutoJs6 6.8.0 配对, 最低 Host versionCode 已冻结并强制为 5275; 最终 clean Host 源码修订和三件 AAR distribution manifest 已写入 lock. 每次新执行都会重新发现 provider; 缺失或禁用时提示安装或启用且绝不 fallback, 安装或重新启用后无需重启 Host. 稳定 APK 身份与该精确 Plugin 源码和 Host lock 绑定.

```text
release target: 0.2.0-alpha.1
release state: post-0.1 U1 clean-source alpha candidate; live stdin interaction is unavailable; U1-R1 E3 exists only when a matching canonical PASS report binds the exact Host/Plugin artifacts tested on QV710AF65F/API 31/arm64; it is not published and does not establish device-matrix, release, or public evidence; prior 0.1.0 artifacts do not cover U1
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- 源码最大 4 MiB, 总输出最大 4 MiB, 单个输出 chunk 最大 16 KiB, 最多 4096 个 chunk.
- 请求超时最大 60 s, 同一进程最多一个活动会话, provider 侧不排队.
- SOURCE 描述符采用 Binder 接收端完整 PFD 所有权, 保留 reliable-pipe 错误通道, 并在终态或关闭时释放.
- 输出当前先在插件内有界缓冲, 再按 credit 发送; 尚不声明执行期间的流式背压.
- 取消模式为进程重启, 不是 CPython 级协作取消; 原生扩展或阻塞调用仍需后续 Android 验证.
- stdlib-only 策略禁止在线 pip 和第三方 Python 包, 合并后的 APK 权限仍须由构建门禁复核.

******

### 未声明的能力

******

- 不提供实时交互式 stdin; 仅支持最大 1 MiB 的有限预置 snapshot. 仍不支持 workspace 写回, 在线 pip 或运行时下载 wheel.
- 不提供 UI 脚本, 调试器, REPL 或任意宿主 Java 对象访问.
- 不提供实时 AutoJs6 能力 broker; 首批 API 仅使用执行启动时冻结的 app/device/execution/project 快照和插件私有 workspace 的有界只读文件接口.
- 不声明 32 位 Android 支持, 也不保证任意第三方 native wheel 可用.
- arm64-v8a 有 API 31 真机证据; x86_64 当前仅有打包证据, 不冒充设备执行或完整设备矩阵.

******

### 路线图

******

R6-P2/P3 的本地 RC 与集中设备证据保留为历史记录. 本次 clean VERSION_BUILD=11 freeze commit 固定了稳定 Plugin 源码身份和精确 Host 6.8.0/5275 lock; 稳定 APK provenance 按这些精确身份核验, 任何 production receipt 也必须使用相同依据. 完整 API×ABI 矩阵和新 soak 不作为自动门禁.

- [查看 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本历史

******

# v0.2.0-alpha.1

###### 2026/08/13

* `提示` 0.1 后的 U1 clean-source alpha 候选; 不提供实时 stdin 交互, U1-R1 E3 验收仅由与 QV710AF65F/API 31/arm64 上 exact Host/Plugin artifacts 匹配的 canonical PASS report 表示, 不属于设备矩阵/发布/公开证据
* `新增` 新增最大 1 MiB 的有限预置 stdin snapshot, 为 `input()` 与 `sys.stdin` 提供确定性输入和 EOF
* `新增` 完善项目导入语义, 支持 workspace 模块, 嵌套入口同级与根模块以及 package-relative import
* `修复` 执行前按 strict UTF-8 解码源码, 非 UTF-8 encoding cookie 不再绕过契约
* `优化` 每次执行使用独立 `__main__`, 并恢复 stdin/stdout/stderr, argv, cwd, `sys.path`, module 与 importer cache 状态
* `优化` 为已打开但未 start 的 session 增加 5 秒 lease, 到期释放输入, descriptor 与单会话占位
* `优化` Provider 在 Binder 入站强制最低 Host versionCode 5275, 不再只依赖 Host 侧发现检查

# v0.1.0

###### 2026/08/12

* `提示` 0.1.0 固定了稳定 Plugin 源码身份和精确 Host 6.8.0/5275 lock
* `新增` 面向 AutoJs6 6.8.0 / versionCode 5275 的 Python 协议 1.0-1.1, 有界项目 workspace 与只读 app/device/execution/project 能力快照
* `新增` 无需重启 Host 的热插拔: 安装或重新启用后下次新执行重新发现并 pin 身份, 缺失或禁用绝不 fallback
* `新增` 在途 Binder death 终止当前执行且不得重放, 后续新执行重新发现 provider
* `优化` 将 Chaquopy 固定为 trusted-local, non-sandbox 运行时; SM003 为长期 signer, SuperMonster003 为 runtime/security/release owner
* `依赖` 锁定 Chaquopy 17.0.0 与 CPython 3.13.9; 稳定 APK 与最终源码身份绑定并通过精确产物验证

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

运行时通过 Maven 锁定 Chaquopy 17.0.0 与 CPython 3.13.9, 仅打包 stdlib. Release gate 按精确身份核对依赖校验元数据, native 库, NOTICE, SM003 signer 和三种发行 APK; 16 KB page 兼容性当前没有专用 gate, 不作为已核验声明.

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
