import streamlit as st
import json
from typing import Dict, List
import time
from config import Config
from agents.title_agent import TitleAgent
from agents.content_agent import ContentAgent

# Page configuration
st.set_page_config(
    page_title="AI Content Strategist",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI with animations
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Card Styles */
    .custom-card {
        background: linear-gradient(135deg, #2A4365 0%, #1A365D 100%); 
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: none;
        color: white;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .content-card {
        background: grey;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border-left: 4px solid #4299E1;
    }
    
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    
    .title-card {
        background: linear-gradient(135deg, #2A4365 0%, #1A365D 100%); 
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: white;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .title-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(255,107,107,0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4299E1 0%, #3182CE 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #2A4365 0%, #1A365D 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    .section-header {
        color: #2D3748;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #4299E1;
        display: inline-block;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #3182CE 0%, #2B6CB0 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(49,130,206,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(49,130,206,0.4);
    }
    
    /* Input Styles */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #E8E8E8;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4299E1;
        box-shadow: 0 0 10px rgba(66,153,225,0.2);
    }
    
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #E8E8E8;
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #2A4365 0%, #1A365D 100%);
    }
    
    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.6s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Loading Animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #FF6B6B;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #48BB78 0%, #38A169 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #F56565 0%, #E53E3E 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'generated_titles' not in st.session_state:
        st.session_state.generated_titles = []
    if 'selected_title' not in st.session_state:
        st.session_state.selected_title = ""
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = {}
    if 'agents_initialized' not in st.session_state:
        st.session_state.agents_initialized = False

def initialize_agents():
    """Initialize AI agents"""
    try:
        Config.validate_config()
        
        if not st.session_state.agents_initialized:
            st.session_state.title_agent = TitleAgent(
                api_key=Config.GOOGLE_API_KEY,
                model_name=Config.MODEL_NAME
            )
            st.session_state.content_agent = ContentAgent(
                api_key=Config.GOOGLE_API_KEY,
                model_name=Config.MODEL_NAME
            )
            st.session_state.agents_initialized = True
        
        return True
    except Exception as e:
        st.error(f"❌ Error initializing agents: {str(e)}")
        st.info("💡 Please make sure to set your GOOGLE_API_KEY in the .env file")
        return False

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🚀 AI Content Strategist</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;">
            Generate SEO-optimized titles and engaging content for any platform
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_input_form():
    """Render the input form"""
    st.markdown('<h2 class="section-header slide-in">📝 Content Configuration</h2>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input(
                "🎯 Topic",
                placeholder="e.g., Digital Marketing Trends 2024",
                help="Enter the main topic for your content"
            )
            
            target_audience = st.text_input(
                "👥 Target Audience",
                placeholder="e.g., Marketing professionals, Small business owners",
                help="Describe your target audience"
            )
        
        with col2:
            content_format = st.selectbox(
                "📱 Content Format",
                ["LinkedIn Post", "Instagram Post", "Newsletter", "Blog Post", "Twitter Thread"],
                help="Choose the platform for your content"
            )
            
            tone = st.selectbox(
                "🎭 Tone",
                ["Professional", "Casual", "Inspirational", "Educational", "Humorous", "Authoritative"],
                help="Select the tone for your content"
            )
    
    # Key points (optional)
    key_points = st.text_area(
        "🔑 Key Points (Optional)",
        placeholder="Enter key points separated by commas",
        help="Add specific points you want to include in your content"
    )
    
    return topic, target_audience, content_format, tone, key_points

def render_title_generation(topic, target_audience, content_format, tone):
    """Render title generation section"""
    st.markdown('<h2 class="section-header">✨ AI-Generated Titles</h2>', unsafe_allow_html=True)
    
    if st.button("🎯 Generate SEO-Optimized Titles", key="generate_titles"):
        if not all([topic, target_audience]):
            st.warning("⚠️ Please fill in at least Topic and Target Audience")
            return
        
        with st.spinner("🤖 Generating compelling titles..."):
            try:
                titles = st.session_state.title_agent.generate_titles(
                    topic=topic,
                    target_audience=target_audience,
                    content_format=content_format,
                    tone=tone
                )
                st.session_state.generated_titles = titles
                
                # Success animation
                st.markdown('<div class="success-message">✅ Titles generated successfully!</div>', unsafe_allow_html=True)
                time.sleep(0.5)
                
            except Exception as e:
                st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
    
    # Display generated titles
    if st.session_state.generated_titles:
        st.markdown("### 🏆 Choose Your Perfect Title:")
        
        for i, title_data in enumerate(st.session_state.generated_titles):
            with st.container():
                st.markdown(f"""
                <div class="title-card fade-in" style="animation-delay: {i*0.1}s;">
                    <h4 style="margin: 0 0 0.5rem 0;">{title_data.get('title', 'Untitled')}</h4>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>📊 SEO Score: {title_data.get('seo_score', 'N/A')}/10</span>
                        <span style="font-size: 0.9rem; opacity: 0.8;">💡 {title_data.get('reasoning', 'Great title choice')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select This Title", key=f"select_title_{i}"):
                    st.session_state.selected_title = title_data.get('title', '')
                    st.success(f"✅ Selected: {st.session_state.selected_title}")

def render_content_generation(topic, target_audience, content_format, tone, key_points):
    """Render content generation section"""
    st.markdown('<h2 class="section-header">🎨 AI-Generated Content</h2>', unsafe_allow_html=True)
    
    if not st.session_state.selected_title:
        st.info("👆 Please select a title first to generate content")
        return
    
    st.markdown(f"**Selected Title:** {st.session_state.selected_title}")
    
    if st.button("🚀 Generate Engaging Content", key="generate_content"):
        with st.spinner("✍️ Crafting your engaging content..."):
            try:
                key_points_list = [point.strip() for point in key_points.split(',')] if key_points else []
                
                content_data = st.session_state.content_agent.generate_content(
                    title=st.session_state.selected_title,
                    topic=topic,
                    target_audience=target_audience,
                    content_format=content_format,
                    tone=tone,
                    key_points=key_points_list
                )
                
                st.session_state.generated_content = content_data
                st.markdown('<div class="success-message">✅ Content generated successfully!</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
    
    # Display generated content
    if st.session_state.generated_content:
        render_content_display()

def render_content_display():
    """Display the generated content with metrics"""
    content_data = st.session_state.generated_content
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{content_data.get('engagement_score', 'N/A')}/10</h3>
            <p>Engagement Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(content_data.get('hashtags', []))}</h3>
            <p>Hashtags</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(content_data.get('content', '').split())}</h3>
            <p>Words</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈</h3>
            <p>{content_data.get('estimated_reach', 'Good')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("""
    <div class="content-card fade-in">
        <h3>📝 Your Generated Content:</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.text_area(
        "Content:",
        value=content_data.get('content', ''),
        height=300,
        key="content_display"
    )
    
    # Additional information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏷️ Suggested Hashtags:**")
        hashtags = content_data.get('hashtags', [])
        if hashtags:
            st.write(" ".join(hashtags))
        else:
            st.write("No hashtags generated")
    
    with col2:
        st.markdown("**📢 Call to Action:**")
        st.write(content_data.get('cta', 'Engage with your audience!'))
    
    # Platform optimization info
    st.markdown("**🎯 Platform Optimization:**")
    st.info(content_data.get('platform_optimization', 'Content optimized for selected platform'))

def render_sidebar():
    """Render the sidebar with additional features"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="color: white;">🚀 Content Strategist</h2>
            <p style="color: rgba(255,255,255,0.8);">AI-Powered Content Creation</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick tips
        st.markdown("### 💡 Quick Tips")
        st.markdown("""
        - **Be Specific**: The more specific your topic, the better the results
        - **Know Your Audience**: Clear audience definition improves content quality
        - **Test Different Tones**: Try various tones to see what works best
        - **Use Key Points**: Add specific points you want to highlight
        """)
        
        st.markdown("---")
        
        # Platform best practices
        st.markdown("### 📱 Platform Best Practices")
        platform_tips = {
            "LinkedIn": "Professional tone, industry insights, thought leadership",
            "Instagram": "Visual storytelling, emojis, lifestyle connection",
            "Newsletter": "Personal touch, exclusive content, clear value",
            "Blog Post": "SEO optimization, comprehensive coverage, authority",
            "Twitter": "Concise, engaging, conversation starters"
        }
        
        for platform, tip in platform_tips.items():
            with st.expander(f"📌 {platform}"):
                st.write(tip)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Check if agents can be initialized
    if not initialize_agents():
        st.stop()
    
    render_header()
    render_sidebar()
    
    # Main content area
    topic, target_audience, content_format, tone, key_points = render_input_form()
    
    st.markdown("---")
    
    # Title generation
    render_title_generation(topic, target_audience, content_format, tone)
    
    st.markdown("---")
    
    # Content generation
    render_content_generation(topic, target_audience, content_format, tone, key_points)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; color: #7F8C8D;">
        <p>Made with ❤️ using Streamlit and Google Generative AI</p>
        <p>🚀 Boost your content strategy with AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()