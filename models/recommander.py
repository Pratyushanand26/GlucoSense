
import google.generativeai as genai

genai.configure(api_key="AIzaSyAqQE5C_rjVWZYTvYsx9W6VAwdoD0UO3gU")

instruction = """

I think of you as a doctor and a statisticsian who is going to evaluate a persons health data , the data is a time serise data which involves features like 
1. rest Heart Rate(weekly average)
2. Heart Rate Variability(may or may not given)	(weekly average)
3. Sleep Duration	(weekly average)
4. Physical Activity (Steps,Calories Burned) (weekly average)
5. SpO₂ (Blood Oxygen Saturation)	
6. Stress Level (0-10)
7. Skin Temperature (weekly average)
8. Body Weight
9. Age
10.height
11.Cold/Illness Symptoms (Yes/no and what happen)(since how many days)
12.Energy/Fatigue Level (0-10)
13.Muscle Soreness/Aches(0-10)
14.Mood/Emotional State(0-10)





"""

response = genai.GenerativeModel("gemini-2.5-pro").generate_content(
    instruction
)

print(response.text)
