import time
from openai import OpenAI, RateLimitError

client = OpenAI()

def llm_call(prompt):

    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            return response.choices[0].message.content

        except RateLimitError:
            print("Rate limit reached... waiting 2 seconds")
            time.sleep(2)




