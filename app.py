import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import io
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def input_image_setup(uploaded_file):
    """Validate and prepare the image for analysis"""
    if uploaded_file is not None:
        try:
            if uploaded_file.size > 10 * 1024 * 1024:
                raise ValueError(
                    "Please upload a smaller image (less than 10MB)")

            valid_formats = ["image/jpeg", "image/jpg", "image/png"]
            if uploaded_file.type not in valid_formats:
                raise ValueError("Please upload a JPG or PNG image")

            bytes_data = uploaded_file.getvalue()
            return [{"mime_type": uploaded_file.type, "data": bytes_data}]
        except Exception as e:
            raise ValueError(f"Invalid image: {str(e)}")
    raise FileNotFoundError("Please upload an image first")


class FoodHistory:
    def __init__(self):
        self.history_file = "food_history.json"
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)

    def add_entry(self, user_id, image_path, analysis, calories):
        entry = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'image_path': image_path,
            'analysis': analysis,
            'calories': calories
        }
        self.history.append(entry)
        self.save_history()

    def get_user_history(self, user_id):
        return [entry for entry in self.history if entry['user_id'] == user_id]


class PDFGenerator:
    @staticmethod
    def create_pdf(analysis_text, image_path=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom style for headers
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#ff4b4b')
        ))

        # Content elements
        elements = []

        # Title
        elements.append(
            Paragraph("Health Analysis Report", styles['CustomTitle']))
        elements.append(Spacer(1, 12))

        # Add image if provided
        if image_path:
            img = RLImage(image_path, width=5*inch, height=4*inch)
            elements.append(img)
            elements.append(Spacer(1, 12))

        # Format analysis text
        for line in analysis_text.split('\n'):
            if line.strip().startswith('#'):
                # Handle headers
                elements.append(Paragraph(line.replace(
                    '#', '').strip(), styles['Heading2']))
            else:
                # Handle regular text
                elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 6))

        doc.build(elements)
        return buffer


class NutritionAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chat_model = genai.GenerativeModel('gemini-1.5-pro')
        self.max_retries = 3
        self.retry_delay = 2
        self.food_history = FoodHistory()

    def extract_calories(self, analysis_text):
        try:
            for line in analysis_text.split('\n'):
                if 'Total Calories:' in line:
                    return int(line.split(':')[1].strip().split()[0])
        except:
            return 0
        return 0

    def analyze_image(self, image_data, user_id, image_path, custom_prompt=""):
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
                response = self.model.generate_content(
                    [full_prompt, image_data[0]])
                analysis = response.text
                calories = self.extract_calories(analysis)

                # Save to history
                self.food_history.add_entry(
                    user_id, image_path, analysis, calories)

                return analysis
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


def main():
    st.set_page_config(
        page_title="Smart Health Analyzer",
        page_icon="🥗",
        layout="wide",
    )

    # Custom CSS with lighter capture section and removed button animation
    st.markdown("""
        <style>
        /* Previous CSS styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        .title {
            background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
            font-weight: 600;
            text-align: center;
            margin-top: -3rem;
        }
        
        .capture-section {
          
    border-radius: 15px;

        }
        
        .stButton button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            background: #ff4b4b !important;
            color: white;
            border: none;
            transition: none;
        }
        
        .stButton button:hover {
            transform: none;
            box-shadow: none;
        }
        
        .history-entry {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border: 1px solid #eee;
        }
        
        .history-date {
            color: #666;
            font-size: 0.9rem;
        }
        
        .history-calories {
            color: #ff4b4b;
            font-weight: bold;
        }
        
        .chat-container {
            border-radius: 15px;
            border: 1px solid #eee;
            padding: 1rem;
            margin: 1rem 0;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .user-message {
            background: #4976ba;
            padding: 0.8rem;
            border-radius: 15px;
            margin: 0.5rem 0;
        }
        
        .bot-message {
            background: #8e60a3;
            padding: 0.8rem;
            border-radius: 15px;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main title
    st.markdown('<h3 class="title">Smart Health Analyzer</h3>',
                unsafe_allow_html=True)

    # Initialize session state for user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(hash(datetime.now().isoformat()))

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Main content area with tabs
    tabs = st.tabs(["📸 Analysis", "💬 Chat", "📊 History"])

    with tabs[0]:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown('<div class="capture-section">',
                        unsafe_allow_html=True)
            st.markdown("### 🥗 Capture or Upload Food Image")

            camera_image = st.camera_input("Take a picture", key="camera")
            uploaded_file = st.file_uploader(
                "Or upload an image",
                type=["jpg", "jpeg", "png"],
                help="Take a clear photo of your food"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            image_file = camera_image if camera_image is not None else uploaded_file

            if image_file:
                image = Image.open(image_file)
                st.image(image, caption="Your Food", use_column_width=True)

            custom_prompt = st.text_input(
                "Any specific concerns?",
                placeholder="E.g., allergies, dietary restrictions..."
            )

            if st.button("Analyze Food", use_container_width=True):
                if image_file:
                    try:
                        with st.spinner("Analyzing your food..."):
                            image_data = input_image_setup(image_file)
                            analyzer = NutritionAnalyzer()

                            # Save image temporarily
                            temp_image = f"food_{st.session_state.user_id}_{
                                int(time.time())}.jpg"
                            image.save(temp_image)

                            analysis = analyzer.analyze_image(
                                image_data,
                                st.session_state.user_id,
                                temp_image,
                                custom_prompt
                            )

                            st.session_state['current_analysis'] = analysis
                            st.session_state['image_data'] = image_data

                            with col2:
                                st.markdown("### 📊 Analysis Results")
                                st.markdown(analysis)

                                # Generate PDF report
                                pdf_generator = PDFGenerator()
                                pdf_buffer = pdf_generator.create_pdf(
                                    analysis, temp_image)

                                st.download_button(
                                    "📥 Download PDF Report",
                                    pdf_buffer.getvalue(),
                                    file_name="health_analysis.pdf",
                                    mime="application/pdf"
                                )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please capture or upload an image first!")

    with tabs[1]:
        st.markdown("### 💬 Chat with AI about Your Food")

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
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': question
                        })

                        analyzer = NutritionAnalyzer()
                        response = analyzer.chat_about_food(
                            st.session_state.image_data,
                            question
                        )

                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response
                        })

                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("Please analyze a food image first to start chatting!")

    with tabs[2]:
        st.markdown("### 📊 Your Food History")

        analyzer = NutritionAnalyzer()
        user_history = analyzer.food_history.get_user_history(
            st.session_state.user_id)

        if user_history:
            for entry in reversed(user_history):
                with st.expander(f"Meal from {datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        if os.path.exists(entry['image_path']):
                            st.image(entry['image_path'],
                                     use_column_width=True)

                    with col2:
                        st.markdown(f"**Calories:** {entry['calories']}")
                        st.markdown(entry['analysis'])
        else:
            st.info("No food history yet. Start by analyzing your first meal!")


if __name__ == "__main__":
    main()
