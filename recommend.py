import openai
from openai import OpenAI
import os

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
    )


def recommend(prompt):
    
    response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-3.5-turbo",
    )
    return response.choices[0].message.content.strip()