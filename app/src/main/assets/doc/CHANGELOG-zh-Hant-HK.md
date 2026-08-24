******

### 版本記錄

******

# v0.5.0-alpha.2

###### 2026/08/24

* `提示` 第二個 M5 current-tree alpha 候選版; Host FIFO 並發准入源碼及離線 JVM/便攜門禁已通過, 但尚未執行 Android 並發冒煙, 不聲明 true parallel CPython、預熱、發佈或 release 完成
* `新增` 在 Provider 探索前以公平 Host FIFO 接納並發 Python 啟動: 1 個 active owner 加最多 32 個 waiter; queued Stop 可中斷, 不綁定插件、不消耗 request timeout, 亦不提前建立長任務前台通知
* `改善` 已 dispatch 會話 close 後最多保留 Provider binding 3 秒, 確認進程代際退休再作 FIFO 交接; 協議 1.6、三件 AAR 及 Plugin 單會話/無 provider 隊列邊界均維持不變

# v0.5.0-alpha.1

###### 2026/08/24

* `提示` 首個 M5 current-tree alpha 候選版; 協議 1.6 前台長任務原始碼及 Host/Plugin 離線 JVM、便攜門禁已通過, 但尚未執行 M5 真機冒煙, 不聲明發佈、並行或程序預熱完成
* `新增` 新增項目級 `executionMode=long-running`: 移除執行 deadline, 由 Host `specialUse` 前台服務、常駐通知及 Stop action 維持生命週期; 排程、後台/Intent/開發者入口穩定拒絕且不降級
* `改善` Provider 每 15 s 發佈有序心跳, Host 強制 2 min 啟動租約、45 s 心跳租約及獨立前台服務租約; 存活性遺失及手動停止均 fail closed 並沿用程序重啟取消, 有界協議 1.0-1.5 保持相容

# v0.4.0-alpha.9

###### 2026/08/24

* `提示` 第九個 current-tree alpha 候選版; M4 Path C native 套件評估以 `NOT_ADMITTED` 關閉, 內置 runtime 保持 `stdlib-only`, 未內置 Pillow、NumPy、OpenCV 或任何傳遞 native payload, 亦不新增裝置驗收聲明
* `改善` ADR 0004 記錄本地 `--no-index --find-links` 雙 ABI offline debug build: Pillow 11.0.0 令每個 APK 增加 2,054,483 bytes, NumPy 1.26.2 增加 21,931,164 bytes, 六個候選輸出均通過 `zipalign -c -P 16 4`
* `改善` NDK 29 全閉包 ELF 審計拒絕雙 ABI 均為 `0x1000` 的 FreeType, 以及 x86_64 為 `0x1000` 的 OpenBLAS/libgfortran; OpenCV 沒有官方 `cp313` Android wheel, 重開須有可重現 NDK r28+ wheel 與 16 KiB 公共引擎驗收

# v0.4.0-alpha.8

###### 2026/08/24

* `提示` 第八個 current-tree alpha 候選版; M4 Path B 構建期套件評估以 `NOT_ADMITTED` 關閉, 內置 runtime 保持 `stdlib-only`, 未內置 `requests` 或任何候選依賴, 亦不新增裝置驗收聲明
* `改善` ADR 0003 固定 stdlib-only debug APK 的 arm64-v8a 23,709,688 bytes、x86_64 23,726,048 bytes 與 universal 34,622,039 bytes 基線; 沒有經審計的離線 wheelhouse 時不報告虛假體積差值, 未來准入必須同時具備 Gradle `--offline`、`--no-index`、`--require-hashes`、許可證/哈希鎖、三 APK 體積差值與 dual ABI 公共引擎驗收

# v0.4.0-alpha.7

###### 2026/08/24

* `提示` 第七個 M3 自動化 current-tree alpha 候選版本；真實 Settings 完整工作流程已於 API 37 模擬器通過，發佈、M4 路徑 B/C 及完整裝置矩陣不在本聲明範圍內
* `新增` 新增 `m3_complete_automation`：使用 `app.launch`、`selector.find`、`selector.click` 及 `images.capture_screen` 的有界真實 Settings 工作流程，嚴格斷言 PNG 結構及目標控制項包含關係
* `修正` Python 序列化前將平台回報的 `right < left` 或 `bottom < top` 無障礙邊界收斂為保留錨點的 zero-area 軸，並以精確 selector 查詢隔離無關樹節點
* `改善` 匯出的 `RunIntentActivity` 公開專案路徑已於 API 37 模擬器通過，產生 1080x2424 PNG 及經 SHA-256 驗證的產物，其後把無障礙恢復為 0/null 並移除全部精確測試暫存

# v0.4.0-alpha.6

###### 2026/08/24

* `提示` 第六個 M3 automation current-tree alpha 候選版; 已配置 Host OCR 的正向識別在具備合資格服務的 API 37 模擬器通過, API 31 實機在不改動其無障礙服務的前提下完成故障關閉; 更豐富的 OCR、發佈及完整裝置矩陣不在本聲明範圍內
* `新增` 新增 `autojs6.ocr.recognize(image)`, 接受有界 PNG/JPEG 字節, 並從已配置 Host OCR 引擎返回有序不可變文字行 tuple
* `改善` 重用 1 MiB PNG/JPEG 上傳、24 KiB 原始分塊及 SHA-256 校驗, 僅選擇已啟用、已授權且兼容的 Host OCR 服務, 結果限制為 256 行、每行 4 KiB 嚴格 UTF-8、合計 48 KiB, 始終 release 並清零緩衝區, 以穩定 `OCR_UNAVAILABLE` 或 `OCR_FAILED` 報告失敗

# v0.4.0-alpha.5

###### 2026/08/24

* `提示` 當前樹第五個 M3 自動化 alpha 候選; 有界模板找圖已在啟用無障礙的 API 37 模擬器通過, API 31 實體機在不改變既有無障礙服務的前提下通過 fail-closed; OCR、發佈及完整裝置矩陣仍不在本次聲明範圍
* `新增` 新增 `autojs6.images.find_image(template, *, region=None, threshold=0)`, 接受 PNG/JPEG 位元組與可選有界區域, 返回左上角座標或 `None`
* `改善` 每次執行上傳一個最大 1 MiB 的模板, 以 24 KiB 原始區塊傳輸並核對 SHA-256, 單邊解碼不超過 2048 像素, 按 row-major 確定性掃描並核對 `autojs6-python-image-match-v1`; 僅全不透明像素參與、其餘為通配, 無需 OpenCV, 始終 release 並清零緩衝區, 且僅對 Android 333 ms 截圖節流執行有界 350 ms 等待重試

# v0.4.0-alpha.4

###### 2026/08/24

* `提示` 當前樹第四個 M3 自動化 alpha 候選; 有界螢幕找色已在啟用無障礙的 API 37 模擬器通過, API 31 物理機在不改變既有無障礙服務的前提下通過 fail-closed; 模板找圖、OCR、發佈及完整設備矩陣仍不在本次聲明範圍
* `新增` 新增 `autojs6.images.find_color(color, *, region=None, threshold=0)`, 接受嚴格 RGB 整數或 `#RRGGBB` 文本、可選有界區域, 返回座標或 `None`
* `改善` 每次呼叫只捕獲一張最新 Android 11+ 無障礙截圖, 以確定性 row-major 順序和 0..255 逐通道閾值掃描, 校驗精確 `autojs6-python-color-match-v1`, 不向 Python 傳輸圖像字節或句柄

# v0.4.0-alpha.3

###### 2026/08/24

* `提示` 目前樹第三個 M3 自動化 alpha 候選; Android 11+ 有界螢幕截圖完整路徑已在啟用無障礙的 API 37 模擬器通過聚焦驗收, API 31 實體裝置在不變更既有無障礙服務的前提下通過 fail-closed; 找圖找色、OCR、發布及完整裝置矩陣仍不在本次聲明範圍
* `新增` 新增 `autojs6.images.capture_screen`, 以 PNG/JPEG 返回經驗證的編碼位元組, 或原子寫入並發布執行輸出產物
* `改善` 每次執行最多保留 1 張截圖, 以 32 KiB 原始區塊傳輸且編碼後最多 4 MiB; Python 核對順序、EOF、SHA-256 及格式簽名並始終 release, Host 在替換/釋放/終態清零, 失敗使用穩定錯誤且不啟用服務、不開啟設定

# v0.4.0-alpha.2

###### 2026/08/24

* `提示` 目前樹第二個 M3 自動化 alpha 候選; 完整有界 selector/UI 樹路徑已在啟用無障礙的 API 37 模擬器通過聚焦驗收, API 31 實體裝置在不變更既有無障礙服務的前提下通過 fail-closed; 截圖, OCR, 發布及完整裝置矩陣仍不在本次聲明範圍
* `新增` 加入即時 `autojs6.selector.snapshot/find/click/set_text` API, 透過不透明的執行級節點引用提供分離的無障礙樹純數據, AND 組合首次匹配查詢及明確動作
* `改善` 限制快照節點, 深度, 載荷及節點文字, 選擇器掃描規模, 查詢/設定文字與保留節點; 掃描不完整返回 `SELECTOR_SCAN_LIMIT_EXCEEDED`, 引用過期返回 `STALE_NODE`, 無障礙不可用時不開啟設定並拋出 `CapabilityUnavailableError`

# v0.4.0-alpha.1

###### 2026/08/23

* `提示` 首個 M3 自動化 current-tree alpha 候選; 有界座標/全域動作已在啟用無障礙的 API 37 模擬器通過聚焦驗收, API 31 實體裝置在不改變既有無障礙服務下通過 fail-closed, selector/UI 樹、截圖、OCR、發佈及完整裝置矩陣不在本次聲明範圍
* `新增` 新增經 Host 無障礙執行的即時 `autojs6.automator.click/long_click/press/swipe/back/home` API, 回傳動作實際分發結果布林值
* `改善` 座標只接受 0 至 1000000 的非布林嚴格整數, press/swipe 持續時間只接受 1 至 4000 ms; Host 無障礙不可用時拋出 `CapabilityUnavailableError`, 不開啟設定

# v0.3.0-alpha.6

###### 2026/08/23

* `提示` 首個 M4 current-tree alpha 候選; 項目本地純 Python 相依套件路徑已通過雙裝置聚焦驗收, 後續 M3/M4 批次、發佈及完整裝置矩陣不在本次聲明範圍
* `新增` 支援從已准入項目根目錄匯入項目本地純 Python 套件及 `.dist-info` 元數據, 提供鎖定版本的 `requests` 可重現範例, 且不引入執行時安裝器
* `改善` 將項目 workspace 上限提高至壓縮 64 MiB、8192 個檔案條目及解壓 128 MiB, 分發前按 snapshot 實際三維需求匹配 Provider 能力; 缺失 import 仍拋出 `ModuleNotFoundError`, 不觸發線上 pip 或引擎回退

# v0.3.0-alpha.5

###### 2026/08/23

* `提示` M3 第五個 current-tree alpha 候選; 第二批有界 Host engines 能力已通過雙裝置聚焦驗收, 後續能力、公開發行及完整裝置矩陣不在本條聲明範圍
* `新增` 新增即時 `autojs6.engines.current/run/stop_self` API, 提供不含絕對路徑的目前引擎資訊、非 Python Host 子指令碼非同步啟動及確定性停止自身
* `改善` 子指令碼僅接受執行根目錄內的規範化相對路徑且每次執行最多成功啟動 16 個; 巢狀 Python 穩定返回 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self` 透過 provider 程序重啟取消目前執行

# v0.3.0-alpha.4

###### 2026/08/23

* `提示` M3 第四個 current-tree alpha 候選; 前台 Host 對話框已通過雙裝置聚焦驗收, 引擎、後續能力、公開發行及完整裝置矩陣不在本條聲明範圍
* `新增` 加入僅限前台的 `autojs6.dialogs.alert/confirm/prompt/select` API, 分別回傳確認完成、布林選擇、可空文字及由零開始的可空選項索引
* `改善` 限制對話框標題、內容、回覆及選項, 串行顯示單一 Host 擁有的對話框, 後台啟動不會開啟 UI 並穩定回傳 `INTERACTIVE_NOT_ALLOWED`

# v0.3.0-alpha.3

###### 2026/08/23

* `提示` M3 第三個 current-tree alpha 候選; 第二批有界 Host files 能力已通過雙裝置聚焦驗收, 對話框、引擎、後續能力、公開發行及完整裝置矩陣不在本條聲明範圍
* `新增` 加入即時 `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` API, 在目前項目根目錄或單檔指令碼目錄內進行有界 UTF-8 文字存取
* `改善` 拒絕不安全或越界路徑, 限制文字及直接目錄列舉, 回傳穩定檔案錯誤, 並明確區分即時 Host 根目錄與凍結的外掛 workspace snapshot

# v0.3.0-alpha.2

###### 2026/08/23

* `提示` M3 第二個 current-tree alpha 候選; 完整首批低風險 Host 能力已實作, 後續能力批次、公開發行及完整裝置矩陣不在本條聲明範圍
* `新增` 加入即時 `autojs6.device.info()` 電量/螢幕/亮度/音量資料、`autojs6.console.log/warn/error` 宿主控制台級別及 `autojs6.notice` 通知
* `改善` 嚴格校驗 device 結果結構, 通知權限不足時穩定傳回 `PERMISSION_DENIED`, 不開啟設定或變更裝置權限狀態

# v0.3.0-alpha.1

###### 2026/08/23

* `提示` M3 首個 current-tree alpha 候選; 協議 1.5 與低風險 Host 能力子集已實作, 後續能力、發行及完整裝置矩陣不在本條聲明範圍
* `新增` 加入協議 1.5 執行級 Host capability broker, 以純數據 JSON 綁定 request UUID、外掛 UID、單調呼叫次序、1024 次配額、64 KiB 訊息及 5 秒 Host 調度上限
* `新增` 加入 `autojs6.toast`, `autojs6.clip.get/set` 及 `autojs6.app.launch/launch_app/open_url` 即時 Host API
* `改善` 終態、取消、Binder death 及清理路徑統一撤銷 broker, Python 端穩定映射 capability unavailable、Host 及協議錯誤

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
