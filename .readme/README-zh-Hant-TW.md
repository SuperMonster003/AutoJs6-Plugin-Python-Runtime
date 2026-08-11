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
- 依原始順序收集 stdout 與 stderr, 再透過有界 chunk 與 credit 傳送.
- 回傳 `SystemExit`, 語法錯誤與執行階段例外, 包含有界結構化 traceback.
- 同一執行環境程序只允許一個作用中工作階段, provider 端不排隊.
- 宿主無須重新啟動; 安裝或重新啟用後下一次新執行會重新發現並 pin provider 身分, 執行中的 Binder death 會終止該次執行且絕不自動重播.

******

### 執行環境與資料格式

******

協定 V1 目前宣告以下範圍:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
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
protocol: 1.0-1.1
```

外掛接收獨立 SOURCE, 可選的有界 workspace archive, 以及協定 1.1 的唯讀宿主能力快照; stdin snapshot 仍關閉. 外掛不會向指令碼注入 Context, Binder, 宿主執行環境物件或 callback sink.

******

### 宿主整合狀態

******

> 0.1.0 只與 AutoJs6 6.8.0 配對, 最低 Host versionCode 已凍結並強制為 5275; 最終 clean Host 原始碼修訂與三件 AAR distribution manifest 已寫入 lock. 每次新執行都重新發現 provider; 缺失或停用時提示安裝或啟用且絕不 fallback, 安裝或重新啟用後無須重新啟動宿主. 穩定 APK 身分與該精確 Plugin 原始碼及 Host lock 綁定.

```text
release target: 0.1.0
release state: stable 0.1.0 source identity frozen by the clean VERSION_BUILD=11 commit with the exact Host 6.8.0/5275 lock
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- 原始碼最大 4 MiB, 總輸出最大 4 MiB, 每個輸出 chunk 最大 16 KiB, 最多 4096 個 chunk.
- 要求逾時最大 60 s, 同一程序最多一個作用中工作階段, provider 端不排隊.
- SOURCE 描述元採用 Binder 接收端完整 PFD 所有權, 保留 reliable-pipe 錯誤通道, 並於終態或關閉時釋放.
- 輸出目前先在外掛內有界緩衝, 再依 credit 傳送; 尚未宣告執行期間的串流背壓.
- 取消模式為程序重啟, 而非 CPython 級協作取消; 原生擴充套件或阻塞呼叫仍需後續 Android 驗證.
- stdlib-only 政策禁止線上 pip 與第三方 Python 套件, 合併後的 APK 權限仍須由建置閘門複核.

******

### 未宣告的能力

******

- 不支援 stdin snapshot, workspace 寫回, 線上 pip 或執行階段下載 wheel.
- 不提供 UI 指令碼, 偵錯器, REPL 或任意宿主 Java 物件存取.
- 不提供即時 AutoJs6 能力 broker; 首批 API 只使用執行開始時凍結的 app/device/execution/project 快照與外掛私有 workspace 的有界唯讀檔案介面.
- 不宣告 32 位元 Android 支援, 也不保證任何第三方 native wheel 可用.
- arm64-v8a 有 API 31 裝置證據; x86_64 目前只有封裝證據, 不會冒充裝置執行或完整裝置矩陣.

******

### 路線圖

******

R6-P2/P3 的本機 RC 與集中裝置證據保留為歷史記錄. 本次 clean VERSION_BUILD=11 freeze commit 固定了穩定 Plugin 原始碼身分與精確 Host 6.8.0/5275 lock; 穩定 APK provenance 按這些精確身分驗證, 任何 production receipt 也必須使用相同依據. 完整 API×ABI 矩陣與新 soak 不屬自動門禁.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本記錄

******

# v0.1.0

###### 2026/08/12

* `提示` 0.1.0 固定了穩定 Plugin 原始碼身分與精確 Host 6.8.0/5275 lock
* `新增` 面向 AutoJs6 6.8.0 / versionCode 5275 的 Python 協定 1.0-1.1, 有界專案 workspace 與唯讀 app/device/execution/project 能力快照
* `新增` 無須重新啟動 Host 的熱插拔: 安裝或重新啟用後下一次新執行重新發現並 pin 身分, 缺失或停用時絕不 fallback
* `新增` 執行中的 Binder death 終止目前執行且不得重播, 後續新執行重新發現 provider
* `改善` 將 Chaquopy 固定為 trusted-local, non-sandbox 執行環境; SM003 為長期 signer, SuperMonster003 為 runtime/security/release owner
* `相依性` 鎖定 Chaquopy 17.0.0 與 CPython 3.13.9; 穩定 APK 與最終原始碼身分綁定並通過精確產物驗證

# v0.1.0-alpha.1

###### 2026/08/09

* `提示` R2 概念驗證原始碼. Gradle, APK, Binder 與裝置驗收尚未執行
* `新增` 獨立 Python 協定 V1 provider scaffold, 專用執行環境程序, 單一作用中工作階段與零 provider 佇列
* `新增` 單一原始碼 `__main__` 執行, 有界 stdout/stderr, 結構化例外與程序重啟式取消
* `新增` 固定順序的 10 種語言 README 與應用程式內更新記錄產生流程
* `相依性` 預選 Chaquopy 17.0.0 與 Python 3.13; 封裝版本和相依性雜湊仍待建置驗證

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

執行環境透過 Maven 鎖定 Chaquopy 17.0.0 與 CPython 3.13.9, 並只封裝 stdlib. Release gate 按精確身分核對相依性資料, native 程式庫, 16 KB page, NOTICE, SM003 signer 與三種發行 APK.

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
