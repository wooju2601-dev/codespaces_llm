import os
from pathlib import Path
from datetime import datetime
from typing import List

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


# ---------------------------------------------------------
# 1. Streamlit 화면 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI 보고서 생성기",
    layout="wide"
)


# ---------------------------------------------------------
# 2. 경로 설정
# ---------------------------------------------------------
# app.py 파일이 있는 폴더를 기준으로 output 폴더를 생성합니다.
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


# ---------------------------------------------------------
# 3. 환경변수 로드 및 OpenAI 클라이언트 생성
# ---------------------------------------------------------
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    st.stop()

client = OpenAI(api_key=api_key)


# ---------------------------------------------------------
# 4. 보고서 데이터 구조 정의
# ---------------------------------------------------------
class VulnerabilityReport(BaseModel):
    title: str
    severity: str
    vulnerability_type: str
    target: str
    description: str
    affected_parameter: str
    proof_of_concept: str
    impact: str
    remediation: List[str]


# ---------------------------------------------------------
# 5. LLM 호출 함수
# ---------------------------------------------------------
def request_to_llm(raw_data: str) -> VulnerabilityReport:
    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": """
당신은 보안 점검 보고서 작성 전문가입니다.
사용자가 제공한 원시 정보를 분석하여 정형화된 취약점 보고서를 작성하세요.

작성 규칙:
1. severity는 반드시 Critical, High, Medium, Low, Informational 중 하나만 사용합니다.
2. 전문 용어를 제외한 모든 내용은 한국어로 작성합니다.
3. 조치 방안은 수강생이 이해할 수 있도록 구체적으로 작성합니다.
4. 확인되지 않은 내용은 단정하지 말고 가능성으로 표현합니다.
"""
            },
            {
                "role": "user",
                "content": raw_data
            }
        ],
        text_format=VulnerabilityReport,
    )

    return response.output_parsed


# ---------------------------------------------------------
# 6. Markdown 변환 함수
# ---------------------------------------------------------
def report_to_markdown(report: VulnerabilityReport) -> str:
    markdown = f"""# 취약점 보고서

## 1. 기본 정보

| 항목 | 내용 |
|---|---|
| 취약점명 | {report.title} |
| 위험도 | {report.severity} |
| 취약점 유형 | {report.vulnerability_type} |
| 대상 시스템 | {report.target} |

---

## 2. 취약점 설명

{report.description}

---

## 3. 영향받는 파라미터

`{report.affected_parameter}`

---

## 4. 재현 예시

```text
{report.proof_of_concept}
```

---

## 5. 예상 영향

{report.impact}

---

## 6. 조치 방안

"""

    for item in report.remediation:
        markdown += f"- {item}\n"

    return markdown


# ---------------------------------------------------------
# 7. 파일 저장 함수
# ---------------------------------------------------------
def save_markdown(markdown: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"vulnerability_report_{report_date}.md"

    filename.write_text(markdown, encoding="utf-8")

    return str(filename)


# ---------------------------------------------------------
# 8. Streamlit 화면 구성
# ---------------------------------------------------------
st.title("AI를 활용한 보고서 작성 웹앱")
st.write("원시 점검 내용을 입력하면 AI가 구조화된 보고서로 정리합니다.")
st.divider()

with st.sidebar:
    st.header("실습 안내")
    st.write("1. 원시 점검 내용을 입력합니다.")
    st.write("2. 보고서 생성 버튼을 누릅니다.")
    st.write("3. AI가 구조화된 보고서를 생성합니다.")
    st.write("4. Markdown 파일로 저장됩니다.")

    st.divider()
    st.write("API Key 상태")
    st.success("API Key 로드 완료")

    st.divider()
    st.write("저장 위치")
    st.code(str(OUTPUT_DIR))


# ---------------------------------------------------------
# 9. 테스트용 입력 데이터
# ---------------------------------------------------------
sample_text = """대상: 사내 게시판 시스템

발견 내용:
- 게시글 검색 기능에서 SQL Injection 의심
- 파라미터: keyword
- payload: ' OR '1'='1
- 검색 결과에 비정상적으로 많은 데이터 노출
- 로그인하지 않은 사용자도 접근 가능
"""


# ---------------------------------------------------------
# 10. 사용자 입력 영역
# ---------------------------------------------------------
raw_data = st.text_area(
    "보고서로 변환할 원시 점검 내용을 입력하세요.",
    value=sample_text,
    height=260
)


# ---------------------------------------------------------
# 11. AI 보고서 생성
# ---------------------------------------------------------
if st.button("AI 보고서 생성", type="primary"):
    if not raw_data.strip():
        st.warning("원시 점검 내용을 입력하세요.")
    else:
        with st.spinner("AI가 보고서를 생성하는 중입니다..."):
            try:
                report = request_to_llm(raw_data)
                markdown = report_to_markdown(report)
                saved_path = save_markdown(markdown)

                st.success("보고서 생성이 완료되었습니다.")
                st.info(f"Markdown 파일 저장 위치: {saved_path}")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("구조화된 보고서 데이터")
                    st.json(report.model_dump())

                with col2:
                    st.subheader("Markdown 보고서 미리보기")
                    st.markdown(markdown)

            except Exception as e:
                st.error("보고서 생성 중 오류가 발생했습니다.")
                st.exception(e)
