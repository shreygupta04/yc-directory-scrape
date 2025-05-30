import json
import pprint

from openai import OpenAI
from pydantic import BaseModel
from typing import List
from scrape import get_links

YOUR_API_KEY = "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"
system_prompt = open("system_prompt.txt", "r").read()
user_prompt = open("user_prompt.txt", "r").read()

class Founder(BaseModel):
    name: str
    linkedin: str = None

class CompanyInfo(BaseModel):
    company_name: str
    batch: str
    description: str
    website: str
    geo: str
    founders: List[Founder]
    notes: str = None


def extract_company_information():
    links = get_links()
    companies = []
    for link in links:
        final_prompt = user_prompt.format(link=link)

        messages = [
            {
                "role": "system",
                "content": (
                    # system_prompt
                ),
            },
            {   
                "role": "user",
                "content": (
                    final_prompt
                ),
            },
        ]

        response_format = {
            "type": "json_schema",
            "json_schema": {"schema": CompanyInfo.model_json_schema()},
        }

        client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

        # chat completion without streaming
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=messages,
            response_format=response_format
        )

        result = response.to_dict()["choices"][0]["message"]["content"]
        result = json.loads(result)
        companies.append(result)
