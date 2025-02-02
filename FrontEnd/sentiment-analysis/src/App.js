import React, { useState } from "react";

const App = () => {
  const [inputText, setInputText] = useState("");
  const [selectedModel, setSelectedModel] = useState("custom");
  const [sentiment, setSentiment] = useState(null);
  const [confidence, setConfidence] = useState(null);

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };

  const analyzeSentiment = async () => {
    // Make the API request to your backend (change URL to match your backend)
    const response = await fetch("http://127.0.0.1:8000/analyze/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: inputText,
        model: selectedModel,
      }),
    });

    const data = await response.json();

    // Handling custom model sentiment values
    if (data.sentiment === "label_1") {
      setSentiment("positive");
    } else if (data.sentiment === "label_0") {
      setSentiment("negative");
    } else {
      setSentiment(data.sentiment); // For Llama model or unexpected result
    }
    setConfidence(data.confidence);
  };

  return (
    <div>
      <h1>Sentiment Analysis</h1>
      <textarea
        value={inputText}
        onChange={handleInputChange}
        placeholder="Enter text for sentiment analysis"
      />
      <br />
      <select value={selectedModel} onChange={handleModelChange}>
        <option value="custom">Custom Model</option>
        <option value="llama">Llama 3</option>
      </select>
      <br />
      <button onClick={analyzeSentiment}>Analyze Sentiment</button>

      {sentiment && (
        <div>
          <h2>Sentiment: {sentiment}</h2>
          {confidence && <p>Confidence: {confidence}</p>}
        </div>
      )}
    </div>
  );
};

export default App;
