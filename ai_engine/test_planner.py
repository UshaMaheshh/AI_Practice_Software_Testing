import json
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


def generate_test_cases(discovery):

    if not OPENAI_API_KEY:
        print("OpenAI API key not configured.")
        return []

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f'''
    Analyze this website discovery data:

    {json.dumps(discovery, indent=2)[:12000]}

    Generate functional QA test cases.

    Return ONLY valid JSON in this format:

    {{
      "test_cases": [
        {{
          "id": "TC001",
          "name": "Homepage loads",
          "priority": "High",
          "description": "Verify homepage loads correctly",
          "expected_result": "Homepage is displayed"
        }}
      ]
    }}

    Do not invent functionality that is not supported
    by the discovery data.
    '''

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional QA test planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(
        response.choices[0].message.content
    )["test_cases"]
