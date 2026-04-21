# Py_to_Anki 🐍🗂️

An automated tool designed to transform Python technical documentation (PDF/Text) into high-quality Anki flashcards using the **Google Gemini AI API**.

## 🚀 Overview
This project helps developers and students convert dense programming books into digestible study material. By leveraging the **Gemini 1.5 Flash** model, it analyzes technical content and generates structured Question-Answer pairs in JSON format, which are then saved as a CSV file ready for Anki import.

## ✨ Key Features
- **Smart Chunking:** Efficiently processes large documents by breaking them into manageable parts.
- **AI-Powered Generation:** Uses state-of-the-art LLMs to identify key Python concepts, syntax, and methods.
- **Modular Architecture:** Clean code structure with separated concerns (API client, file handling, and processing logic).
- **Security First:** Implements `.env` support to keep API keys safe.
- **Rate-Limit Management:** Optimized for the Google Gemini Free Tier with built-in delays and error handling.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **AI Orchestration:** `google-genai` (Official SDK)
- **Environment Management:** `python-dotenv`
- **Data Format:** CSV / JSON

## 📋 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/Py_to_Anki.git](https://github.com/yourusername/Py_to_Anki.git)
   cd Py_to_Anki
