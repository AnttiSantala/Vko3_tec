import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os
from groq import Groq  # Import the Groq class
import socket
import subprocess
import time

# Initialize FastAPI app
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Add the CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Load the fine-tuned model from Hugging Face (Step 7: Load Models)
model_name = "anttisantala/my_finetuned_distilbert_model"  # Replace with your model's name or path
tokenizer = AutoTokenizer.from_pretrained(model_name)
fine_tuned_model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Create the pipeline using the fine-tuned model
fine_tuned_pipeline = pipeline("sentiment-analysis", model=fine_tuned_model, tokenizer=tokenizer)
print("Huggingface model loaded")

# Setting up Llama3 (Step 7: Load Models)
api_key = ""  # Your Groq API Key
client = Groq(api_key=api_key)  # Initialize Groq client with the API key

# Define request schema
class SentimentRequest(BaseModel):  # Step 6: Set Up the Backend API (POST endpoint)
    text: str
    model: str  # "custom" or "llama"

@app.post("/analyze/")  # Step 6: Set Up the Backend API (POST endpoint)
async def analyze_sentiment(request: SentimentRequest):
    if request.model == "custom":  # For the custom fine-tuned model
        # Use the custom fine-tuned sentiment analysis model
        result = fine_tuned_pipeline(request.text)[0]
        sentiment_label = "positive" if result["label"] == "LABEL_1" else "negative"
    elif request.model == "llama":  # For the Llama model via Groq API
        # Step 9: Define the Llama 3 Prompt
        # Call the Llama 3 model via the Groq API with a clear and reusable prompt
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Classify the sentiment of this text as positive or negative and give a sentiment score: {request.text}. Don't give reasons, just the label and a score"
            }],
            model="llama-3.3-70b-versatile"  # Replace with the correct model
        )
        sentiment = response.choices[0].message.content
        score = float(sentiment[9:].strip())  # Extract the score part
        # Map Llama's response to sentiment label and confidence score
        if "positive" in sentiment.lower():
            result = {"label": "positive", "score": score}
        else:
            result = {"label": "negative", "score": score}
    else:
        return {"error": "Invalid model. Choose 'custom' or 'llama'."}

    return {
        
        "sentiment": result["label"].lower(),  # Sentiment (positive/negative) (Step 6)
        
        
        "confidence": result["score"]  # Confidence score (Step 6)
    }

# Run FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
