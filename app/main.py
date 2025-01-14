import os
import json
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.agents import AgentType

# 환경변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("환경변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")


def search_restaurants(query):
    """
    맛집 추천 도구: 문자열 입력을 파싱하여 처리
    """
    # 예시 맛집 데이터
    restaurants = [
        {
            "name": "해운대 고기집",
            "type": "한식",
            "price": "중가",
            "region": "부산 해운대",
            "suitable_for": "가족",
            "capacity": "4-10인",
            "signature": "생고기, 된장찌개",
            "description": "단체석 있음, 가족 모임에 적합",
        },
        {
            "name": "광안리 초밥집",
            "type": "일식",
            "price": "고가",
            "region": "부산 광안리",
            "suitable_for": "친구",
            "capacity": "2-6인",
            "signature": "모듬초밥, 연어초밥",
            "description": "오션뷰, 데이트 코스",
        },
        {
            "name": "해운대 디저트 카페",
            "type": "디저트",
            "price": "저가",
            "region": "부산 해운대",
            "suitable_for": "커플",
            "capacity": "2-4인",
            "signature": "티라미수, 망고빙수",
            "description": "아늑한 분위기, 커플석 있음",
        },
    ]

    # 입력 문자열에서 정보 추출
    location = "부산 해운대"  # 기본값
    people_count = 4  # 기본값

    # 위치 정보 추출
    if "부산" in query:
        if "해운대" in query:
            location = "부산 해운대"
        elif "광안리" in query:
            location = "부산 광안리"

    # 인원 수 추출
    if "명" in query:
        for word in query.split():
            if word.isdigit():
                people_count = int(word)

    # 지역 및 인원수 기반 필터링
    filtered = [r for r in restaurants if location in r["region"]]
    if not filtered:
        return "추천 가능한 맛집이 없습니다."

    # 추천 결과 생성
    recommendations = []
    for r in filtered:
        recommendation = (
            f"[{r['name']}]\n"
            f"- 음식 종류: {r['type']}\n"
            f"- 가격대: {r['price']}\n"
            f"- 수용 인원: {r['capacity']}\n"
            f"- 대표메뉴: {r['signature']}\n"
            f"- 특징: {r['description']}"
        )
        recommendations.append(recommendation)

    return "\n\n".join(recommendations)


# LangChain Tool 정의
restaurant_tool = Tool(
    name="맛집검색",
    func=search_restaurants,
    description="지역명과 인원수로 맛집을 검색합니다. 반드시 한국어로 입력하세요. 예시) '부산 해운대 4명'",
)

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
)

# 시스템 메시지 정의
system_message = """당신은 한국어로만 응답하는 맛집 추천 AI assistant입니다.

절대적인 규칙:
1. 모든 생각(Thought)과 답변(Final Answer)은 반드시 한국어로만 작성합니다.
2. 영어 사용은 절대 금지입니다.

맛집 추천시 다음 순서로 진행하세요:
1. '맛집검색' 도구를 사용하여 맛집 정보를 찾습니다.
2. 검색 결과를 바탕으로 다음 형식에 맞춰 답변합니다.

[맛집 추천 결과]
식당명: (이름)
- 음식 종류: (한식/일식/양식 등)
- 가격대: (고가/중가/저가)
- 수용 인원: (인원수)
- 대표메뉴: (메뉴 이름)
- 특징: (식당 특징)

예시 답변:
[맛집 추천 결과]
식당명: 해운대 고기집
- 음식 종류: 한식
- 가격대: 중가
- 수용 인원: 4-10인
- 대표메뉴: 생고기, 된장찌개
- 특징: 단체석 있음, 가족 모임에 적합

이 형식을 반드시 지켜서 답변하세요."""

# 에이전트 초기화
agent = initialize_agent(
    tools=[restaurant_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,  # 파싱 오류 처리 추가
    agent_kwargs={"system_message": system_message},
)

# 사용자 입력 처리
user_input = {"location": "부산 해운대", "num_people": "4명", "days": "2박 3일"}

# 에이전트 실행
response = agent.invoke(
    {
        "input": f"{user_input['location']} 지역에 {user_input['num_people']}이서 {user_input['days']} 동안 식사할 맛집을 추천해주세요."
    }
)

# 결과 출력
print("\n추천된 맛집:")
print(response)
