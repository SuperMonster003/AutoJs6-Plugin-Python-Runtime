******

### 版本历史

******

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
