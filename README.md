# 🧠 AI Meeting Transcript Analyzer  
### 🚀 Developed During Internship at **Quasar Digital Solutions**

---

## 📄 Overview
This project automatically analyzes meeting transcripts using **Google’s Gemini AI**.  
It generates a structured **AI Analysis Report (PDF)** with:

- ✅ Concise summary (100–150 words)  
- ✅ Sentiment analysis (Positive / Negative / Neutral)  
- ✅ Key conclusions or recommendations (50–100 words)

This project was created by **Ayaan Khan** during his **internship at Quasar Digital Solutions**, where he worked on AI-powered tools for intelligent text summarization and analysis.

---

## 🧩 Key Features
- 🎙️ **Transcript Input** – Reads from a `transcript.txt` file or command-line argument.  
- 🤖 **Gemini AI Integration** – Uses `gemini-1.5-flash` for natural language understanding.  
- 📊 **Structured AI Output** – Produces Summary, Sentiment, and Conclusion sections.  
- 📄 **Automated PDF Report** – Saves output as a timestamped PDF file.  
- 🕒 **Time-Stamped Reports** – Each run creates a uniquely named report.

---

## 🧠 How It Works
1. Load a text transcript (e.g., from Zoom, Meet, or any conversation).  
2. Send it to the **Gemini AI model** for deep analysis.  
3. Parse and structure the AI’s response.  
4. Automatically generate a **professional PDF report** summarizing the meeting.

---

## 🧰 Tech Stack
| Component | Description |
|------------|-------------|
| **Python 3.9+** | Core programming language |
| **Google Generative AI (Gemini)** | Text understanding and summarization |
| **FPDF** | PDF report generation |
| **Time module** | For timestamped output |
| **Sys & OS** | File management utilities |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone this repository
```bash
git clone https://github.com/<your-username>/AI-Meeting-Transcript-Analyzer.git
cd AI-Meeting-Transcript-Analyzer
