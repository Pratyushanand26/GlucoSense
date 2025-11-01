
import google.generativeai as genai
from prompt import Recommendor_command
from evaluator import evaluate 


API_KEY='AIzaSyDkrK1EkbwCnvxFsGEBjeaeBtLDOHPljzE'


def recommender(data, API_KEY=API_KEY):
  result= evaluate(data)
  genai.configure(api_key=API_KEY)
  recommendor_command = f"""
{Recommendor_command}

Now generate a personalized recommendation based on this:
Result Summary:
{result}

User Data:
{data}

Output strictly in this Python dictionary format (no text or greeting outside JSON):

{{
  "Status": str,
  "Summary": str,
  "Observations": {{
    "Positives": list,
    "Concerns": list,
    "Trends": list
  }},
  "Recommendations": {{
    "Immediate_Actions": list,
    "Lifestyle_Suggestions": list,
    "Follow_Up_Advice": list,
    "When_to_Seek_Care": list
  }},
  "Safe_Wellness_Tips": list,
  "Disclaimer": "This analysis supports monitoring only and is not a medical diagnosis."
}}
"""
  print("reccomender working...")
  response_2 = genai.GenerativeModel("gemini-2.5-pro").generate_content(
      recommendor_command 
  )
  
  print(response_2.text)
  return response_2.text

data='''Female, 45 years old

Height: 162 cm

Weight: 79 kg initially

Genetic history: Type 2 diabetes, hypertension

Lifestyle: Sedentary job, inconsistent sleep

5 week data 

| Week | Date Range | Rest HR (bpm) | HRV (ms) | Sleep (hrs) | Steps | Calories Burned | SpO₂ (%) | Stress (0-10) | Skin Temp (°C) | Body Wt (kg) | Cold/Illness | Energy (0-10) | Muscle Soreness (0-10) | Mood (0-10) | Location (lat, lon) |
|------|-------------|---------------|-----------|--------------|--------|------------------|----------|----------------|----------------|---------------|----------------|----------------|----------------|-------------|
| 1 | Sep 30 – Oct 6 | 78 | 38 | 6.0 | 4800 | 1950 | 97 | 6 | 36.9 | 79.0 | No | 5 | 3 | 6 | 12.97, 77.59 |
| 2 | Oct 7 – Oct 13 | 80 | 34 | 5.8 | 4200 | 1880 | 96 | 7 | 37.0 | 79.3 | Headache (2 days) | 4 | 4 | 5 | 12.97, 77.59 |
| 3 | Oct 14 – Oct 20 | 83 | 29 | 5.4 | 4000 | 1820 | 95 | 8 | 37.2 | 79.7 | Fatigue (whole week) | 3 | 5 | 4 | 12.97, 77.59 |
| 4 | Oct 21 – Oct 27 | 85 | 26 | 5.1 | 3700 | 1760 | 94 | 8 | 37.3 | 80.0 | No | 3 | 6 | 4 | 12.97, 77.59 |
| 5 | Oct 28 – Nov 3 | 88 | 25 | 5.0 | 3600 | 1740 | 93 | 9 | 37.4 | 80.3 | Chest tightness (3 days) | 2 | 7 | 3 | 12.97, 77.59 |
'''

response = recommender(data)
print(response)
