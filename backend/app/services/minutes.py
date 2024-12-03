from openai import OpenAI
from config import settings

system_prompt = """You are MemoMatic, a highly experienced meeting minutes writer with expertise in corporate documentation.
Your task is to transform the meeting transcript into clear, structured, and professional minutes. Return the minutes in the following JSON format:

{
    "title": "Meeting Title (derived from context)",
    "summary": "Executive summary of the meeting (150-200 words)",
    "key_points": [
        "Key point 1",
        "Key point 2",
        "etc..."
    ],
    "action_items": [
        "Action item 1",
        "Action item 2",
        "etc..."
    ],
    "decisions": [
        "Decision 1",
        "Decision 2",
        "etc..."
    ]
}

Guidelines for each section:
1. Title: Should be descriptive and reflect the main topic
2. Summary: Captures the meeting's primary purpose. Highlights major decisions made. Summarizes key outcomes
3. Key Points: Maximum 5 points, clear and concise
4. Action Items: Include what needs to be done and who is responsible
5. Decisions: List all key decisions made

Important: Ensure the response is in valid JSON format.
"""

async def generate_minutes(transcript: str) -> dict:
    client = OpenAI(
        base_url=settings.MESOLITICA_API_URL,
        api_key=settings.MESOLITICA_API_KEY,
    )
    
    try:
        response = client.chat.completions.create(
            model="mallam-small",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Minutes generation error: {str(e)}")