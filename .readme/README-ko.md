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
- stdout과 stderr 순서를 유지하고 제한된 chunk를 credit으로 전달합니다.
- `SystemExit`, 구문 오류 및 런타임 예외를 제한된 구조화 traceback과 함께 반환합니다.
- 프로세스마다 활성 세션 하나만 허용하며 provider 큐를 두지 않습니다.
- 호스트 재시작이 필요 없습니다. 설치 또는 재활성화 후 다음 새 실행이 provider를 다시 검색하고 pin하며, 실행 중 Binder death는 해당 실행을 종료하고 자동 재실행하지 않습니다.

******

### 런타임 및 데이터 형식

******

프로토콜 V1은 현재 다음 범위를 선언합니다:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
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
protocol: 1.0-1.1
```

독립 SOURCE, 선택적인 제한 workspace archive 및 프로토콜 1.1의 읽기 전용 호스트 capability snapshot을 받습니다. stdin snapshot은 비활성 상태이며 Context, Binder, 호스트 런타임 객체 또는 callback sink를 주입하지 않습니다.

******

### 호스트 통합 상태

******

> 0.1.0은 AutoJs6 6.8.0 전용이며 최소 Host versionCode 5275가 동결되어 강제됩니다. 최종 clean Host source revision과 3개 AAR distribution manifest는 lock에 기록되었습니다. 새 실행마다 provider를 다시 검색하며, 없거나 비활성 상태면 install/enable을 안내하고 fallback하지 않습니다. 설치 또는 재활성화 후 Host 재시작은 필요 없습니다. stable APK identity는 해당 exact Plugin source와 Host lock에 결속됩니다.

```text
release target: 0.1.0
release state: stable 0.1.0 source identity frozen by the clean VERSION_BUILD=10 commit with the exact Host 6.8.0/5275 lock
paired host: AutoJs6 6.8.0 / versionCode 5275
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

- 소스는 4 MiB, 전체 출력은 4 MiB, chunk는 16 KiB, 개수는 4096로 제한합니다.
- timeout은 최대 60 s, 활성 세션은 하나이며 provider 큐가 없습니다.
- Binder 수신 측의 완전한 PFD 소유권을 채택하고 종료 또는 close 시 닫습니다.
- 출력은 먼저 제한된 메모리에 버퍼링한 뒤 credit으로 전송합니다. 실행 중 backpressure는 선언하지 않습니다.
- 취소는 프로세스 재시작 방식입니다. native extension과 blocking 호출은 Android 검증이 필요합니다.
- stdlib-only 정책으로 online pip와 타사 Python 패키지를 금지합니다. 병합 APK 권한은 빌드 때 확인해야 합니다.

******

### 선언하지 않은 기능

******

- stdin snapshot, workspace 쓰기, online pip 및 wheel 다운로드를 지원하지 않습니다.
- UI 스크립트, debugger, REPL 또는 호스트 Java 객체 임의 접근이 없습니다.
- 실시간 AutoJs6 capability broker는 없습니다. 첫 API는 실행 시작 시 동결된 app/device/execution/project snapshot과 plugin-private workspace의 제한된 읽기 전용 접근만 사용합니다.
- 32비트 Android와 임의의 native wheel은 보장하지 않습니다.
- arm64-v8a에는 API 31 기기 증거가 있습니다. x86_64는 현재 packaging 증거만 있으며 기기 실행이나 완전한 기기 matrix로 제시하지 않습니다.

******

### 로드맵

******

R6-P2/P3의 로컬 RC와 집중 기기 증거는 이력으로 보존됩니다. 이 clean VERSION_BUILD=10 freeze commit이 stable Plugin source identity와 exact Host 6.8.0/5275 lock을 고정합니다. stable APK provenance는 해당 exact identity를 기준으로 평가되며 production receipt도 같은 기준을 사용해야 합니다. 전체 API×ABI matrix와 새 soak는 자동 gate가 아닙니다.

- [ROADMAP.md 보기](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 변경 이력

******

# v0.1.0

###### 2026/08/12

* `안내` 0.1.0은 stable Plugin source identity와 exact Host 6.8.0/5275 lock을 고정합니다
* `추가` AutoJs6 6.8.0 / versionCode 5275와 함께 사용하는 Python 프로토콜 1.0-1.1, 제한된 project workspace 및 읽기 전용 app/device/execution/project snapshot
* `추가` 호스트 재시작 없는 hot-plug: install 또는 재활성화 후 다음 새 실행이 ID를 다시 검색하고 pin하며 없거나 비활성 상태면 fallback하지 않습니다
* `추가` 실행 중 Binder death는 replay 없이 현재 실행을 종료하고 이후 새 실행이 provider를 다시 검색합니다
* `개선` Chaquopy를 trusted-local, non-sandbox runtime으로 고정. 장기 signer는 SM003이며 runtime/security/release owner는 SuperMonster003
* `의존성` Chaquopy 17.0.0과 CPython 3.13.9를 lock. stable APK는 final source identity에 결속되고 exact artifact로 검증됩니다

# v0.1.0-alpha.1

###### 2026/08/09

* `안내` R2 개념 증명 소스. Gradle, APK, Binder 및 기기 승인은 미실행
* `추가` 전용 프로세스, 활성 세션 하나, provider 큐 없음으로 구성한 독립 Python V1 provider scaffold
* `추가` 단일 소스 `__main__` 실행, 제한된 stdout/stderr, 구조화 예외 및 프로세스 재시작 취소
* `추가` 고정 순서로 10개 언어 README와 앱 내 변경 이력 생성
* `의존성` Chaquopy 17.0.0 및 Python 3.13 사전 선택. 패키지 버전과 의존성 hash는 빌드 검증 필요

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

Maven의 Chaquopy 17.0.0과 CPython 3.13.9를 lock하고 stdlib만 package합니다. release gate는 의존성 metadata, native library, 16 KB page, NOTICE, SM003 signer 및 배포 APK 세 개를 exact identity에 대해 확인합니다.

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
