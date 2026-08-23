<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>獨立 Python 執行環境外掛. 在專用外掛程序中執行 Python 指令碼</p>

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
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- 繁體中文 (台灣) [zh-Hant-TW] # 目前
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

Python Runtime 是獨立的 Python 協定 V1 provider. 宿主將單一 Python 原始碼快照交給專用外掛程序, 外掛使用 CPython 執行並回傳有界輸出, 結構化例外與唯一終態.

> 0.1.0 原始碼身分與精確 Host lock 已凍結. 既有本機 RC 的建置, APK, Binder 與一部 API 31 arm64-v8a 裝置證據仍屬歷史證據; 穩定 APK/P3 provenance 與精確 release identity 綁定, production receipt 是發布後的獨立證據層級.

******

### 功能

******

- 將一個 UTF-8 Python 原始碼快照當作 `__main__` 執行.
- 接收最大 1 MiB 的有限預置 stdin snapshot; snapshot 到達 EOF 後, 明確前景啟動可透過協定 1.3 的有界 prompt/reply 繼續內建 `input()`, 而標準庫 `getpass.getpass()` 使用隱藏回顯.
- 為已准入專案明確選擇 `entryMode=file|module`; module 模式使用標準 `runpy` 中繼資料、專案根目錄 `sys.path[0]` 與 package-relative import, file 模式保留一般指令碼語義.
- 從已准入專案根目錄 import 專案本地純 Python 套件與 `.dist-info` 中繼資料, 無須線上 pip 或執行期安裝.
- 在腳本執行期間依 stdout/stderr 原始順序透過有界 chunk 與 credit 傳送; credit 耗盡會對執行施加背壓.
- 透過協定 1.4 明確設定最大 64 KiB 的嚴格 JSON 結果, 並傳送最多 16 個具有路徑、大小與 SHA-256 限制的可選輸出 artifact; 絕不從 stdout 推斷結果.
- 透過協定 1.5 的執行級純資料 broker 即時呼叫 `toast`、`clip.get/set`、`app.launch/launch_app/open_url`、`device.info`、`console.log/warn/error`、權限感知 `notice`、有界 `files.read_text/write_text/exists/is_file/is_dir/list`、僅限前景的 `dialogs.alert/confirm/prompt/select`、`engines.current/run/stop_self`、有界 `automator.click/long_click/press/swipe/back/home`、有界 `selector.snapshot/find/click/set_text`、`images.capture_screen` 與 `images.find_color`, 終態後自動撤銷.
- 回傳 `SystemExit`, 語法錯誤與執行階段例外, 包含有界結構化 traceback.
- 同一執行環境程序只允許一個作用中工作階段, provider 端不排隊.
- 宿主無須重新啟動; 安裝或重新啟用後下一次新執行會重新發現並 pin provider 身分, 執行中的 Binder death 會終止該次執行且絕不自動重播.

******

### 執行環境與資料格式

******

協定 V1 目前宣告以下範圍:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

建置要求 Python 3.13. 已凍結的本機 RC 產物與精確裝置執行記錄為 CPython 3.13.9; 最終 0.1.0 在原始碼凍結後仍須重新核對版本與雜湊.

******

### 外掛介面

******

宿主透過以下識別資料探索並呼叫外掛:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.5
```

外掛接收獨立 SOURCE, 可選的有界 workspace archive, 最大 1 MiB 的有限預置 stdin snapshot, 以及協定 1.1 的唯讀宿主能力快照. 協定 1.2 為已准入專案加入明確 file/module 入口協商. 協定 1.3 在 snapshot EOF 後為內建 `input()` 加入由 Host 持有且僅限前景的 prompt/reply; 標準庫 `getpass.getpass()` 使用隱藏回顯. 協定 1.4 加入明確嚴格 JSON 結果與可選的 SHA-256 manifest 輸出 artifact, stdout 僅供診斷且絕不解析為結果. 協定 1.5 加入綁定單次執行、外掛 UID、呼叫序號與配額的純資料 Host capability broker. Host 對話框也要求由有效 Activity 支援的前景授權; 背景啟動不會開啟 UI, 而是穩定回傳 `INTERACTIVE_NOT_ALLOWED`. 直接 `sys.stdin` 始終有限, 背景啟動絕不開啟輸入 UI, 使用者指令碼也不會取得 Context、原始 Binder、宿主執行環境物件或 callback sink.

******

### 宿主整合狀態

******

> 0.1.0 只與 AutoJs6 6.8.0 配對, 最低 Host versionCode 已凍結並強制為 5275; 最終 clean Host 原始碼修訂與三件 AAR distribution manifest 已寫入 lock. 每次新執行都重新發現 provider; 缺失或停用時提示安裝或啟用且絕不 fallback, 安裝或重新啟用後無須重新啟動宿主. 穩定 APK 身分與該精確 Plugin 原始碼及 Host lock 綁定.

```text
release target: 0.4.0-alpha.4
release state: 0.4.0-alpha.4 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, and one-shot RGB find_color passed their enabled-service paths on the emulator and fail-closed on the physical device without changing its accessibility services; template image matching, OCR, later M3/M4 batches, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### 安全性與隱私

******

Chaquopy 執行環境只供可信本機指令碼使用, 並非 hostile-code sandbox. Exported service 要求宿主簽章權限並核對 UID, 套件與 signer; 獨立 Android UID, 專用程序與窄 Binder 邊界可降低宿主暴露, 但不會讓 Python 成為沙箱. SM003 是長期發行 signer, SuperMonster003 負責 runtime, security 與 release.

******

### 執行限制

******

- 原始碼最大 4 MiB, 總輸出最大 16 MiB, 每個輸出 chunk 最大 16 KiB, 最多 16384 個 chunk.
- 要求逾時最大 30 min, 同一程序最多一個作用中工作階段, provider 端不排隊.
- 專案 workspace 上限為壓縮後 64 MiB、8192 個檔案項目及解壓後 128 MiB; 分發前 Provider 選擇必須同時滿足 snapshot 的實際三維需求.
- SOURCE 描述元採用 Binder 接收端完整 PFD 所有權, 保留 reliable-pipe 錯誤通道, 並於終態或關閉時釋放.
- 輸出在執行期間依 credit 逐 chunk 傳送; credit 耗盡會暫停腳本, 已接受的輸出先於唯一終態, 終態後禁止輸出.
- 結構化 JSON 最大 64 KiB; 輸出 artifact 最多 16 個, 路徑最大 1024 UTF-8 bytes, 單個最大 4 MiB, 合計最大 8 MiB, Host 必須核對精確長度、EOF 與 SHA-256.
- 協定 1.5 每次執行最多 1024 次 Host 呼叫, 每個請求/回應最大 64 KiB, 文字最大 32 KiB, 一般 Host 主執行緒動作最多等待 5 s. Host files 使用最大 4 KiB 的相對路徑、最大 32 KiB 的 UTF-8 文字, 每次最多列出 128 個名稱, 每個最大 255 UTF-8 bytes. 前景對話框標題最大 256 UTF-8 bytes, 內容最大 4 KiB, prompt 預設值/回覆最大 32 KiB, select 最多 64 項、每項最大 1 KiB、合計最大 32 KiB, 單次使用者回應最多等待 5 min. 每次執行最多成功非同步啟動 16 個限定根目錄內的非 Python Host 子指令碼; 巢狀 Python 傳回 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self` 透過程序重啟取消自身.
- Automator 座標只接受 0 到 1000000 的嚴格整數, press 與 swipe 持續時間為 1 ms 到 4 s; Host 無障礙不可用時拋出 `CapabilityUnavailableError`, 不開啟設定.
- Selector snapshot 最多接受 128 個節點、深度 32 及 48 KiB JSON; find 最多掃描 1024 個節點, 節點文字上限為 256 Unicode code points, 查詢文字上限為 1024 UTF-8 bytes, set_text 上限為 4 KiB, 每次執行最多保留 128 個節點參照. 掃描不完整時回傳 `SELECTOR_SCAN_LIMIT_EXCEEDED`, 參照過期時回傳 `STALE_NODE`.
- 螢幕擷取每次執行最多保留 1 張, 單張編碼後最大 4 MiB, 以 32 KiB 原始區塊傳輸, 單邊最大 8192 像素且總計最多 16777216 像素. Python 在回傳前核對長度、順序、EOF、SHA-256 與格式簽章; 無障礙/API 不可用拋出 `CapabilityUnavailableError`, 其他穩定錯誤包括 `SCREEN_CAPTURE_FAILED`、`RESULT_LIMIT_EXCEEDED` 與 `STALE_IMAGE`. 找色在一張最新擷取畫面內依列優先掃描, 支援有界可選區域及最大 255 的逐通道閾值, 只傳回座標或未命中且不傳輸影像位元組.
- 取消模式為程序重啟, 而非 CPython 級協作取消; 原生擴充套件或阻塞呼叫仍需後續 Android 驗證.
- 外掛已授予 `INTERNET` 以支援腳本透過標準函式庫直接連線; 仍不支援線上 pip、自動下載程式碼或執行期安裝第三方套件.

******

### 未宣告的能力

******

- 不提供通用即時 stdin 或直接 `sys.stdin` callback streaming. 前景互動僅適用於最大 1 MiB 的有限 snapshot 到達 EOF 後的內建 `input()` 與標準庫 `getpass.getpass()`. 仍不支援 workspace 寫回, 線上 pip 或執行階段下載 wheel.
- 不提供 UI 指令碼, 偵錯器, REPL 或任意宿主 Java 物件存取.
- 即時 broker 已涵蓋完整首批低風險能力、有界 Host files、前景對話框、有界 engines、明確座標/全域 automator 動作、有界 selector/UI 樹快照與動作、有界螢幕擷取及有界 `find_color`; `find_image`、模板上傳與 OCR 仍未宣告.
- 不宣告 32 位元 Android 支援, 也不保證任何第三方 native wheel 可用.
- 目前樹已有 API 31 arm64-v8a 實機冒煙證據與 API 37 x86_64 16 KB page 模擬器冒煙證據; 兩者都不冒充完整裝置矩陣或發行資格.

******

### 路線圖

******

M4 路徑 A 已完成, M3 自動化現已透過 Host 無障礙接通有界座標/全域動作、有界 selector/UI 樹資料面、有界螢幕擷取及單次 RGB 找色. 模板找圖、OCR 與 M4 建置期/native 套件路徑依使用者價值繼續推進; 歷史證據工具保留但不作自動發佈門禁.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本記錄

******

# v0.4.0-alpha.4

###### 2026/08/24

* `提示` 目前樹第四個 M3 自動化 alpha 候選; 有界螢幕找色已在啟用無障礙的 API 37 模擬器通過, API 31 實體裝置在不改變既有無障礙服務的前提下通過 fail-closed; 模板找圖、OCR、發佈及完整裝置矩陣仍不在本次聲明範圍
* `新增` 新增 `autojs6.images.find_color(color, *, region=None, threshold=0)`, 接受嚴格 RGB 整數或 `#RRGGBB` 文字、可選有界區域, 傳回座標或 `None`
* `改善` 每次呼叫只擷取一張最新 Android 11+ 無障礙畫面, 以確定性 row-major 順序和 0..255 逐通道閾值掃描, 驗證精確 `autojs6-python-color-match-v1`, 不向 Python 傳輸影像位元組或控制代碼

# v0.4.0-alpha.3

###### 2026/08/24

* `提示` 目前樹第三個 M3 自動化 alpha 候選; Android 11+ 有界螢幕擷取完整路徑已在啟用無障礙的 API 37 模擬器通過聚焦驗收, API 31 實體裝置在不變更既有無障礙服務的前提下通過 fail-closed; 找圖找色、OCR、發布及完整裝置矩陣仍不在本次宣告範圍
* `新增` 新增 `autojs6.images.capture_screen`, 以 PNG/JPEG 回傳經驗證的編碼位元組, 或原子寫入並發布執行輸出成品
* `改善` 每次執行最多保留 1 張擷取, 以 32 KiB 原始區塊傳輸且編碼後最多 4 MiB; Python 核對順序、EOF、SHA-256 與格式簽章並一律 release, Host 在替換/釋放/終態清零, 失敗使用穩定錯誤且不啟用服務、不開啟設定

# v0.4.0-alpha.2

###### 2026/08/24

* `提示` 目前樹第二個 M3 自動化 alpha 候選; 完整有界 selector/UI 樹路徑已在啟用無障礙的 API 37 模擬器通過聚焦驗收, API 31 實體裝置在不變更既有無障礙服務的前提下通過 fail-closed; 截圖, OCR, 發布及完整裝置矩陣仍不在本次宣告範圍
* `新增` 新增即時 `autojs6.selector.snapshot/find/click/set_text` API, 透過不透明的執行級節點參照提供分離的無障礙樹純資料, AND 組合首次符合查詢及明確動作
* `改善` 限制快照節點, 深度, 載荷及節點文字, 選擇器掃描規模, 查詢/設定文字與保留節點; 掃描不完整傳回 `SELECTOR_SCAN_LIMIT_EXCEEDED`, 參照過期傳回 `STALE_NODE`, 無障礙不可用時不開啟設定並拋出 `CapabilityUnavailableError`

##### 更多版本

* [CHANGELOG-zh-Hant-TW.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-zh-Hant-TW.md)

******

### 驗證

******

不呼叫 Gradle 或 ADB 的檔案系統靜態檢查:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

使用本機 CPython 執行可攜式 bootstrap 語意測試:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

靜態與本機 CPython 檢查不能取代 Android 證據. 現有本機 RC 與單一裝置結果屬歷史證據; release acceptance 使用與精確身分直接綁定的建置, APK, Binder 與代表性裝置驗證.

******

### 建置

******

文件產生本身不執行建置. Release 設定會在協定 AAR, SHA-256, signer 或執行環境鎖漂移時 fail closed; 穩定產物只在綁定精確 release identity 時獲接受.

建置前必須在儲存庫 `libs` 目錄暫存並鎖定以下 release AAR:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

執行環境透過 Maven 鎖定 Chaquopy 17.0.0 與 CPython 3.13.9, 並只封裝 stdlib. Release gate 按精確身分核對相依性資料, native 程式庫, NOTICE, SM003 signer 與三種發行 APK. 目前樹已通過 API 37 x86_64 16 KB page 模擬器的聚焦冒煙; 這不等同完整相容性 gate 或裝置矩陣聲明.

******

### 授權條款

******

專案原始碼採用 MPL-2.0. Chaquopy, CPython 與其他第三方元件繼續適用各自授權條款; 歸屬, 上游原始碼與本專案原始碼取得說明見 `THIRD_PARTY_NOTICES.md`.

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

`.python/generate_markdown.py` 從固定順序的 JSON 來源產生 10 種語言的 README 與應用程式內更新記錄. Android 字串由各自資源目錄管理.

******

### 連結

******

- AutoJs6 文件: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
