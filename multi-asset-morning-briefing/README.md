# Multi-Asset Morning Briefing

> 글로벌 주식·금리·외환·원자재·변동성을 하나의 흐름으로 연결하고, 한국시장 전달 경로와 향후 5거래일 일정을 근거 링크와 함께 정리하는 AI 에이전트 스킬

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-stdlib%20only-2ea44f)](scripts/market_data.py)
[![Data](https://img.shields.io/badge/data-official%20sources-0A66C2)](#공식-데이터-원천)
[![Tests](https://img.shields.io/badge/offline%20tests-30%20passing-2ea44f)](tests/test_market_data.py)
[![Upstream PR](https://img.shields.io/badge/upstream-PR%20%23675-8957e5?logo=github)](https://github.com/NomaDamas/k-skill/pull/675)

## 왜 만들었나

모닝 브리핑은 숫자를 많이 모으는 것보다 **같은 세션의 숫자를 정확히 연결하는 일**이 어렵습니다.

- 서울 아침 기준 미국 오버나잇과 한국 전일의 거래일이 다를 수 있음
- 휴장·주말·발표 지연 때문에 달력상 `D-1`과 실제 최근 완료 세션이 어긋남
- 현물 종가, 선물 정산가, 장중 값이 섞이면 방향과 등락률이 충돌함
- 뉴스 제목의 단순 키워드 분류는 `공원화 → 원화` 같은 오탐을 만듦
- 한 데이터 원천의 장애가 전체 브리핑 실패로 번질 수 있음

이 스킬은 미국과 한국의 세션을 **독립 판별**하고, 공식 원천의 관측일·단위·가격 기준을 보존하며, 실패한 원천만 격리합니다.

## 결과물

파일을 만들지 않고 대화에 다음 7개 섹션을 출력합니다.

```text
YYYY.MM.DD Morning Market Briefing

1. Summary
2. Rates
3. FX
4. Commodity
5. Equity, Vol
6. 한국 증시
7. 주요 일정
```

각 bullet은 핵심 수치 또는 주장을 먼저 제시하고, 의미와 한국시장 전달 경로를 한 문장 안에서 연결하며, 직접 근거가 되는 Markdown 링크로 끝납니다.

## 처리 흐름

```mermaid
flowchart LR
    A[서울 기준 브리핑일] --> B1[Cboe VIX 관측일]
    A --> B2[한국은행 ECOS 관측일]
    B1 --> C1[미국 최근 완료 세션]
    B2 --> C2[한국 최근 완료 세션]
    C1 --> D[공식 기초 데이터]
    C2 --> D
    D --> E[원문 뉴스·공식 일정 보강]
    E --> F[세션·단위·cutoff 검증]
    F --> G[7개 섹션 브리핑]
```

## 공식 데이터 원천

| 원천 | 수집 항목 | 검증 기준 |
|---|---|---|
| [U.S. Treasury](https://home.treasury.gov/resource-center/data-chart-center/interest-rates) | 미국 국채 2Y·10Y·30Y, 2s10s | 미국 목표 세션과 동일한 관측일 |
| [Cboe](https://www.cboe.com/tradable_products/vix/) | VIX 종가, 미국 최근 완료 세션 | `pt`, regular close |
| [ECB Data Portal](https://data.ecb.europa.eu/data/datasets/EXR) | EUR/USD·USD/JPY·GBP/USD | reference rate, 통화쌍별 단위 |
| [한국은행 ECOS](https://ecos.bok.or.kr/) | KOSPI·KOSDAQ, 한국 최근 완료 세션 | `pt`, 한국시장 종가 |

로그인·API 키·프록시 없이 공개 read-only endpoint를 직접 호출합니다. FRED 시계열은 발표 지연을 명시하는 보조 fallback으로만 사용하며, 목표 세션과 관측일이 다르면 브리핑에서 제외합니다.

## 빠른 시작

### 1. 스킬 설치·갱신

```bash
npx -y @nomadamas/k-skill@0 update
```

### 2. 에이전트 지침 확인

```bash
npx -y @nomadamas/k-skill@0 instruct multi-asset-morning-briefing
```

### 3. 공식 기초 데이터 수집

```bash
npx -y @nomadamas/k-skill@0 exec multi-asset-morning-briefing scripts/market_data.py -- \
  snapshot --briefing-date 2026-09-17
```

개별 원천을 다시 확인할 수도 있습니다.

```bash
# 미국 국채 금리
npx -y @nomadamas/k-skill@0 exec multi-asset-morning-briefing scripts/market_data.py -- \
  yields --last 5 --session 2026-09-16

# Cboe VIX
npx -y @nomadamas/k-skill@0 exec multi-asset-morning-briefing scripts/market_data.py -- \
  cboe-vix --last 5 --session 2026-09-16

# ECB 주요 통화쌍
npx -y @nomadamas/k-skill@0 exec multi-asset-morning-briefing scripts/market_data.py -- \
  ecb-fx --last 5 --session 2026-09-16
```

## 신뢰성 설계

- **독립 세션 판별** — 미국은 Cboe, 한국은 ECOS의 실제 관측일로 각각 결정
- **Fail-Closed** — 세션·단위·가격 기준을 해결하지 못한 값은 추정하지 않고 제외
- **실패 격리** — 한 원천의 HTTP·파싱 실패를 `failures[]`에 기록하고 나머지 수집 지속
- **응답 크기 제한** — `Content-Length`와 스트리밍 양쪽에서 8 MiB 상한 적용
- **뉴스 cutoff** — 기본 `07:00 KST` 이후 기사를 해당 브리핑 근거에서 제외
- **공식 일정 우선** — 제3자 HTML 자동 파싱 대신 중앙은행·통계기관·기업 IR 일정 사용

## 테스트

```bash
python -m unittest discover -s multi-asset-morning-briefing/tests -p "test_*.py"
ruff format --check multi-asset-morning-briefing/scripts/market_data.py \
  multi-asset-morning-briefing/tests/test_market_data.py
ruff check multi-asset-morning-briefing/scripts/market_data.py \
  multi-asset-morning-briefing/tests/test_market_data.py
```

오프라인 테스트 30건이 다음을 검증합니다.

- 공식 CSV·JSON 파싱과 FRED ZIP 병합
- 미국·한국 휴장일이 다른 경우의 독립 세션
- 2s10s·bp 변화·curve 분류 산술
- 미국 국채·FX·VIX의 자산별 단위
- 비정상 JSON과 원천별 장애의 구조화된 실패
- 선언/스트리밍 응답 크기 제한
- 완성 브리핑의 제목·7개 섹션·링크·리서치 메모형 문체

## 저장소 구조

```text
multi-asset-morning-briefing/
├── skill.json                 # frontmatter·profile 원본
├── instruction.md             # 에이전트 workflow 원본
├── SKILL.md                   # 자동 생성 CLI adapter
├── scripts/market_data.py     # stdlib 공식 데이터 helper
├── references/format-rules.md # 산술·단위·문체 검수 규칙
└── tests/                     # 오프라인 회귀·E2E 계약 테스트
```

`SKILL.md`는 직접 편집하지 않으며 `skill.json`과 `instruction.md`에서 생성합니다.

## 기여 현황

- 제안 이슈: [NomaDamas/k-skill #674](https://github.com/NomaDamas/k-skill/issues/674)
- 업스트림 PR: [NomaDamas/k-skill #675](https://github.com/NomaDamas/k-skill/pull/675)
- 라이선스: [MIT](https://github.com/NomaDamas/k-skill/blob/dev/LICENSE)
