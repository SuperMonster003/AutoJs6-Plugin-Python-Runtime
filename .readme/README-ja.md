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
- 最大 1 MiB の有限な事前供給 stdin snapshot を受け付けます. snapshot が EOF に達した後は, 明示的な foreground 起動で protocol 1.3 の上限付き prompt/reply により組み込み `input()` を継続でき, 標準ライブラリの `getpass.getpass()` は非表示入力を使用します.
- 許可済み project では `entryMode=file|module` を明示的に選択します. module mode は標準 `runpy` metadata, project root の `sys.path[0]`, package-relative import を使用し, file mode は通常の script semantics を維持します.
- スクリプト実行中に stdout/stderr の元の順序を保って上限付き chunk を credit で送信し, credit 枯渇時は実行に backpressure をかけます.
- protocol 1.4 で最大 64 KiB の明示的な厳密 JSON result を設定し, path, size, SHA-256 上限付きの任意 output artifact を最大 16 個転送します. stdout から result を推測しません.
- 実行単位の pure-data protocol 1.5 broker を通して `toast`、`clip.get/set`、`app.launch/launch_app/open_url`、`device.info`、`console.log/warn/error`、権限を考慮した `notice` をリアルタイムに呼び出し、terminal 時に無効化します.
- `SystemExit`, 構文エラー, 実行時例外を上限付き構造化 traceback とともに返します.
- プロセスごとに 1 セッションのみ許可し, provider 側ではキューを持ちません.
- ホスト再起動は不要です. インストールまたは再有効化後の次の新規実行で provider を再検出して pin し, 実行中の Binder death はその実行を終了して自動再実行しません.

******

### ランタイムとデータ形式

******

プロトコル V1 は現在次の範囲を宣言します:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
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
protocol: 1.0-1.5
```

独立 SOURCE, 任意の上限付き workspace archive, 最大 1 MiB の有限な事前供給 stdin snapshot, プロトコル 1.1 の読み取り専用ホスト能力 snapshot を受け付けます. プロトコル 1.2 は許可済み project に明示的な file/module entry negotiation を追加します. プロトコル 1.3 は snapshot EOF 後の組み込み `input()` に, Host 所有かつ foreground 限定の prompt/reply を追加し, 標準ライブラリの `getpass.getpass()` は非表示入力を使用します. プロトコル 1.4 は明示的な厳密 JSON と任意の SHA-256 manifest output artifact を追加し, stdout は診断のままで result として解析しません. プロトコル 1.5 は 1 回の実行、plugin UID、call 順序、有限 quota に結び付く pure-data Host broker を追加します. 直接の `sys.stdin` は有限のままで, background 起動は入力 UI を開かず, user script に Context、raw Binder、Host runtime object、callback sink は渡しません.

******

### ホスト統合状況

******

> 0.1.0 は AutoJs6 6.8.0 専用で, 最小 Host versionCode 5275 は凍結され強制されます. 最終 clean Host source revision と 3 AAR distribution manifest は lock に記録済みです. 新規実行ごとに provider を再検出し, 不在または無効時は install/enable を案内して fallback しません. インストールまたは再有効化に Host 再起動は不要です. stable APK identity はその exact Plugin source と Host lock に紐づきます.

```text
release target: 0.3.0-alpha.2
release state: 0.3.0-alpha.2 current-tree candidate; M1 and M2 are complete, and the complete first low-risk protocol 1.5 Host capability slice passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3 batches, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
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

- ソースは 4 MiB, 総出力は 16 MiB, 1 chunk は 16 KiB, chunk 数は 16384 が上限です.
- timeout は最大 30 min, 同時セッションは 1, provider キューはありません.
- Binder 受信側の完全な PFD を所有し, 終端または close 時に閉じます.
- 出力は実行中に credit ごとに chunk 単位で送信します. credit 枯渇時はスクリプトを停止し, 受理済み出力は唯一の terminal より前に置かれ, terminal 後の出力は禁止されます.
- 構造化 JSON は 64 KiB, artifact は最大 16 個, path は 1024 UTF-8 bytes, 1 file は 4 MiB, 合計は 8 MiB が上限で, Host が正確な長さ, EOF, SHA-256 を検証します.
- プロトコル 1.5 は実行ごとに最大 1024 Host call、request/response ごとに 64 KiB、text に 32 KiB、1 dispatch の待機に 5 s の上限を設けます.
- キャンセルはプロセス再起動方式です. native extension とブロッキング呼び出しは Android 検証が必要です.
- `INTERNET` 権限によりスクリプトは標準ライブラリのネットワーク機能を直接利用できますが、online pip、自動コードダウンロード、実行時の第三者パッケージ導入は引き続き非対応です.

******

### 未宣言の機能

******

- 汎用 live stdin と直接の `sys.stdin` callback streaming は未対応です. foreground 対話は最大 1 MiB の有限 snapshot が EOF に達した後の組み込み `input()` と標準ライブラリの `getpass.getpass()` のみに適用されます. workspace への書き戻し, online pip, wheel ダウンロードも引き続き未対応です.
- UI スクリプト, debugger, REPL, ホスト Java オブジェクトへの任意アクセスはありません.
- live broker は最初の低リスク機能一式を提供します. files、dialogs、accessibility、screenshot、OCR は未宣言です.
- 32 bit Android と任意の native wheel は保証しません.
- 現在の tree には API 31 arm64-v8a 実機 smoke evidence と API 37 x86_64 16 KB page emulator smoke evidence がありますが, 完全な device matrix や release qualification とは扱いません.

******

### ロードマップ

******

R6-P2/P3 のローカル RC と集中端末証拠は履歴として保持されます. この clean VERSION_BUILD=11 freeze commit が stable Plugin source identity と exact Host 6.8.0/5275 lock を固定します. stable APK provenance はそれらの exact identity に対して評価され, production receipt も同じ基準を使用しなければなりません. 完全な API×ABI matrix と新 soak は自動 gate ではありません.

- [ROADMAP.md を表示](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 更新履歴

******

# v0.3.0-alpha.2

###### 2026/08/23

* `注記` M3 2 番目の current-tree alpha candidate です. 最初の低リスク Host capability 一式を実装しましたが, 後続 batch、公開、完全な device matrix はこの宣言に含みません
* `追加` live `autojs6.device.info()` のバッテリー/画面/明るさ/音量データ、`autojs6.console.log/warn/error` Host console レベル、`autojs6.notice` 通知を追加
* `改善` device result schema を厳密に検証し、通知権限不足を設定画面や権限状態の変更なしで安定した `PERMISSION_DENIED` として返す

# v0.3.0-alpha.1

###### 2026/08/23

* `注記` M3 最初の current-tree alpha candidate です. protocol 1.5 と低リスク Host capability subset を実装しましたが, 後続 capability、公開、完全な device matrix はこの宣言に含みません
* `追加` request UUID、plugin UID、単調 call ID、1024 call quota、64 KiB message、5 秒 Host dispatch 上限に結び付く pure-data JSON の protocol 1.5 execution-scoped Host capability broker を追加
* `追加` live Host API `autojs6.toast`、`autojs6.clip.get/set`、`autojs6.app.launch/launch_app/open_url` を追加
* `改善` terminal、cancel、Binder death、cleanup の全経路で broker を無効化し、unavailable capability と Host/protocol error を安定した Python error に変換

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

Maven の Chaquopy 17.0.0 と CPython 3.13.9 を lock し, stdlib のみを package します. release gate は依存 metadata, native library, NOTICE, SM003 signer, 3 種の配布 APK を exact identity に対して確認します. 現在の tree では API 37 x86_64 16 KB page emulator の focused smoke が合格していますが, 包括的な互換性 gate や device matrix の主張ではありません.

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
