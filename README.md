\# SnapperAI



SnapperAI is an AI-powered screenshot assistant that allows users to capture or select screenshots and use AI to understand, analyze, and research the content shown.



\## Features



\- 📸 Capture screenshots

\- 🖼️ Select existing screenshots

\- 🤖 Explain screenshots

\- 📝 Summarize screenshots

\- 🐛 Find visible errors in code/screenshots

\- 📄 Extract important information

\- 🔎 Research topics directly from screenshots

\- 💬 Ask custom questions about screenshots

\- 🕘 Clickable screenshot history



\## How It Works



SnapperAI combines local AI, OCR, and live web search.



1\. The user captures or selects a screenshot.

2\. The screenshot is analyzed using a local Ollama vision model.

3\. For the Research feature, Tesseract OCR extracts text from the screenshot.

4\. The extracted topic is sent to SerpApi for live web search.

5\. Search results are processed by the AI.

6\. The result is displayed inside SnapperAI.



\## Research Feature



The Research feature allows SnapperAI to go beyond the information directly visible in a screenshot.



When the user selects \*\*Research\*\*:



1\. Tesseract OCR extracts text from the screenshot.

2\. SnapperAI identifies a useful research query.

3\. The query is sent to SerpApi.

4\. Live Google search results are retrieved.

5\. The results are processed by the AI.

6\. The research answer and source results are displayed in the application.



\## Technologies



\- Python

\- PySide6

\- Ollama

\- Tesseract OCR

\- Pillow

\- SerpApi

\- PySide6 QThread



\## Requirements



Before running SnapperAI, install:



\- Python 3.x

\- Ollama

\- Tesseract OCR

\- A compatible Ollama vision model

\- SerpApi API key



\## Installation



\### 1. Clone the repository



```bash

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd snapperAI

