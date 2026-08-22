******

### 변경 이력

******

# v0.2.0-alpha.1

###### 2026/08/13

* `안내` 0.1 이후 U1 current-tree alpha candidate. U1-R2 module entry, live output, foreground 내장 input, 명시적 structured JSON 및 제한 output artifact는 E2까지만 완료되었습니다. background 실행과 직접 sys.stdin은 비대화형으로 유지되고 R2 E3는 아직 열려 있으며 current-tree 결과는 device matrix/release/public 증거가 아닙니다
* `추가` 최대 1 MiB의 유한한 사전 제공 stdin snapshot을 추가하여 `input()`과 `sys.stdin`에 결정적 입력과 EOF 제공
* `추가` workspace module, 중첩 entry의 sibling/root module 및 package-relative import를 지원하도록 project import semantics 완성
* `추가` 프로토콜 1.2의 명시적 `entryMode=file|module`을 추가하고 module 실행은 `runpy`로 올바른 `__package__`, `__spec__`, project root의 `sys.path[0]` 및 relative import를 사용하며 file mode는 변경하지 않음
* `추가` 프로토콜 1.3에서 유한 snapshot EOF 뒤 내장 `input()`에 foreground 전용 제한 prompt/reply를 추가하고, background 실행은 입력 UI를 열지 않으며 직접 `sys.stdin`은 유한하게 유지
* `추가` 프로토콜 1.4에서 명시적 엄격 JSON 결과와 선택적 output artifact를 추가하고 count, normalized path, file/aggregate size, exact PFD reference 및 SHA-256을 제한하며 stdout에서 결과를 추론하지 않음
* `수정` 실행 전에 source를 strict UTF-8로 decode하여 비 UTF-8 encoding cookie가 contract를 우회하지 못하도록 수정
* `개선` 신뢰된 스크립트가 표준 라이브러리 네트워크 클라이언트를 직접 사용하도록 `INTERNET` 권한을 부여하되 online pip와 자동 코드 다운로드는 계속 비활성화
* `개선` Provider 실행 상한을 30분, 제한 출력 상한을 16 MiB / 16384 chunks로 확대
* `개선` 제한된 stdout/stderr chunk와 credit backpressure를 스크립트 실행 중으로 이동해 terminal 전의 순서 있는 부분 출력을 보존하고 이후 출력을 금지
* `개선` 실행마다 독립 `__main__`을 사용하고 stdin/stdout/stderr, argv, cwd, `sys.path`, module 및 importer cache 상태 복원
* `개선` open 후 start되지 않은 session에 5초 lease를 적용하고 만료 시 input, descriptor 및 단일 session slot 해제
* `개선` Host 측 discovery에만 의존하지 않고 Provider Binder 경계에서 최소 Host versionCode 5275 강제

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
