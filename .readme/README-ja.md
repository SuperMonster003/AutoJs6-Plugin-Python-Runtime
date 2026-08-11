<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>独立した Python ランタイムプラグイン. 専用プロセスで Python スクリプトを実行</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 言語

******

現在の README.md は次の言語に対応しています:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- 日本語 [ja] # 現在
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### 概要

******

Python Runtime は Python プロトコル V1 の独立 provider です. ホストから 1 つの Python ソーススナップショットを専用プロセスで受け取り, CPython で実行して, 制限付き出力, 構造化例外, 1 つの終端状態を返します.

> 現段階は R2 概念実証です. ランタイムソースとローカル bootstrap 意味テストはありますが, Gradle 設定, Android コンパイル, APK 検査, Binder 検証, 端末受け入れテストは未実施です.

******

### 機能

******

- 1 つの UTF-8 Python ソースを `__main__` として実行します.
- stdout と stderr の順序を保ち, 上限付き chunk を credit で送信します.
- `SystemExit`, 構文エラー, 実行時例外を上限付き構造化 traceback とともに返します.
- プロセスごとに 1 セッションのみ許可し, provider 側ではキューを持ちません.
- キャンセル, timeout, callback death 後はスクリプトを再実行せず専用プロセスを破棄します.

******

### ランタイムとデータ形式

******

プロトコル V1 は現在次の範囲を宣言します:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

ビルドは Python 3.13 を要求します. 3.13.9 は現在の Chaquopy リリース情報による期待値であり, APK 検査と端末実行までは検証済み事実ではありません.

******

### プラグインインターフェース

******

ホストは次の識別子でプラグインを検出して呼び出します:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

SOURCE descriptor のみ受け付けます. workspace archive と stdin snapshot の上限は 0 で, Context, Binder, ホストオブジェクト, callback sink をスクリプトへ注入しません.

******

### ホスト統合状況

******

> プロトコルとホスト配線は進行中ですが, 必要な release AAR は未公開・未検証です. この scaffold をインストールするだけでは Python エンジンは利用できません.

******

### セキュリティとプライバシー

******

ソース manifest は Android 権限を要求しません. exported service はホスト署名権限を要求し, Binder 入口で UID, インストール済みホスト, 現在の署名を再検査します. Chaquopy の Java bridge は利用可能なため, 分離 UID, 専用プロセス, 狭い Binder 境界に依存し, CPython を安全な sandbox とはみなしません.

******

### 動作制限

******

- ソースは 4 MiB, 総出力は 4 MiB, 1 chunk は 16 KiB, chunk 数は 4096 が上限です.
- timeout は最大 60 s, 同時セッションは 1, provider キューはありません.
- Binder 受信側の完全な PFD を所有し, 終端または close 時に閉じます.
- 出力は先に上限付きでバッファし credit で送信します. 実行中の backpressure は未対応です.
- キャンセルはプロセス再起動方式です. native extension とブロッキング呼び出しは Android 検証が必要です.
- stdlib-only で online pip と第三者パッケージを禁止します. 結合 APK の権限はビルド時に検査します.

******

### 未宣言の機能

******

- workspace archive, stdin snapshot, online pip, wheel ダウンロードは未対応です.
- UI スクリプト, debugger, REPL, ホスト Java オブジェクトへの任意アクセスはありません.
- AutoJs6 capability broker とホスト API 接続はまだありません.
- 32 bit Android と任意の native wheel は保証しません.
- ローカル CPython テストは Chaquopy, Android, Binder, 端末の受け入れ証拠ではありません.

******

### ロードマップ

******

独立 R2 リポジトリ, 静的境界, provider/bootstrap ソース, ローカル意味テストは用意済みです. QV710AF65F の保護 soak 中は Gradle と ADB を延期します. release AAR, 依存解決, Android コンパイル, APK/16 KB, Binder/PFD, 端末マトリクスは未完了です.

- [ROADMAP.md を表示](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 更新履歴

******

# v0.1.0-alpha.1

###### 2026/08/09

* `注記` R2 概念実証ソース. Gradle, APK, Binder, 端末受け入れは未実施
* `追加` 専用プロセス, 1 セッション, provider キューなしの独立 Python V1 provider scaffold
* `追加` 単一ソースの `__main__` 実行, 上限付き stdout/stderr, 構造化例外, プロセス再起動キャンセル
* `追加` 固定順で 10 言語の README とアプリ内更新履歴を生成
* `依存関係` Chaquopy 17.0.0 と Python 3.13 を仮選定. パッケージ版と依存 hash はビルド検証待ち

##### その他のバージョン

* [CHANGELOG-ja.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-ja.md)

******

### 検証

******

Gradle と ADB を使わないファイルシステム静的検査:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

ローカル CPython による可搬 bootstrap 意味テスト:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

これらは Android 動作を証明しません. Gradle, APK, Binder, 端末検証は保護 soak 後に行います.

******

### ビルド

******

現在はビルドしません. AAR または SHA-256 が未固定なら release 設定は fail closed します.

ビルド前に次の release AAR を `libs` に配置して固定する必要があります:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

Maven の Chaquopy 17.0.0 と stdlib のみを使う予定です. 依存検証, native ライブラリ, ライセンス, 16 KB page 対応は未検証です.

******

### ライセンス

******

プロジェクトソースは MPL-2.0 です. Chaquopy, CPython, その他の依存物は各ライセンスに従います.

******

### リソース構成

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` は固定順 JSON から 10 言語の README とアプリ内更新履歴を生成します. Android 文字列は各リソースディレクトリで管理します.

******

### リンク

******

- AutoJs6 ドキュメント: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
