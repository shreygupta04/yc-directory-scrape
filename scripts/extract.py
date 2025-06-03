import json
import os
import requests

from openai import OpenAI
from pydantic import BaseModel
from bs4 import BeautifulSoup
from typing import List
from dotenv import load_dotenv

load_dotenv()

def extract_company_information(links, progress_callback=None):
    """Process HTML contents one at a time to minimize memory usage"""
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

    total = len(links)
    processed = 0
    errors = 0
    companies = []
    
    # Process one HTML content at a time
    for i, link in enumerate(links):
        try:
            # Process this single HTML content
            html_content = get_content(link) 
            final_prompt = user_prompt.format(link=html_content)
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
            companies.append(result)
            print(f"Successfully extracted info for: {result.get('company_name', 'Unknown')}")
            
        except Exception as e:
            print(f"Error processing company {i+1}: {e}")
            errors += 1
            
        finally:
            processed += 1
            if progress_callback:
                progress_callback(processed, total, errors)

    print(f"Extraction completed. Processed: {processed}, Errors: {errors}, Companies: {len(companies)}")
    return companies

def get_content(link):
    response = requests.get(link, timeout=10, allow_redirects=True)

    response.raise_for_status()  # Raises exception for 4xx/5xx status codes

    soup = BeautifulSoup(response.content, "html.parser")
    elements = soup.find('body')
    relevant_links = [link.get('href') for link in soup.find_all('a', href=True)]
    return elements.text + '\n' + '\n'.join(relevant_links)