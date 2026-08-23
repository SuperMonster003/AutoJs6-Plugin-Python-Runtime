******

### 변경 이력

******

# v0.3.0-alpha.6

###### 2026/08/23

* `안내` 첫 M4 current-tree alpha candidate. Project-local pure-Python dependency path가 두 device의 focused acceptance를 통과했으며 이후 M3/M4 batch, publication 및 전체 device matrix는 이 claim의 범위에 포함되지 않습니다
* `추가` 승인된 project root의 project-local pure-Python package와 `.dist-info` metadata를 지원하고 version이 고정된 재현 가능한 `requests` example을 제공하며 runtime installer는 추가하지 않음
* `개선` Workspace 제한을 압축 후 64 MiB, file entry 8192개, 추출 후 128 MiB로 확대하고 dispatch 전에 snapshot의 실제 3차원 요구량을 Provider capability와 대조. Missing import는 online pip 또는 engine fallback 없이 `ModuleNotFoundError`로 유지

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

# v0.3.0-alpha.2

###### 2026/08/23

* `안내` 두 번째 M3 current-tree alpha candidate입니다. 첫 저위험 Host capability 전체를 구현했지만 이후 batch, 공개 배포 및 전체 device matrix는 이 선언에 포함하지 않습니다
* `추가` live `autojs6.device.info()` 배터리/화면/밝기/볼륨 데이터, `autojs6.console.log/warn/error` Host console 레벨 및 `autojs6.notice` 알림 추가
* `개선` device 결과 schema를 엄격히 검증하고 알림 권한 부족을 설정 화면이나 기기 권한 변경 없이 안정된 `PERMISSION_DENIED`로 반환

# v0.3.0-alpha.1

###### 2026/08/23

* `안내` 첫 M3 current-tree alpha candidate입니다. 프로토콜 1.5와 저위험 Host capability subset은 구현했지만 이후 capability, 배포 및 전체 device matrix는 이 선언에 포함하지 않습니다
* `추가` request UUID, plugin UID, 단조 call ID, 1024회 quota, 64 KiB message 및 5초 Host dispatch 상한에 묶인 pure-data JSON 프로토콜 1.5 execution-scoped Host capability broker 추가
* `추가` live Host API `autojs6.toast`, `autojs6.clip.get/set`, `autojs6.app.launch/launch_app/open_url` 추가
* `개선` terminal, cancel, Binder death 및 cleanup 경로에서 broker를 일관되게 폐기하고 unavailable capability와 Host/protocol error를 안정된 Python error로 변환

# v0.2.0-alpha.1

###### 2026/08/13

* `안내` 0.1 이후 U1 current-tree alpha candidate. U1-R2 module entry, live output, foreground 내장 input, 명시적 structured JSON 및 제한 output artifact는 E2까지만 완료되었습니다. background 실행과 직접 sys.stdin은 비대화형으로 유지되고 R2 E3는 아직 열려 있으며 current-tree 결과는 device matrix/release/public 증거가 아닙니다
* `추가` 최대 1 MiB의 유한한 사전 제공 stdin snapshot을 추가하여 `input()`과 `sys.stdin`에 결정적 입력과 EOF 제공
* `추가` workspace module, 중첩 entry의 sibling/root module 및 package-relative import를 지원하도록 project import semantics 완성
* `추가` 프로토콜 1.2의 명시적 `entryMode=file|module`을 추가하고 module 실행은 `runpy`로 올바른 `__package__`, `__spec__`, project root의 `sys.path[0]` 및 relative import를 사용하며 file mode는 변경하지 않음
* `추가` 프로토콜 1.3에서 유한 snapshot EOF 뒤 foreground 전용 제한 prompt/reply를 추가해 내장 `input()`은 표시 입력, `getpass.getpass()`는 숨김 입력을 사용하고, background 실행은 입력 UI를 열지 않으며 직접 `sys.stdin`은 유한하게 유지
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
