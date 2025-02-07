function showSolution() {
    document.getElementById("solution").style.display = "block";
}
function checkAnswer() {
    let userCode = document.getElementById("user_code").value;
    let correctAnswer = document.getElementById("correct-answer").textContent;

    fetch("/check_answer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            code: userCode,
            answer: correctAnswer
        })
    })
    .then(response => response.json())
    .then(data => {
        let resultElement = document.getElementById("result");
        let solutionBtn = document.getElementById("solution-btn");

        if (data.correct) {
            resultElement.innerHTML = "✅ 정답입니다!";
            solutionBtn.disabled = false; // 정답을 맞히면 풀이 버튼 활성화
        } else {
            resultElement.innerHTML = "❌ 오답입니다. 다시 시도해 보세요.";
        }
    })
    .catch(error => console.error("오류 발생:", error));
}

function showSolution() {
    document.getElementById("solution").style.display = "block";
}
