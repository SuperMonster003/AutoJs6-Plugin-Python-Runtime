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

> 현재 R2 개념 증명 단계입니다. 런타임 소스와 로컬 bootstrap 의미 검사는 있지만 Gradle 설정, Android 컴파일, APK 검사, Binder 검증 및 기기 승인은 실행하지 않았습니다.

******

### 기능

******

- UTF-8 Python 소스 스냅샷 하나를 `__main__`으로 실행합니다.
- stdout과 stderr 순서를 유지하고 제한된 chunk를 credit으로 전달합니다.
- `SystemExit`, 구문 오류 및 런타임 예외를 제한된 구조화 traceback과 함께 반환합니다.
- 프로세스마다 활성 세션 하나만 허용하며 provider 큐를 두지 않습니다.
- 취소, timeout 또는 callback death 후 스크립트를 재실행하지 않고 전용 프로세스를 폐기합니다.

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

빌드는 Python 3.13을 요청합니다. 3.13.9는 현재 Chaquopy 릴리스 정보에 따른 예상 패키지 버전이며 APK 검사와 기기 실행 전에는 검증된 사실이 아닙니다.

******

### 플러그인 인터페이스

******

호스트는 다음 식별자로 플러그인을 검색하고 호출합니다:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

SOURCE descriptor만 받습니다. workspace archive와 stdin snapshot 한도는 0이며 Context, Binder, 호스트 런타임 객체 또는 callback sink를 주입하지 않습니다.

******

### 호스트 통합 상태

******

> 프로토콜 및 호스트 연결은 진행 중이지만 필요한 release AAR은 아직 게시 및 검증되지 않았습니다. 이 scaffold 설치만으로 동작하는 Python 엔진이 구성되지는 않습니다.

******

### 보안 및 개인정보

******

소스 manifest는 Android 권한을 요청하지 않습니다. exported service는 호스트 서명 권한을 요구하고 Binder 진입점에서 호출 UID, 설치된 호스트 패키지 및 현재 서명을 다시 확인합니다. Chaquopy Java bridge에는 접근할 수 있으므로 별도 Android UID, 전용 프로세스 및 좁은 Binder 경계에 의존하며 CPython을 보안 sandbox로 간주하지 않습니다.

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

- workspace archive, stdin snapshot, online pip 및 wheel 다운로드를 지원하지 않습니다.
- UI 스크립트, debugger, REPL 또는 호스트 Java 객체 임의 접근이 없습니다.
- AutoJs6 capability broker 및 호스트 API 연결은 아직 없습니다.
- 32비트 Android와 임의의 native wheel은 보장하지 않습니다.
- 로컬 CPython 테스트는 Chaquopy, Android, Binder 또는 기기 승인 증거가 아닙니다.

******

### 로드맵

******

독립 R2 저장소, 정적 경계, provider/bootstrap 소스 및 로컬 의미 테스트가 준비되었습니다. QV710AF65F의 보호 soak 동안 Gradle과 ADB를 연기합니다. release AAR, 의존성 해석, Android 컴파일, APK/16 KB, Binder/PFD 및 기기 매트릭스는 미완료입니다.

- [ROADMAP.md 보기](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### 변경 이력

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

로컬 CPython을 사용한 이식 가능한 bootstrap 의미 테스트:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

이 검사는 Android 동작을 증명하지 않습니다. Gradle, APK, Binder 및 기기 검증은 보호 soak 이후 수행해야 합니다.

******

### 빌드

******

현재 빌드하지 않습니다. AAR 또는 SHA-256이 고정되지 않으면 release 설정은 fail closed됩니다.

빌드 전에 다음 release AAR을 `libs`에 배치하고 고정해야 합니다:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

Maven의 Chaquopy 17.0.0과 stdlib만 사용할 예정입니다. 의존성 검증, native 라이브러리, 라이선스 및 16 KB page 호환성은 미검증입니다.

******

### 라이선스

******

프로젝트 소스는 MPL-2.0입니다. Chaquopy, CPython 및 기타 구성 요소는 각 라이선스를 따릅니다.

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
