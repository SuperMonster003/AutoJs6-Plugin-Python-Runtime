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
