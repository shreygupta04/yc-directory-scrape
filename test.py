import requests
from bs4 import BeautifulSoup
import json
import os
import gc

from openai import OpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

response = requests.get("https://www.ycombinator.com/companies/probo", timeout=10, allow_redirects=True)

response.raise_for_status()  # Raises exception for 4xx/5xx status codes

soup = BeautifulSoup(response.content, "html.parser")
elements = soup.find('body')
relevant_links = [link.get('href') for link in soup.find_all('a', href=True)]
output = elements.text + '\n' + '\n'.join(relevant_links)

base_dir = os.path.dirname(__file__)
user_prompt_path = os.path.join(base_dir, "user_prompt.txt")
user_prompt = open(user_prompt_path, "r").read()

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


client = OpenAI()

final_prompt = user_prompt.format(link=output)
response = client.chat.completions.create(
    model="gpt-4o-mini-2024-07-18",
    messages=[
        {
            "role": "user",
            "content": final_prompt
        }
    ],
    response_format={ "type": "json_object" }
)


result = response.to_dict()["choices"][0]["message"]["content"]
result = json.loads(result)
print(result)