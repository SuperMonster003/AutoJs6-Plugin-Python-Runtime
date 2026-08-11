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

> 目前只是 R2 概念驗證. 執行環境原始碼及本機 bootstrap 語義檢查已完成, 但尚未執行 Gradle 設定, Android 編譯, APK 檢查, Binder 驗證或裝置驗收.

******

### 功能

******

- 將一個 UTF-8 Python 原始碼快照作為 `__main__` 執行.
- 按原始次序收集 stdout 和 stderr, 再透過有界 chunk 與 credit 傳送.
- 傳回 `SystemExit`, 語法錯誤和執行階段例外, 包括有界結構化 traceback.
- 同一執行環境程序只允許一個使用中工作階段, provider 端不排隊.
- 取消, 逾時, callback 死亡及需要隔離的關閉路徑會淘汰專用程序, 且不會自動重播指令碼.

******

### 執行環境與資料格式

******

協議 V1 目前聲明以下範圍:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

建置要求 Python 3.13. 3.13.9 是根據目前 Chaquopy 發佈資料記錄的預期封裝版本, 在 APK 分析及裝置執行完成前不視為已驗證事實.

******

### 外掛程式介面

******

宿主透過以下識別資料探索及呼叫外掛程式:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

外掛程式只接收 SOURCE 描述元. workspace archive 與 stdin snapshot 的上限均為零, 亦不會向指令碼注入 Context, Binder, 宿主執行環境物件或 callback sink.

******

### 宿主整合狀態

******

> 協議及宿主接線路線圖正在推進, 但本儲存庫所需的 release AAR 尚未發佈及驗證. 只安裝目前 scaffold 並不能建立可用的端對端 Python 引擎.

******

### 安全性與私隱

******

原始碼 manifest 不要求 Android 權限. Exported service 要求宿主簽署權限, 並在 Binder 入口重新核對呼叫 UID, 已安裝宿主套件及目前簽署集合. Python 透過 Chaquopy 仍可存取 Java bridge, 因此本外掛程式依賴獨立 Android UID, 專用程序與窄 Binder 能力邊界, 不會把 CPython 聲明為安全沙箱.

******

### 執行限制

******

- 原始碼最大 4 MiB, 總輸出最大 4 MiB, 每個輸出 chunk 最大 16 KiB, 最多 4096 個 chunk.
- 要求逾時最大 60 s, 同一程序最多一個使用中工作階段, provider 端不排隊.
- SOURCE 描述元採用 Binder 接收端完整 PFD 擁有權, 保留 reliable-pipe 錯誤通道, 並在終態或關閉時釋放.
- 輸出目前先在外掛程式內有界緩衝, 再按 credit 傳送; 尚未聲明執行期間的串流背壓.
- 取消模式是程序重啟, 而非 CPython 級協作取消; 原生擴充套件或阻塞呼叫仍需後續 Android 驗證.
- stdlib-only 政策禁止線上 pip 及第三方 Python 套件, 合併後的 APK 權限仍須由建置閘門覆核.

******

### 未聲明的能力

******

- 不支援 workspace archive, stdin snapshot, 線上 pip 或執行階段下載 wheel.
- 不提供 UI 指令碼, 除錯器, REPL 或任意宿主 Java 物件存取.
- 不提供 AutoJs6 能力 broker; console, 檔案, 裝置, 輔助功能, shell 等宿主 API 尚未接入.
- 不聲明 32 位元 Android 支援, 亦不保證任何第三方 native wheel 可用.
- 不會把本機 CPython 單元測試視為 Chaquopy, Android, Binder 或裝置驗收證據.

******

### 路線圖

******

R2 的獨立儲存庫, 靜態邊界, provider/bootstrap 原始碼及本機語義測試已完成. 因 QV710AF65F 正進行受保護 soak, 所有 Gradle 與 ADB 工作暫緩. release AAR, 相依性解析, Android 編譯, APK/16 KB page 檢查, Binder/PFD 驗證及裝置矩陣仍未完成; 勾選狀態以專案路線圖為準.

- [檢視 ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 版本記錄

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

使用本機 CPython 執行可攜式 bootstrap 語義測試:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

這兩項檢查都不能證明 Android runtime 可用. Gradle, APK, Binder 與裝置驗證必須在受保護 soak 完成後另行補齊.

******

### 建置

******

目前不執行建置. Release 設定會在協議 AAR 缺失或 SHA-256 尚未鎖定時 fail closed.

建置前必須在儲存庫 `libs` 目錄暫存並鎖定以下 release AAR:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

執行環境計劃透過 Maven 使用 Chaquopy 17.0.0, 並只封裝 stdlib. 相依性驗證中繼資料, native 程式庫清單, 授權義務及 16 KB page 相容性仍屬建置驗收項目.

******

### 授權條款

******

專案原始碼採用 MPL-2.0. Chaquopy, CPython 及其他第三方元件繼續適用各自授權條款.

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
