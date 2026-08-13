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

> 0.1.0 source identity と exact Host lock は凍結済みです. ローカル RC の build, APK, Binder, API 31 arm64-v8a 端末 1 台の証拠は履歴証拠のままです. stable APK/P3 provenance は exact release identity に紐づき, production receipt は公開後の独立した証拠レベルです.

******

### 機能

******

- 1 つの UTF-8 Python ソースを `__main__` として実行します.
- `input()` 用に最大 1 MiB の有限な事前供給 stdin snapshot を受け付けます. リアルタイムの prompt/reply 対話は提供しません.
- stdout と stderr の順序を保ち, 上限付き chunk を credit で送信します.
- `SystemExit`, 構文エラー, 実行時例外を上限付き構造化 traceback とともに返します.
- プロセスごとに 1 セッションのみ許可し, provider 側ではキューを持ちません.
- ホスト再起動は不要です. インストールまたは再有効化後の次の新規実行で provider を再検出して pin し, 実行中の Binder death はその実行を終了して自動再実行しません.

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

ビルドは Python 3.13 を要求します. 凍結済みローカル RC 産物と正確な端末実行では CPython 3.13.9 を記録しました. 最終 0.1.0 はソース凍結後に版と hash を再検証します.

******

### プラグインインターフェース

******

ホストは次の識別子でプラグインを検出して呼び出します:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.1
```

独立 SOURCE, 任意の上限付き workspace archive, 最大 1 MiB の有限な事前供給 stdin snapshot, プロトコル 1.1 の読み取り専用ホスト能力 snapshot を受け付けます. stdin はリアルタイム対話チャネルではなく, Context, Binder, ホストオブジェクト, callback sink は注入しません.

******

### ホスト統合状況

******

> 0.1.0 は AutoJs6 6.8.0 専用で, 最小 Host versionCode 5275 は凍結され強制されます. 最終 clean Host source revision と 3 AAR distribution manifest は lock に記録済みです. 新規実行ごとに provider を再検出し, 不在または無効時は install/enable を案内して fallback しません. インストールまたは再有効化に Host 再起動は不要です. stable APK identity はその exact Plugin source と Host lock に紐づきます.

```text
release target: 0.2.0-alpha.1
release state: post-0.1 U1 alpha source candidate; not published, E3 device acceptance pending, and prior 0.1.0 artifacts do not cover the current source
paired host: AutoJs6 6.8.0 / versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### セキュリティとプライバシー

******

Chaquopy runtime は信頼するローカルスクリプト向けで, hostile-code sandbox ではありません. exported service はホスト署名権限を要求し UID, package, signer を再検査します. 分離 Android UID, 専用プロセス, 狭い Binder 境界は露出を減らしますが Python を sandbox 化しません. 長期リリース signer は SM003, runtime/security/release owner は SuperMonster003 です.

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

- リアルタイム対話 stdin は未対応で, 最大 1 MiB の有限な事前供給 snapshot のみ対応します. workspace への書き戻し, online pip, wheel ダウンロードも引き続き未対応です.
- UI スクリプト, debugger, REPL, ホスト Java オブジェクトへの任意アクセスはありません.
- リアルタイム AutoJs6 capability broker はありません. 最初の API は実行開始時に凍結した app/device/execution/project snapshot と plugin-private workspace の上限付き読み取り専用アクセスだけを使います.
- 32 bit Android と任意の native wheel は保証しません.
- arm64-v8a には API 31 端末証拠があります. x86_64 は現時点で packaging 証拠のみで, 端末実行や完全な端末 matrix とは扱いません.

******

### ロードマップ

******

R6-P2/P3 のローカル RC と集中端末証拠は履歴として保持されます. この clean VERSION_BUILD=11 freeze commit が stable Plugin source identity と exact Host 6.8.0/5275 lock を固定します. stable APK provenance はそれらの exact identity に対して評価され, production receipt も同じ基準を使用しなければなりません. 完全な API×ABI matrix と新 soak は自動 gate ではありません.

- [ROADMAP.md を表示](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 更新履歴

******

# v0.2.0-alpha.1

###### 2026/08/13

* `注記` 0.1 後の U1 source alpha. live stdin interaction は未提供で, E3 端末受け入れは未実施
* `追加` 最大 1 MiB の有限な事前提供 stdin snapshot を追加し, `input()` と `sys.stdin` に決定的な入力と EOF を提供
* `追加` workspace module, nested entry の sibling/root module, package-relative import に対応して project import semantics を完成
* `修正` 実行前に source を strict UTF-8 で decode し, 非 UTF-8 encoding cookie による contract 回避を防止
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

##### その他のバージョン

* [CHANGELOG-ja.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-ja.md)

******

### 検証

******

Gradle と ADB を使わないファイルシステム静的検査:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

ローカル CPython による可搬 bootstrap 意味テスト:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

静的検査とローカル CPython は Android 証拠を代替しません. 既存 RC と単一端末結果は履歴です. release acceptance は exact identity に直接結び付くビルド, APK, Binder, 代表端末検証を使用します.

******

### ビルド

******

ドキュメント生成自体はビルドを実行しません. release 設定は AAR, SHA-256, signer, runtime lock の drift で fail closed します. stable artifact は exact release identity に紐づく場合だけ受け入れます.

ビルド前に次の release AAR を `libs` に配置して固定する必要があります:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

Maven の Chaquopy 17.0.0 と CPython 3.13.9 を lock し, stdlib のみを package します. release gate は依存 metadata, native library, NOTICE, SM003 signer, 3 種の配布 APK を exact identity に対して確認します. 16 KB page 互換性には現在専用 gate がなく, 検証済みとは宣言しません.

******

### ライセンス

******

プロジェクトソースは MPL-2.0 です. Chaquopy, CPython, その他の依存物は各ライセンスに従い, 帰属と upstream/project source の取得方法は `THIRD_PARTY_NOTICES.md` に記載します.

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
