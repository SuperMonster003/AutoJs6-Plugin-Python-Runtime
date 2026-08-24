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

独立 SOURCE, 任意の上限付き workspace archive, 最大 1 MiB の有限な事前供給 stdin snapshot, プロトコル 1.1 の読み取り専用ホスト能力 snapshot を受け付けます. プロトコル 1.2 は許可済み project に明示的な file/module entry negotiation を追加します. プロトコル 1.3 は snapshot EOF 後の組み込み `input()` に, Host 所有かつ foreground 限定の prompt/reply を追加し, 標準ライブラリの `getpass.getpass()` は非表示入力を使用します. プロトコル 1.4 は明示的な厳密 JSON と任意の SHA-256 manifest output artifact を追加し, stdout は診断のままで result として解析しません. プロトコル 1.5 は 1 回の実行、plugin UID、call 順序、有限 quota に結び付く pure-data Host broker を追加します. Host dialog にも live Activity に裏付けられた foreground 認可が必要で, background 起動は UI を開かず `INTERACTIVE_NOT_ALLOWED` を返します. 直接の `sys.stdin` は有限のままで, background 起動は入力 UI を開かず, user script に Context、raw Binder、Host runtime object、callback sink は渡しません.

******

### ホスト統合状況

******

> 0.1.0 は AutoJs6 6.8.0 専用で, 最小 Host versionCode 5275 は凍結され強制されます. 最終 clean Host source revision と 3 AAR distribution manifest は lock に記録済みです. 新規実行ごとに provider を再検出し, 不在または無効時は install/enable を案内して fallback しません. インストールまたは再有効化に Host 再起動は不要です. stable APK identity はその exact Plugin source と Host lock に紐づきます.

```text
release target: 0.4.0-alpha.6
release state: 0.4.0-alpha.6 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, one-shot RGB find_color, bounded PNG/JPEG find_image template matching, and configured Host OCR recognition passed their eligible-service paths on the emulator and failed closed on the physical device without changing its accessibility services; later M3/M4 batches, a complete device matrix, publication, and release evidence remain outside this claim
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

M4 Path A は完了し, M3 automation は有界な座標/global action、有界な selector/UI tree data plane、screen capture、one-shot RGB color search、有界な PNG/JPEG template matching、設定済み Host OCR engine による line-oriented recognition を提供します. より高度な image/OCR operation と M4 build-time/native package path は user value に従って進め, 歴史的 evidence tool は利用可能なままですが自動 release gate にはしません.

- [ROADMAP.md を表示](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 更新履歴

******

# v0.4.0-alpha.6

###### 2026/08/24

* `注記` 6 番目の M3 automation current-tree alpha candidate. 設定済み Host OCR recognition は eligible service のある API 37 emulator で成功し、API 31 physical device では accessibility service を変更せず fail-closed しました. より高度な OCR、publication、完全な device matrix はこの claim の対象外です
* `追加` 有界な PNG/JPEG bytes を受け取り、設定済み Host OCR engine の ordered immutable text-line tuple を返す `autojs6.ocr.recognize(image)` を追加
* `改善` 1 MiB の PNG/JPEG upload、24 KiB raw chunk、SHA-256 verification を再利用し、enabled/authorized/compatible な Host OCR service だけを選択します. 結果を 256 行、1 行 4 KiB strict UTF-8、合計 48 KiB に制限し、buffer を常に release/zeroize し、`OCR_UNAVAILABLE` または `OCR_FAILED` を安定して報告します

# v0.4.0-alpha.5

###### 2026/08/24

* `注記` 現行 tree の第 5 M3 automation alpha candidate です. 有界 template matching は accessibility 有効の API 37 emulator で成功し、API 31 実機では accessibility service を変更せず fail-closed しました. OCR、公開、完全な device matrix はこの主張に含みません
* `追加` PNG/JPEG bytes、任意の有界 region、左上座標または `None` を扱う `autojs6.images.find_image(template, *, region=None, threshold=0)` を追加
* `改善` 実行ごとに最大 1 MiB の template 1 個を 24 KiB raw chunk と SHA-256 検証で upload し、各辺 2048 pixel 以下で decode、`autojs6-python-image-match-v1` の row-major 順で deterministic scan します. 完全 opaque pixel だけを対象、他を wildcard とし、OpenCV は不要で、必ず release と buffer の zero 化を行い、Android の 333 ms screenshot throttle だけを有界な 350 ms 待機後に retry します

# v0.4.0-alpha.4

###### 2026/08/24

* `注記` 現行 tree の第 4 M3 automation alpha candidate; 有界 screen color search は accessibility 有効の API 37 emulator で成功し、API 31 実機では既存 service を変更せず fail-closed を確認; template image matching、OCR、公開、完全な device matrix は対象外
* `追加` 厳密な RGB integer または `#RRGGBB` text、任意の有界 region、座標または `None` result を持つ `autojs6.images.find_color(color, *, region=None, threshold=0)` を追加
* `改善` 呼び出しごとに新しい Android 11+ accessibility screenshot を 1 枚取得し、0..255 の channel 別 threshold で deterministic row-major 順に走査し、厳密な `autojs6-python-color-match-v1` を検証して image byte や handle を Python へ転送しない

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
