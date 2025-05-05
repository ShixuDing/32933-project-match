import os
import json
import openai
from fastapi import HTTPException
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv('DEEPSEEK_API_KEY')
openai.api_base = os.getenv('DEEPSEEK_API_BASE', "https://api.deepseek.com/v1")

async def call_deepseek_api(messages: List[Dict[str, str]], expect_json: bool = True):
    """Calls the DeepSeek API."""
    try:
        response_format = {"type": "json_object"} if expect_json else {"type": "text"}
        response = openai.ChatCompletion.create(
            model=os.getenv('DEEPSEEK_MODEL', "deepseek-chat"),
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
            response_format=response_format
        )
        content = response.choices[0].message.content

        if expect_json:
            content_cleaned = content.strip().removeprefix('```json').removeprefix('```').removesuffix('```')
            parsed_content = json.loads(content_cleaned)
            return parsed_content
        else:
            return content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI API call failed: {str(e)}")

async def analyze_user_requirements_internal(user_input: str) -> Optional[Dict[str, Any]]:
    """Analyzes user requirements, extracts fields/keywords/features."""
    ask_keywords = ['what projects', 'which projects', 'all projects', 'show projects', 'list projects', 'view projects']
    if any(k in user_input.lower() for k in ask_keywords):
        return None

    messages = [
        {"role": "system", "content": "..."},  
        {"role": "user", "content": user_input}
    ]
    response_data = await call_deepseek_api(messages, expect_json=True)

    if not response_data or not isinstance(response_data, dict):
        return None

    if not all(k in response_data for k in ["fields", "keywords", "features"]):
        return None

    if not response_data.get("fields") and not response_data.get("keywords") and not response_data.get("features"):
        return None

    return response_data

async def rank_projects_internal(requirements: Optional[Dict[str, Any]], projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ranks projects based on user requirements."""
    if not requirements or not projects:
        return [{**p, 'score': None, 'reasoning': 'Not ranked'} for p in projects]

    messages = [
        {"role": "system", "content": "..."},  
        {"role": "user", "content": json.dumps({
            "requirements": requirements,
            "projects": projects
        }, ensure_ascii=False)}
    ]

    response_data = await call_deepseek_api(messages, expect_json=True)

    if not response_data or 'ranked_projects' not in response_data:
        return [{**p, 'score': None, 'reasoning': 'AI ranking failed'} for p in projects]

    ranked_info = {str(item['id']): item for item in response_data['ranked_projects'] if 'id' in item}

    final_ranked = []
    for p in projects:
        proj_id = str(p.get("id"))
        rank_info = ranked_info.get(proj_id, {})
        final_ranked.append({**p, "score": rank_info.get("score"), "reasoning": rank_info.get("reasoning")})

    return final_ranked
