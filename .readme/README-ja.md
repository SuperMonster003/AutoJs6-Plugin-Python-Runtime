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
- 許可済み project root から project-local pure-Python package と `.dist-info` metadata を import でき, online pip や runtime install は行いません.
- スクリプト実行中に stdout/stderr の元の順序を保って上限付き chunk を credit で送信し, credit 枯渇時は実行に backpressure をかけます.
- protocol 1.4 で最大 64 KiB の明示的な厳密 JSON result を設定し, path, size, SHA-256 上限付きの任意 output artifact を最大 16 個転送します. stdout から result を推測しません.
- 実行単位の pure-data protocol 1.5 broker を通して `toast`、`clip.get/set`、`app.launch/launch_app/open_url`、`device.info`、`console.log/warn/error`、権限を考慮した `notice`、有界な `files.read_text/write_text/exists/is_file/is_dir/list`、foreground 限定の `dialogs.alert/confirm/prompt/select`、`engines.current/run/stop_self`、有界な `automator.click/long_click/press/swipe/back/home`、有界な `selector.snapshot/find/click/set_text`、`images.capture_screen`、`images.find_color`、`images.find_image`、`ocr.recognize` をリアルタイムに呼び出し、terminal 時に無効化します.
- プロトコル 1.6 は明示的な `executionMode=long-running` project に実行 deadline のない mode、Host foreground 通知、Stop action、15 s ごとの順序付き Provider heartbeat を追加します. background 起動 surface は downgrade せず fail closed します.
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
protocol: 1.0-1.6
```

独立 SOURCE, 任意の上限付き workspace archive, 最大 1 MiB の有限な事前供給 stdin snapshot, プロトコル 1.1 の読み取り専用ホスト能力 snapshot を受け付けます. プロトコル 1.2 は許可済み project に明示的な file/module entry negotiation を追加します. プロトコル 1.3 は snapshot EOF 後の組み込み `input()` に, Host 所有かつ foreground 限定の prompt/reply を追加し, 標準ライブラリの `getpass.getpass()` は非表示入力を使用します. プロトコル 1.4 は明示的な厳密 JSON と任意の SHA-256 manifest output artifact を追加し, stdout は診断のままで result として解析しません. プロトコル 1.5 は 1 回の実行、plugin UID、call 順序、有限 quota に結び付く pure-data Host broker を追加します. Host dialog にも live Activity に裏付けられた foreground 認可が必要で, background 起動は UI を開かず `INTERACTIVE_NOT_ALLOWED` を返します. 直接の `sys.stdin` は有限のままで, background 起動は入力 UI を開かず, user script に Context、raw Binder、Host runtime object、callback sink は渡しません.

******

### ホスト統合状況

******

> 0.1.0 は AutoJs6 6.8.0 専用で, 最小 Host versionCode 5275 は凍結され強制されます. 最終 clean Host source revision と 3 AAR distribution manifest は lock に記録済みです. 新規実行ごとに provider を再検出し, 不在または無効時は install/enable を案内して fallback しません. インストールまたは再有効化に Host 再起動は不要です. stable APK identity はその exact Plugin source と Host lock に紐づきます.

```text
release target: 0.5.0-alpha.1
release state: 0.5.0-alpha.1 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, configured Host OCR recognition, and a complete Settings launch/find/click/screenshot workflow passed their eligible-service paths on the emulator, while the applicable capability-unavailable paths failed closed on the physical device without changing its accessibility services; the M4 Path B build-time pure-Python and M4 Path C native-package evaluations are complete with decision NOT_ADMITTED, so the embedded package policy remains stdlib-only with zero packages and online pip disabled; Path C built the official Pillow 11.0.0 and NumPy 1.26.2 dual-ABI closures offline, but transitive 4 KiB ELF LOAD segments failed the 16 KiB gate, and the official OpenCV index had no cp313 Android wheel; no candidate dependency payload was added; protocol 1.6 adds an explicit foreground-only long-running mode with a Host specialUse foreground notification, manual Stop, and 15-second Provider heartbeats under fail-closed leases; Host and Plugin offline JVM plus portable source gates passed, but no M5 Android device smoke has run and no new device claim is made; concurrency, prewarm, later demand-driven M3 batches, M4 Path D, a complete device matrix, publication, and release evidence remain outside this claim
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
- 有界 request の timeout は最大 30 min です. 明示的 long-running project に実行 deadline はありませんが, Host foreground lifetime、2 min の start lease、45 s の heartbeat lease が必要です. active session は 1 つのままで provider queue はありません.
- Project workspace は圧縮後 64 MiB, file entry 8192 件, 展開後 128 MiB が上限です. Dispatch 前の Provider 選択では snapshot の実際の 3 次元要件をすべて満たす必要があります.
- Binder 受信側の完全な PFD を所有し, 終端または close 時に閉じます.
- 出力は実行中に credit ごとに chunk 単位で送信します. credit 枯渇時はスクリプトを停止し, 受理済み出力は唯一の terminal より前に置かれ, terminal 後の出力は禁止されます.
- 構造化 JSON は 64 KiB, artifact は最大 16 個, path は 1024 UTF-8 bytes, 1 file は 4 MiB, 合計は 8 MiB が上限で, Host が正確な長さ, EOF, SHA-256 を検証します.
- プロトコル 1.5 は実行ごとに最大 1024 Host call、request/response ごとに 64 KiB、text に 32 KiB、通常の Host main-thread action の待機に 5 s の上限を設けます. Host files は 4 KiB の相対 path、32 KiB の UTF-8 text、最大 128 件かつ各 255 UTF-8 bytes の名前に制限されます. Foreground dialog は title 256 UTF-8 bytes、content 4 KiB、prompt default/reply 32 KiB、select 最大 64 項・各 1 KiB・合計 32 KiB に制限され、1 回の応答を最大 5 min 待ちます. 1 実行で成功できるのは scope 内の非 Python Host child script の非同期起動 16 回までで、nested Python は `NESTED_PYTHON_NOT_ALLOWED`、`stop_self` は process restart による cancel になります.
- Automator 座標は 0 から 1000000 までの厳密な整数で、press と swipe の継続時間は 1 ms から 4 s です. Host accessibility が利用できない場合は設定を開かず `CapabilityUnavailableError` を送出します.
- Selector snapshot は最大 128 node、深さ 32、JSON 48 KiB までです. find は最大 1024 node を走査し、node text は 256 Unicode code points、query text は 1024 UTF-8 bytes、set_text は 4 KiB、各実行の保持 node reference は 128 に制限されます. 不完全な走査は `SELECTOR_SCAN_LIMIT_EXCEEDED`、期限切れ reference は `STALE_NODE` を返します.
- Screen capture は各実行で最大 1 枚を保持し、encoded data は 4 MiB、raw chunk は 32 KiB、各辺は 8192 pixel、総面積は 16777216 pixel に制限します. Python は返却前に length、order、EOF、SHA-256、format signature を検証します. accessibility/API が利用できない場合は `CapabilityUnavailableError`、その他の安定した error は `SCREEN_CAPTURE_FAILED`、`RESULT_LIMIT_EXCEEDED`、`STALE_IMAGE` です. Color search は新しい screenshot を row-major 順で走査し、任意の有界 region と channel ごとに最大 255 の threshold を使い、image byte を転送せず座標または未検出だけを返します. Template search は各実行で最大 1 個の PNG/JPEG template を保持し、1 MiB、raw chunk 24 KiB、各辺 2048、面積 1048576、search region 4194304、comparison 16777216 に制限します. 完全に opaque な pixel だけが参加し、他は wildcard、走査は deterministic row-major で、buffer は terminal 時に release と zero 化されます.
- `ocr.recognize` は 1 MiB、raw chunk 24 KiB、一辺 2048 pixel、decode 後 1048576 pixel の PNG/JPEG template envelope を再利用します. 設定済み Host OCR engine は既存の 60 s admission/call budget 内で最大 256 行、1 行 4 KiB の strict UTF-8、合計 48 KiB を返します. 利用不可と失敗は `OCR_UNAVAILABLE` と `OCR_FAILED` で報告し、upload は常に release/zeroize されます.
- キャンセルはプロセス再起動方式です. native extension とブロッキング呼び出しは Android 検証が必要です.
- `INTERNET` 権限によりスクリプトは標準ライブラリのネットワーク機能を直接利用できますが、online pip、自動コードダウンロード、実行時の第三者パッケージ導入は引き続き非対応です.

******

### 未宣言の機能

******

- 汎用 live stdin と直接の `sys.stdin` callback streaming は未対応です. foreground 対話は最大 1 MiB の有限 snapshot が EOF に達した後の組み込み `input()` と標準ライブラリの `getpass.getpass()` のみに適用されます. workspace への書き戻し, online pip, wheel ダウンロードも引き続き未対応です.
- UI スクリプト, debugger, REPL, ホスト Java オブジェクトへの任意アクセスはありません.
- live broker は最初の低リスク機能一式、有界な Host files、foreground dialogs、有界な engines、明示的な座標/global automator action、有界な selector/UI tree snapshot/action、有界な screen capture、`find_color`、`find_image`、line-oriented OCR を提供します. OCR box/confidence/options、mutable image processing、multi-scale matching は未宣言です.
- 32 bit Android と任意の native wheel は保証しません.
- 現在の tree には API 31 arm64-v8a 実機 smoke evidence と API 37 x86_64 16 KB page emulator smoke evidence がありますが, 完全な device matrix や release qualification とは扱いません.

******

### ロードマップ

******

M4 Path A は完了しました. M4 Paths B/C の評価はいずれも `NOT_ADMITTED` で、組み込み runtime は `stdlib-only` を維持します. Path C では Pillow/NumPy を offline build できましたが、完全な native closure は dual ABI 16 KiB ELF gate に失敗し、OpenCV には `cp313` Android wheel がありません. Path D は明確な需要時に進めます. M3 automation は有界 action、selector/UI tree、screen capture、color search、PNG/JPEG template matching、Host OCR を提供します. 歴史的 evidence tool は自動 release gate にはしません.

- [ROADMAP.md を表示](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 更新履歴

******

# v0.5.0-alpha.1

###### 2026/08/24

* `注記` 最初の M5 current-tree alpha 候補です. protocol 1.6 foreground long-running source と offline Host/Plugin JVM・portable gate は成功しましたが, M5 Android smoke は未実行で publication、concurrency、process prewarm は主張しません
* `追加` project 単位の `executionMode=long-running` を追加し実行 deadline をなくします. Host `specialUse` foreground service、常駐 notification、Stop action が lifetime を所有し, schedule、background/Intent、developer launch は downgrade せず拒否します
* `改善` Provider は 15 s ごとに順序付き heartbeat を送信し, Host は start 2 min、heartbeat 45 s、独立 foreground-service lease を強制します. liveness loss と Stop は process-restart cancellation で fail closed し, bounded protocol 1.0-1.5 は互換のままです

# v0.4.0-alpha.9

###### 2026/08/24

* `注記` 9 番目の current-tree alpha 候補. M4 Path C native package 評価を `NOT_ADMITTED` で完了し、組み込み runtime は `stdlib-only` を維持します. Pillow、NumPy、OpenCV または推移的 native payload は追加せず、新しい device acceptance も主張しません
* `改善` ADR 0004 は `--no-index --find-links` による dual ABI offline debug build を記録します. Pillow 11.0.0 は各 APK に 2,054,483 bytes、NumPy 1.26.2 は 21,931,164 bytes を追加し、6 出力すべてが `zipalign -c -P 16 4` を通過しました
* `改善` NDK 29 の完全 closure ELF 監査は両 ABI の FreeType `0x1000` と x86_64 の OpenBLAS/libgfortran `0x1000` を拒否します. OpenCV に公式 `cp313` Android wheel はなく、再開には再現可能な NDK r28+ wheel と 16 KiB public-engine acceptance が必要です

# v0.4.0-alpha.8

###### 2026/08/24

* `注記` 8 番目の current-tree alpha 候補. M4 Path B build-time package 評価を `NOT_ADMITTED` で完了し、組み込み runtime は `stdlib-only` を維持します. `requests` を含む候補依存関係は追加せず、新しい device acceptance も主張しません
* `改善` ADR 0003 は stdlib-only debug APK baseline を arm64-v8a 23,709,688 bytes、x86_64 23,726,048 bytes、universal 34,622,039 bytes と記録します. 監査済み offline wheelhouse なしの虚偽の差分を避け、将来の採用には Gradle `--offline`、`--no-index`、`--require-hashes`、license/hash lock、3 APK の size delta と dual ABI public-engine acceptance を要求します

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
