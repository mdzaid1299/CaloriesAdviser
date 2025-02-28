Sure! Here’s a **README.md** you can use for your project:

---

# 🍽️ Calorie Advisor

Smart Health Analyzer is a **Streamlit-based web application** that allows users to capture or upload food images and receive a comprehensive nutrition analysis using **Google Gemini AI**. It also provides calorie estimates, exercise recommendations to burn those calories, and personalized health suggestions.

---

## 📋 Features

- 📸 **Food Image Analysis**  
  Upload or capture images of your meals and get detailed nutritional analysis, calorie counts, and health recommendations.

- 📊 **Calorie Tracking & Health Reports**  
  The app generates a **PDF report** with an overview of the food analysis, calories, and recommendations.

- 💬 **AI Chat About Food**  
  After analysis, users can chat with the AI to ask follow-up questions, such as dietary suggestions, allergies, or fitness tips.

- 📂 **Food History Tracking**  
  The app maintains a personal history of analyzed meals for each user, including analysis results, calories, and timestamps.

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** (UI framework)
- **Pillow** (Image processing)
- **Google Gemini AI (via google.generativeai)** (AI analysis and chatbot)
- **ReportLab** (PDF generation)
---

## 📂 Project Structure

```
.
├── app.py                # Main application file
├── food_history.json     # JSON file to store user food history (auto-generated)
├── requirements.txt      # Python dependencies
├── .env                   # Environment variables (Google API key)
├── README.md              # Project documentation
```

---

## ⚙️ Configuration

- **Google API Key:**  
  Obtain your API key from Google AI Studio and set it in `.env` file.

- **File Storage:**  
  The app saves food images temporarily in the root directory and logs all analysis data in `food_history.json`.
---

## 📄 Example Analysis Output

```
## 🍽️ Food Analysis
1. Grilled Chicken - 250 calories
2. Mashed Potatoes - 200 calories
3. Steamed Vegetables - 150 calories
Total Calories: 600

## 💪 Exercise to Burn These Calories
• Walking: 120 minutes
• Running: 60 minutes
• Swimming: 90 minutes
• Cycling: 80 minutes
• Yoga: 150 minutes

## 🏥 Health Assessment
• Healthiness Score: 8/10
• Pros:
    - High protein content
    - Contains vegetables
• Cons:
    - High carb content in potatoes

## 💡 Recommendations
• Replace mashed potatoes with quinoa or brown rice.
• Portion size: Medium (keep protein to 150g).
• Best time to consume: Lunch.
```

---
