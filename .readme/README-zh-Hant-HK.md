<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>獨立 Python 執行環境外掛程式. 在專用外掛程式程序執行 Python 指令碼</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 語言

******

目前 README.md 支援以下語言:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- 繁體中文 (香港) [zh-Hant-HK] # 目前
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### 簡介

******

Python Runtime 是獨立的 Python 協議 V1 provider. 宿主將單一 Python 原始碼快照交給專用外掛程式程序, 外掛程式使用 CPython 執行並傳回有界輸出, 結構化例外及唯一終態.

> 0.1.0 原始碼身分及精確 Host lock 已凍結. 既有本機 RC 的建置, APK, Binder 及一部 API 31 arm64-v8a 裝置證據仍屬歷史證據; 穩定 APK/P3 provenance 與精確 release identity 綁定, production receipt 是發佈後的獨立證據層級.

******

### 功能

******

- 將一個 UTF-8 Python 原始碼快照作為 `__main__` 執行.
- 接收最大 1 MiB 的有限預置 stdin snapshot; snapshot 到達 EOF 後, 明確前台啟動可透過協議 1.3 的有界 prompt/reply 繼續內置 `input()`, 而標準庫 `getpass.getpass()` 使用隱藏回顯.
- 為已准入項目明確選擇 `entryMode=file|module`; module 模式使用標準 `runpy` 元數據、項目根目錄 `sys.path[0]` 及 package-relative import, file 模式保留普通指令碼語義.
- 在腳本執行期間按 stdout/stderr 原始次序透過有界 chunk 與 credit 傳送; credit 用盡會對執行施加背壓.
- 透過協議 1.4 明確設定最大 64 KiB 的嚴格 JSON 結果, 並傳送最多 16 個具有路徑、大小及 SHA-256 限制的可選輸出 artifact; 絕不從 stdout 推斷結果.
- 傳回 `SystemExit`, 語法錯誤和執行階段例外, 包括有界結構化 traceback.
- 同一執行環境程序只允許一個使用中工作階段, provider 端不排隊.
- 宿主毋須重新啟動; 安裝或重新啟用後下一次新執行會重新發現並 pin provider 身分, 執行中的 Binder death 會終止該次執行且絕不自動重播.

******

### 執行環境與資料格式

******

協議 V1 目前聲明以下範圍:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

建置要求 Python 3.13. 已凍結的本機 RC 產物及精確裝置執行記錄為 CPython 3.13.9; 最終 0.1.0 在原始碼凍結後仍須重新核對版本及雜湊.

******

### 外掛程式介面

******

宿主透過以下識別資料探索及呼叫外掛程式:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.4
```

外掛程式接收獨立 SOURCE, 可選的有界 workspace archive, 最大 1 MiB 的有限預置 stdin snapshot, 以及協議 1.1 的唯讀宿主能力快照. 協議 1.2 為已准入項目加入明確 file/module 入口協商. 協議 1.3 在 snapshot EOF 後為內置 `input()` 加入由 Host 持有且僅限前台的 prompt/reply; 標準庫 `getpass.getpass()` 使用隱藏回顯. 協議 1.4 加入明確嚴格 JSON 結果及可選的 SHA-256 manifest 輸出 artifact, stdout 只供診斷且絕不解析為結果. 直接 `sys.stdin` 始終有限, 後台啟動絕不開啟輸入 UI, 外掛程式亦不會向指令碼注入 Context, Binder, 宿主執行環境物件或 callback sink.

******

### 宿主整合狀態

******

> 0.1.0 只與 AutoJs6 6.8.0 配對, 最低 Host versionCode 已凍結並強制為 5275; 最終 clean Host 原始碼修訂及三件 AAR distribution manifest 已寫入 lock. 每次新執行均重新發現 provider; 缺失或停用時提示安裝或啟用且絕不 fallback, 安裝或重新啟用後毋須重新啟動宿主. 穩定 APK 身分與該精確 Plugin 原始碼及 Host lock 綁定.

```text
release target: 0.2.0-alpha.1
release state: 0.2.0 current-tree candidate; M1 and M2 are implemented and smoke-tested on an API 31 arm64 device plus an API 37 x86_64 16 KiB-page emulator; background direct sys.stdin remains finite, and no complete device-matrix, publication, or release evidence is claimed
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### 安全性與私隱

******

Chaquopy 執行環境只供可信本機指令碼使用, 並非 hostile-code sandbox. Exported service 要求宿主簽署權限並核對 UID, 套件及 signer; 獨立 Android UID, 專用程序與窄 Binder 邊界可降低宿主暴露, 但不會令 Python 成為沙箱. SM003 是長期發行 signer, SuperMonster003 負責 runtime, security 及 release.

******

### 執行限制

******

- 原始碼最大 4 MiB, 總輸出最大 16 MiB, 每個輸出 chunk 最大 16 KiB, 最多 16384 個 chunk.
- 要求逾時最大 30 min, 同一程序最多一個使用中工作階段, provider 端不排隊.
- SOURCE 描述元採用 Binder 接收端完整 PFD 擁有權, 保留 reliable-pipe 錯誤通道, 並在終態或關閉時釋放.
- 輸出在執行期間按 credit 逐 chunk 傳送; credit 用盡會暫停腳本, 已接受的輸出先於唯一終態, 終態後禁止輸出.
- 結構化 JSON 最大 64 KiB; 輸出 artifact 最多 16 個, 路徑最大 1024 UTF-8 bytes, 每個最大 4 MiB, 合計最大 8 MiB, Host 必須核對精確長度、EOF 及 SHA-256.
- 取消模式是程序重啟, 而非 CPython 級協作取消; 原生擴充套件或阻塞呼叫仍需後續 Android 驗證.
- 插件已授予 `INTERNET` 以支援腳本透過標準庫直接連線; 仍不支援線上 pip、自動下載程式碼或執行時安裝第三方套件.

******

### 未聲明的能力

******

- 不提供通用即時 stdin 或直接 `sys.stdin` callback streaming. 前台互動只適用於最大 1 MiB 的有限 snapshot 到達 EOF 後的內置 `input()` 與標準庫 `getpass.getpass()`. 仍不支援 workspace 寫回, 線上 pip 或執行階段下載 wheel.
- 不提供 UI 指令碼, 除錯器, REPL 或任意宿主 Java 物件存取.
- 不提供即時 AutoJs6 能力 broker; 首批 API 只使用執行開始時凍結的 app/device/execution/project 快照及外掛程式私有 workspace 的有界唯讀檔案介面.
- 不聲明 32 位元 Android 支援, 亦不保證任何第三方 native wheel 可用.
- 目前樹已有 API 31 arm64-v8a 真機冒煙證據與 API 37 x86_64 16 KB page 模擬器冒煙證據; 兩者都不冒充完整裝置矩陣或發行資格.

******

### 路線圖

******

R6-P2/P3 的本機 RC 及集中裝置證據保留為歷史記錄. 本次 clean VERSION_BUILD=11 freeze commit 固定了穩定 Plugin 原始碼身分及精確 Host 6.8.0/5275 lock; 穩定 APK provenance 按這些精確身分驗證, 任何 production receipt 亦必須使用相同依據. 完整 API×ABI 矩陣及新 soak 不屬自動門禁.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本記錄

******

# v0.2.0-alpha.1

###### 2026/08/13

* `提示` 0.1 之後的 U1 current-tree alpha 候選; U1-R2 module entry、live output、前台內置 input、明確結構化 JSON 及有界輸出 artifact 只完成至 E2, 後台啟動及直接 sys.stdin 仍非互動, R2 E3 尚未完成, 且這些目前樹結果不屬於裝置矩陣/發佈/公開證據
* `新增` 新增最大 1 MiB 的有限預先提供 stdin snapshot, 為 `input()` 及 `sys.stdin` 提供確定輸入和 EOF
* `新增` 完善專案 import 語義, 支援 workspace 模組, 巢狀入口同層及根模組與 package-relative import
* `新增` 新增協議 1.2 明確 `entryMode=file|module`; module 執行透過 `runpy` 提供正確的 `__package__`、`__spec__`、項目根目錄 `sys.path[0]` 及相對 import, file 模式維持不變
* `新增` 新增協議 1.3: 有限 snapshot 到達 EOF 後, 只有前台內置 `input()` 使用可見回顯、標準庫 `getpass.getpass()` 使用隱藏回顯的有界 prompt/reply; 後台啟動絕不開啟輸入 UI, 直接 `sys.stdin` 始終有限
* `新增` 新增協議 1.4 明確嚴格 JSON 結果及可選輸出 artifact, 對數量、標準化路徑、每個/合計大小、精確 PFD 引用及 SHA-256 設限, 且絕不從 stdout 推斷結果
* `修正` 執行前以 strict UTF-8 解碼原始碼, 非 UTF-8 encoding cookie 不再繞過合約
* `改善` 授予 `INTERNET`, 讓可信腳本可直接使用標準庫網絡客戶端, 同時仍停用線上 pip 與自動程式碼下載
* `改善` 將 Provider 執行上限提高至 30 分鐘, 有界輸出提高至 16 MiB / 16384 個 chunk
* `改善` 將 stdout/stderr 的有界 chunk 與 credit 背壓前移到腳本執行期間, 保留終態前的有序部分輸出並禁止終態後輸出
* `改善` 每次執行使用獨立 `__main__`, 並還原 stdin/stdout/stderr, argv, cwd, `sys.path`, module 及 importer cache 狀態
* `改善` 為已開啟但未 start 的 session 加入 5 秒 lease, 到期釋放輸入, descriptor 及單一工作階段佔位
* `改善` Provider 在 Binder 傳入邊界強制最低 Host versionCode 5275, 不再只依賴 Host 端探索檢查

# v0.1.0

###### 2026/08/12

* `提示` 0.1.0 固定了穩定 Plugin 原始碼身分及精確 Host 6.8.0/5275 lock
* `新增` 面向 AutoJs6 6.8.0 / versionCode 5275 的 Python 協議 1.0-1.1, 有界專案 workspace 及唯讀 app/device/execution/project 能力快照
* `新增` 毋須重新啟動 Host 的熱插拔: 安裝或重新啟用後下一次新執行重新發現並 pin 身分, 缺失或停用時絕不 fallback
* `新增` 執行中的 Binder death 終止目前執行且不得重播, 後續新執行重新發現 provider
* `改善` 將 Chaquopy 固定為 trusted-local, non-sandbox 執行環境; SM003 為長期 signer, SuperMonster003 為 runtime/security/release owner
* `相依項目` 鎖定 Chaquopy 17.0.0 及 CPython 3.13.9; 穩定 APK 與最終原始碼身分綁定並通過精確產物驗證

# v0.1.0-alpha.1

###### 2026/08/09

* `提示` R2 概念驗證原始碼. Gradle, APK, Binder 及裝置驗收尚未執行
* `新增` 獨立 Python 協議 V1 provider scaffold, 專用執行環境程序, 單一使用中工作階段及零 provider 佇列
* `新增` 單一原始碼 `__main__` 執行, 有界 stdout/stderr, 結構化例外及程序重啟式取消
* `新增` 固定次序的 10 種語言 README 與應用程式內更新記錄產生流程
* `相依項目` 預選 Chaquopy 17.0.0 及 Python 3.13; 封裝版本與相依性雜湊仍待建置驗證

##### 更多版本

* [CHANGELOG-zh-Hant-HK.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hant-HK.md)

******

### 驗證

******

不呼叫 Gradle 或 ADB 的檔案系統靜態檢查:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

使用本機 CPython 執行可攜式 bootstrap 語義測試:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

靜態及本機 CPython 檢查不能取代 Android 證據. 現有本機 RC 及單一裝置結果屬歷史證據; release acceptance 使用與精確身分直接綁定的建置, APK, Binder 及代表性裝置驗證.

******

### 建置

******

文件產生本身不執行建置. Release 設定會在協議 AAR, SHA-256, signer 或執行環境鎖漂移時 fail closed; 穩定產物只在綁定精確 release identity 時獲接受.

建置前必須在儲存庫 `libs` 目錄暫存並鎖定以下 release AAR:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

執行環境透過 Maven 鎖定 Chaquopy 17.0.0 及 CPython 3.13.9, 並只封裝 stdlib. Release gate 按精確身分核對相依性資料, native 程式庫, NOTICE, SM003 signer 及三種發行 APK. 目前樹已通過 API 37 x86_64 16 KB page 模擬器的聚焦冒煙; 這不等同完整相容性 gate 或裝置矩陣聲明.

******

### 授權條款

******

專案原始碼採用 MPL-2.0. Chaquopy, CPython 及其他第三方元件繼續適用各自授權條款; 歸屬, 上游原始碼及本專案原始碼取得說明見 `THIRD_PARTY_NOTICES.md`.

******

### 資源配置

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` 從固定次序的 JSON 來源產生 10 種語言的 README 與應用程式內更新記錄. Android 字串由各自資源目錄管理.

******

### 連結

******

- AutoJs6 文件: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
