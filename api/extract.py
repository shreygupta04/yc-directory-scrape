import json
import os
import sys

from openai import OpenAI
from pydantic import BaseModel
from typing import List
from api.scrape import get_links
from dotenv import load_dotenv

load_dotenv()

def extract_company_information(links, progress_callback=None):
    base_dir = os.path.dirname(__file__)
    system_prompt_path = os.path.join(base_dir, "system_prompt.txt")
    system_prompt = open(system_prompt_path, "r").read()

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


    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {   
            "role": "user",
            "content": None
        },
    ]
    response_format = {
        "type": "json_schema",
        "json_schema": {"schema": CompanyInfo.model_json_schema()},
    }
    client = OpenAI(api_key=os.getenv('PERPLEXITY_API_KEY'), base_url="https://api.perplexity.ai")

    total = len(links)
    processed = 0
    errors = 0
    companies = []
    for link in links:
        try:
            final_prompt = user_prompt.format(link=link)
            messages[1]["content"] = final_prompt

            response = client.chat.completions.create(
                model="sonar-pro",
                messages=messages,
                response_format=response_format
            )

            result = response.to_dict()["choices"][0]["message"]["content"]
            result = json.loads(result)
            companies.append(result)
        except Exception as e:
            errors += 1
            continue
        finally:
            processed += 1
            if progress_callback:
                progress_callback(processed, total, errors)
            progress_message = {
                "processed": processed,
                "total": total,
                "errors": errors,
                "message": f"Processed {processed}/{total}"
            }
            print("PROGRESS:" + json.dumps(progress_message))
    
    print("RESULT:" + json.dumps({
        "companies": companies
    }))
    return companies