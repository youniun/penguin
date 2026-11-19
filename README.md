# 🐧 Penguin Lab — 남극 펭귄 데이터 대시보드

Streamlit으로 만든 펭귄 생태 데이터 분석 사이트입니다. 실제 **Palmer Penguins** 공개 데이터(`penguins.csv`, 344행)를 사용합니다.

## 기능
- 종, 섬, 성별, 조사 연도에 따른 동적 필터링
- 관측 개체 수, 평균 몸무게, 평균 날개 길이 KPI
- 종별 분포, 섬별 구성, 연도별 관측 수
- 신체 특징 산점도·히스토그램·상관계수
- 종별 평균 비교, 원본 표, 결측치 확인
- 필터링된 CSV 다운로드

## 실행

이 폴더에서 VS Code 터미널을 열고:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포
1. `app.py`, `penguins.csv`, `requirements.txt`를 모두 하나의 GitHub 저장소에 업로드합니다.
2. [share.streamlit.io](https://share.streamlit.io) → **Create app** → GitHub 저장소를 선택합니다.
3. **Main file path**에 `app.py`(저장소 루트에 있는 경우)를 입력하고 **Deploy**를 누릅니다.
4. 이후 GitHub 웹에서 `app.py`를 편집하고 **Commit changes**를 누르면 변경사항이 자동 반영됩니다.

> 파일을 하위 폴더에 둔 경우 Main file path는 `penguin_dashboard/app.py`처럼 실제 상대경로를 입력하세요.

## 데이터 출처
- [palmerpenguins 공식 프로젝트](https://allisonhorst.github.io/palmerpenguins/)
- [원본 CSV](https://github.com/allisonhorst/palmerpenguins/blob/main/inst/extdata/penguins.csv)
- 수집: Dr. Kristen Gorman / Palmer Station LTER, 2007–2009
- CC0 1.0 라이선스. `penguins.csv`는 동일 공개 데이터의 로컬 복사본입니다.

본 앱의 개체 수는 연구에서 관측한 **표본 수**이며 전 세계 야생 개체 수가 아닙니다.
