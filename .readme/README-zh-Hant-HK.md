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
- 從已准入項目根目錄 import 項目本地純 Python 套件及 `.dist-info` 元數據, 毋須線上 pip 或執行時安裝.
- 在腳本執行期間按 stdout/stderr 原始次序透過有界 chunk 與 credit 傳送; credit 用盡會對執行施加背壓.
- 透過協議 1.4 明確設定最大 64 KiB 的嚴格 JSON 結果, 並傳送最多 16 個具有路徑、大小及 SHA-256 限制的可選輸出 artifact; 絕不從 stdout 推斷結果.
- 透過協議 1.5 的執行級純數據 broker 即時呼叫 `toast`、`clip.get/set`、`app.launch/launch_app/open_url`、`device.info`、`console.log/warn/error`、權限感知 `notice`、有界 `files.read_text/write_text/exists/is_file/is_dir/list`、僅限前台的 `dialogs.alert/confirm/prompt/select`、`engines.current/run/stop_self`、有界 `automator.click/long_click/press/swipe/back/home`、有界 `selector.snapshot/find/click/set_text`、`images.capture_screen`、`images.find_color`、`images.find_image` 及 `ocr.recognize`, 終態後自動撤銷.
- 協議 1.6 透過 `executionMode=long-running` 為明確前台項目加入無執行 deadline 的長任務模式, 由 Host 前台通知及 Stop action 維持生命週期, Provider 每 15 s 發佈有序心跳; 後台入口會穩定拒絕且絕不降級.
- 配對 Host 在 Provider 探索前以公平 FIFO 准入並發 Python 啟動: 1 個 active owner 及最多 32 個 waiter; queued Stop 可中斷, 已 dispatch 代際最多等待 3 s Binder 退出後交接, Provider 仍維持單會話且無隊列.
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
protocol: 1.0-1.6
```

外掛程式接收獨立 SOURCE, 可選的有界 workspace archive, 最大 1 MiB 的有限預置 stdin snapshot, 以及協議 1.1 的唯讀宿主能力快照. 協議 1.2 為已准入項目加入明確 file/module 入口協商. 協議 1.3 在 snapshot EOF 後為內置 `input()` 加入由 Host 持有且僅限前台的 prompt/reply; 標準庫 `getpass.getpass()` 使用隱藏回顯. 協議 1.4 加入明確嚴格 JSON 結果及可選的 SHA-256 manifest 輸出 artifact, stdout 只供診斷且絕不解析為結果. 協議 1.5 加入綁定單次執行、外掛 UID、呼叫次序及配額的純數據 Host capability broker. Host 對話框亦要求由有效 Activity 支援的前台授權; 後台啟動不會開啟 UI, 而是穩定回傳 `INTERACTIVE_NOT_ALLOWED`. 直接 `sys.stdin` 始終有限, 後台啟動絕不開啟輸入 UI, 使用者指令碼亦不會取得 Context、原始 Binder、宿主執行環境物件或 callback sink.

******

### 宿主整合狀態

******

> 0.1.0 只與 AutoJs6 6.8.0 配對, 最低 Host versionCode 已凍結並強制為 5275; 最終 clean Host 原始碼修訂及三件 AAR distribution manifest 已寫入 lock. 每次新執行均重新發現 provider; 缺失或停用時提示安裝或啟用且絕不 fallback, 安裝或重新啟用後毋須重新啟動宿主. 0.5.0-alpha.6 為部分 OEM 首次安裝後的 stopped/notLaunched 狀態提供 Plugin Center ACTIVATE/WakeActivity 復原路徑. Host 與 Plugin APK 必須使用同一 signer; debug Host 與 production Plugin 混合安裝會穩定拒絕為 PYTHON_RUNTIME_PROVIDER_UNTRUSTED. 穩定 APK 身分與該精確 Plugin 原始碼及 Host lock 綁定.

```text
release target: 0.5.0
release state: 0.5.0 stable source candidate; protocol 1.0-1.6 and cumulative M1-M5 capabilities remain frozen with the embedded runtime stdlib-only; the exact SM003-signed 0.5.0-beta.1 arm64 APK from commit 4bbae75dbfb496995e5278684024f63ae9f71a43 was pulled from QV710AF65F with SHA-256 80FA480ACAE1C66C07DC59C9B588603B7F787E21DE72BB5A5521A2732B0C695F, byte-identical to the formal candidate, and passed all ten manual Android smoke items (10/10 PASS); the preceding exact alpha run and a matching Android-Debug run on OnePlus OPD2413 also passed 10/10, including OEM ACTIVATE recovery; deterministic item 2/3/4 materials live in examples/python/m6_manual_smoke; a stable signed artifact, exact stable smoke, stable tag, push, publication, and post-publication evidence remain outside this source claim
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
- 有界要求逾時最大 30 min. 明確長任務不設執行 deadline, 但必須維持 Host 前台生命週期、2 min 啟動租約及 45 s 心跳租約; 同一程序仍最多一個使用中工作階段, provider 端不排隊.
- 項目 workspace 上限為壓縮後 64 MiB、8192 個檔案條目及解壓後 128 MiB; 分發前 Provider 選擇必須同時滿足 snapshot 的實際三維需求.
- SOURCE 描述元採用 Binder 接收端完整 PFD 擁有權, 保留 reliable-pipe 錯誤通道, 並在終態或關閉時釋放.
- 輸出在執行期間按 credit 逐 chunk 傳送; credit 用盡會暫停腳本, 已接受的輸出先於唯一終態, 終態後禁止輸出.
- 結構化 JSON 最大 64 KiB; 輸出 artifact 最多 16 個, 路徑最大 1024 UTF-8 bytes, 每個最大 4 MiB, 合計最大 8 MiB, Host 必須核對精確長度、EOF 及 SHA-256.
- 協議 1.5 每次執行最多 1024 次 Host 呼叫, 每個要求/回應最大 64 KiB, 文字最大 32 KiB, 一般 Host 主線程動作最多等待 5 s. Host files 使用最大 4 KiB 的相對路徑、最大 32 KiB 的 UTF-8 文字, 每次最多列出 128 個名稱, 每個最大 255 UTF-8 bytes. 前台對話框標題最大 256 UTF-8 bytes, 內容最大 4 KiB, prompt 預設值/回覆最大 32 KiB, select 最多 64 項、每項最大 1 KiB、合計最大 32 KiB, 單次使用者回應最多等待 5 min. 每次執行最多成功非同步啟動 16 個限定根目錄內的非 Python Host 子指令碼; 巢狀 Python 返回 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self` 透過程序重啟取消自身.
- Automator 座標只接受 0 至 1000000 的嚴格整數, press 及 swipe 持續時間為 1 ms 至 4 s; Host 無障礙不可用時拋出 `CapabilityUnavailableError`, 不開啟設定.
- Selector snapshot 最多接受 128 個節點、深度 32 及 48 KiB JSON; find 最多掃描 1024 個節點, 節點文字上限為 256 Unicode code points, 查詢文字上限為 1024 UTF-8 bytes, set_text 上限為 4 KiB, 每次執行最多保留 128 個節點引用. 掃描不完整時返回 `SELECTOR_SCAN_LIMIT_EXCEEDED`, 引用過期時返回 `STALE_NODE`.
- 螢幕截圖每次執行最多保留 1 張, 單張編碼後最大 4 MiB, 以 32 KiB 原始區塊傳輸, 單邊最大 8192 像素且總計最多 16777216 像素. Python 在返回前核對長度、順序、EOF、SHA-256 及格式簽名; 無障礙/API 不可用拋出 `CapabilityUnavailableError`, 其他穩定錯誤包括 `SCREEN_CAPTURE_FAILED`、`RESULT_LIMIT_EXCEEDED` 及 `STALE_IMAGE`. 找色在一張最新截圖內按行優先掃描, 支援有界可選區域及最大 255 的逐通道閾值, 只返回座標或未命中且不傳輸圖像字節. 模板找圖每次執行最多保留 1 個 PNG/JPEG 模板, 最大 1 MiB, 以 24 KiB 原始區塊上傳; 單邊最大 2048, 面積最大 1048576, 搜尋區域最大 4194304, 比較次數最大 16777216; 僅全不透明像素參與匹配, 其餘為通配, 按 row-major 確定性掃描, 終態釋放並清零緩衝區.
- `ocr.recognize` 重用最大 1 MiB、24 KiB 原始區塊、單邊 2048 像素及解碼後 1048576 像素的 PNG/JPEG 模板信封. 已配置的 Host OCR 引擎在現有 60 s 准入/呼叫預算內最多返回 256 行, 每行 4 KiB 嚴格 UTF-8, 合計 48 KiB; 引擎不可用及執行失敗分別報告 `OCR_UNAVAILABLE` 及 `OCR_FAILED`, 上傳始終釋放並清零.
- 取消模式是程序重啟, 而非 CPython 級協作取消; 原生擴充套件或阻塞呼叫仍需後續 Android 驗證.
- 插件已授予 `INTERNET` 以支援腳本透過標準庫直接連線; 仍不支援線上 pip、自動下載程式碼或執行時安裝第三方套件.

******

### 未聲明的能力

******

- 不提供通用即時 stdin 或直接 `sys.stdin` callback streaming. 前台互動只適用於最大 1 MiB 的有限 snapshot 到達 EOF 後的內置 `input()` 與標準庫 `getpass.getpass()`. 仍不支援 workspace 寫回, 線上 pip 或執行階段下載 wheel.
- 不提供 UI 指令碼, 除錯器, REPL 或任意宿主 Java 物件存取.
- 即時 broker 已涵蓋完整首批低風險能力、有界 Host files、前台對話框、有界 engines、顯式座標/全域 automator 動作、有界 selector/UI 樹快照與動作、有界螢幕截圖、`find_color`、`find_image` 及行級 OCR. OCR 檢測框/置信度/選項、可變圖像處理及多尺度匹配仍未聲明.
- 不聲明 32 位元 Android 支援, 亦不保證任何第三方 native wheel 可用.
- 目前樹已有 API 31 arm64-v8a 真機冒煙證據與 API 37 x86_64 16 KB page 模擬器冒煙證據; 兩者都不冒充完整裝置矩陣或發行資格.

******

### 路線圖

******

M4 路徑 A 已完成; M4 路徑 B 與 Path C 評估均以 `NOT_ADMITTED` 關閉, 內置 runtime 保持 `stdlib-only`. Path C 的 Pillow/NumPy 可離線構建, 但完整 native 閉包未通過雙 ABI 16 KiB ELF 門禁, OpenCV 沒有 `cp313` Android wheel; 路徑 D 只在有明確需求時啟動. M3 自動化已接通有界動作、selector/UI 樹、截圖、找色、PNG/JPEG 模板找圖與 Host OCR. 歷史證據工具不作自動發佈門禁.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本記錄

******

# v0.5.1

###### 2026/09/12

* `修正` 執行 clean 後 Chaquopy 混淆規則檔案遺失導致 Release 構建失敗的問題
* `改善` 建置階段校驗 64 位原生程式庫的 16 KB 頁面大小對齊, 檢查 manifest 契約並輸出 JSON 報告

# v0.5.0

###### 2026/08/25

* `提示` 0.5.0 累計穩定版原始碼候選; 精確 SM003 簽署的 beta 候選已通過 10 項 Android 冒煙測試, 尚不聲明穩定 APK、tag 或 publication 完成
* `新增` M6 彙總 M1-M5 能力與可重用的 2/3/4 測試材料, 固定 alpha → beta → stable 的輕量候選及發佈邊界
* `改善` 從 QV710AF65F 回拉的 0.5.0-beta.1 arm64 APK 與正式候選逐位元組一致, 第二輪完整十項清單結果為 10/10 PASS

# v0.5.0-beta.1

###### 2026/08/25

* `提示` 0.5.0-beta.1 功能凍結原始碼候選; 精確 SM003 簽署的 alpha 候選已通過 10 項 Android 冒煙測試, 尚不聲明 beta APK、穩定版或 publication 完成
* `新增` M6 新增可重用的 2/3/4 測試專案與獨立 artifact 驗證材料, 讓匯入、stdin/互動輸入和結構化結果可重複驗收
* `改善` 從 QV710AF65F 回拉的 0.5.0-alpha.6 arm64 APK 與正式候選逐位元組一致, 完整十項清單結果為 10/10 PASS

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


[16 KB page alignment and build verification](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/docs/16kb.md)
