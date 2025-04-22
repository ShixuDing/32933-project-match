import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import openai
import uvicorn

# Load environment variables
load_dotenv()

# --- OpenAI/DeepSeek Configuration ---
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print("Warning: DEEPSEEK_API_KEY environment variable not set!")
openai.api_key = api_key
openai.api_base = os.getenv('DEEPSEEK_API_BASE', "https://api.deepseek.com/v1")

# --- FastAPI Application Instance ---
app = FastAPI(
    title="Project Matching AI Service",
    description="Provides user requirement analysis and project ranking features based on DeepSeek.",
    version="1.0.0"
)

# --- Pydantic Model Definitions ---

class AnalyzeRequest(BaseModel):
    user_input: str = Field(..., description="User's original requirement text", example="I want an AI project related to healthcare.")

class AnalyzeResponse(BaseModel):
    fields: Optional[List[str]] = Field(None, description="List of matched project fields", example=["Artificial Intelligence", "Healthcare"])
    keywords: Optional[List[str]] = Field(None, description="Extracted technical keywords", example=["Machine Learning", "Image Recognition"])
    features: Optional[List[str]] = Field(None, description="Specific project features mentioned by the user", example=["Needs a deep learning model"])

class ProjectInput(BaseModel):
    id: Any = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    field: Optional[str] = Field(None, description="Field the project belongs to")
    # Add more project attributes as needed

class RequirementsInput(BaseModel):
    fields: Optional[List[str]] = Field(None, description="Fields from user requirements")
    keywords: Optional[List[str]] = Field(None, description="Keywords from user requirements")
    features: Optional[List[str]] = Field(None, description="Features from user requirements")

class RankRequest(BaseModel):
    requirements: Optional[RequirementsInput] = Field(None, description="Structured user requirements (null if not sorting by specific needs)")
    projects: List[ProjectInput] = Field(..., description="List of projects to be ranked")

class RankedProjectOutput(BaseModel):
    id: Any = Field(..., description="Unique identifier for the project")
    score: Optional[float] = Field(None, description="Matching score (null if no scoring performed)")
    reasoning: Optional[str] = Field(None, description="Reasoning for the score (null if no scoring performed)")
    # Include original project info or just ID and score
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    field: Optional[str] = Field(None, description="Field the project belongs to")


class RankResponse(BaseModel):
    ranked_projects: List[RankedProjectOutput] = Field(..., description="List of ranked projects")


# --- Core AI Logic Functions ---

async def call_deepseek_api(messages: List[Dict[str, str]], expect_json: bool = True):
    """Asynchronously calls the DeepSeek API for conversation."""
    try:
        if not openai.api_key:
            print("Error: API Key not configured!")
            raise HTTPException(status_code=500, detail="AI service API Key not configured properly")

        print("\n" + "="*50)
        print("Starting DeepSeek API call")
        print(f"Request Messages: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        print(f"API Base: {openai.api_base}")
        print(f"Expect JSON: {expect_json}")
        print("-"*50)

        # Note: Asynchronous calls with the openai library might require `async openai` or `httpx`.
        # For simplicity, synchronous calls are kept here, but async is recommended in FastAPI.
        # If performance issues arise, switch to an async HTTP client library (e.g., httpx or aiohttp).

        response_format = {"type": "json_object"} if expect_json else {"type": "text"}

        # Using openai.ChatCompletion.create (consider migrating to newer client methods if available)
        response = openai.ChatCompletion.create(
            model=os.getenv('DEEPSEEK_MODEL', "deepseek-chat"),
            messages=messages,
            temperature=0.3,
            max_tokens=1500, # Increased token limit for potentially long project lists
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
            response_format=response_format
        )
        content = response.choices[0].message.content
        print(f"API Raw Response Content: {content}")
        print("="*50 + "\n")

        if expect_json:
            try:
                # Attempt to clean potential Markdown code block markers
                content_cleaned = content.strip().removeprefix('```json').removeprefix('```').removesuffix('```')
                parsed_content = json.loads(content_cleaned)
                print(f"Parsed JSON: {json.dumps(parsed_content, ensure_ascii=False, indent=2)}")
                return parsed_content
            except json.JSONDecodeError as json_e:
                print(f"API Response JSON parsing error: {str(json_e)}")
                print(f"Original response: {content}")
                # Could implement more robust parsing or raise the error
                raise HTTPException(status_code=500, detail=f"AI service returned invalid JSON format: {content}")
        else:
            return content

    except openai.error.AuthenticationError as e:
        print(f"API Authentication Error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"DeepSeek API Authentication Failed: {str(e)}")
    except openai.error.OpenAIError as e: # Catch more general OpenAI errors
        print(f"API Call Error: {str(e)}")
        print("="*50 + "\n")
        raise HTTPException(status_code=503, detail=f"Error calling DeepSeek API: {str(e)}")
    except Exception as e:
        print(f"Unknown error during DeepSeek API call: {str(e)}")
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=f"Internal error processing AI request: {str(e)}")


async def analyze_user_requirements_internal(user_input: str) -> Optional[Dict[str, Any]]:
    """Analyzes user requirements, extracts keywords and fields (internal implementation)."""
    print(f"\nStarting user requirement analysis for: {user_input}")

    # Simple keyword check to see if the user is just asking for a list of projects
    ask_keywords = ['what projects', 'which projects', 'all projects', 'show projects', 'list projects', 'view projects']
    normalized_input = user_input.lower()
    if any(keyword in normalized_input for keyword in ask_keywords):
        print("User might be asking for all projects, returning None (indicating no specific requirements extracted)")
        return None # Return None to indicate no specific requirements were extracted

    messages = [
        {
            "role": "system",
            "content": """#### Role
- Assistant Name: Project Requirement Analysis Expert
- Primary Task: Analyze student project requirements, extract key information, and match to predefined project fields.

#### Capabilities
- Requirement Analysis: Accurately understand project interests and needs expressed by students.
- Field Matching: Precisely match requirements to predefined project fields (if possible).
- Keyword Extraction: Identify technical keywords within the requirements.
- Feature Summarization: Extract explicitly stated project feature requirements.

#### Reference Project Fields (for reference only; prioritize matching user's text)
  - Healthcare
  - Blockchain
  - Artificial Intelligence
  - Internet of Things (IoT)
  - Big Data
  - Cloud Computing
  - Cybersecurity

#### Output Format
Must output valid JSON format. If specific requirements are analyzed, use the following format:
{
    "fields": ["Field1"],  // Array, 1-2 most relevant fields (if clearly inferable)
    "keywords": ["Keyword1", "Keyword2"],  // Array, max 3 technical keywords
    "features": ["Feature1"]  // Array, explicitly mentioned feature requirements
}
If the user input cannot be analyzed for specific requirements, or is just small talk/greeting, output:
{
    "fields": [],
    "keywords": [],
    "features": []
}

#### Matching Rules
1. Fields: Try to extract or infer from user text, referencing the list above. Leave empty if uncertain.
2. Keywords: Prioritize technical terms.
3. Features: Only extract requirements explicitly stated by the user (e.g., specific tech stack, functionality).
4. Brevity: Include only the most core requirement information."""
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    print("Calling DeepSeek API for requirement analysis...")
    response_data = await call_deepseek_api(messages, expect_json=True)

    if not response_data or not isinstance(response_data, dict):
         print("Requirement analysis API call failed or returned incorrect format, returning None")
         return None # Or return a specific structure indicating failure

    # Basic validation: ensure it's a dict and has expected keys (values can be empty lists)
    if not all(k in response_data for k in ["fields", "keywords", "features"]):
        print(f"Requirement analysis result missing necessary fields: {response_data}")
        return None # Treat as invalid

    # If all fields are empty, also consider it as no effective requirements extracted
    if not response_data.get("fields") and not response_data.get("keywords") and not response_data.get("features"):
        print("Requirement analysis resulted in empty fields, keywords, and features, returning None")
        return None

    print(f"Requirement analysis result: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
    return response_data


async def rank_projects_internal(requirements: Optional[Dict[str, Any]], projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ranks projects based on user requirements (internal implementation)."""
    print(f"\nStarting project ranking...")
    print(f"User Requirements: {json.dumps(requirements, ensure_ascii=False) if requirements else 'No specific requirements'}")
    # Print only partial project info to avoid excessive logging
    print(f"Number of projects to rank: {len(projects)}")
    print(f"Sample projects (first 3): {[{'id': p.get('id'), 'name': p.get('name'), 'field': p.get('field')} for p in projects[:3]]}")

    # If no valid requirements are provided, or the project list is empty, return the original list (unranked)
    if not requirements or not projects:
        print("No specific requirements or empty project list, returning all projects in original order.")
        # Add null score and reasoning to each project
        return [{**p, 'score': None, 'reasoning': 'Not ranked due to missing requirements or empty list'} for p in projects]

    # Prepare project information, including only necessary fields to reduce token usage
    projects_for_api = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "description": p.get("description", ""), # Provide empty string if None
            "field": p.get("field", "")
        } for p in projects
    ]


    messages = [
        {
            "role": "system",
            "content": """#### Role
- Assistant Name: Project Matching Expert
- Primary Task: Score and rank the provided list of projects based on student requirements.

#### Capabilities
- Requirement Understanding: Precisely understand student's field interests, technical keywords, and specific project features.
- Project Analysis: Analyze each project's name, description, and field information.
- Relevance Scoring: Calculate the matching degree of each project to the student's requirements, providing a score from 0 to 10.
- Ranking: Sort projects based on their scores in descending order.

#### Scoring Rules (Total 10 points)
1.  **Field Match (0-4 points)**:
    *   Requirement field exactly matches project field: 4 pts
    *   Requirement field highly relevant to project field (e.g., AI vs Machine Learning): 3 pts
    *   Requirement field somewhat related (e.g., Big Data vs Data Visualization): 2 pts
    *   No field specified in requirement, but project field relates to keywords/features: 1 pt
    *   Completely unrelated: 0 pts
2.  **Keyword Match (0-4 points)**:
    *   Each core technical keyword from requirements explicitly found in project name/description: +1 pt/keyword (max 4 pts)
    *   Related concepts of keywords reflected: +0.5 pts/keyword
3.  **Feature Match (0-2 points)**:
    *   Project explicitly meets feature requirements stated by the user (e.g., specific tech, function): +1 pt/feature (max 2 pts)

#### Important Instructions
- **Must** score and rank **every** project in the provided list.
- **Must** output valid JSON format.
- **Must** include `id`, `score`, and `reasoning` fields for each project. `reasoning` should briefly explain the score.

#### Output Format
Must output a valid JSON object with a root key "ranked_projects". The value should be a list containing ALL input projects, each with id, score, and reasoning.
```json
{
    "ranked_projects": [
        {
            "id": "proj_abc",
            "score": 9.5,
            "reasoning": "Field match (4pts), keywords 'AI' & 'image recognition' match (2pts), feature 'deep learning' met (2pts), bonus (1.5pts)."
        },
        {
            "id": "proj_def",
            "score": 7.0,
            "reasoning": "Related field (3pts), keyword 'Web dev' match (1pt), features partially met (1pt), overall (2pts)."
        },
        // ... include scores for all other projects ...
        {
            "id": "proj_xyz",
            "score": 3.0,
            "reasoning": "No field match (0pts), no keyword match (0pts), no feature match (0pts), base score (3pts)."
        }
    ]
}
```"""
        },
        {
            "role": "user",
            "content": f"""Please score (0-10) and rank the following project list based on the student requirements provided.

Student Requirements:
{json.dumps(requirements, ensure_ascii=False, indent=2)}

Project List:
{json.dumps(projects_for_api, ensure_ascii=False, indent=2)}"""
        }
    ]

    print("Calling DeepSeek API for project matching and ranking...")
    response_data = await call_deepseek_api(messages, expect_json=True)

    if not response_data or 'ranked_projects' not in response_data or not isinstance(response_data.get('ranked_projects'), list):
        print("Project ranking API call failed or returned incorrect format. Returning projects in original order.")
        return [{**p, 'score': None, 'reasoning': 'AI ranking failed or returned invalid format'} for p in projects] # Return original list, mark failure

    try:
        # Create a dictionary for quick lookup of score and reasoning by ID
        ranked_info = {str(item['id']): {'score': item.get('score'), 'reasoning': item.get('reasoning')}
                       for item in response_data['ranked_projects'] if 'id' in item}

        # Reconstruct the project list based on the AI's ranking and scores
        final_ranked_projects = []
        original_projects_dict = {str(p['id']): p for p in projects} # Use string IDs for consistency

        # Add projects in the order returned by the AI
        seen_ids = set()
        for item in response_data['ranked_projects']:
            project_id_str = str(item.get('id')) # Use string ID
            if project_id_str in original_projects_dict:
                original_project = original_projects_dict[project_id_str]
                # Get score/reasoning, provide defaults if missing in AI response
                score_info = ranked_info.get(project_id_str, {'score': None, 'reasoning': 'Score not returned by AI'})
                # Merge original project data with scoring info
                final_ranked_projects.append({**original_project, **score_info})
                seen_ids.add(project_id_str)
            # else: # Log if AI returns an ID not in the original list (optional)
            #     print(f"Warning: AI returned rank for unknown project ID {project_id_str}")

        # Add any projects potentially missed by the AI (shouldn't happen based on prompt, but as a safeguard)
        for project_id_str, original_project in original_projects_dict.items():
            if project_id_str not in seen_ids:
                 print(f"Warning: Project ID {project_id_str} was not found in AI ranking results. Appending to the end.")
                 final_ranked_projects.append({**original_project, 'score': 0, 'reasoning': 'Not ranked by AI'})

        print(f"Project ranking complete. Returning {len(final_ranked_projects)} projects.")
        # Print sample of ranked projects with scores
        print(f"Sample ranked projects (first 3): {[{'id': p.get('id'), 'name': p.get('name'), 'score': p.get('score')} for p in final_ranked_projects[:3]]}")

        return final_ranked_projects

    except Exception as e:
        print(f"Error processing project ranking results: {str(e)}")
        print(f"API Raw Response causing error: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        # Return original list but mark the error
        return [{**p, 'score': None, 'reasoning': f'Error processing ranking results: {str(e)}'} for p in projects]

# --- API Endpoints ---

# Example usage comment:
# To call this endpoint, send a POST request to /analyze-requirements
# with a JSON body like: {"user_input": "I need a project about big data analysis"}
# Example curl command:
# curl -X POST "http://127.0.0.1:8001/analyze-requirements" \
# -H "Content-Type: application/json" \
# -d '{"user_input": "I am interested in web security and blockchain projects"}'
@app.post("/analyze-requirements", response_model=AnalyzeResponse, summary="Analyze user requirement text")
async def analyze_requirements(request: AnalyzeRequest):
    """
    Receives user input text and calls the AI to analyze and extract key project requirement information.

    - **user_input**: Natural language text describing the user's project requirements.

    Returns the structured requirements including fields, keywords, and features.
    If the input doesn't contain specific requirements (e.g., greeting or asking for all projects),
    it will return a response with empty lists.
    """
    analysis_result = await analyze_user_requirements_internal(request.user_input)

    # If analysis_result is None (indicating no specific requirements or analysis failure),
    # return a default response with empty lists.
    if analysis_result is None:
        return AnalyzeResponse(fields=[], keywords=[], features=[])

    # Otherwise, populate the response model with the analysis result.
    return AnalyzeResponse(**analysis_result)


# Example usage comment:
# To call this endpoint, send a POST request to /rank-projects
# with a JSON body containing 'requirements' (output from /analyze-requirements, can be null)
# and a 'projects' list (fetched from your database).
# Example curl command:
# curl -X POST "http://127.0.0.1:8001/rank-projects" \
# -H "Content-Type: application/json" \
# -d '{ 
#       "requirements": {"fields": ["AI"], "keywords": ["NLP"], "features": []}, 
#       "projects": [ 
#         {"id": 1, "name": "Chatbot", "description": "NLP based chatbot", "field": "AI"}, 
#         {"id": 2, "name": "Data Viz", "description": "Visualize sales data", "field": "Big Data"} 
#       ]
#     }'
# Example with null requirements (returns projects, potentially unranked or default ranked):
# curl -X POST "http://127.0.0.1:8001/rank-projects" \
# -H "Content-Type: application/json" \
# -d '{ 
#       "requirements": null, 
#       "projects": [ 
#         {"id": 1, "name": "Chatbot", "description": "NLP based chatbot", "field": "AI"}, 
#         {"id": 2, "name": "Data Viz", "description": "Visualize sales data", "field": "Big Data"} 
#       ]
#     }'
@app.post("/rank-projects", response_model=RankResponse, summary="Rank a list of projects based on requirements")
async def rank_projects_endpoint(request: RankRequest):
    """
    Receives structured user requirements and a list of projects, then calls the AI
    to score and rank the projects based on relevance.

    - **requirements**: (Optional) Structured representation of user needs (from /analyze-requirements).
                      If null or empty, projects might be returned unranked or based on general AI understanding.
    - **projects**: List of projects to be ranked. Each project should include id, name, description, field, etc.

    Returns the ranked list of projects, each including its ID, match score, and scoring reasoning.
    """
    # Convert Pydantic models to dictionaries for internal function calls
    projects_dict_list = [p.model_dump() for p in request.projects]
    requirements_dict = request.requirements.model_dump() if request.requirements else None

    ranked_projects_list = await rank_projects_internal(requirements_dict, projects_dict_list)

    # Convert the list of dictionaries returned by the internal function
    # back to a list of Pydantic models for the response.
    validated_ranked_projects = []
    for proj_data in ranked_projects_list:
        # Ensure all required fields for the output model exist, or provide defaults
        # Use .get() for safety, especially for optional fields like score/reasoning
        validated_data = {
            "id": proj_data.get("id"),
            "score": proj_data.get("score"),
            "reasoning": proj_data.get("reasoning"),
            "name": proj_data.get("name", "Unknown Project"), # Default name if missing
            "description": proj_data.get("description"),
            "field": proj_data.get("field")
        }
        # Add stricter validation here if needed (e.g., check score range)
        if validated_data["id"] is not None: # Ensure ID exists before adding
             validated_ranked_projects.append(RankedProjectOutput(**validated_data))
        else:
            print(f"Warning: Removing project from ranked results due to missing ID: {proj_data}")

    return RankResponse(ranked_projects=validated_ranked_projects)

# --- Running the FastAPI Application ---
# You can run this service using: uvicorn backend.ai:app --reload --port 8001
if __name__ == "__main__":
    # Get port from environment variable or default to 8001
    port = int(os.getenv("PORT", 8001))
    print(f"Starting AI service on http://127.0.0.1:{port}")
    # Note: In production, using Gunicorn + Uvicorn workers is recommended.
    uvicorn.run("backend.ai:app", host="127.0.0.1", port=port, log_level="info", reload=True)

# --- requirements.txt Notes ---
# To run this file, ensure the following dependencies are installed:
# pip install fastapi "uvicorn[standard]" python-dotenv openai pydantic
