import openai
from flask import Flask, render_template, request, jsonify
from config import GPT_API_URL, GPT_API_KEY
import json
import subprocess
import re

app = Flask(__name__)

client = openai.OpenAI(api_key=GPT_API_KEY)


PYTHON_TOPICS = {
    "리스트 컴프리헨션": "리스트 컴프리헨션은 리스트를 간결하게 생성하는 방법입니다.",
    "map": "map() 함수는 반복 가능한 객체의 요소를 지정된 함수로 변환합니다.",
    "dict 활용": "딕셔너리는 키-값 쌍을 저장하는 자료구조입니다.",
    "lambda": "lambda 함수는 짧고 간단한 익명 함수를 만들 때 사용합니다.",
    # 총 30개 개념 추가 가능
}


def generate_question(topic=None):
    """ChatGPT API를 이용해 Python 문제를 생성"""
    if topic:
        prompt = f"""{topic} 개념을 테스트할 수 있는 Python 문제를 만들어주세요.

        * 문제 만들 때 주의사항
        1. 반드시 한국어로 작성해주세요.
        2. JSON 형식으로 반환해주세요.
        3. 존댓말을 사용하세요.
        4. 문장이 매끄럽게 이어지도록 하세요.

        
        * 문제 형식
        {{
            "문제명": "문제의 제목",
            "난이도": "난이도 (예: 쉬움, 중, 어려움)",
            "문제": "문제 내용",
            "입력설명": "입력에 대한 설명",
            "출력설명": "출력에 대한 설명",
            "예제입력": ["입력 예시"],
            "예제출력": ["출력 예시"],
            "힌트": "힌트"
        }}
        """
    else:
        prompt = """Python 기초 코딩 테스트 문제를 만들어주세요.

        * 문제 만들 때 주의사항
        1. 반드시 한국어로 작성해주세요.
        2. JSON 형식으로 반환해주세요.
        3. 존댓말을 사용하세요.
        4. 문장이 매끄럽게 이어지도록 하세요.

        
        * 문제 형식
        {{
            "문제명": "문제의 제목",
            "난이도": "난이도 (예: 쉬움, 중, 어려움)",
            "문제": "문제 내용",
            "입력설명": "입력에 대한 설명",
            "출력설명": "출력에 대한 설명",
            "예제입력": ["입력 예시"],
            "예제출력": ["출력 예시"],
            "힌트": "힌트"
        }}
        """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 Python 코딩 문제를 만드는 AI입니다. 모든 문제는 반드시 한국어로 제공되어야 하며, 문장이 매끄럽게 만들어주세요."},
            {"role": "user", "content": prompt}
        ]
    )
    
    raw_content = response.choices[0].message.content.strip()
    print(f"GPT 응답 내용: {raw_content}")  # 디버깅용 출력
    
    try:
        question_data = json.loads(raw_content)  # 문자열을 JSON 객체로 변환
        print(f"문제 변환 완료: {question_data}")
        return question_data
    except json.JSONDecodeError as e:
        print(f"JSON 변환 실패: {e}")
        return {"question": "문제를 불러오는 데 실패했습니다.", "answer": ""}





@app.route("/")
def home():
    return render_template("index.html")

@app.route("/topics")
def topics():
    return render_template("topics.html", topics=PYTHON_TOPICS.keys())

@app.route("/topics/<topic_name>")
def topic_detail(topic_name):
    description = PYTHON_TOPICS.get(topic_name, "설명이 없습니다.")
    print(f"topic_datail {topic_name} 찾았다")
    return render_template("topic_detail.html", topic_name=topic_name, description=description)

@app.route("/topics/<topic_name>/quiz")
def topic_quiz(topic_name):
    question = generate_question(topic_name)
    print(f"topic_quiz {topic_name} 찾았다. 생성된 문제: {question}")

    # 예제 데이터가 없을 경우 기본 값 제공
    if not question.get("example"):
        question["example"] = [{"input": [], "output": "예제 없음"}]

    return render_template("topic_quiz.html", topic_name=topic_name, question=question)



@app.route("/quiz")
def quiz():
    question = generate_question()
    print(f"{question}이다")
    return render_template("quiz.html", question=question)


@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.json
    user_code = data.get("code", "")
    correct_answer = data.get("answer", "")

    try:
        # 사용자가 입력한 코드 실행
        process = subprocess.run(["python3", "-c", user_code], capture_output=True, text=True, timeout=5)
        user_output = process.stdout.strip()

        if user_output == correct_answer.strip():
            return jsonify({"correct": True})
        return jsonify({"correct": False, "output": user_output})
    except Exception as e:
        return jsonify({"correct": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
