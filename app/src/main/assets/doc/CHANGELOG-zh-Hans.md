******

### 版本历史

******

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
