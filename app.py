"""Palmer Penguins Explorer — Streamlit Community Cloud-ready dashboard."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Penguin Lab | 펭귄 생태 데이터",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
SPECIES_KO = {"Adelie": "아델리", "Chinstrap": "턱끈", "Gentoo": "젠투"}
SPECIES_COLORS = {"Adelie": "#26A69A", "Chinstrap": "#F5A623", "Gentoo": "#8B7CF4"}
MEASURES = {
    "몸무게 (g)": "body_mass_g",
    "날개 길이 (mm)": "flipper_length_mm",
    "부리 길이 (mm)": "bill_length_mm",
    "부리 깊이 (mm)": "bill_depth_mm",
}
LABELS = {
    "species": "종", "island": "관측 섬", "sex": "성별", "year": "관측 연도",
    "bill_length_mm": "부리 길이 (mm)", "bill_depth_mm": "부리 깊이 (mm)",
    "flipper_length_mm": "날개 길이 (mm)", "body_mass_g": "몸무게 (g)",
    "count": "관측 개체 수", "value": "평균값",
}

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1450px;}
.hero {background: linear-gradient(110deg,#0c2847,#16475f 58%,#126d6b); color:#fff;
       border-radius:22px;padding:27px 32px;margin-bottom:20px;}
.hero .eyebrow {font-size:.77rem;letter-spacing:.18em;color:#9ee6d6;font-weight:700;}
.hero h1 {font-size:2.25rem;margin:.3rem 0 .5rem;color:white;line-height:1.3;}
.hero p {font-size:.96rem;color:#d7edf2;margin:0;}
.note {background:rgba(120,150,160,.1);border-left:3px solid #22a699;padding:11px 14px;
       border-radius:5px;margin:12px 0;font-size:.91rem;}
.smallmuted {color:#71808e;font-size:.84rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data

def load_data() -> pd.DataFrame:
    """Read the bundled CSV (works identically locally and on Streamlit Cloud)."""
    df = pd.read_csv(BASE_DIR / "penguins.csv")
    numeric = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "year"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["sex"] = df["sex"].fillna("미상").replace({"male": "수컷", "female": "암컷"})
    df["species_ko"] = df["species"].map(SPECIES_KO).fillna(df["species"])
    return df

try:
    data = load_data()
except (FileNotFoundError, pd.errors.ParserError) as exc:
    st.error("penguins.csv 파일을 읽을 수 없습니다. app.py와 같은 폴더에 CSV가 있는지 확인하세요.")
    st.exception(exc)
    st.stop()

st.markdown("""
<div class="hero"><div class="eyebrow">DATA EXPLORATION · ANTARCTICA</div>
<h1>🐧 Penguin Lab</h1>
<p>남극 펭귄의 생태를 데이터로 탐험해 보세요. 종별 신체 특징과 서식지 차이를 비교합니다.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("🔎 데이터 탐색 조건")
st.sidebar.caption("선택을 바꾸면 모든 지표와 그래프가 함께 업데이트됩니다.")
all_species = sorted(data["species"].dropna().unique().tolist())
all_islands = sorted(data["island"].dropna().unique().tolist())
all_sexes = ["암컷", "수컷", "미상"]
selected_species = st.sidebar.multiselect(
    "펭귄 종", all_species, default=all_species,
    format_func=lambda s: f"{SPECIES_KO.get(s, s)} ({s})"
)
selected_islands = st.sidebar.multiselect("관측 섬", all_islands, default=all_islands)
selected_sexes = st.sidebar.multiselect("성별", all_sexes, default=all_sexes)
min_year, max_year = int(data["year"].min()), int(data["year"].max())
selected_years = st.sidebar.slider(
    "관측 연도", min_value=min_year, max_value=max_year,
    value=(min_year, max_year), step=1,
)
st.sidebar.divider()
st.sidebar.caption("📚 Palmer Penguins · Gorman et al. · 2007–2009 관측자료")
st.sidebar.caption("기본 제공 자료는 실시간 관측이 아닌 교육·연구용 데이터입니다.")

view = data.loc[
    data["species"].isin(selected_species)
    & data["island"].isin(selected_islands)
    & data["sex"].isin(selected_sexes)
    & data["year"].between(*selected_years)
].copy()

if view.empty:
    st.warning("선택한 조건에 맞는 관측 기록이 없습니다. 왼쪽 필터를 넓혀 주세요.")
    if st.button("필터 초기화 안내"):
        st.info("사이드바에서 종·섬·성별을 모두 선택하고 연도를 전체로 지정하세요.")
    st.stop()

valid_mass = view["body_mass_g"].dropna()
valid_flipper = view["flipper_length_mm"].dropna()

k1, k2, k3, k4 = st.columns(4)
k1.metric("관측 개체 수", f"{len(view):,}마리")
k2.metric("관측된 종", f"{view['species'].nunique()}종")
k3.metric("평균 몸무게", f"{valid_mass.mean():,.0f} g" if len(valid_mass) else "측정값 없음")
k4.metric("평균 날개 길이", f"{valid_flipper.mean():.1f} mm" if len(valid_flipper) else "측정값 없음")

st.caption(f"전체 {len(data):,}건 중 {len(view):,}건 표시 · 측정값 결측치는 해당 분석에서 제외")

overview, body, compare, records = st.tabs([
    "📊 한눈에 보기", "📐 신체 특징 분석", "⚖️ 종별 비교", "📁 원본 데이터"
])

with overview:
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("종별 관측 개체 수")
        counts = view.groupby("species", as_index=False).size().rename(columns={"size": "count"})
        fig = px.bar(
            counts, x="species", y="count", color="species", text="count",
            color_discrete_map=SPECIES_COLORS, labels=LABELS,
            category_orders={"species": all_species},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, margin=dict(t=20, b=10, l=0, r=0), height=370)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("섬별 종 구성")
        island_counts = view.groupby(["island", "species"], as_index=False).size().rename(columns={"size": "count"})
        fig = px.bar(
            island_counts, x="island", y="count", color="species", barmode="stack",
            color_discrete_map=SPECIES_COLORS, labels=LABELS,
            category_orders={"species": all_species},
        )
        fig.update_layout(legend_title_text="펭귄 종", margin=dict(t=20, b=10, l=0, r=0), height=370)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("연도별 관측 기록")
    year_counts = view.groupby(["year", "species"], as_index=False).size().rename(columns={"size": "count"})
    fig = px.line(
        year_counts, x="year", y="count", color="species", markers=True,
        color_discrete_map=SPECIES_COLORS, labels=LABELS,
        category_orders={"species": all_species},
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(legend_title_text="펭귄 종", height=340, margin=dict(t=20, b=10, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    st.info("관측 개체 수는 조사 표본의 개수입니다. 실제 남극 전체 펭귄 개체 수를 뜻하지 않습니다.")

with body:
    st.subheader("신체 특징 사이의 관계")
    ctrl1, ctrl2 = st.columns(2)
    with ctrl1:
        x_name = st.selectbox("가로축", list(MEASURES.keys()), index=1)
    with ctrl2:
        y_name = st.selectbox("세로축", list(MEASURES.keys()), index=0)
    x_col, y_col = MEASURES[x_name], MEASURES[y_name]
    plot_df = view.dropna(subset=[x_col, y_col]).copy()
    if not plot_df.empty:
        fig = px.scatter(
            plot_df, x=x_col, y=y_col, color="species", symbol="sex",
            hover_data=["island", "year"], opacity=0.78,
            color_discrete_map=SPECIES_COLORS, labels=LABELS,
            category_orders={"species": all_species},
        )
        fig.update_traces(marker=dict(size=10, line=dict(width=0.5, color="white")))
        fig.update_layout(height=490, margin=dict(t=20, b=10, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        if x_col != y_col and plot_df[x_col].nunique() > 1 and plot_df[y_col].nunique() > 1:
            corr = plot_df[[x_col, y_col]].corr().iloc[0, 1]
            st.caption(f"선택된 전체 표본의 피어슨 상관계수: {corr:+.3f} · 상관관계는 인과관계를 의미하지 않습니다.")
    else:
        st.info("선택한 신체 측정값을 모두 가진 관측 기록이 없습니다.")

    st.subheader("측정값의 분포")
    metric_name = st.selectbox("분포를 볼 지표", list(MEASURES.keys()), index=0)
    metric_col = MEASURES[metric_name]
    hist_df = view.dropna(subset=[metric_col])
    if not hist_df.empty:
        fig = px.histogram(
            hist_df, x=metric_col, color="species", barmode="overlay", nbins=22,
            opacity=0.68, color_discrete_map=SPECIES_COLORS, labels=LABELS,
            category_orders={"species": all_species},
        )
        fig.update_layout(height=365, margin=dict(t=15, b=10, l=0, r=0), yaxis_title="관측 빈도")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("선택한 측정 지표에 유효한 값이 없습니다.")

with compare:
    st.subheader("종별 평균 신체 특징")
    selected_measure_name = st.selectbox("비교할 지표", list(MEASURES.keys()), index=0, key="compare_metric")
    selected_col = MEASURES[selected_measure_name]
    average = view.groupby("species", as_index=False)[selected_col].mean().dropna()
    if not average.empty:
        fig = px.bar(
            average, x="species", y=selected_col, color="species", text_auto=".1f",
            color_discrete_map=SPECIES_COLORS, labels=LABELS,
            category_orders={"species": all_species},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, height=370, margin=dict(t=20, b=10, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("평균을 계산할 유효 측정값이 없습니다.")

    st.subheader("종별 신체 측정값 요약")
    summary = view.groupby("species").agg(
        관측수=("species", "size"),
        평균몸무게_g=("body_mass_g", "mean"),
        평균날개길이_mm=("flipper_length_mm", "mean"),
        평균부리길이_mm=("bill_length_mm", "mean"),
        평균부리깊이_mm=("bill_depth_mm", "mean"),
    ).round(1)
    st.dataframe(summary, use_container_width=True)
    st.markdown('<div class="note">💡 평균은 해당 측정값이 기록된 개체만으로 계산합니다. 표본 수가 적거나 편중된 그룹의 평균 비교는 주의가 필요합니다.</div>', unsafe_allow_html=True)

with records:
    st.subheader("필터링된 원본 관측 기록")
    show_missing = st.checkbox("결측치가 있는 행만 표시", value=False)
    table_df = view.copy()
    if show_missing:
        raw_measurements = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
        table_df = table_df.loc[table_df[raw_measurements].isna().any(axis=1) | (table_df["sex"] == "미상")]
    shown_columns = ["species", "island", "year", "sex", "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    st.dataframe(table_df[shown_columns].rename(columns=LABELS), use_container_width=True, hide_index=True)
    st.caption(f"현재 표에 표시된 행: {len(table_df):,}건")
    st.download_button(
        label="⬇️ 현재 표 CSV 다운로드",
        data=table_df[shown_columns].to_csv(index=False).encode("utf-8-sig"),
        file_name="penguins_filtered.csv", mime="text/csv", use_container_width=True,
    )
    with st.expander("데이터 사전 및 출처"):
        st.markdown("""
        - **species:** 펭귄 종 (Adelie, Chinstrap, Gentoo)
        - **island:** 관측 섬 (Biscoe, Dream, Torgersen)
        - **year:** 조사 연도 (2007~2009)
        - **sex:** 성별 (원본 결측값은 '미상'으로 표시)
        - **bill_length_mm / bill_depth_mm:** 부리 길이 / 깊이 (mm)
        - **flipper_length_mm:** 날개 길이 (mm)
        - **body_mass_g:** 몸무게 (g)

        **출처:** [palmerpenguins 공개 프로젝트](https://allisonhorst.github.io/palmerpenguins/)  
        **원본 데이터:** [GitHub penguins.csv](https://github.com/allisonhorst/palmerpenguins/blob/main/inst/extdata/penguins.csv)  
        데이터 수집: Dr. Kristen Gorman 및 Palmer Station LTER.  
        라이선스: CC0 1.0.
        """)

st.divider()
st.caption("🐧 Penguin Lab · Built with Streamlit, Pandas & Plotly · Palmer Penguins open dataset")
