from google import genai
from prompt import Instruction
from uitls import extract_json_from_text

API_KEY="AIzaSyDkrK1EkbwCnvxFsGEBjeaeBtLDOHPljzE"

def evaluate(data ,  API_KEY=API_KEY):
  print('evaluating...')
  client = genai.Client(api_key=API_KEY)


  instruction = Instruction

  response = client.models.generate_content(
  model="gemini-2.5-pro",
  contents=f"{instruction}\n\nOutput the final analysis strictly in the following Python dictionary format in json format(no extra text outside JSON):\n\n{{\n  'STATUS': str,\n  'Evaluation Period': str,\n  'Current Status': str,\n  'What_We’re_Seeing': str,\n  'Key_Observations': {{\n      'Going_Well': list,\n      'Worth_Noting': list,\n      'Needs_Attention': list\n  }},\n  'Recommendations': {{\n      'Immediate_Actions': list,\n      'Monitoring_&_Follow_up': list,\n      'Professional_Consultation': list,\n      'When_to_Seek_Care': list\n  }}\n}}",)

  json_str = response.text

  result = extract_json_from_text(json_str)
  if result:
    pass
  else:
    print("No valid JSON extracted.")
  return response.text,result

"""data='''Female, 45 years old

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

evaluate(data)"""