******

### 版本記錄

******

# v0.2.0-alpha.1

###### 2026/08/13

* `提示` 0.1 之後的 U1 current-tree alpha 候選; U1-R2 module entry、live output、前台內置 input、明確結構化 JSON 及有界輸出 artifact 只完成至 E2, 後台啟動及直接 sys.stdin 仍非互動, R2 E3 尚未完成, 且這些目前樹結果不屬於裝置矩陣/發佈/公開證據
* `新增` 新增最大 1 MiB 的有限預先提供 stdin snapshot, 為 `input()` 及 `sys.stdin` 提供確定輸入和 EOF
* `新增` 完善專案 import 語義, 支援 workspace 模組, 巢狀入口同層及根模組與 package-relative import
* `新增` 新增協議 1.2 明確 `entryMode=file|module`; module 執行透過 `runpy` 提供正確的 `__package__`、`__spec__`、項目根目錄 `sys.path[0]` 及相對 import, file 模式維持不變
* `新增` 新增協議 1.3: 有限 snapshot 到達 EOF 後, 只有前台內置 `input()` 使用有界 prompt/reply; 後台啟動絕不開啟輸入 UI, 直接 `sys.stdin` 始終有限
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
