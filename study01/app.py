import time
import streamlit as st
import pandas as pd
import random

# ---------------------------------------------------------
# 실험 데이터 누적 + 표 + 그래프 시각화 (Streamlit 내장만 사용)
# ---------------------------------------------------------

st.title("실험 데이터 누적 + 시각화 (Streamlit 기본 차트)")

# 1. 세션 상태 초기화
if "logs" not in st.session_state:
    st.session_state.logs = []

# 2. 실험 입력 UI
col1, col2, col3 = st.columns(3)

with col1:
    model = st.selectbox("모델 선택", ["gpt-4.1-mini", "gpt-4.1"])
with col2:
    prompt = st.text_input("프롬프트", value="안녕하세요")
with col3:
    temperature = st.slider("temperature", 0.0, 1.0, 0.2, 0.1)

# 3. 실험 실행
if st.button("실험 1회 실행"):
    start = time.time()
    time.sleep(random.uniform(0.05, 0.25))
    latency = round((time.time() - start) * 1000, 1)

    st.session_state.logs.append({
        "모델": model,
        "프롬프트길이": len(prompt),
        "temperature": temperature,
        "토큰추정치": len(prompt) * 2,
        "지연시간(ms)": latency,
    })

if st.button("로그 초기화"):
    st.session_state.logs = []

# 4. 표 출력
df = pd.DataFrame(st.session_state.logs)
st.subheader("누적 실험 로그")
st.dataframe(df, use_container_width=True)

# 5. 그래프 시각화 (Streamlit 기본)
if not df.empty:
    df_plot = df.copy()
    df_plot["실행순서"] = range(1, len(df_plot) + 1)

    st.subheader("실행 순서별 지연시간 변화")
    st.line_chart(df_plot.set_index("실행순서")[["지연시간(ms)"]])

    st.subheader("모델별 평균 지연시간")
    st.bar_chart(
        df_plot.groupby("모델")[["지연시간(ms)"]].mean()
    )
