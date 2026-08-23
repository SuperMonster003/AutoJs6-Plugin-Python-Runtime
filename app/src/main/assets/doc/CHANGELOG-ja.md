******

### 更新履歴

******

# v0.2.0-alpha.1

###### 2026/08/13

* `注記` 0.1 後の U1 current-tree alpha candidate. U1-R2 の module entry, live output, foreground 組み込み input, 明示的 structured JSON, 上限付き output artifact は E2 までのみ完了しています. background 起動と直接の sys.stdin は非対話のままで, R2 E3 は未完了であり, current-tree の結果は device matrix/release/public evidence ではありません
* `追加` 最大 1 MiB の有限な事前提供 stdin snapshot を追加し, `input()` と `sys.stdin` に決定的な入力と EOF を提供
* `追加` workspace module, nested entry の sibling/root module, package-relative import に対応して project import semantics を完成
* `追加` プロトコル 1.2 の明示的な `entryMode=file|module` を追加し, module 実行は `runpy` により正しい `__package__`, `__spec__`, project root の `sys.path[0]`, relative import を使用し, file mode は変更しない
* `追加` プロトコル 1.3 で有限 snapshot の EOF 後に foreground 限定の上限付き prompt/reply を追加し, 組み込み `input()` は表示入力, `getpass.getpass()` は非表示入力を使用し, background 起動では入力 UI を開かず, 直接の `sys.stdin` は有限のままにする
* `追加` プロトコル 1.4 で明示的な厳密 JSON result と任意 output artifact を追加し, count, normalized path, file/aggregate size, exact PFD reference, SHA-256 を制限して stdout から result を推測しない
* `修正` 実行前に source を strict UTF-8 で decode し, 非 UTF-8 encoding cookie による contract 回避を防止
* `改善` `INTERNET` を付与して信頼済みスクリプトが標準ライブラリのネットワーククライアントを直接利用できるようにし、online pip と自動コードダウンロードは引き続き無効化
* `改善` Provider の実行上限を 30 分、有界出力を 16 MiB / 16384 chunks に拡大
* `改善` 上限付き stdout/stderr chunk と credit backpressure をスクリプト実行中へ移し, terminal 前の順序付き部分出力を保持して terminal 後の出力を禁止
* `改善` 実行ごとに独立した `__main__` を使用し, stdin/stdout/stderr, argv, cwd, `sys.path`, module, importer cache の状態を復元
* `改善` open 後に start されない session に 5 秒 lease を適用し, 期限後に input, descriptor, 単一 session slot を解放
* `改善` Host 側 discovery だけに依存せず, Provider の Binder 境界で最低 Host versionCode 5275 を強制

# v0.1.0

###### 2026/08/12

* `注記` 0.1.0 は stable Plugin source identity と exact Host 6.8.0/5275 lock を固定します
* `追加` AutoJs6 6.8.0 / versionCode 5275 と組み合わせる Python プロトコル 1.0-1.1, 上限付き project workspace, 読み取り専用 app/device/execution/project snapshot
* `追加` ホスト再起動なしの hot-plug: install または再有効化後の次の新規実行で ID を再検出・pin し, 不在・無効時は fallback しません
* `追加` 実行中の Binder death は replay せず現在の実行を終了し, 後続の新規実行で provider を再検出します
* `改善` Chaquopy を trusted-local, non-sandbox runtime として固定. 長期 signer は SM003, runtime/security/release owner は SuperMonster003
* `依存関係` Chaquopy 17.0.0 と CPython 3.13.9 を lock. stable APK は final source identity に紐づき, exact artifact として検証されます

# v0.1.0-alpha.1

###### 2026/08/09

* `注記` R2 概念実証ソース. Gradle, APK, Binder, 端末受け入れは未実施
* `追加` 専用プロセス, 1 セッション, provider キューなしの独立 Python V1 provider scaffold
* `追加` 単一ソースの `__main__` 実行, 上限付き stdout/stderr, 構造化例外, プロセス再起動キャンセル
* `追加` 固定順で 10 言語の README とアプリ内更新履歴を生成
* `依存関係` Chaquopy 17.0.0 と Python 3.13 を仮選定. パッケージ版と依存 hash はビルド検証待ち
