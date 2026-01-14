# 🔍 Smart ATS Checker

An AI-powered application that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). Built with [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/), and [Groq](https://groq.com/).

## 🚀 Features

- **Instant Analyze**: Compares your CV contents directly against the Job Description.
- **Scoring System**: Provides a match score (0-100) to gauge relevance.
- **Detailed Feedback**: Lists exactly which requirements are matched and which are missing.
- **AI Recommendations**: actionable advice on how to improve your CV for the specific role.

## 🛠️ Technologies Used

- **Python**: Core programming language.
- **Streamlit**: For the interactive web interface.
- **LangChain**: For orchestration and agentic workflows.
- **Groq API**: Leveraging high-speed LLMs (e.g., Qwen/Llama 3) for analysis.
- **Pydantic**: For structured data extraction and validation.

## 📋 Prerequisites

- Python 3.8 or higher.
- A [Groq API Key](https://console.groq.com/keys) (Free tier available).

## ⚙️ Installation

1. **Clone the repository** (or download the files):
   ```bash
   git clone <repository-url>
   cd "ats checker"
   ```

2. **Install dependencies**:
   Run the following command (ensure you are in the directory containing `requirements.txt` or install packages manually):
   ```bash
   pip install streamlit langchain langchain-groq python-dotenv pydantic
   ```
   *Note: If you have a `requirements.txt` in the parent directory, use `pip install -r ../requirements.txt`*

3. **Set up Environment Variables**:
   Create a `.env` file in the project root (or ensure it exists in the parent directory) and add your API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## ▶️ Usage

Run the Streamlit application:

```bash
streamlit run ats_checker.py
```

The app will open in your default browser at `http://localhost:8501`.

1. Paste the **Job Description** in the left text area.
2. Paste your **CV / Resume** text in the right text area.
3. Click **Analyze**.
4. Review your score, matched/missing keywords, and recommendations!

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
