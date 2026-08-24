# Python Runtime 插件 Roadmap

> 初衷: 让 AutoJs6 用户 "装上插件就能流畅运行 Python 脚本", 并逐步获得与 JS 脚本对等的
> AutoJs6 自动化 API 能力。本 Roadmap 以用户可感知的能力为主线, 逐项可勾选、可落地。
>
> 开发哲学: **先让脚本跑起来, 快速迭代, 出现异常就修复异常。**
> 不追求一次性完美方案, 不用无休止的测试与安全边界堆砌代码, 不把验证流程当作产品本体。
> 协议既有的进程隔离、fail-closed、有界传输等骨架保持不变 (它们已被真机验证且不妨碍迭代),
> 但**新能力不再以证据链流程为前置门槛**。
>
> 仓库标注: `[P]` = 本插件仓库; `[H]` = 宿主 AutoJs6 仓库 (D:\idea-projects\AutoJs6);
> `[H+P]` = 双仓协同 (通常涉及协议 AAR 更新)。
>
> 历史 U1 路线图 (英文, 证据等级驱动) 已归档至
> [docs/legacy/ROADMAP-u1-en.md](docs/legacy/ROADMAP-u1-en.md), 其既有结论与真机证据继续有效,
> 但不再约束后续开发节奏。

******

## 基线: 当前已具备的能力 (截至 0.4.0-alpha.8 current tree, 均有代码与本地构建门禁支撑)

### 运行时与执行

- [x] 独立插件 APK 与专用 `:python_runtime` 进程运行 CPython 3.13.9 (Chaquopy 17.0.0),
  支持 arm64-v8a 与 x86_64, 宿主进程零 Python 加载。
- [x] 单文件脚本执行 (file 模式): 严格 UTF-8 源码, 正确的 `__name__`/`__file__`/`sys.argv`,
  独立 `__main__`, 执行后完整还原解释器状态 (modules/path/cwd/stdio/importer cache)。
- [x] Python 项目执行: 项目打包为 workspace zip (归档 ≤64 MiB, 解压 ≤128 MiB, ≤8192 条目)
  传入插件私有目录; 入口同级与项目根导入、常规/命名空间包、相对导入、循环导入均可用。
- [x] module 入口模式 (`python -m` 语义, 协议 1.2): `runpy` 执行, 正确的
  `__package__`/`__spec__`/`sys.path[0]` —— 插件侧完整, 宿主暂未暴露入口 (见 M2)。
- [x] 完整 CPython 标准库随包可用; 已准入项目可随 workspace 携带纯 Python 包与
  `.dist-info` 元数据; 缺失的第三方包仍按标准语义抛 `ModuleNotFoundError`。
- [x] stdin 快照 (≤1 MiB, 协议 1.1): 支撑 `input()` 与 `sys.stdin.read*()` 的确定性输入
  —— 插件侧完整, 宿主暂无写入 UI (见 M2)。
- [x] 前台交互式 `input()` (协议 1.3): 快照 EOF 后经宿主 MaterialDialog 弹框继续输入,
  后台启动立即报错而非挂起。
- [x] 执行期流式输出协议 (chunk + credit 背压, 协议 1.1): 插件在脚本运行期间逐块发送
  stdout/stderr, 宿主按流增量解码 UTF-8 并即时写入控制台。
- [x] 结构化 JSON 结果 (`autojs6.result.set`, ≤64 KiB) 与输出产物
  (`autojs6.artifacts.path`, ≤16 个 / 合计 ≤8 MiB, SHA-256 校验, 协议 1.4)
  —— 插件侧完整, 宿主已在控制台展示结果并安全发布产物 (见 M2)。
- [x] 结构化 traceback: project/stdlib/package 来源分类, 行号与源码行, 不泄漏插件私有路径。
- [x] 超时、取消、Binder death 均有确定性唯一终态; 取消模式为进程重启
  (`PROCESS_RESTART_ONLY`); 已 dispatch 的请求绝不自动重放。
- [x] 热插拔: 安装/重新启用插件后下一次执行即可用, 无需重启宿主; 缺失/禁用时提示安装,
  绝不回落到其他引擎。

### 宿主侧已接通入口

- [x] 编辑器运行按钮、文件管理器单文件运行、Explorer 项目工具栏 Run、项目启动器、
  定时任务、Intent (本地 file 路径)、脚本重启。
- [x] `import autojs6` 只读 API: `app.snapshot()` / `device.snapshot()` /
  `execution.snapshot()` / `project.read_text|read_bytes|exists` (项目执行时)。
- [x] 协议 1.5 实时 Host API 完整首批低风险能力: `toast`, `clip.get/set`,
  `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, `notice`;
  每次执行独立 broker, 终态自动撤销。
- [x] 协议 1.5 实时 Host files API: 项目根/单文件脚本目录内的 UTF-8 文本读写、
  存在/类型检查及直接目录枚举; 严格相对路径与容量边界阻止越过执行根目录。
- [x] 协议 1.5 前台 Host dialogs API: `alert/confirm/prompt/select`; 复用 Activity-backed
  前台授权, 后台与定时启动稳定返回 `INTERACTIVE_NOT_ALLOWED` 且不打开 UI。
- [x] 协议 1.5 Host engines API: `current/run/stop_self`; 返回不含绝对路径的纯数据身份,
  仅异步启动执行根内的非 Python Host 脚本, 并以进程重启确定性停止自身。
- [x] 协议 1.5 Host automator 基础动作: `click/long_click/press/swipe/back/home`;
  严格限制坐标与持续时间, 返回平台实际布尔结果, 无障碍不可用时 fail closed 且不打开设置。
- [x] 协议 1.5 Host selector/UI 树: 有界 `snapshot/find/click/set_text`, 节点引用绑定
  单次执行并在失效后返回稳定类型化错误。
- [x] 协议 1.5 Host images: Android 11+ 有界 `capture_screen`、宿主内
  `find_color` 与有界 PNG/JPEG `find_image`; 找色仅返回坐标/未命中, 找图只上传
  执行级模板且不跨进程传输截图字节。
- [x] 单文件脚本 `ModuleNotFoundError` 时提示用户改用显式 Python 项目。

### 真机与构建证据 (历史, 保持有效)

- [x] R1 真机事务 PASS (API 31 / arm64-v8a): stdin PFD、真机 CPython `input()`、项目导入、
  顺序会话隔离与清理。
- [x] R2 功能门禁 (module entry / 流式输出 / 交互输入 / 结构化结果) 本地构建全绿。
- [x] 0.1.0 稳定版已发布 (配对宿主 6.8.0 / versionCode 5275)。

******

## M1 —— 跑得爽: 体验补全 (目标版本 0.2.0)

> 主题: 用户点击运行 .py 后的体验与 JS 脚本一致 —— 实时看到输出, 脚本能跑足够久,
> 停止按钮可靠。全部为存量协议的收尾, 无协议变更, 风险低。

- [x] [H] **控制台实时输出实现**: `PythonRuntimeClient.acceptOutput` 收到 chunk 后即时写入
  GlobalConsole (stdout→INFO, stderr→ERROR), stdout/stderr 各自使用增量 UTF-8 解码器保留
  跨 chunk 码点, 终态只排空截断尾字节, 不再重复输出。宿主提交: `b1b6b43d0`。
- [x] [H+P] **控制台实时输出真机验收**: 90 s 内每秒 `print(..., flush=True)` 一次,
  第 3 个 tick 出现时执行尚未终止, `tick:0` 到 `tick:89` 与结尾标记均到达控制台。
- [x] [P] **放宽执行超时**: `maxTimeoutMillis` 60 s → 30 min (宿主当前请求 5 min,
  双向取小后立即生效为 5 min)。
- [x] [H+P] **长时脚本真机验收**: 配置 120 s 超时的 90 s 脚本完整运行并成功终止。
- [x] [H] **超时可配置**: Python 项目 `project.json` 支持可选正整数 `timeout` 字段
  (毫秒); 默认 5 min, 宿主上限 30 min, 并继续与插件能力上限取小。宿主提交:
  `2f0f766e1`。
- [x] [H+P] **停止按钮真机冒烟**: 宿主停止运行中的 Python 脚本 → cancel → 插件进程重启,
  紧接着再次运行成功; 冒烟测试同时确认两次执行的插件 PID 不同。
- [x] [H+P] **放宽输出上限**: 总输出 4 MiB → 16 MiB, chunk 数 4096 → 16384;
  插件 metadata 与宿主默认策略已对齐。
- [x] [H+P] **长日志真机验收**: 4.25 MiB stdout 完整计数, 尾标记到达控制台并正常终止。
- [x] [H] **后台输入冒烟**: 无前台交互授权时调用 `input()` 在约 1 s 内以带 traceback 的
  `EOFError` 结束, 不弹框、不挂起。
- [x] [H] **定时任务入口冒烟**: 宿主定时任务调度器在物理设备 `QV710AF65F`
  实际触发一个 .py 项目并正常终止。
- [x] [P] **插件 manifest 增加 `INTERNET` 权限**: 解锁 Python 标准库
  `urllib.request`/`socket`/`http.client` 的直接联网能力, 零协议改动,
  立即满足 "脚本内发 HTTP 请求" 这一高频需求; 源 manifest 与合并/打包 manifest
  均已确认只声明一次该权限。
- [x] [P] **标准库联网真机验收**: `urllib.request.urlopen('https://...')` 经 CPython SSL
  栈读取 HTTPS 200 响应成功。
- [ ] [H+P] 以上完成后发布 **0.2.0** (双 ABI + universal APK, 真机冒烟清单通过即发)。

### 2026-08-23 M1 真机与模拟器冒烟记录

- 物理设备: Sony XQ-AT72, API 31 / arm64-v8a / 4 KiB page; 补充模拟器:
  API 37 / x86_64 / 16 KiB page。两者均使用 canonical AutoJs6 6.8.0
  (`versionCode=5276`) + Python Runtime 0.2.0-alpha.1 (`versionCode=14`), 同一 SM003 签名。
- 公共路径: `project.json` 严格准入 → `ScriptEngineService` → `PythonPluginScriptEngine` →
  实际插件 Binder/PFD 会话 → `GlobalConsole`, 没有直接调用插件内部测试接口。
- 两套环境均 PASS: 逐秒实时输出 + 90 s 长任务、4.25 MiB stdout、标准库 HTTPS、
  停止后 PID 更新并立即重跑、无前台授权的 `input()` 明确 `EOFError`、
  协议 1.4 结构化 JSON 与二进制产物回归。
- 用户补充确认物理设备 `QV710AF65F` 的定时任务调度器已实际触发 .py 项目并成功终止，
  M1 的功能实现与入口冒烟项至此全部完成。
- 冒烟过程中修复了一个真实异常: 成功脚本未调用 `autojs6.result.set()` 时,
  Python `None` 曾被 Chaquopy Map 解码误判为字段缺失; 插件提交 `cf516c7` 已修复。

******

## M2 —— 半成品收尾: 已实现协议的宿主入口 (目标版本 0.2.x)

> 主题: 插件侧早已实现、但宿主没有入口或没有消费的通道, 逐个接通。全部为宿主侧改动。

- [x] [H] **module 入口模式暴露**: Python 项目 `project.json` 支持声明 module 入口
  (如 `"entryMode": "module", "main": "pkg.main"`), 写入 `ENTRY_MODE_ARGUMENT`。
  含相对导入的包项目已在物理设备与 16 KiB page 模拟器以 module 语义运行成功;
  宿主提交: `d3f623217`。
- [x] [H] **stdin 快照入口**: `project.json` 支持 `"stdin"` 字段; JSON 字符串始终表示
  内联文本, `{"file":"fixtures/input.txt"}` 显式表示项目内相对文件, 写入现有
  `STDIN_SNAPSHOT_ARGUMENT`; 单文件脚本暂不提供 UI (需求出现再加)。
  `sys.stdin.read()` 公共路径已在物理设备与 16 KiB page 模拟器以预置输入运行成功;
  宿主提交: `e3a5b6da3`。
- [x] [H] **结构化结果展示**: 脚本终态后, 若存在 `structuredJson`, 在控制台以
  `[result] {...}` 追加展示; 已校验 artifacts 经隐藏 staging 目录整体发布到
  `<项目根或脚本目录>/.python-artifacts/execution-<执行id>-<request UUID>/`,
  并以 `[artifact] <绝对路径>` 打印。保留输出目录不进入后续项目 workspace 快照;
  发布失败不覆盖旧结果且以稳定宿主错误终止。宿主提交: `c4066c8e9`。
- [x] [H+P] **交互式输入多入口冒烟**: 编辑器运行的 `input()` 与 Explorer 运行的
  `getpass.getpass()` 均弹出 Host 输入框; 后者使用密码输入类型且回复不写入全局控制台。
  插件补齐执行局部 `getpass` patch/restore。插件提交: `d8747c3`; 宿主提交:
  `70ea17097`。
- [x] [H] **清理陈旧注释与文档漂移**: `PythonProjectLaunchPolicy` 的历史 workspace
  fail-closed 注释与 `R5_CAPABILITY_PREVIEW.md` 的退役 Gradle flag 已和稳定通道事实对齐;
  宿主提交: `70ea17097`。

### 2026-08-23 M2 module 入口验收记录

- `project.json` 使用 `{"type":"python","entryMode":"module","main":"pkg.main"}`，
  经严格项目准入和统一 Launch 配置写入现有 `autojs6.python.entryMode` 参数。
- 公共宿主路径继续复用协议 1.2 与插件 `runpy.run_module` 实现，没有新增跨进程协议字段。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 与 API 37 /
  x86_64 / 16 KiB page 模拟器均 PASS; 验收覆盖 `__package__`、`__spec__`、包内相对导入、
  结构化 JSON 与二进制 artifact。

### 2026-08-23 M2 stdin 快照入口验收记录

- `project.json` 使用 `"stdin":"literal text"` 声明内联 UTF-8 文本, 或使用
  `"stdin":{"file":"fixtures/input.txt"}` 声明项目内相对文件; 普通字符串绝不猜测为路径,
  显式空字符串保留为零字节快照。
- 文件路径仅接受 NFC 规范化的正斜杠相对路径, 拒绝绝对路径、URI、反斜杠、控制字符、
  `.` / `..`、符号链接、缺失或非普通文件; 单次快照上限与当前插件一致为 1 MiB。
- 宿主在统一 Launch 配置中读取并固定文件字节, 继续复用协议 1.1 stdin PFD 通道,
  没有新增跨进程字段; 私有传输前同时复验 manifest 中的 stdin 声明。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 用时 0.963 秒,
  API 37 / x86_64 / 16 KiB page 模拟器用时 1.503 秒, 均为 `OK (1 test)`;
  验收覆盖项目文件快照、Unicode `sys.stdin.read()`、重复读取 EOF、无交互弹框与传输清理。

### 2026-08-23 M2 结构化结果展示验收记录

- 宿主继续消费协议 1.4 已完成长度、EOF 与 SHA-256 校验的 Host-owned bytes, 没有新增
  跨进程字段; JSON-looking stdout 仍是普通诊断输出, 绝不被推断为显式结果。
- 非空 `structuredJson` 以 `[result]` 前缀写入全局控制台; 每个已发布文件以
  `[artifact] <绝对路径>` 报告, 返回的 `PythonRuntimeExecutionResult` 仍保留防御性字节副本。
- artifact 先写入同级隐藏 staging 目录并复验逻辑路径、长度与摘要, 全部成功后整体重命名;
  目录名同时绑定执行 ID 与协议 request UUID。已有终态目录拒绝覆盖, 路径穿越、前缀冲突、
  中断或文件系统失败均清理 staging 并返回 `PYTHON_RUNTIME_RESULT_PUBLICATION_FAILED`。
- `.python-artifacts` 是宿主保留的顶层输出目录, 后续项目快照会跳过它, 且项目入口不得位于其中。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 用时 0.891 秒,
  API 37 / x86_64 / 16 KiB page 模拟器用时 1.054 秒, 均为 `OK (1 test)`;
  验收覆盖真实插件会话、控制台前缀、二进制字节、用户可见目录与无 staging 残留。

### 2026-08-23 M2 前台交互输入验收记录

- 插件执行期同时临时替换 `builtins.input` 与标准库 `getpass.getpass`; 两者都先消费有限
  stdin snapshot, EOF 后才请求一次有界前台回复。`input()` 使用 visible echo 并把提示写入
  stdout; `getpass.getpass()` 使用 hidden echo 并把提示写入显式 stream 或 stderr。
- 宿主测试直接调用编辑器使用的 `Scripts.runWithBroadcastSenderInteractive` 与 Explorer
  使用的 `Scripts.runInteractive`, 没有绕过统一 Launch、脚本引擎或真实插件 Binder 会话。
- Android 无障碍测试节点确认编辑器输入框 `isPassword=false`, Explorer/getpass 输入框
  `isPassword=true`; 两次回复均得到预期结构化结果, 且回复文本未出现在全局控制台。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 用时 2.232 秒,
  API 37 / x86_64 / 16 KiB page 模拟器用时 8.853 秒, 均为 `OK (1 test)`。

******

## M3 —— 兑现初衷: AutoJs6 API 实时能力 broker (目标版本 0.3.0 起)

> 主题: 进入 M3 前, Python 只有 4 个只读快照, 而 JS 有约 45 个模块。当前树已打通
> 协议 1.5 broker 骨架、完整第一批低风险能力、第二批 files/dialogs/engines 及第三批
> automator 基础动作。后续继续按用户价值
> 逐批扩面。方案不必从零设计 —— 宿主已有两个现成参照:
> Lua broker (机制完整: executionId 绑定、防重放、配额、唯一终态, 能力仅 2 项) 与
> Node.js broker (能力面完整: 31 个模块)。Python 取两者之长:
> **复用 Lua 的会话绑定机制, 逐批移植 Node 的能力面**。
>
> 原则: 每批能力做完即真机冒烟 + 示例脚本, 随即可发 alpha; 能力不可用时明确抛
> `CapabilityUnavailableError`; 不做 default-off 灰度与逐能力证据报告。

### 协议与骨架

- [x] [H+P] **协议 1.5: 双向能力通道**: 新增 `IPythonHostCapabilityBroker`
  (`dispatch(requestBytes) -> resultBytes`, 纯数据 JSON, 绑定 executionId + 配额 + 超时),
  随 openSession 传入插件; 终态后调用一律拒绝。
  宿主提交: `60118678b`; 三件 API AAR 已重新生成, 插件 `libs/` 与精确 lock 已更新。
- [x] [P] **Python 同步调用层**: `autojs6._broker` 封装跨进程调用
  (请求-响应, 阻塞式, 超时抛异常), 各能力模块在其上以普通函数暴露。
- [x] [H] **宿主 dispatcher**: `PythonHostCapabilityDispatcher` 按能力名路由到现有
  runtime API 实现类, 并在每次执行上绑定 request UUID、插件 UID、1024 次调用配额、
  64 KiB 请求/响应上限与 5 s 单次 Host 调度上限。宿主提交: `3c94f7f60`。

### 第一批: 低风险高频 (0.3.0)

- [x] [H+P] `autojs6.toast(text)` —— Toaster
- [x] [H+P] `autojs6.clip.get() / set(text)` —— 剪贴板
- [x] [H+P] `autojs6.app.launch(package) / launch_app(name) / open_url(url)` —— AppUtils
- [x] [H+P] `autojs6.device.info()` 动态查询 (电量/屏幕状态/亮度/音量, 区别于启动时快照)
- [x] [H+P] `autojs6.console.log/warn/error` 直写宿主控制台 (与 print 并存, 带级别)
- [x] [H+P] `autojs6.notice(text)` —— 权限不足时稳定返回 `PERMISSION_DENIED`, 不主动打开设置
- [x] [P] 首批低风险能力示例脚本
  (`examples/python/m3_low_risk_capabilities.py`)。
- [x] [H+P] 协议 1.5 公共引擎双设备冒烟 (物理设备 arm64 + 16 KiB page x86_64 模拟器)。
- [ ] 发布 0.3.0-alpha。

### 2026-08-23 M3 首批 broker 验收记录

- 协议骨架由宿主提交 `60118678b` 引入, dispatcher 与首批能力由 `3c94f7f60` 接通;
  公共引擎验收用例由宿主提交 `e2a1723d4` 固定。插件锁定该干净 Host HEAD 的三件
  release API AAR, 协议分发门禁 PASS。
- 验收脚本经严格 `project.json` 准入 → `ScriptEngineService` →
  `PythonPluginScriptEngine` → 真实插件 Binder/PFD 会话 → 协议 1.5 Host broker,
  没有直接调用插件内部接口。
- 脚本实际调用 `toast`, `clip.set/get`, 对不存在目标调用 `app.launch/launch_app`
  并得到 `False`, 同时用被准入层拒绝的 `ftp://` URL 验证
  `HostCapabilityError.code == "INVALID_ARGUMENT"`, 避免验收测试打开外部页面。
- 结构化结果验证 execution-bound 往返内容; Android 剪贴板内容与 Python 读回一致,
  测试结束恢复原始 `ClipData`, 项目与私有传输快照均清理。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 用时 1.607 秒,
  API 37 / x86_64 / 16 KiB page 模拟器用时 7.183 秒, 均为 `OK (1 test)`。
  这是首批能力的聚焦 current-tree 冒烟, 不代表后续 M3 模块、完整设备矩阵或公开发布。
- 完整首批剩余能力由宿主提交 `ce721077e` 接通, 测试由 `19ec9b894` 固定;
  插件 API 与测试分别由 `6f0785a`、`20305cf` 引入。新增公共引擎用例严格校验
  `device.info()` schema/range、宿主 D/W/E 日志级别与 execution-tagged 通知; 测试仅取消
  自己的 UUID 通知, 不改通知权限或设置。
- `0.3.0-alpha.2` current tree 上, 新增用例在上述物理机与模拟器分别用时 1.047 秒、
  1.268 秒, 两台都实际发布并核验通知; 原 toast/clipboard/app 用例回归分别用时
  1.567 秒、7.913 秒。四次均为 `OK (1 test)`。

### 第二批: 文件、对话框与引擎 (0.3.x)

- [x] [H+P] `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` —— 经宿主
  broker 访问实时用户脚本目录; 项目执行以项目根为界, 单文件以脚本所在目录为界;
  仅限 NFC 规范化相对路径与 UTF-8 文本 (≤32 KiB), 枚举最多 128 个直接子项,
  不提供删除、递归、二进制或自动创建父目录。宿主提交: `3cadd1497`、`6911116bc`;
  插件提交: `69d24a0`、`be72119`。
- [x] [P] Host files 示例脚本 (`examples/python/m3_host_files.py`)。
- [x] [H+P] `autojs6.dialogs.alert/confirm/prompt/select` —— 前台弹窗; 复用协议 1.3
  的 Activity-backed 前台授权, 标题/正文/prompt 回复/select 数量与总量均有界,
  后台稳定返回 `INTERACTIVE_NOT_ALLOWED`。宿主提交: `7788da650`、`108095b42`、
  `c7c9e9b05`、`f9eef7848`; 插件提交: `171cfa0`、`03e599b`。
- [x] [P] Host dialogs 示例脚本 (`examples/python/m3_dialogs.py`)。
- [x] [H+P] `autojs6.engines.current/run/stop_self` 最小集: 不含绝对路径的当前引擎信息、
  执行根目录内非 Python Host 子脚本异步启动及确定性停止自身; 每次执行最多成功启动
  16 个子脚本, 嵌套 Python 稳定返回 `NESTED_PYTHON_NOT_ALLOWED`。宿主提交:
  `3707d9318`、`0c4df640e`; 插件提交: `454fcd3`、`cd204f2`。
- [x] [P] Host engines 示例脚本 (`examples/python/m3_engines.py` 与
  `examples/python/m3_engines_child.js`)。
- [ ] 发布 0.3.x alpha

### 2026-08-23 M3 Host files 验收记录

- 宿主实现与 JVM 测试分别由提交 `3cadd1497`、`6911116bc` 固定; 插件 façade 与便携
  测试分别由 `69d24a0`、`be72119` 固定。三件 release AAR 经干净宿主
  `6911116bc04c21ab82a8d1d8c9676db1ca7d6bdf` 的 distribution gate 重新生成并锁定。
- 公共引擎用例经真实项目准入、workspace snapshot、插件 Binder 会话和协议 1.5 broker,
  实际执行 Host seed 读取、实时文件写入/回读、存在与类型检查、项目根直接枚举、
  `PATH_NOT_FOUND` 稳定错误及本地 `../` 拒绝。
- 用例同时证明 Host 输出文件在执行后真实存在, 而已冻结的插件 workspace 在同次执行中
  看不到该写入; 临时项目与私有传输快照均完成清理。
- `0.3.0-alpha.3` current tree 在 Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a /
  4 KiB page) 用时 0.811 秒, API 37 / x86_64 / 16 KiB page 模拟器用时 3.295 秒,
  均为 `OK (1 test)`。这是 files 能力的双设备聚焦验收, 不冒充公开发布或完整设备矩阵。

### 2026-08-23 M3 Host dialogs 验收记录

- 宿主实现与首轮测试由 `7788da650`、`108095b42` 固定; `c7c9e9b05` 补齐
  `PendingFileExecution` 编译契约, `f9eef7848` 让 MaterialDialog 正按钮选择不依赖设备与
  应用语言是否同步。插件 façade、示例与便携测试由 `171cfa0`、`03e599b` 固定。
- 三件 release AAR 经干净宿主 `f9eef784855f64da4ac0a9f33ad89688b3f3bd03`
  的 protocol 1.5 distribution gate 重新生成并锁定; Host 源指纹为
  `6fd409c181514be7e0dc6859ab6855b0b3e3c24792c351960ddd23d4736b6b56`。
- 前台公共路径经 `Scripts.runInteractive` → `ScriptEngineService` →
  `PythonPluginScriptEngine` → 真实插件 Binder 会话, 依次完成 alert、confirm 正向选择、
  prompt 默认值替换及 select 第二项, 并核对精确结构化结果与私有传输清理。
- 后台项目路径不携带前台授权, `dialogs.alert` 稳定返回 `INTERACTIVE_NOT_ALLOWED`,
  全程不打开 UI。对话框仍由 Host 独占持有, Python 只接收纯数据结果。
- `0.3.0-alpha.4` current tree 上, 前台用例在 Sony XQ-AT72 (`QV710AF65F`, API 31 /
  arm64-v8a / 4 KiB page) 与 API 37 / x86_64 / 16 KiB page 模拟器分别用时 1.838 秒、
  8.295 秒; 后台用例分别用时 0.988 秒、0.936 秒。四次均为 `OK (1 test)`。
  APK 全部以同一 SM003 签名执行 `install -r -t`, 未卸载、未清数据, 已有定时任务状态保留。

### 2026-08-23 M3 Host engines 验收记录

- 宿主实现与 JVM/仪器测试由 `3707d9318`、`0c4df640e` 固定; 插件 façade、示例与便携
  测试由 `454fcd3`、`cd204f2` 固定。三件 release AAR 经干净宿主
  `0c4df640ed1a3e08cda72899d080f0ae01238df9` 的 distribution gate 重新生成并锁定;
  Host 源指纹为 `6fd409c181514be7e0dc6859ab6855b0b3e3c24792c351960ddd23d4736b6b56`,
  manifest SHA-256 为 `ce9c5fe48bab5c2ba6d645fb8d792976bfae2080976b0e608f71039b38df8d89`。
- `engines.current()` 经真实公共引擎返回严格 schema、Host execution ID、相对入口、
  project 标记与启动时间, 且结构化结果不含项目绝对路径。`engines.run("child.js")`
  实际由 `ScriptEngineService` 异步运行项目内 JavaScript 并写出 Host 实时文件标记;
  同项目 `nested.py` 被稳定拒绝为 `NESTED_PYTHON_NOT_ALLOWED`。
- `engines.stop_self()` 前的实时 Host 文件写入成功, 调用后的语句没有执行; 验收比较前后
  CPython PID 证明 provider 进程已退休, 紧接着的新 Python 项目成功运行。
- `0.3.0-alpha.5` current tree 上, 上述两项在 Sony XQ-AT72 (`QV710AF65F`, API 31 /
  arm64-v8a / 4 KiB page) 与 API 37 / x86_64 / 16 KiB page 模拟器分别合计用时
  3.122 秒、4.566 秒, 均为 `OK (2 tests)`。完整首批、Host files 与后台 dialogs 的
  4 项非交互回归分别用时 3.622 秒、12.982 秒, 均为 `OK (4 tests)`。
- Host 5276、插件 alpha.5/45 与测试 APK 均以 SM003 签名执行 `adb install -r -t`;
  未卸载、未清数据, 物理机既有定时任务状态保留。

### 第三批: 自动化核心 (0.4.0)

- [x] [H+P] `autojs6.automator.click/long_click/press/swipe/back/home`: 经宿主无障碍执行
  有界坐标手势与返回/主页动作; 坐标为 0..1,000,000 的非布尔严格整数, press/swipe
  持续时间为 1..4,000 ms, 返回动作实际布尔结果。无障碍缺失、断连或未进入工作状态时
  稳定映射为 `CapabilityUnavailableError`, 不启用服务、不打开设置、不重试动作。
  宿主实现/测试提交: `6938110f7`、`57650212c`、`9678c8d48`、`786335ff9`、
  `53b73f2ee`、`216468a8a`、`417ed0b82`、`843f528bb`; 插件实现/便携测试提交:
  `25468e8`、`760e44f`。
- [x] [P] 基础 automator 示例 (`examples/python/m3_automator.py`) 与使用说明
  (`docs/python/HOST_AUTOMATOR.md`)。
- [x] [H+P] `autojs6.selector`: 有界 UI 树只读快照 + AND 条件
  `find/click/set_text` 显式动作; 快照、查询与节点均以严格纯数据跨界, 原生节点引用绑定当前
  执行并设 128 个保留上限, 新快照、淘汰、窗口失效或执行终态后稳定返回 `STALE_NODE`。
  扫描无法在节点/深度上限内证明不存在时返回 `SELECTOR_SCAN_LIMIT_EXCEEDED`, 不伪装成未找到。
  宿主实现/测试提交: `66874d195`、`87c367c49`、`c118ebc73`、`93b86c3c3`;
  插件实现/便携测试提交: `4af84bc`、`e665f00`。
- [x] [P] selector 示例 (`examples/python/m3_selector.py`) 与完整边界/生命周期说明
  (`docs/python/HOST_SELECTOR.md`)。
- [x] [H+P] `autojs6.images.capture_screen()` 有界截图: Android 11+ 通过宿主
  无障碍 `takeScreenshot` 捕获 PNG/JPEG, 返回经长度、顺序、EOF、SHA-256 与格式签名
  验证的字节, 或原子写入执行产物。宿主每次执行最多保留 1 张、编码后最多 4 MiB,
  以 32 KiB 原始块传输; 替换、release 与执行终态清零。无障碍/API 不可用时 fail-closed,
  不启用服务、不打开设置、不触发 MediaProjection。宿主实现/测试提交:
  `d6c463ca2`、`799e31311`、`e9e7a53eb`、`8bd79e18e`、`27d38f1dd`;
  插件实现/便携测试提交: `5e2f6ad`、`91824f6`。
- [x] [P] 截图示例 (`examples/python/m3_capture_screen.py`) 与完整传输/资源/错误说明
  (`docs/python/HOST_IMAGES.md`)。
- [x] [H+P] `autojs6.images.find_color(color, *, region=None, threshold=0)` 有界找色:
  接受 `0x000000..0xFFFFFF` 严格整数或精确 `#RRGGBB`, 可选 `(x, y, width, height)`
  区域及 0..255 逐通道阈值。每次调用只捕获一张最新 Android 11+ 无障碍截图,
  全程在宿主逐行扫描并按上到下、左到右返回首个绝对坐标, 穷尽未命中返回 `None`;
  不向插件传输或保留截图/像素字节。宿主隔离分支实现/测试提交: `acfcb1dfb`、
  `7235034f0`、`604ffc777`、`155b9e566`; 插件实现/便携测试提交:
  `1e6836c`、`9d3c790`。
- [x] [P] 找色示例 (`examples/python/m3_find_color.py`) 与区域/阈值/扫描顺序/错误说明
  (`docs/python/HOST_IMAGES.md`)。
- [x] [H+P] `autojs6.images.find_image(template, *, region=None, threshold=0)` 有界模板找图:
  接受最大 1 MiB 的 PNG/JPEG bytes-like 模板, 以 24 KiB 顺序块和 SHA-256 上传到单次
  执行唯一模板槽; Android 解码限制单边 2048 / 总计 1,048,576 像素, 搜索区域限制
  4,194,304 像素且比较预算为 16,777,216。仅 alpha=255 的模板像素参与逐通道 RGB
  阈值匹配, 其余像素为 wildcard, 按行优先返回模板左上角或 `None`; 不依赖 OpenCV。
  宿主隔离分支实现/测试提交: `f20f123b4`、`301da08f7`、`9d3940fb8`; 连续截图遵守
  Android 333 ms 节流的有界重试修复: `f94df3b6f`; 插件实现/便携测试提交:
  `e51ce0f`、`38187ee`。
- [x] [P] 找图示例 (`examples/python/m3_find_image.py`) 与上传/解码/alpha/预算/错误说明
  (`docs/python/HOST_IMAGES.md`)。
- [x] [H+P] `autojs6.ocr.recognize(image)` 有界行级识别: 接受最大 1 MiB 的 PNG/JPEG
  bytes-like 图像, 复用 24 KiB 分块、SHA-256、单边 2048 / 总计 1,048,576 像素的
  模板上传信封; 只选择宿主已启用、已授权且兼容的 OCR 服务, 返回最多 256 行、每行
  4 KiB 严格 UTF-8、合计 48 KiB 的有序不可变 tuple。无合格引擎稳定返回
  `OCR_UNAVAILABLE`, 已选择引擎执行失败返回 `OCR_FAILED`; 不安装/启用/授权服务,
  不向 Python 暴露 Bitmap、Binder 或 OCR 插件对象。宿主实现/测试提交:
  `337841107`、`4961ac13a`; 插件 façade 与 36 项聚焦 broker 测试提交:
  `1923992`、`7538d4d`; 示例与完整契约分别为 `examples/python/m3_ocr.py` 和
  `docs/python/HOST_OCR.md`。
- [x] 完整自动化示例: 一个真实的 "打开应用 → 找控件 → 点击 → 截图断言" Python 脚本
- [ ] 发布 0.4.0

### 2026-08-23 M3 automator 基础动作验收记录

- 宿主动作实现与单元测试由 `6938110f7`、`57650212c` 固定; 受控无障碍 Activity、
  service 启动/工作状态探测及 fail-closed 公开引擎测试由 `9678c8d48`、`786335ff9`、
  `53b73f2ee`、`216468a8a`、`417ed0b82`、`843f528bb` 固定。插件 façade 与便携测试
  由 `25468e8`、`760e44f` 固定。
- API 37 / x86_64 / 16 KiB page 模拟器启用 AutoJs6 无障碍后, 公共 Python 项目依次执行
  click、press、long-click、swipe、Back 与 Home, 六项均返回 `true`; 受控界面独立观察到
  2 次按钮激活、1 次长按与 1 次滑动。测试体用时 19.713 秒, `OK (1 test)`。instrumentation
  结束后已恢复 service restart backoff, 组件为启用、已绑定且无 crashed 状态。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 刻意不启用 AutoJs6
  无障碍; 公共 Python 项目调用 `automator.click` 时稳定得到 `CapabilityUnavailableError`
  与精确消息, 用时 0.879 秒, `OK (1 test)`。运行前后既有无障碍服务列表逐字一致,
  未打开设置; 因此本条只声明物理机 fail-closed, 不声明物理机手势成功。
- Host 5276、插件 `0.4.0-alpha.1`/51 与测试 APK 均保持 SM003 signer; 覆盖安装采用
  `adb install --no-streaming -r -t`, 未卸载、未清数据。用户已另行确认 QV710AF65F
  定时任务成功, 本轮验收未修改其定时任务或无障碍配置。

### 2026-08-24 M3 selector/UI 树验收记录

- 宿主 selector 数据面、dispatcher/边界测试、受控无障碍 Activity 与公开 Python 引擎
  instrumentation 分别由 `66874d195`、`87c367c49`、`c118ebc73`、`93b86c3c3`
  固定; 插件 façade 与便携测试由 `4af84bc`、`e665f00` 固定。
- API 37 / x86_64 / 16 KiB page 模拟器启用 AutoJs6 无障碍后, 公共 Python 项目通过
  `selector.snapshot/find/click/set_text` 验证 `autojs6-python-ui-tree-v1`、资源 ID、
  AND 首次匹配、穷尽缺失返回、真实点击与文本写入回执, 并在新快照后得到精确
  `STALE_NODE` 错误。受控界面独立观察到 1 次按钮激活及目标文本; 用时 4.863 秒,
  `OK (1 test)`。instrumentation 结束后已恢复 service restart backoff, 组件为启用、
  已绑定, `Binding services:{}` 且 `Crashed services:{}`。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 刻意不启用
  AutoJs6 无障碍; 公共 Python 项目调用 `selector.snapshot` 时稳定得到
  `CapabilityUnavailableError` 与精确消息, 用时 0.869 秒, `OK (1 test)`。运行前后
  `accessibility_enabled=1`, 既有六个无障碍服务列表逐字一致且 AutoJs6 服务始终缺席;
  未打开设置, 因此本条只声明物理机 fail-closed, 不声明物理机 UI 树动作成功。
- Host 5276、插件 `0.4.0-alpha.2`/54 与测试 APK 均以覆盖方式安装; 使用
  `adb install --no-streaming -r -t`, 未卸载、未清数据。用户已确认 QV710AF65F 定时
  任务成功, 本轮 selector 验收未修改其定时任务或无障碍配置。

### 2026-08-24 M3 screen capture 验收记录

- 宿主有界截图、dispatcher/资源边界测试、受控颜色 Activity 与公开 Python 引擎
  instrumentation 分别由 `d6c463ca2`、`799e31311`、`e9e7a53eb`、`8bd79e18e`
  固定; `27d38f1dd` 让正向无障碍验收在 instrumentation 内确定性刷新既有 AutoJs6
  组件并以十六进制文本核对结构化 SHA-256。插件 façade 与 25 项聚焦便携测试由
  `5e2f6ad`、`91824f6` 固定。
- API 37 / x86_64 / 16 KiB page 模拟器启用 AutoJs6 无障碍后, 公共 Python 项目调用
  `images.capture_screen(format="png", quality=100, path="screens/python-capture.png")`;
  验收确认产物可解码、PNG 签名正确、受控 `#123456` 像素命中、编码结果不超过 4 MiB,
  且 Python 读取值、插件重组值与宿主发布产物的长度和 SHA-256 完全一致。用时
  5.867 秒, `OK (1 test)`。结束后组件已恢复为启用且已绑定,
  `Binding services:{}` 与 `Crashed services:{}` 均为空。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 刻意不启用
  AutoJs6 无障碍; 公共 Python 项目调用 `images.capture_screen()` 时稳定得到
  `CapabilityUnavailableError` 与精确消息, 未发布任何产物, 用时 0.866 秒,
  `OK (1 test)`。运行前后 `accessibility_enabled=1`, 既有六个无障碍服务列表逐字
  一致且 AutoJs6 服务始终缺席; 未打开设置, 因此本条只声明物理机 fail-closed。
- Host 5276、插件 `0.4.0-alpha.3`/57 与测试 APK 均保持 SM003 signer; 覆盖安装采用
  `adb install --no-streaming -r -t`, 未卸载、未清数据。用户已确认 QV710AF65F
  定时任务成功, 本轮截图验收未修改其定时任务或无障碍配置。

### 2026-08-24 M3 screen color search 验收记录

- 宿主找色能力、逐行扫描算法/dispatcher 边界测试、受控颜色区域与公开 Python 引擎
  instrumentation 由隔离分支提交 `acfcb1dfb`、`7235034f0`、`604ffc777`、
  `155b9e566` 固定; 插件 façade 与聚焦便携测试由 `1e6836c`、`9d3c790` 固定。
- API 37 / x86_64 / 16 KiB page 模拟器启用 AutoJs6 无障碍后, 公共 Python 项目以
  受控目标 bounds 作为 region、逐通道阈值 2 调用 `images.find_color(0x123456, ...)`;
  返回两元素坐标且严格落在受控 `#123456` 区域内, 不发布图像产物。用时 5.707 秒,
  `OK (1 test)`。instrumentation 结束后已恢复 `accessibility_enabled=1`、唯一 AutoJs6
  service、已绑定, `Binding services:{}` 与 `Crashed services:{}` 均为空。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 刻意不启用
  AutoJs6 无障碍; 公共 Python 项目调用 `images.find_color(0x123456)` 时稳定得到
  `CapabilityUnavailableError` 与精确消息, 用时 0.945 秒, `OK (1 test)`。运行前后
  `accessibility_enabled=1`, 既有六个无障碍服务列表逐字一致且 AutoJs6 服务始终缺席,
  `Binding services:{}` 与 `Crashed services:{}` 均为空。
- Host 5276、插件 `0.4.0-alpha.4`/60 与测试 APK 均保持 SM003 signer; 仅采用
  `adb install --no-streaming -r -t` 覆盖安装, 未卸载、未清数据。用户已确认
  QV710AF65F 定时任务成功, 本轮找色验收未修改其定时任务或无障碍配置。

### 2026-08-24 M3 screen template search 验收记录

- 宿主模板上传/解码/匹配、dispatcher 与生命周期测试、公开 Python 引擎 instrumentation
  由隔离分支提交 `f20f123b4`、`301da08f7`、`9d3940fb8` 固定; 首次设备运行还发现
  Android 对相邻无障碍截图强制 333 ms 间隔, `f94df3b6f` 将原先不足的 50 ms 重试
  收敛为仅针对精确限流错误的 350 ms 等待、最多 3 次且仍受 4 秒总 deadline 约束。
  插件 façade 与 32 项聚焦 broker 测试由 `e51ce0f`、`38187ee` 固定。
- API 37 / x86_64 / 16 KiB page 模拟器启用 AutoJs6 无障碍后, 同一个公共 Python 项目
  上传 3 x 3 PNG 模板, 在受控 `#123456` bounds 内以逐通道阈值 2 返回模板左上角;
  随后立即上传第二个 PNG 并穷尽返回 `None`, 同时覆盖连续截图限流路径。最终用时
  5.841 秒, `OK (1 test)`；instrumentation 前后三份 codePath 完全一致。结束后已恢复
  `accessibility_enabled=1`、唯一 AutoJs6 service、已绑定, `Binding services:{}` 与
  `Crashed services:{}` 均为空, 且无测试进程残留。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 刻意不启用 AutoJs6
  无障碍; 公共 Python 项目调用 `images.find_image(...)` 时稳定得到精确
  `CapabilityUnavailableError`, 用时 0.979 秒, `OK (1 test)`。运行前后
  `accessibility_enabled=1`, 既有六个无障碍服务列表逐字一致且 AutoJs6 服务始终缺席,
  `Binding services:{}` 与 `Crashed services:{}` 均为空。
- Host 5276、插件 `0.4.0-alpha.5`/63 与测试 APK 均保持 SM003 signer; 仅采用
  `adb install --no-streaming -r -t` 覆盖安装, 未卸载、未清数据。用户已确认
  QV710AF65F 定时任务成功, 本轮找图验收未修改其定时任务或无障碍配置。

### 2026-08-24 M3 Host OCR 验收记录

- 宿主 OCR 选择/临时 Bitmap 生命周期、dispatcher 与结果边界测试由隔离分支提交
  `337841107`、`4961ac13a` 固定, 并由 `f3167c703` 非快进合并到宿主主分支;
  插件有界上传 façade、不可变结果、错误映射与恶意
  返回防御由 `1923992`、`7538d4d` 固定。插件 188 项便携测试全部通过; 插件
  `:app:testDebugUnitTest :app:assembleDebug` 离线构建 38 秒通过, 宿主
  `:app:assembleAppDebug :app:assembleAppDebugAndroidTest` 离线构建 1 分 50 秒通过。
- API 37 / x86_64 / 16 KiB page 模拟器安装同一 SM003 signer 的 ML Kit OCR
  `1.0.0`/4 测试依赖。公共 Python 项目上传 instrumentation 现场生成的 1200 x 320
  PNG `AUTOJS6 OCR 2026`, 经宿主既有 `OcrPluginHost` 选择并调用合格服务; 返回值类型
  精确为 `tuple`, 合并文本同时包含 `AUTOJS6`、`OCR` 与 `2026`, 不发布产物。测试体
  用时 2.873 秒, `OK (1 test)`。运行前后 `accessibility_enabled=0`、服务列表为 `null`,
  证明该路径未借用或修改无障碍; 宿主、测试包及 Python Runtime 无进程残留。为遵守
  不卸载约束, 已核验 OCR 测试依赖继续保留在该模拟器上。
- Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 不安装 OCR 服务;
  公共 Python 项目调用 `ocr.recognize(...)` 时稳定得到
  `CapabilityUnavailableError` 与精确消息
  `No enabled, authorized, and compatible Host OCR engine is available`, 不发布产物。
  测试体用时 0.918 秒, `OK (1 test)`。运行前后 `accessibility_enabled=1`, 既有六个
  无障碍服务列表逐字一致且 AutoJs6 始终缺席; 测试包及 Python Runtime 无进程残留。
- Host 5276、插件 `0.4.0-alpha.6`/66、测试 APK 与 ML Kit OCR 测试依赖均经 APK
  Signature v2 校验为 SM003 证书 SHA-256
  `31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213`。仅采用
  `adb install --no-streaming -r -t` 覆盖安装, 未卸载、未清数据、未访问非授权设备。
  用户已确认 QV710AF65F 定时任务成功, 本轮 OCR 验收未修改其定时任务或无障碍配置。

### 2026-08-24 M3 完整自动化示例验收记录

- `examples/python/m3_complete_automation` 由插件提交 `36cf965`、`ce951df`、
  `4a19ba9`、`5ff3282` 固定: 通过 `app.launch` 打开真实 Android Settings, 以有界
  `selector.find` 精确查找并通过 `selector.click` 点击搜索控件, 验证目标 EditText,
  再用 `images.capture_screen` 发布 PNG 并断言目标控件完整落在截图内。所有等待、
  Back 归一化与截图解析均有界; 3 项便携测试覆盖成功路径、转场期节点先隐藏后可见、
  以及截图尺寸不包含目标控件时的 fail-closed。
- 首次设备探索发现 Settings 树中存在平台上报的 `right < left` 离屏节点。宿主提交
  `4d13653fd` 在 `PythonHostSelectorBounds.fromPlatform` 将异常轴收敛为保持锚点的
  zero-area 边界, 不交换坐标或虚构面积; 聚焦单元测试离线通过, 并由 `6f33bf4cb`
  非快进合并到宿主主分支。示例同时改用精确 `find`, 避免无关节点决定整条工作流。
- API 37 / x86_64 / 16 KiB page 模拟器安装 Host 5276 的 SM003 x86_64 修复 APK,
  通过导出的 `RunIntentActivity` 及 `path` / `source_kind=python_project_v1` /
  `project_root` 公开参数进入真实项目准入、workspace、Binder 会话和协议 1.5 broker。
  工作流得到 `backSteps=0`、点击成功、目标边界 `(126,195)-(1080,384)` 与结构化
  `[result]`; `[artifact]` PNG 为 1080 x 2424、54,453 字节, SHA-256 为
  `9dee9783b6677f47d966c69be8d164f94eea64ff7aca10c1d972e1c6691ab572`, IHDR CRC、
  目标资源 ID 与截图包含关系均通过。
- 验收仅使用 `emulator-5554`; 未访问 QV710AF65F。事务结束后模拟器恢复
  `accessibility_enabled=0`、服务列表 `null`、Launcher 前台, Host 私有项目、执行产物、
  UI dump 与 `/data/local/tmp` 精确暂存目录均已删除。覆盖安装未卸载、未清数据; 用户
  已确认 QV710AF65F 定时任务成功。

### 后续批次 (需求驱动, 出现用例再排期)

- [ ] [H+P] `shell` (root/shizuku)、`sensors`、`media`、`sqlite`、`storages`、
  `floaty` 悬浮窗、`web` 等 —— 逐个按需移植, 不一次性批量接入。

******

## M4 —— 第三方 Python 包 (与 M3 并行推进)

> 主题: stdlib-only 是 0.1.0 的发布策略而非产品终点。按成本从低到高三条路径推进,
> 不做签名 pack manifest / SBOM 全家桶。

- [x] [H+P] **路径 A (零协议成本, 项目本地依赖)**: 纯 Python 依赖直接放进项目目录随 workspace
  打包 (`sys.path` 已含项目根, 天然可 import)。
  配套放宽 workspace 限制: 条目 1024 → 8192, 归档 16 → 64 MiB, 解压 32 → 128 MiB。
  验收: 项目内置 `requests` 源码目录 (含 urllib3 等依赖) 后 `import requests` 成功
  (配合 M1 的 INTERNET 权限实测发请求)。
  - `0.3.0-alpha.6` current tree 使用锁定的 `requests 2.34.2`、`urllib3 2.7.0`、
    `certifi 2026.7.22`、`charset-normalizer 3.4.9` 与 `idna 3.18`; 依赖夹具含
    125 个运行文件且无 `.so/.pyd/.dll/.dylib/.exe`, SHA-256 为
    `880EBB02E4C264F9D8B82521C090F7592ABF0663E67BFC6DC4F224CB636F101B`。
  - 验收项目构造 1100 个 workspace 文件、33 MiB 可压缩数据及 17 MiB 确定性随机数据,
    同时跨越旧版 1024 条目、16 MiB 归档与 32 MiB 解压上限; HTTPS 返回 200 且结构化
    结果精确核对上述五个版本。
  - Sony XQ-AT72 (`QV710AF65F`, API 31 / arm64-v8a / 4 KiB page) 用时 5.040 秒,
    API 37 / x86_64 / 16 KiB page 模拟器用时 5.406 秒, 均为 `OK (1 test)`; 安装采用
    `adb install -r -t` 并保留应用数据。使用说明与可复现示例见
    [PROJECT_LOCAL_PACKAGES.md](docs/python/PROJECT_LOCAL_PACKAGES.md) 与
    [m4_project_local_requests](examples/python/m4_project_local_requests)。
- [x] [P] **路径 B (构建期精选包评估)**: 结论为 `NOT_ADMITTED`, 当前 APK 继续
  `stdlib-only`。候选固定为路径 A 已验收的 `requests 2.34.2` 五包闭包; 它的主要收益
  只是免去选择该库的项目准备步骤, 而标准库联网与项目本地依赖均已可用。内置后却会让
  每个 APK 无条件承担体积、五包更新/安全维护及许可证成本, `charset_normalizer` 单独
  内置也没有足够通用价值。
  - `0.4.0-alpha.7` stdlib-only debug APK 输出基线为 arm64-v8a 23,709,688 bytes、
    x86_64 23,726,048 bytes、universal 34,622,039 bytes。仓库没有经审计的离线 wheelhouse
    与哈希锁, 而 Gradle `--offline` 不会自动约束 Chaquopy 的独立 pip 子进程; 本次拒绝
    联网临时下载, 因此不伪造不可复现的候选体积差值。缺少 hermetic 输入本身即为准入阻断。
  - 当前不添加 `pip` block, `python-runtime.lock` 保持 packages policy=`stdlib-only`、
    count=0、online pip=false, NOTICE 明确候选未随 APK 分发。未来只有在出现路径 A
    明显不足的真实高频用例, 并同时提交本地 wheel、精确版本/哈希、许可证、无 native
    payload 扫描、断网 clean build、三种 APK 体积差值与双 ABI 公共引擎验收后才重开。
  - 完整决策与准入清单见
    [ADR 0003](docs/adr/0003-build-time-python-package-admission.md)。
- [ ] [P] **路径 C (native 包)**: 评估 Chaquopy 官方 wheel 源的 numpy/pillow/opencv
  构建期打包可行性 (Chaquopy 提供预编译 Android wheel); 逐包实测, 能用即收录,
  16 KB page 等兼容性问题出现时针对性修复。
- [ ] [P] **路径 D (运行时安装, 可选进阶)**: 插件内 pip 安装到私有目录并纳入 `sys.path`
  (需 INTERNET; 作为显式用户操作, 不做隐式解析)。有明确用户需求再启动。

******

## M5 —— 长任务与稳定性 (目标版本 0.5.x)

- [ ] [H+P] **长任务模式**: 前台通知 + 心跳, 移除常规超时上限, 支持手动停止
  (不是简单调大 60 s, 而是独立的运行档位)。
- [ ] [P] **进程预热评估**: 实测 CPython 冷启动耗时; 若显著 (>1 s), 提供
  "执行后保留进程" 选项 (放弃 per-execution 退休, 状态污染问题出现再修)。
- [ ] [H+P] **并发执行**: 多脚本同时运行 (多会话或宿主侧排队, 按实现成本选择;
  当前限制为全局单会话)。
- [ ] [H] **异常修复通道**: 用户脚本报错场景收集 (issue 驱动), 每个真实异常配一个
  回归脚本, 修复即关闭 —— 这是本项目唯一持续增长的 "测试集"。

******

## M6 —— 版本节奏与验证约定

### 版本规划

| 版本 | 内容 | 状态 |
| --- | --- | --- |
| 0.1.0 | 协议 1.0-1.1 基线, 独立进程执行 | 已发布 |
| 0.2.0 | M1 体验补全 + M2 入口收尾 | 进行中 |
| 0.3.x | M3 broker 骨架 + 第一二批能力 + M4 路径 A | 进行中 (路径 A 已完成) |
| 0.4.0 | M3 自动化核心 + M4 第三方包路径 B/C | 进行中 (自动化核心已完成; 路径 B 已评估且不接纳, 路径 C 待评估) |
| 0.5.x | M5 长任务/并发/预热 | 计划 |
| 1.0.0 | 能力面稳定, API 冻结 | 计划 |

### 轻量验证约定 (代替证据等级流程)

- 本地快速回归 (离线, 避免外网 Cloudflare 超时):
  ```powershell
  $env:PYTHONDONTWRITEBYTECODE = '1'
  python -B -m unittest tools.tests.test_bootstrap -v
  .\gradlew.bat --offline --console=plain :app:testDebugUnitTest :app:assembleDebug
  ```
- 发版前: 真机冒烟清单 (约 10 项手动操作, 覆盖当版新能力 + 停止/重启/热插拔),
  通过即发布。
- 历史 U1 证据工具 (`tools/verify-u1-*`, `tools/device/*`) 与报告继续保留可用,
  供需要时复核, 但**不再作为任何版本的发布前置**。
- 新能力的验证方式: 一个示例脚本在真机跑通即视为完成; 后续异常按 M5 异常修复通道处理。

### 双仓协同约定

- 协议/AAR 变更 (仅 M3 骨架与 M5 长任务涉及): 宿主生成三件 release AAR →
  拷贝至插件 `libs/` → 更新 `locks/host-api-aars.lock` → 双仓分别提交。
- 其余批次均为单仓独立改动, 互不阻塞。
