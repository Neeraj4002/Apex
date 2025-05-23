
# 🚀 Apex - AI Content Strategist

An intelligent web application that leverages Google's Gemini AI to generate SEO-optimized content titles, create platform-specific content, and manage a content calendar - all through an intuitive Streamlit interface.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-API-orange.svg)

## ✨ Features

### 🎯 Title Generation Agent
- Generate 5-7 SEO-optimized, catchy content titles
- Powered by Google Gemini AI with dynamic generation
- No hardcoded templates - 100% AI-generated creativity
- Intelligent keyword analysis and trend awareness

### 📝 Content Generation Agent
- Create platform-specific content (Blog, LinkedIn, Instagram, Twitter, Facebook)
- Target multiple audience segments simultaneously
- Automatic formatting with appropriate emojis, hashtags, and structure
- Context-aware content generation based on platform best practices

### 📅 Content Calendar Agent
- Visual content calendar with interactive timeline
- Automatic scheduling with 1-day intervals
- Export functionality to CSV for external use
- Plotly-powered visualization for better planning

### 🎨 Modern UI/UX
- Clean 3-step workflow with progress indicators
- Responsive design with custom CSS styling
- Session state management for seamless experience
- Professional gradient headers and smooth transitions


## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Step 1: Clone the Repository
git clone https://github.com/Neeraj4002/Apex.git
cd ai-content-strategist

### Step 2: Create Virtual Environment (Recommended)
# Windows
python -m venv venv
venv\Scripts\activate

### Step 3: Install Dependencies
pip install -r requirements.txt

### Step 4: Run the Application
streamlit run app.py

The application will open in your default browser at `http://localhost:8501`

## 📋 Usage Guide

### 1️⃣ Initial Setup
- Enter your Google Gemini API key in the sidebar
- The key is stored in session state for the current session

### 2️⃣ Generate Titles
- Enter a seed keyword or topic (e.g., "AI productivity tools")
- Click "Generate Titles" to get 5-7 AI-generated options
- Select your favorite title and click "Lock Title"

### 3️⃣ Create Content
- Choose your content format (Blog, LinkedIn, Instagram, etc.)
- Select target audience(s) from the multi-select dropdown
- Click "Generate Content" to create platform-optimized content

### 4️⃣ Manage Calendar
- Review the generated content
- Click "Add to Calendar" to schedule the post
- View the visual timeline and download as CSV

## 📁 Project Structure

ai-content-strategist/
│
├── app.py                 # Main Streamlit application
├── title_agent.py         # Title generation logic using Gemini
├── content_agent.py       # Content generation with platform specs
├── calendar_agent.py      # Calendar management and visualization
├── ui_utils.py           # UI utilities and custom CSS
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation

## 🔧 Configuration

### API Key Setup
The application uses Google's Gemini API. You'll need to:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Enter it in the application sidebar

## 🚀 Technologies Used

- **[Streamlit](https://streamlit.io/)** - Web application framework
- **[LangChain](https://python.langchain.com/)** - LLM orchestration
- **[Google Gemini AI](https://deepmind.google/technologies/gemini/)** - Content generation
- **[Plotly](https://plotly.com/python/)** - Interactive visualizations
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation
- **Python 3.8+** - Core programming language

## 📊 API Usage

The application makes API calls to Google Gemini for:
- Title generation (1 call per generation)
- Content creation (1 call per content piece)

Monitor your API usage in the [Google Cloud Console](https://console.cloud.google.com/).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- Content generation may take 10-15 seconds depending on length
- Calendar visualization requires at least one saved item
- API rate limits apply based on your Google Cloud tier

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



---

<p align="center">
  Made with ❤️ by [S.N.K]
