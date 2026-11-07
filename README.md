# 강동 베이커리 상권분석

서울시 상권분석서비스 Open API 데이터로 베이커리 1호점 입지를 분석하고, 프랜차이즈 확장을 전제로 한 사업계획을 정리한 프로젝트입니다.

- `bakery_report.html`: 사업계획 보고서 (30초 숏츠 영상 포함, 브라우저로 열기)
- `bakery_shorts.html`: 30초 세로형 소개 영상
- `fetch_bakery.py`, `fetch_growth.py`: 데이터 수집 스크립트 (`.env`에 `SEOUL_API_KEY` 필요)
- `score_areas.py`, `score_franchise.py`: 4축(수요·소비력·공급경쟁) 및 확장성 점수 계산
- `data/`: 수집한 원자료와 점수 결과 CSV

수치는 서울시 추정 카드매출(2025년 4분기) 기반이며, 손익 수치는 모두 추정입니다.
