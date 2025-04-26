# StormSurge - 강력한 DOS 테스트 툴

## 개요

StormSurge는 교육 및 테스트 목적으로 개발된 강력한 DOS(Denial of Service) 테스트 툴입니다. 이 도구는 다양한 공격 벡터를 사용하여 웹 서버 및 네트워크 서비스의 부하 테스트를 수행할 수 있습니다.

> **⚠️ 주의사항**: 이 도구는 교육 및 테스트 목적으로만 사용해야 합니다. 허가받지 않은 시스템에 대한 공격은 불법이며 법적 처벌을 받을 수 있습니다.

## 주요 기능

- **다중 공격 벡터**: HTTP 플러딩, 슬로우로리스, TCP/UDP 플러딩 등 다양한 공격 방식 지원
- **고성능 비동기 처리**: 비동기 및 멀티스레딩 기술을 활용한 고성능 공격 엔진
- **실시간 모니터링**: 컬러 코딩된 터미널 UI로 공격 진행 상황 실시간 모니터링
- **자동 로깅**: 모든 공격 활동 자동 기록
- **회피 기술**: 다양한 사용자 에이전트 및 HTTP 헤더 무작위화

## 설치 방법

### 요구 사항

- Python 3.8 이상
- 필수 패키지: colorama, tqdm, requests, aiohttp

### 설치 단계

1. 저장소 클론 또는 압축 파일 다운로드
2. 필요한 패키지 설치:

```bash
pip3 install colorama tqdm requests aiohttp
```

3. 실행 권한 부여:

```bash
chmod +x stormsurge.py
```

## 사용 방법

### 기본 사용법

```bash
python3 stormsurge.py -s [URL | IP] -t [TIME] -m [MODE]
```

### 매개변수

- `-s, --server`: 대상 URL 또는 IP 주소 (필수)
- `-t, --time`: 공격 지속 시간 (밀리초, 선택 사항)
- `-m, --mode`: 공격 모드 (http, slowloris, tcp, udp, mixed)
- `-p, --port`: 대상 포트 (기본값: 프로토콜에 따라 자동 설정)
- `-th, --threads`: 스레드 수 (기본값: 500)
- `-v, --verbose`: 상세 출력 모드

### 사용 예시

1. HTTP 플러딩 공격 (10초):

```bash
python3 stormsurge.py -s http://example.com -t 10000 -m http
```

2. 슬로우로리스 공격 (무제한 시간):

```bash
python3 stormsurge.py -s example.com -m slowloris
```

3. 다중 공격 벡터 (30초, 1000개 스레드):

```bash
python3 stormsurge.py -s http://example.com -t 30000 -m mixed -th 1000
```

4. 특정 포트에 대한 TCP 플러딩:

```bash
python3 stormsurge.py -s example.com -p 8080 -m tcp -t 5000
```

## 공격 모드 설명

1. **HTTP 플러딩 (http)**: 대상 웹 서버에 대량의 HTTP 요청을 전송하여 서버 리소스를 고갈시킵니다.

2. **슬로우로리스 (slowloris)**: 많은 연결을 열고 유지하여 웹 서버의 연결 풀을 고갈시킵니다.

3. **TCP 플러딩 (tcp)**: 대상 서버에 대량의 TCP 연결을 시도하여 네트워크 리소스를 고갈시킵니다.

4. **UDP 플러딩 (udp)**: 대상 서버에 대량의 UDP 패킷을 전송하여 네트워크 대역폭을 소비합니다.

5. **다중 공격 (mixed)**: 위의 모든 공격 방식을 동시에 사용하여 더 강력한 공격을 수행합니다.

## 로그 파일

모든 공격 활동은 `logs` 디렉토리에 자동으로 기록됩니다. 로그 파일은 다음 형식으로 저장됩니다:

```
stormsurge_YYYYMMDD_HHMMSS.log
```

## 성능 최적화 팁

1. **스레드 수 조정**: 시스템 성능에 따라 `-th` 옵션으로 스레드 수를 조정하세요.
2. **공격 모드 선택**: 대상 서버 유형에 따라 적절한 공격 모드를 선택하세요.
   - 웹 서버: `http` 또는 `slowloris`
   - 일반 서버: `tcp` 또는 `udp`
   - 최대 효과: `mixed`
3. **네트워크 대역폭**: 공격 효과는 로컬 네트워크 대역폭에 따라 제한될 수 있습니다.

## 문제 해결

1. **연결 오류**: 대상 서버가 온라인 상태이고 접근 가능한지 확인하세요.
2. **성능 저하**: 스레드 수를 줄이거나 시스템 리소스를 확인하세요.
3. **의존성 오류**: 필요한 모든 패키지가 설치되어 있는지 확인하세요.

## 프로젝트 구조

```
stormsurge/
├── stormsurge.py (메인 실행 파일)
├── core/
│   ├── async_engine.py (비동기 처리 엔진)
│   ├── thread_manager.py (스레드 관리)
│   └── network.py (네트워크 연결 처리)
├── vectors/
│   ├── http_flood.py (HTTP 플러딩 공격)
│   ├── tcp_flood.py (TCP 플러딩 공격)
│   ├── udp_flood.py (UDP 플러딩 공격)
│   ├── slowloris.py (슬로우로리스 공격)
│   └── mixed_attack.py (다중 공격 벡터)
├── utils/
│   ├── headers.py (헤더 생성 및 관리)
│   ├── useragents.py (사용자 에이전트 관리)
│   └── logger.py (로깅 기능)
└── ui/
    ├── terminal.py (터미널 UI)
    └── progress.py (진행 상황 표시)
```

## 면책 조항

이 도구는 교육 및 테스트 목적으로만 제공됩니다. 개발자는 이 도구의 오용으로 인한 어떠한 법적 책임도 지지 않습니다. 사용자는 모든 관련 법률과 규정을 준수할 책임이 있습니다.
