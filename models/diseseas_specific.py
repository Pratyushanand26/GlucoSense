from google import genai
from prompt import Disease_prompt

API_KEY='AIzaSyBqYJqqT33hQuwmWZWCzOtDrjUpqYgrSbQ'
def Disease_specific_evaluator_and_recommender(data,API_KEY=API_KEY):
  print("working....")
  client = genai.Client(api_key=API_KEY)

  prompt=Disease_prompt
  response = client.models.generate_content(
     model="gemini-2.5-pro",  
     contents=prompt,
  )

  print(response.text)
  return(response.text)

data='''Male, 38 years old
Height: 170 cm
Weight: 82 kg initially
Genetic history: Hypertension (father)
Lifestyle: Desk job, low activity, irregular diet
Location: Delhi, India (28.61°N, 77.23°E)

5 week data:

| Week | Date Range | Rest HR (bpm) | HRV (ms) | Sleep (hrs) | Steps | Calories Burned | SpO₂ (%) | Stress (0-10) | Skin Temp (°C) | Body Wt (kg) | Cold/Illness | Energy (0-10) | Muscle Soreness (0-10) | Mood (0-10) | Location (lat, lon) |
|------|-------------|---------------|-----------|--------------|--------|------------------|----------|----------------|----------------|---------------|----------------|----------------|----------------|-------------|
| 1 | Sep 30 – Oct 6 | 76 | 45 | 6.4 | 6100 | 2000 | 97 | 5 | 36.8 | 82.0 | No | 6 | 3 | 6 | 28.61, 77.23 |
| 2 | Oct 7 – Oct 13 | 77 | 43 | 6.1 | 5800 | 1980 | 97 | 6 | 36.9 | 82.2 | No | 5 | 4 | 6 | 28.61, 77.23 |
| 3 | Oct 14 – Oct 20 | 79 | 40 | 5.9 | 5400 | 1940 | 96 | 6 | 37.0 | 82.5 | Headache (2 days) | 5 | 5 | 5 | 28.61, 77.23 |
| 4 | Oct 21 – Oct 27 | 81 | 37 | 5.6 | 5100 | 1900 | 96 | 7 | 37.1 | 82.9 | No | 4 | 5 | 5 | 28.61, 77.23 |
| 5 | Oct 28 – Nov 3 | 82 | 35 | 5.5 | 4900 | 1880 | 96 | 7 | 37.2 | 83.1 | No | 4 | 5 | 5 | 28.61, 77.23 |
'''

Disease_specific_evaluator_and_recommender(data)