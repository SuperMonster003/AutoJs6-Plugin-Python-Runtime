******

### 更新履歴

******

# v0.1.0

###### 2026/08/11 (リリース準備中; tag・公開前)

* `注記` 0.1.0 は準備中です. 最終ホスト ID, GitHub repository と認証, 公式 plugin index, production receipt は未完了です
* `追加` AutoJs6 6.8.0 と組み合わせる Python プロトコル 1.0-1.1, 上限付き project workspace, 読み取り専用 app/device/execution/project snapshot
* `追加` ホスト再起動なしの hot-plug: install または再有効化後の次の新規実行で ID を再検出・pin し, 不在・無効時は fallback しません
* `追加` 実行中の Binder death は replay せず現在の実行を終了し, 後続の新規実行で provider を再検出します
* `改善` Chaquopy を trusted-local, non-sandbox runtime として固定. 長期 signer は SM003, runtime/security/release owner は SuperMonster003
* `依存関係` Chaquopy 17.0.0 と CPython 3.13.9 を lock. 最終 artifact はソース凍結後に再検証します

# v0.1.0-alpha.1

###### 2026/08/09

* `注記` R2 概念実証ソース. Gradle, APK, Binder, 端末受け入れは未実施
* `追加` 専用プロセス, 1 セッション, provider キューなしの独立 Python V1 provider scaffold
* `追加` 単一ソースの `__main__` 実行, 上限付き stdout/stderr, 構造化例外, プロセス再起動キャンセル
* `追加` 固定順で 10 言語の README とアプリ内更新履歴を生成
* `依存関係` Chaquopy 17.0.0 と Python 3.13 を仮選定. パッケージ版と依存 hash はビルド検証待ち
