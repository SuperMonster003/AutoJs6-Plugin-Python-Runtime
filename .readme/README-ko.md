<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>독립 Python 런타임 플러그인. 전용 프로세스에서 Python 스크립트 실행</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### 언어

******

현재 README.md는 다음 언어를 지원합니다:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- [English [en]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-en.md)
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- 한국어 [ko] # 현재
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### 소개

******

Python Runtime은 Python 프로토콜 V1의 독립 provider입니다. 호스트가 하나의 Python 소스 스냅샷을 전용 프로세스에 전달하면 CPython으로 실행하고 제한된 출력, 구조화된 예외, 하나의 종료 상태를 반환합니다.

> 0.1.0 source identity와 exact Host lock은 동결되었습니다. 기존 로컬 RC build, APK, Binder 및 API 31 arm64-v8a 기기 한 대의 증거는 이력 증거로 남습니다. stable APK/P3 provenance는 exact release identity에 결속되고 production receipt는 게시 후의 독립 증거 수준입니다.

******

### 기능

******

- UTF-8 Python 소스 스냅샷 하나를 `__main__`으로 실행합니다.
- 최대 1 MiB의 유한한 사전 제공 stdin snapshot을 받습니다. snapshot이 EOF에 도달한 뒤에는 명시적 foreground 실행에서 프로토콜 1.3의 제한된 prompt/reply로 내장 `input()`을 계속할 수 있고 표준 라이브러리 `getpass.getpass()`는 숨김 입력을 사용합니다.
- 승인된 project에서 `entryMode=file|module`을 명시적으로 선택합니다. module mode는 표준 `runpy` metadata, project root의 `sys.path[0]` 및 package-relative import를 사용하고 file mode는 일반 script semantics를 유지합니다.
- 승인된 project root에서 project-local pure-Python package와 `.dist-info` metadata를 import하며 online pip 또는 runtime install을 수행하지 않습니다.
- 스크립트 실행 중 stdout/stderr의 원래 순서대로 제한된 chunk를 credit으로 전달하며, credit이 소진되면 실행에 backpressure를 적용합니다.
- 프로토콜 1.4에서 최대 64 KiB의 명시적 엄격 JSON 결과를 설정하고 path, size 및 SHA-256 제한이 있는 선택적 output artifact를 최대 16개 전달하며 stdout에서 결과를 추론하지 않습니다.
- 실행 범위 pure-data 프로토콜 1.5 broker를 통해 `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, 권한 인식 `notice`, 제한된 `files.read_text/write_text/exists/is_file/is_dir/list`, foreground 전용 `dialogs.alert/confirm/prompt/select`, `engines.current/run/stop_self`, 제한된 `automator.click/long_click/press/swipe/back/home`, 제한된 `selector.snapshot/find/click/set_text`, `images.capture_screen` 및 `images.find_color`를 실시간 호출하고 terminal에서 폐기합니다.
- `SystemExit`, 구문 오류 및 런타임 예외를 제한된 구조화 traceback과 함께 반환합니다.
- 프로세스마다 활성 세션 하나만 허용하며 provider 큐를 두지 않습니다.
- 호스트 재시작이 필요 없습니다. 설치 또는 재활성화 후 다음 새 실행이 provider를 다시 검색하고 pin하며, 실행 중 Binder death는 해당 실행을 종료하고 자동 재실행하지 않습니다.

******

### 런타임 및 데이터 형식

******

프로토콜 V1은 현재 다음 범위를 선언합니다:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

빌드는 Python 3.13을 요청합니다. 동결된 로컬 RC 산출물과 정확한 기기 실행은 CPython 3.13.9를 기록했습니다. 최종 0.1.0은 소스 동결 후 버전과 hash를 다시 검증해야 합니다.

******

### 플러그인 인터페이스

******

호스트는 다음 식별자로 플러그인을 검색하고 호출합니다:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.5
```

독립 SOURCE, 선택적인 제한 workspace archive, 최대 1 MiB의 유한한 사전 제공 stdin snapshot 및 프로토콜 1.1의 읽기 전용 호스트 capability snapshot을 받습니다. 프로토콜 1.2는 승인된 project에 명시적인 file/module entry negotiation을 추가합니다. 프로토콜 1.3은 snapshot EOF 뒤 내장 `input()`에 Host 소유의 foreground 전용 prompt/reply를 추가하고 표준 라이브러리 `getpass.getpass()`는 숨김 입력을 사용합니다. 프로토콜 1.4는 명시적 엄격 JSON과 선택적 SHA-256 manifest output artifact를 추가하며 stdout은 진단 텍스트로 유지되고 결과로 분석되지 않습니다. 프로토콜 1.5는 단일 실행, plugin UID, call 순서 및 유한 quota에 묶인 pure-data Host broker를 추가합니다. Host dialog도 live Activity 기반 foreground 승인이 필요하며 background 실행은 UI를 열지 않고 `INTERACTIVE_NOT_ALLOWED`를 반환합니다. 직접 `sys.stdin`은 계속 유한하며 background 실행은 입력 UI를 열지 않고 user script에 Context, raw Binder, Host runtime 객체 또는 callback sink를 제공하지 않습니다.

******

### 호스트 통합 상태

******

> 0.1.0은 AutoJs6 6.8.0 전용이며 최소 Host versionCode 5275가 동결되어 강제됩니다. 최종 clean Host source revision과 3개 AAR distribution manifest는 lock에 기록되었습니다. 새 실행마다 provider를 다시 검색하며, 없거나 비활성 상태면 install/enable을 안내하고 fallback하지 않습니다. 설치 또는 재활성화 후 Host 재시작은 필요 없습니다. stable APK identity는 해당 exact Plugin source와 Host lock에 결속됩니다.

```text
release target: 0.4.0-alpha.4
release state: 0.4.0-alpha.4 current-tree candidate; the pre-existing M1/M2 and protocol 1.5 slices plus M4 Path A project-local pure-Python packages passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; bounded automator actions, execution-local selector/UI-tree snapshot/find/click/set_text, bounded Android 11+ screen capture, and one-shot RGB find_color passed their enabled-service paths on the emulator and fail-closed on the physical device without changing its accessibility services; template image matching, OCR, later M3/M4 batches, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### 보안 및 개인정보

******

Chaquopy runtime은 신뢰하는 로컬 스크립트 전용이며 hostile-code sandbox가 아닙니다. exported service는 호스트 서명 권한을 요구하고 UID, package 및 signer를 다시 확인합니다. 별도 Android UID, 전용 프로세스 및 좁은 Binder 경계는 노출을 줄이지만 Python을 sandbox로 만들지 않습니다. 장기 릴리스 signer는 SM003이며 runtime/security/release owner는 SuperMonster003입니다.

******

### 실행 제한

******

- 소스는 4 MiB, 전체 출력은 16 MiB, chunk는 16 KiB, 개수는 16384로 제한합니다.
- timeout은 최대 30 min, 활성 세션은 하나이며 provider 큐가 없습니다.
- Project workspace는 압축 후 64 MiB, file entry 8192개, 추출 후 128 MiB로 제한되며 dispatch 전에 Provider 선택이 snapshot의 실제 3차원 요구량을 모두 충족해야 합니다.
- Binder 수신 측의 완전한 PFD 소유권을 채택하고 종료 또는 close 시 닫습니다.
- 출력은 실행 중 credit에 따라 chunk 단위로 전달됩니다. credit 소진 시 스크립트가 일시 중지되고, 수락된 출력은 유일한 terminal보다 먼저 전달되며 terminal 이후 출력은 금지됩니다.
- 구조화 JSON은 64 KiB, artifact는 최대 16개, path는 1024 UTF-8 bytes, file당 4 MiB, 합계 8 MiB로 제한하며 Host가 정확한 길이, EOF 및 SHA-256을 검증합니다.
- 프로토콜 1.5는 실행당 Host call을 최대 1024회, request/response를 각각 64 KiB, text를 32 KiB, 일반 Host main-thread action 대기를 5 s로 제한합니다. Host files는 4 KiB 상대 경로, 32 KiB UTF-8 text, 최대 128개 및 각 255 UTF-8 bytes의 이름으로 제한됩니다. Foreground dialog는 title 256 UTF-8 bytes, content 4 KiB, prompt default/reply 32 KiB, select 최대 64개·각 1 KiB·합계 32 KiB로 제한되며 사용자 응답을 최대 5 min 기다립니다. 한 실행에서 범위가 제한된 비 Python Host child script를 비동기로 성공 실행할 수 있는 횟수는 16회이며, 중첩 Python은 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self`는 process restart 취소를 사용합니다.
- Automator 좌표는 0부터 1000000까지의 엄격한 정수이며 press와 swipe 지속 시간은 1 ms부터 4 s까지입니다. Host accessibility를 사용할 수 없으면 설정을 열지 않고 `CapabilityUnavailableError`를 발생시킵니다.
- Selector snapshot은 최대 128개 node, 깊이 32, JSON 48 KiB를 허용합니다. find는 최대 1024개 node를 검색하고 node text는 256 Unicode code points, query text는 1024 UTF-8 bytes, set_text는 4 KiB, 실행별 보존 node reference는 128개로 제한됩니다. 불완전한 검색은 `SELECTOR_SCAN_LIMIT_EXCEEDED`, 오래된 reference는 `STALE_NODE`를 반환합니다.
- Screen capture는 실행당 최대 1개 이미지를 보존하고 encoded data를 4 MiB, raw chunk를 32 KiB, 각 변을 8192 pixel, 총 면적을 16777216 pixel로 제한합니다. Python은 반환 전에 length, order, EOF, SHA-256 및 format signature를 검증합니다. accessibility/API를 사용할 수 없으면 `CapabilityUnavailableError`, 기타 안정 오류는 `SCREEN_CAPTURE_FAILED`, `RESULT_LIMIT_EXCEEDED`, `STALE_IMAGE`입니다. Color search는 새 screenshot을 row-major 순서로 스캔하고 선택적 제한 region과 채널별 최대 255 threshold를 사용하며 image byte를 전송하지 않고 좌표 또는 미검출만 반환합니다.
- 취소는 프로세스 재시작 방식입니다. native extension과 blocking 호출은 Android 검증이 필요합니다.
- `INTERNET` 권한으로 스크립트가 표준 라이브러리 네트워크 기능을 직접 사용할 수 있지만, online pip, 자동 코드 다운로드, 런타임 타사 패키지 설치는 계속 지원하지 않습니다.

******

### 선언하지 않은 기능

******

- 일반 live stdin과 직접 `sys.stdin` callback streaming은 제공하지 않습니다. foreground 상호작용은 최대 1 MiB의 유한 snapshot이 EOF에 도달한 뒤 내장 `input()`과 표준 라이브러리 `getpass.getpass()`에만 적용됩니다. workspace 쓰기, online pip 및 wheel 다운로드는 계속 지원하지 않습니다.
- UI 스크립트, debugger, REPL 또는 호스트 Java 객체 임의 접근이 없습니다.
- live broker는 첫 저위험 기능 전체, 제한된 Host files, foreground dialogs, 제한된 engines, 명시적 좌표/global automator action, 제한된 selector/UI tree snapshot/action, 제한된 screen capture 및 `find_color`를 제공합니다. `find_image`, template upload 및 OCR은 아직 선언하지 않습니다.
- 32비트 Android와 임의의 native wheel은 보장하지 않습니다.
- 현재 tree에는 API 31 arm64-v8a 실제 기기 smoke evidence와 API 37 x86_64 16 KB page emulator smoke evidence가 있으며, 어느 쪽도 완전한 기기 matrix나 release qualification으로 제시하지 않습니다.

******

### 로드맵

******

M4 Path A가 완료되었고 M3 automation은 이제 Host accessibility를 통한 제한된 좌표/global action, 제한된 selector/UI tree data plane, screen capture 및 one-shot RGB color search를 포함합니다. Template image matching, OCR 및 M4 build-time/native package path는 user value에 따라 진행하며, 과거 evidence tool은 계속 사용할 수 있지만 자동 release gate로 사용하지 않습니다.

- [ROADMAP.md 보기](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 변경 이력

******

# v0.4.0-alpha.4

###### 2026/08/24

* `안내` 현재 tree의 네 번째 M3 automation alpha candidate; 제한된 screen color search는 accessibility가 활성화된 API 37 emulator에서 통과하고 API 31 실제 기기에서는 기존 service를 변경하지 않고 fail-closed 통과; template image matching, OCR, 공개 및 전체 device matrix는 범위 밖
* `추가` 엄격한 RGB integer 또는 `#RRGGBB` text, 선택적 제한 region, 좌표 또는 `None` 결과를 제공하는 `autojs6.images.find_color(color, *, region=None, threshold=0)` 추가
* `개선` 호출마다 새 Android 11+ accessibility screenshot 한 장을 캡처하고 0..255 채널별 threshold로 deterministic row-major 순서로 스캔하며 정확한 `autojs6-python-color-match-v1`을 검증하고 image byte나 handle을 Python으로 전송하지 않음

# v0.4.0-alpha.3

###### 2026/08/24

* `안내` 현재 tree의 세 번째 M3 automation alpha candidate입니다. 제한된 Android 11+ screen-capture 전체 경로는 accessibility service를 활성화한 API 37 emulator에서 focused acceptance를 통과했고, fail-closed는 기존 accessibility service를 변경하지 않고 API 31 physical device에서 통과했습니다; image/color matching, OCR, publication 및 전체 device matrix는 이 선언에 포함하지 않습니다
* `추가` 검증된 PNG/JPEG encoded bytes를 반환하거나 execution output artifact를 atomic하게 기록하고 게시하는 `autojs6.images.capture_screen`을 추가
* `개선` 실행당 최대 1 capture를 보존하고 32 KiB raw chunk로 전송하며 encoded data를 4 MiB로 제한합니다. Python은 order, EOF, SHA-256 및 format signature를 검증하고 항상 release하며 Host는 replacement/release/terminal에서 zero 처리하고 service 활성화나 설정 열기 없이 안정 오류를 반환합니다

# v0.4.0-alpha.2

###### 2026/08/24

* `안내` 현재 tree의 두 번째 M3 automation alpha candidate입니다. 제한된 selector/UI tree 전체 경로는 accessibility service를 활성화한 API 37 emulator에서 focused acceptance를 통과했고, fail-closed는 기존 accessibility service를 변경하지 않고 API 31 physical device에서 통과했습니다; screenshot, OCR, publication 및 전체 device matrix는 이 선언에 포함하지 않습니다
* `추가` 분리된 accessibility tree data, AND 조합 first-match query 및 불투명한 execution-local node reference를 통한 명시적 action을 제공하는 live `autojs6.selector.snapshot/find/click/set_text` API 추가
* `개선` Snapshot node, depth, payload, node text, selector scan size, query/set text 및 retained node를 제한; 불완전 scan은 `SELECTOR_SCAN_LIMIT_EXCEEDED`, stale reference는 `STALE_NODE`, accessibility 사용 불가는 설정을 열지 않고 `CapabilityUnavailableError`로 보고

##### 다른 버전

* [CHANGELOG-ko.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-ko.md)

******

### 검증

******

Gradle이나 ADB를 호출하지 않는 파일시스템 정적 검사:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

로컬 CPython을 사용한 이식 가능한 bootstrap 의미 테스트:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

정적 검사와 로컬 CPython은 Android 증거를 대체하지 않습니다. 기존 RC와 단일 기기 결과는 이력입니다. release acceptance는 exact identity에 직접 연결된 빌드, APK, Binder 및 대표 기기 검사를 사용합니다.

******

### 빌드

******

문서 생성 자체는 빌드를 실행하지 않습니다. release 설정은 AAR, SHA-256, signer 또는 runtime lock drift 시 fail closed됩니다. stable artifact는 exact release identity에 결속될 때만 허용됩니다.

빌드 전에 다음 release AAR을 `libs`에 배치하고 고정해야 합니다:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

Maven의 Chaquopy 17.0.0과 CPython 3.13.9를 lock하고 stdlib만 package합니다. release gate는 의존성 metadata, native library, NOTICE, SM003 signer 및 배포 APK 세 개를 exact identity에 대해 확인합니다. 현재 tree의 API 37 x86_64 16 KB page emulator focused smoke는 통과했지만, 포괄적인 호환성 gate나 기기 matrix를 의미하지 않습니다.

******

### 라이선스

******

프로젝트 소스는 MPL-2.0입니다. Chaquopy, CPython 및 기타 구성 요소는 각 라이선스를 따르며 attribution과 upstream/project source 접근은 `THIRD_PARTY_NOTICES.md`에 기록됩니다.

******

### 리소스 구성

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py`는 고정 순서 JSON에서 10개 언어 README와 앱 내 변경 이력을 생성합니다. Android 문자열은 각 리소스 디렉터리에서 관리합니다.

******

### 링크

******

- AutoJs6 문서: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
