import json
import os
import gc

from openai import OpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

def extract_company_information_streaming(html_contents, progress_callback=None):
    """Process HTML contents one at a time to minimize memory usage"""
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
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": None},
    ]
    
    response_format = {
        "type": "json_schema",
        "json_schema": {"schema": CompanyInfo.model_json_schema()},
    }
    
    client = OpenAI(
        api_key=os.getenv('PERPLEXITY_API_KEY'), 
        base_url="https://api.perplexity.ai"
    )

    total = len(html_contents)
    processed = 0
    errors = 0
    companies = []
    
    # Process one HTML content at a time
    for i, html_content in enumerate(html_contents):
        try:
            # Process this single HTML content
            final_prompt = user_prompt.format(link=html_content)
            messages[1]["content"] = final_prompt

            response = client.chat.completions.create(
                model="sonar-pro",
                messages=messages,
                response_format=response_format
            )

            result = response.to_dict()["choices"][0]["message"]["content"]
            result = json.loads(result)
            companies.append(result)
            print(f"Successfully extracted info for: {result.get('company_name', 'Unknown')}")
            
        except Exception as e:
            print(f"Error processing company {i+1}: {e}")
            errors += 1
        finally:
            processed += 1
            if progress_callback:
                progress_callback(processed, total, errors)
            
            # Clear the processed HTML from memory
            html_contents[i] = None

            if processed % 5 == 0:
                gc.collect()

    print(f"Extraction completed. Processed: {processed}, Errors: {errors}, Companies: {len(companies)}")
    return companies