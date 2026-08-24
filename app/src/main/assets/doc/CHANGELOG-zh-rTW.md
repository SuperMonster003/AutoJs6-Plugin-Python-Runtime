******

### 版本記錄

******

# v0.4.0-alpha.6

###### 2026/08/24

* `提示` 第六個 M3 automation current-tree alpha 候選版; 已設定 Host OCR 的正向辨識在具備合格服務的 API 37 模擬器通過, API 31 實機在不變更其無障礙服務的前提下完成故障關閉; 更豐富的 OCR、發佈及完整裝置矩陣不在本聲明範圍內
* `新增` 新增 `autojs6.ocr.recognize(image)`, 接受有界 PNG/JPEG 位元組, 並從已設定 Host OCR 引擎回傳有序不可變文字行 tuple
* `改善` 重用 1 MiB PNG/JPEG 上傳、24 KiB 原始分塊與 SHA-256 驗證, 僅選擇已啟用、已授權且相容的 Host OCR 服務, 結果限制為 256 行、每行 4 KiB 嚴格 UTF-8、合計 48 KiB, 一律 release 並清零緩衝區, 以穩定 `OCR_UNAVAILABLE` 或 `OCR_FAILED` 回報失敗

# v0.4.0-alpha.5

###### 2026/08/24

* `提示` 目前樹第五個 M3 自動化 alpha 候選; 有界模板找圖已在啟用無障礙的 API 37 模擬器通過, API 31 實體裝置在不改變既有無障礙服務的前提下通過 fail-closed; OCR、發布及完整裝置矩陣仍不在本次聲明範圍
* `新增` 新增 `autojs6.images.find_image(template, *, region=None, threshold=0)`, 接受 PNG/JPEG 位元組與可選有界區域, 回傳左上角座標或 `None`
* `改善` 每次執行上傳一個最大 1 MiB 的模板, 以 24 KiB 原始區塊傳輸並核對 SHA-256, 單邊解碼不超過 2048 像素, 依 row-major 確定性掃描並核對 `autojs6-python-image-match-v1`; 僅全不透明像素參與、其餘為通配, 無需 OpenCV, 一律 release 並清零緩衝區, 且僅對 Android 333 ms 截圖節流執行有界 350 ms 等待重試

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

# v0.4.0-alpha.1

###### 2026/08/23

* `提示` 首個 M3 自動化 current-tree alpha 候選; 有界座標/全域動作已在啟用無障礙的 API 37 模擬器通過聚焦驗收, API 31 實體裝置在不變更既有無障礙服務下通過 fail-closed, selector/UI 樹、截圖、OCR、發佈與完整裝置矩陣不在本次聲明範圍
* `新增` 新增經 Host 無障礙執行的即時 `autojs6.automator.click/long_click/press/swipe/back/home` API, 回傳動作實際分派結果布林值
* `改善` 座標只接受 0 到 1000000 的非布林嚴格整數, press/swipe 持續時間只接受 1 到 4000 ms; Host 無障礙不可用時拋出 `CapabilityUnavailableError`, 不開啟設定

# v0.3.0-alpha.6

###### 2026/08/23

* `提示` 首個 M4 current-tree alpha 候選; 專案本地純 Python 相依套件路徑已通過雙裝置聚焦驗收, 後續 M3/M4 批次、發佈與完整裝置矩陣不在本次聲明範圍
* `新增` 支援從已准入專案根目錄匯入專案本地純 Python 套件與 `.dist-info` 中繼資料, 提供鎖定版本的 `requests` 可重現範例, 且不引入執行期安裝器
* `改善` 將專案 workspace 上限提高至壓縮 64 MiB、8192 個檔案項目與解壓 128 MiB, 分發前依 snapshot 實際三維需求比對 Provider 能力; 缺失 import 仍拋出 `ModuleNotFoundError`, 不觸發線上 pip 或引擎回復

# v0.3.0-alpha.5

###### 2026/08/23

* `提示` M3 第五個 current-tree alpha 候選; 第二批有界 Host engines 能力已通過雙裝置聚焦驗收, 後續能力、公開發行與完整裝置矩陣不在本項宣告範圍
* `新增` 新增即時 `autojs6.engines.current/run/stop_self` API, 提供不含絕對路徑的目前引擎資訊、非 Python Host 子指令碼非同步啟動與確定性停止自身
* `改善` 子指令碼僅接受執行根目錄內的正規化相對路徑且每次執行最多成功啟動 16 個; 巢狀 Python 穩定傳回 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self` 透過 provider 程序重啟取消目前執行

# v0.3.0-alpha.4

###### 2026/08/23

* `提示` M3 第四個 current-tree alpha 候選; 前景 Host 對話框已通過雙裝置聚焦驗收, 引擎、後續能力、公開發行與完整裝置矩陣不在本項宣告範圍
* `新增` 新增僅限前景的 `autojs6.dialogs.alert/confirm/prompt/select` API, 分別回傳確認完成、布林選擇、可空文字與從零開始的可空選項索引
* `改善` 限制對話框標題、內容、回覆與選項, 依序顯示單一 Host 擁有的對話框, 背景啟動不會開啟 UI 並穩定回傳 `INTERACTIVE_NOT_ALLOWED`

# v0.3.0-alpha.3

###### 2026/08/23

* `提示` M3 第三個 current-tree alpha 候選; 第二批有界 Host files 能力已通過雙裝置聚焦驗收, 對話框、引擎、後續能力、公開發行與完整裝置矩陣不在本項宣告範圍
* `新增` 新增即時 `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` API, 在目前專案根目錄或單檔指令碼目錄內進行有界 UTF-8 文字存取
* `改善` 拒絕不安全或越界路徑, 限制文字與直接目錄列舉, 回傳穩定檔案錯誤, 並明確區分即時 Host 根目錄與凍結的外掛 workspace snapshot

# v0.3.0-alpha.2

###### 2026/08/23

* `提示` M3 第二個 current-tree alpha 候選; 完整首批低風險 Host 能力已實作, 後續能力批次、公開發行與完整裝置矩陣不在本項宣告範圍
* `新增` 新增即時 `autojs6.device.info()` 電量/螢幕/亮度/音量資訊、`autojs6.console.log/warn/error` 宿主控制台級別與 `autojs6.notice` 通知
* `改善` 嚴格驗證 device 結果結構, 通知權限不足時穩定傳回 `PERMISSION_DENIED`, 不開啟設定或變更裝置權限狀態

# v0.3.0-alpha.1

###### 2026/08/23

* `提示` M3 首個 current-tree alpha 候選; 協定 1.5 與低風險 Host 能力子集已實作, 後續能力、發行與完整裝置矩陣不在本項宣告範圍
* `新增` 新增協定 1.5 執行級 Host capability broker, 以純資料 JSON 綁定 request UUID、外掛 UID、單調呼叫序號、1024 次配額、64 KiB 訊息與 5 秒 Host 調度上限
* `新增` 新增 `autojs6.toast`, `autojs6.clip.get/set` 與 `autojs6.app.launch/launch_app/open_url` 即時 Host API
* `改善` 終態、取消、Binder death 與清理路徑統一撤銷 broker, Python 端穩定映射 capability unavailable、Host 與協定錯誤

# v0.2.0-alpha.1

###### 2026/08/13

* `提示` 0.1 之後的 U1 current-tree alpha 候選; U1-R2 module entry、live output、前景內建 input、明確結構化 JSON 與有界輸出 artifact 僅完成至 E2, 背景啟動與直接 sys.stdin 仍非互動, R2 E3 尚未完成, 且這些目前樹結果不屬於裝置矩陣/發布/公開證據
* `新增` 新增最大 1 MiB 的有限預先提供 stdin snapshot, 為 `input()` 與 `sys.stdin` 提供確定性輸入和 EOF
* `新增` 完善專案 import 語義, 支援 workspace 模組, 巢狀入口同層與根模組以及 package-relative import
* `新增` 新增協定 1.2 明確 `entryMode=file|module`; module 執行透過 `runpy` 提供正確的 `__package__`、`__spec__`、專案根目錄 `sys.path[0]` 與相對 import, file 模式維持不變
* `新增` 新增協定 1.3: 有限 snapshot 到達 EOF 後, 僅前景內建 `input()` 使用可見回顯、標準庫 `getpass.getpass()` 使用隱藏回顯的有界 prompt/reply; 背景啟動絕不開啟輸入 UI, 直接 `sys.stdin` 始終有限
* `新增` 新增協定 1.4 明確嚴格 JSON 結果與可選輸出 artifact, 對數量、正規化路徑、單個/合計大小、精確 PFD 引用與 SHA-256 設限, 且絕不從 stdout 推斷結果
* `修正` 執行前以 strict UTF-8 解碼原始碼, 非 UTF-8 encoding cookie 不再繞過契約
* `改善` 授予 `INTERNET`, 讓可信腳本可直接使用標準函式庫網路用戶端, 同時仍停用線上 pip 與自動程式碼下載
* `改善` 將 Provider 執行上限提高至 30 分鐘, 有界輸出提高至 16 MiB / 16384 個 chunk
* `改善` 將 stdout/stderr 的有界 chunk 與 credit 背壓前移到腳本執行期間, 保留終態前的有序部分輸出並禁止終態後輸出
* `改善` 每次執行使用獨立 `__main__`, 並還原 stdin/stdout/stderr, argv, cwd, `sys.path`, module 與 importer cache 狀態
* `改善` 為已開啟但未 start 的 session 加入 5 秒 lease, 到期釋放輸入, descriptor 與單一工作階段占位
* `改善` Provider 在 Binder 傳入邊界強制最低 Host versionCode 5275, 不再只依賴 Host 端探索檢查

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
