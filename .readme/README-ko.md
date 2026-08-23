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
- 실행 범위 pure-data 프로토콜 1.5 broker를 통해 `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, 권한 인식 `notice`, 제한된 `files.read_text/write_text/exists/is_file/is_dir/list`, foreground 전용 `dialogs.alert/confirm/prompt/select` 및 `engines.current/run/stop_self`를 실시간 호출하고 terminal에서 폐기합니다.
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
release target: 0.3.0-alpha.5
release state: 0.3.0-alpha.5 current-tree candidate; M1 and M2, the complete first low-risk protocol 1.5 Host capability slice, and the bounded Host-files, foreground-dialog, and engines portions of the second slice passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3 batches, a complete device matrix, publication, and release evidence remain outside this claim
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
- 취소는 프로세스 재시작 방식입니다. native extension과 blocking 호출은 Android 검증이 필요합니다.
- `INTERNET` 권한으로 스크립트가 표준 라이브러리 네트워크 기능을 직접 사용할 수 있지만, online pip, 자동 코드 다운로드, 런타임 타사 패키지 설치는 계속 지원하지 않습니다.

******

### 선언하지 않은 기능

******

- 일반 live stdin과 직접 `sys.stdin` callback streaming은 제공하지 않습니다. foreground 상호작용은 최대 1 MiB의 유한 snapshot이 EOF에 도달한 뒤 내장 `input()`과 표준 라이브러리 `getpass.getpass()`에만 적용됩니다. workspace 쓰기, online pip 및 wheel 다운로드는 계속 지원하지 않습니다.
- UI 스크립트, debugger, REPL 또는 호스트 Java 객체 임의 접근이 없습니다.
- live broker는 첫 저위험 기능 전체, 제한된 Host files, foreground dialogs 및 제한된 engines를 제공합니다. accessibility, screenshot 및 OCR은 아직 선언하지 않습니다.
- 32비트 Android와 임의의 native wheel은 보장하지 않습니다.
- 현재 tree에는 API 31 arm64-v8a 실제 기기 smoke evidence와 API 37 x86_64 16 KB page emulator smoke evidence가 있으며, 어느 쪽도 완전한 기기 matrix나 release qualification으로 제시하지 않습니다.

******

### 로드맵

******

R6-P2/P3의 로컬 RC와 집중 기기 증거는 이력으로 보존됩니다. 이 clean VERSION_BUILD=11 freeze commit이 stable Plugin source identity와 exact Host 6.8.0/5275 lock을 고정합니다. stable APK provenance는 해당 exact identity를 기준으로 평가되며 production receipt도 같은 기준을 사용해야 합니다. 전체 API×ABI matrix와 새 soak는 자동 gate가 아닙니다.

- [ROADMAP.md 보기](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 변경 이력

******

# v0.3.0-alpha.5

###### 2026/08/23

* `안내` 다섯 번째 M3 current-tree alpha candidate입니다. 두 번째 batch의 제한된 Host engines가 두 device의 focused acceptance를 통과했지만 이후 capability, 공개 배포 및 전체 device matrix는 포함하지 않습니다
* `추가` 경로 없는 현재 engine metadata, 비 Python Host child script 비동기 실행 및 결정적 self-stop을 제공하는 live `autojs6.engines.current/run/stop_self` API 추가
* `개선` child 경로는 실행 root 상대 정규화 형식만 허용하고 실행당 성공 실행은 최대 16회; 중첩 Python은 `NESTED_PYTHON_NOT_ALLOWED`, `stop_self`는 provider process restart로 취소

# v0.3.0-alpha.4

###### 2026/08/23

* `안내` 네 번째 M3 current-tree alpha candidate입니다. Foreground Host dialogs가 두 device의 focused acceptance를 통과했지만 engines, 이후 capability, 공개 배포 및 전체 device matrix는 포함하지 않습니다
* `추가` foreground 전용 `autojs6.dialogs.alert/confirm/prompt/select` API를 추가하고 acknowledgement, boolean, nullable text 및 0-based nullable index 결과를 제공합니다
* `개선` dialog title, content, reply 및 item을 제한하고 Host 소유 dialog를 한 번에 하나씩 직렬화하며 background 실행은 UI를 열지 않고 안정된 `INTERACTIVE_NOT_ALLOWED`로 거부합니다

# v0.3.0-alpha.3

###### 2026/08/23

* `안내` 세 번째 M3 current-tree alpha candidate입니다. 두 번째 batch의 제한된 Host files가 두 device의 focused acceptance를 통과했지만 dialogs, engines, 이후 capability, 공개 배포 및 전체 device matrix는 포함하지 않습니다
* `추가` 현재 project root 또는 standalone script directory 안에서 제한된 UTF-8 text access를 제공하는 live `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` API 추가
* `개선` 안전하지 않거나 root를 벗어나는 path를 거부하고 text와 direct listing을 제한하며 안정된 file error를 반환하고 live Host root와 고정된 Plugin workspace snapshot을 명확히 분리

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
