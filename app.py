import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from anthropic import Anthropic

# 페이지 설정
st.set_page_config(page_title="스타트업 내비게이터", page_icon="🚀", layout="wide")

# 탭 생성
tab1, tab2 = st.tabs(["사업 성과 시뮬레이터", "창업 아이템 분석기"])

# 사업 성과 시뮬레이터 함수
def run_simulation(years=5):
    revenue = [initial_investment * 0.5]  # 첫 해 매출 가정
    profit = [0]
    cash_flow = [-initial_investment]
    market_share = [0.01]  # 초기 시장 점유율 1% 가정

    for _ in range(1, years):
        # 시장 상황에 따른 매출 성장
        market_factor = 1 + (market_growth / 100)
        competition_factor = {"낮음": 1.1, "중간": 1.0, "높음": 0.9}[competition_level]
        
        # 성장 전략에 따른 영향
        strategy_factor = {"공격적": 1.2, "중립적": 1.0, "보수적": 0.8}[growth_strategy]
        
        # 인력 생산성 영향
        productivity_factor = 0.5 + (employee_productivity / 10)

        new_revenue = revenue[-1] * market_factor * competition_factor * strategy_factor * productivity_factor
        new_profit = new_revenue * (1 - operating_expenses / 100)
        new_cash_flow = new_profit - (employee_count * 3000)  # 직원당 평균 연봉 3000만원 가정

        revenue.append(new_revenue)
        profit.append(new_profit)
        cash_flow.append(new_cash_flow)
        market_share.append(min(market_share[-1] * 1.2, 1))  # 시장 점유율 성장, 최대 100%

    return revenue, profit, cash_flow, market_share

# 창업 아이템 분석기 함수
def get_startup_analysis(api_key, idea):
    client = Anthropic(api_key=api_key)
    
    prompt = f"""As an AI startup analyst, provide a comprehensive analysis for the startup idea: "{idea}". Structure your response in the following format:

    ## 1. 시장 동향 분석

    - 현재 국내 및 글로벌 시장 규모 (금액):
    - 주요 소비자 트렌드:
    - 시장을 주도하는 핵심 기술이나 혁신 요소:

    ## 2. 경쟁 상황 평가
    - 국내외 주요 경쟁사와 각 기업의 강점 및 약점:
    - 시장 점유율 상위 3개 기업의 점유율:
    - 주요 진입 장벽:
    - 대체 상품/서비스의 위협 정도:

    ## 3. 성장 전망 예측
    - 향후 3년, 5년간의 예상 시장 성장률:
    - 낙관적, 중립적, 비관적 시나리오별 성장 전망:
    - 시장 성장에 영향을 미칠 수 있는 주요 외부 요인:

    ## 4. 성공 사례 분석
    - 성공한 국내외 기업 사례:
    - 각 성공 사례의 주요 성공 요인:
    - 초기 진입 전략과 성장 과정에서의 주요 전환점:
    - 경쟁사와의 차별화 포인트:

    ## 5. 실패 사례 분석
    - 실패한 국내외 기업 사례:
    - 각 실패 사례의 주요 실패 원인:
    - 실패를 극복하기 위한 구체적인 방안:
    - 각 실패 사례에서 얻을 수 있는 핵심 교훈:

    ## 6. 핵심 성공 요인 도출
    - 핵심 성공 요인 (1-10 척도의 중요도 포함):
    - 제시된 창업 아이템의 각 성공 요인에 대한 적합성 평가 및 개선 방안:
    - 아이템의 장기적 성공을 위한 전략적 제언:

    Provide detailed and data-driven insights for each section. Use realistic but imaginary data where specific numbers are required. Ensure the analysis is comprehensive and tailored to the specific startup idea."""

    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        temperature=0.7,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

# 사업 성과 시뮬레이터 탭
with tab1:
    st.title("사업 성과 시뮬레이터")

    # 사이드바 입력
    st.sidebar.header("시뮬레이션 파라미터")

    # 시장 상황
    market_growth = st.sidebar.slider("시장 성장률 (%)", -10.0, 20.0, 5.0)
    competition_level = st.sidebar.selectbox("경쟁 수준", ["낮음", "중간", "높음"])

    # 인력 구성
    employee_count = st.sidebar.number_input("직원 수", 1, 1000, 50)
    employee_productivity = st.sidebar.slider("직원 생산성 (1-10)", 1, 10, 5)

    # 재무 요소
    initial_investment = st.sidebar.number_input("초기 투자금 (만원)", 1000, 1000000, 100000)
    operating_expenses = st.sidebar.slider("운영 비용 비율 (%)", 10.0, 90.0, 60.0)

    # 성장 전략
    growth_strategy = st.sidebar.selectbox("성장 전략", ["공격적", "중립적", "보수적"])

    # 시뮬레이션 실행
    if st.sidebar.button("시뮬레이션 실행"):
        revenue, profit, cash_flow, market_share = run_simulation()

        # 결과 데이터프레임
        df = pd.DataFrame({
            "연도": range(1, 6),
            "매출 (만원)": revenue,
            "순이익 (만원)": profit,
            "현금흐름 (만원)": cash_flow,
            "시장 점유율 (%)": [x * 100 for x in market_share]
        })

        # 결과 표시
        st.subheader("사업 성과 시뮬레이션 결과")

        # 재무 지표 차트
        fig_finance = go.Figure()
        fig_finance.add_trace(go.Scatter(x=df['연도'], y=df['매출 (만원)'], mode='lines+markers', name='매출'))
        fig_finance.add_trace(go.Scatter(x=df['연도'], y=df['순이익 (만원)'], mode='lines+markers', name='순이익'))
        fig_finance.add_trace(go.Scatter(x=df['연도'], y=df['현금흐름 (만원)'], mode='lines+markers', name='현금흐름'))
        fig_finance.update_layout(title='재무 지표 추이', xaxis_title='연도', yaxis_title='금액 (만원)')
        st.plotly_chart(fig_finance)

        # 시장 점유율 차트
        fig_market = px.line(df, x='연도', y='시장 점유율 (%)', title='시장 점유율 추이')
        st.plotly_chart(fig_market)

        # 주요 성과 지표
        st.subheader("주요 성과 지표")
        col1, col2, col3 = st.columns(3)
        col1.metric("5년 후 예상 매출", f"{revenue[-1]:,.0f} 만원")
        col2.metric("5년 후 예상 순이익", f"{profit[-1]:,.0f} 만원")
        col3.metric("5년 후 예상 시장 점유율", f"{market_share[-1]*100:.1f}%")

        # 상세 결과 테이블
        st.subheader("연도별 상세 결과")
        st.dataframe(df.style.format({
            "매출 (만원)": "{:,.0f}",
            "순이익 (만원)": "{:,.0f}",
            "현금흐름 (만원)": "{:,.0f}",
            "시장 점유율 (%)": "{:.2f}"
        }))

        # 리스크 분석
        st.subheader("리스크 분석")
        risks = [
            ("시장 성장률 저하", market_growth < 0),
            ("높은 경쟁 수준", competition_level == "높음"),
            ("낮은 직원 생산성", employee_productivity < 5),
            ("높은 운영 비용", operating_expenses > 70),
            ("보수적 성장 전략", growth_strategy == "보수적")
        ]
        
        for risk, condition in risks:
            if condition:
                st.warning(f"리스크 요인: {risk}")
                if risk == "시장 성장률 저하":
                    st.info("대응 전략: 새로운 시장 진출 또는 제품 다각화를 고려하세요.")
                elif risk == "높은 경쟁 수준":
                    st.info("대응 전략: 차별화된 가치 제안과 마케팅 전략을 개발하세요.")
                elif risk == "낮은 직원 생산성":
                    st.info("대응 전략: 직원 교육 및 훈련 프로그램을 강화하세요.")
                elif risk == "높은 운영 비용":
                    st.info("대응 전략: 비용 절감 방안을 검토하고 효율성을 개선하세요.")
                elif risk == "보수적 성장 전략":
                    st.info("대응 전략: 시장 기회를 재평가하고 적절한 위험 감수를 고려하세요.")

# 창업 아이템 분석기 탭
with tab2:
    st.title('🚀 창업 아이템 분석기')

    api_key = st.text_input("Anthropic API 키를 입력하세요", type="password")
    idea = st.text_area("창업 아이디어를 입력하세요", height=100)

    if st.button('분석 시작', key='analyze'):
        if not api_key:
            st.error('API 키를 입력해주세요.')
        elif not idea:
            st.error('창업 아이디어를 입력해주세요.')
        else:
            with st.spinner('아이디어를 분석 중입니다...'):
                try:
                    analysis = get_startup_analysis(api_key, idea)
                    st.markdown(analysis)
                except Exception as e:
                    st.error(f'오류가 발생했습니다: {str(e)}')

    st.markdown("""
    ### 사용 방법
    1. Anthropic API 키를 입력하세요.
    2. 분석하고 싶은 창업 아이디어를 입력하세요.
    3. '분석 시작' 버튼을 클릭하세요.
    4. 결과를 기다리세요. 분석에는 약간의 시간이 소요될 수 있습니다.
    """)

# 사이드바 정보
st.sidebar.markdown("---")
st.sidebar.header("About")
st.sidebar.info(
    "고용노동부 공공데이터 활용공모전, 스타트업 내비게이터에 오신 것을 환영합니다.\n\n"
    "이 앱은 창업 아이디어를 분석하고 사업 성과를 시뮬레이션하여 \n"
    "1) 시장 동향, 2) 경쟁 상황, 3) 성장 전망, 4) 성공 및 실패 사례, 5) 핵심 성공 요인을 제공합니다.\n\n"
    "생성형 AI와 공공데이터를 활용하여 스타트업 창업자들에게 유용한 인사이트를 제공합니다."
)
st.sidebar.write("© 2024 스타트업 내비게이터")