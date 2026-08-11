******

### 版本記錄

******

# v0.1.0

###### 2026/08/12 (原始碼已凍結; 尚未 tag 或發布)

* `提示` 0.1.0 原始碼身分與精確 Host lock 已凍結; 最終 APK/P3 provenance, 官方外掛索引, tag/Release 與 production receipt 尚待完成
* `新增` 面向 AutoJs6 6.8.0 / versionCode 5275 的 Python 協定 1.0-1.1, 有界專案 workspace 與唯讀 app/device/execution/project 能力快照
* `新增` 無須重新啟動 Host 的熱插拔: 安裝或重新啟用後下一次新執行重新發現並 pin 身分, 缺失或停用時絕不 fallback
* `新增` 執行中的 Binder death 終止目前執行且不得重播, 後續新執行重新發現 provider
* `改善` 將 Chaquopy 固定為 trusted-local, non-sandbox 執行環境; SM003 為長期 signer, SuperMonster003 為 runtime/security/release owner
* `相依性` 鎖定 Chaquopy 17.0.0 與 CPython 3.13.9; 正式產物須在最終原始碼凍結後重新驗證

# v0.1.0-alpha.1

###### 2026/08/09

* `提示` R2 概念驗證原始碼. Gradle, APK, Binder 與裝置驗收尚未執行
* `新增` 獨立 Python 協定 V1 provider scaffold, 專用執行環境程序, 單一作用中工作階段與零 provider 佇列
* `新增` 單一原始碼 `__main__` 執行, 有界 stdout/stderr, 結構化例外與程序重啟式取消
* `新增` 固定順序的 10 種語言 README 與應用程式內更新記錄產生流程
* `相依性` 預選 Chaquopy 17.0.0 與 Python 3.13; 封裝版本和相依性雜湊仍待建置驗證
