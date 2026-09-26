import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [quiz, setQuiz] = useState([]);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleAnswerSelect = (questionIndex, answer) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer,
    });
  };

  const handleSubmitQuiz = () => {
    let currentScore = 0;
    for (let i = 0; i < quiz.length; i++) {
      if (selectedAnswers[i] === quiz[i].correct_answer) {
        currentScore++;
      }
    }
    setScore(currentScore);
    setSubmitted(true);
  };

  const handleReset = () => {
    setQuestion("");
    setFile(null);
    setQuiz([]);
    setSelectedAnswers({});
    setScore(0);
    setError("");
    setSubmitted(false);
  };

  const handleGenerateQuiz = async () => {
    if (!question || !file) {
      alert("Please enter a question and upload a PDF.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const formData = new FormData();

      formData.append("question", question);
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/upload-pdf", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      setQuiz(data.quiz);
    } catch (error) {
      setError("Failed to generate quiz.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="quiz-container">
        <h1>AI QUIZ GENERATOR</h1>

        <label htmlFor="question">Enter Question</label>

        <input
          id="question"
          type="text"
          className="question-input"
          placeholder="Enter your question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        ></input>

        <label htmlFor="pdf">Upload PDF</label>

        <input
          id="pdf"
          type="file"
          accept=".pdf"
          className="file-input"
          onChange={(e) => setFile(e.target.files[0])}
        ></input>

        <button
          className="generate-btn"
          onClick={handleGenerateQuiz}
          disabled={loading}
        >
          {loading ? "Generating..." : "Generate Quiz"}
        </button>

        <p>{error}</p>

        <div className="quiz-section">
          {quiz.map((item, index) => (
            <div className="question-card" key={index}>
              <h3>
                {index + 1}. {item.question}
              </h3>

              <div className="options">
                <button
                  className={selectedAnswers[index] === "A" ? "selected" : ""}
                  onClick={() => handleAnswerSelect(index, "A")}
                >
                  {item.options.A}
                </button>
                <button
                  className={selectedAnswers[index] === "B" ? "selected" : ""}
                  onClick={() => handleAnswerSelect(index, "B")}
                >
                  {item.options.B}
                </button>
                <button
                  className={selectedAnswers[index] === "C" ? "selected" : ""}
                  onClick={() => handleAnswerSelect(index, "C")}
                >
                  {item.options.C}
                </button>
                <button
                  className={selectedAnswers[index] === "D" ? "selected" : ""}
                  onClick={() => handleAnswerSelect(index, "D")}
                >
                  {item.options.D}
                </button>
              </div>
            </div>
          ))}
        </div>

        {quiz.length > 0 && !submitted && (
          <button className="submit-btn" onClick={handleSubmitQuiz}>
            Submit quiz
          </button>
        )}

        {submitted && (
          <>
            <p className="score">Your Score: {score}</p>

            <button className="reset-btn" onClick={handleReset}>
              Start New quiz
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
