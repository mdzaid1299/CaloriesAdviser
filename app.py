import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class NutritionAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat_model = genai.GenerativeModel('gemini-1.5-pro')
        self.max_retries = 3
        self.retry_delay = 2

    def analyze_image(self, image_data, custom_prompt=""):
        """Analyze food image with health insights and exercise recommendations"""
        prompt = """
        You are an expert nutritionist and fitness coach. Analyze the food in the image and provide:

        ## 🍽️ Food Analysis
        • List each food item with calories:
          1. Item 1 - X calories
          2. Item 2 - X calories
          ...
        • Total Calories: X

        ## 💪 Exercise to Burn These Calories
        • Walking: X minutes
        • Running: X minutes
        • Swimming: X minutes
        • Cycling: X minutes
        • Yoga: X minutes

        ## 🏥 Health Assessment
        • Healthiness Score: X/10
        • Pros:
          - Point 1
          - Point 2
        • Cons:
          - Point 1
          - Point 2

        ## 💡 Recommendations
        • Healthier alternatives (if needed)
        • Portion size suggestions
        • Best time to consume

        Please format the response in clean markdown with emojis for better readability.
        If you're unsure about any item, provide an estimate and mention it.
        """
        
        full_prompt = prompt + "\n" + custom_prompt if custom_prompt else prompt
        
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content([full_prompt, image_data[0]])
                return response.text
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Analysis failed: {str(e)}")
                time.sleep(self.retry_delay)

    def chat_about_food(self, image_data, question):
        """Handle follow-up questions about the food"""
        prompt = f"""
        As a nutrition and fitness expert, answer this question about the food in the image:
        {question}

        Provide a detailed but concise response. If the question is about nutrition or health,
        include scientific backing where relevant.
        """
        try:
            response = self.model.generate_content([prompt, image_data[0]])
            return response.text
        except Exception as e:
            raise Exception(f"Chat response failed: {str(e)}")

def input_image_setup(uploaded_file):
    """Process the uploaded image file"""
    if uploaded_file is not None:
        try:
            if uploaded_file.size > 10 * 1024 * 1024:
                raise ValueError("Please upload a smaller image (less than 10MB)")
            
            valid_formats = ["image/jpeg", "image/jpg", "image/png"]
            if uploaded_file.type not in valid_formats:
                raise ValueError("Please upload a JPG or PNG image")
            
            bytes_data = uploaded_file.getvalue()
            return [{"mime_type": uploaded_file.type, "data": bytes_data}]
        except Exception as e:
            raise ValueError(f"Invalid image: {str(e)}")
    raise FileNotFoundError("Please upload an image first")

def main():
    st.set_page_config(
        page_title="Smart Health Analyzer",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for modern UI
    st.markdown("""
        <style>
        /* Modern styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Cards */
        .stCard {
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin: 1rem 0;
            background: white;
        }
        
        /* Buttons */
        .stButton button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            background: linear-gradient(45deg, #ff4b4b, #ff6b6b);
            color: white;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #333;
            font-weight: 600;
        }
        
        /* Chat container */
        .chat-container {
            border-radius: 15px;
            border: 1px solid #eee;
            padding: 1rem;
            margin: 1rem 0;
            max-height: 400px;
            overflow-y: auto;
        }
        
        /* Messages */
        .user-message {
            background: #f0f2f5;
            padding: 0.8rem;
            border-radius: 15px;
            margin: 0.5rem 0;
        }
        
        .bot-message {
            background: #fff3f3;
            padding: 0.8rem;
            border-radius: 15px;
            margin: 0.5rem 0;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar for settings and information
    with st.sidebar:
        st.image("https://via.placeholder.com/150.png?text=Health+AI", width=150)
        st.markdown("### 🎯 How to use")
        st.markdown("""
        1. Upload a food image
        2. Get instant analysis
        3. Chat with AI about your food
        4. Learn about nutrition & exercise
        """)
        
        st.markdown("### 🎨 Theme")
        theme = st.selectbox("Select theme:", ["Light", "Dark"])
        
        st.markdown("### 📱 Display")
        st.checkbox("Compact mode", help="Enable for smaller screens")

    # Main content area with tabs
    st.title("🥗 Smart Health Analyzer")
    tabs = st.tabs(["📸 Analysis", "💬 Chat", "📊 History"])

    with tabs[0]:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Upload Your Food Image")
            uploaded_file = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png"],
                help="Take a clear photo of your food"
            )
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Your Food", use_column_width=True)

            custom_prompt = st.text_input(
                "Any specific concerns?",
                placeholder="E.g., allergies, dietary restrictions..."
            )

            if st.button("Analyze Food", use_container_width=True):
                if uploaded_file:
                    try:
                        with st.spinner("AI is analyzing your food..."):
                            image_data = input_image_setup(uploaded_file)
                            analyzer = NutritionAnalyzer()
                            analysis = analyzer.analyze_image(image_data, custom_prompt)
                            
                            # Store analysis in session state for chat
                            st.session_state['current_analysis'] = analysis
                            st.session_state['image_data'] = image_data
                            
                            # Display analysis in the second column
                            with col2:
                                st.markdown("### 📊 Analysis Results")
                                st.markdown(analysis)
                                
                                # Download button
                                st.download_button(
                                    "📥 Download Report",
                                    analysis,
                                    file_name="health_analysis.md",
                                    mime="text/markdown"
                                )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please upload an image first!")

    with tabs[1]:
        st.markdown("### 💬 Chat with AI about Your Food")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="user-message">👤 You: {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">🤖 AI: {message["content"]}</div>', 
                          unsafe_allow_html=True)

        # Chat input
        if 'image_data' in st.session_state:
            question = st.text_input("Ask about your food:", 
                                   placeholder="E.g., Is this meal suitable for diabetics?")
            
            if st.button("Send", use_container_width=True):
                if question:
                    try:
                        # Add user message to history
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': question
                        })
                        
                        # Get AI response
                        analyzer = NutritionAnalyzer()
                        response = analyzer.chat_about_food(
                            st.session_state.image_data, 
                            question
                        )
                        
                        # Add AI response to history
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        
                        # Rerun to update chat display
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("Please analyze a food image first to start chatting!")

    with tabs[2]:
        st.markdown("### 📊 Analysis History")
        st.info("Coming soon: Track your nutrition and exercise history over time!")

if __name__ == "__main__":
    main()