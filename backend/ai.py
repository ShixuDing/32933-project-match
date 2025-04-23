import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError, AuthenticationError, APIConnectionError, RateLimitError, APIStatusError
import uvicorn

# Load environment variables
load_dotenv()

# --- How to Run This Service ---
# 1. Ensure you have a .env file in the project root with your DEEPSEEK_API_KEY.
#    Optionally, set DEEPSEEK_API_BASE, DEEPSEEK_MODEL, and PORT in the .env file.
# 2. Make sure all dependencies from backend/requirements.txt are installed in your virtual environment.
#    (Run `pip install -r backend/requirements.txt` in the activated venv)
# 3. Run the service from the project root directory using uvicorn:
#    uvicorn backend.ai:app --reload --port 8001 
#    (Replace 8001 if you set a different PORT in .env or want to use another port)
# 4. The service will be available at http://127.0.0.1:8001 (or your specified port).
# 5. Access interactive API documentation at http://127.0.0.1:8001/docs
#
# --- Integration Notes for Other Backend Services ---
# - This service provides two main endpoints: /analyze-requirements and /rank-projects.
# - Call these endpoints using HTTP POST requests from your main backend application.
# - The typical flow is:
#   1. Main backend receives user input.
#   2. Main backend fetches relevant student background info (major, interests) from the database.
#   3. Main backend calls POST /analyze-requirements with user_input and student info.
#   4. Main backend receives structured requirements (fields, keywords, features).
#   5. Main backend fetches relevant projects from the database (including project_type, supervisor_expertise).
#   6. Main backend calls POST /rank-projects with the structured requirements and the project list.
#   7. Main backend receives the ranked list of projects and uses it for recommendations.
#
# --- OpenAI/DeepSeek Configuration ---
api_key = os.getenv('DEEPSEEK_API_KEY')
api_base_url = os.getenv('DEEPSEEK_API_BASE', "https://api.deepseek.com/v1")

if not api_key:
    print("Warning: DEEPSEEK_API_KEY environment variable not set!")

# Create the AsyncOpenAI client instance
client = AsyncOpenAI(
    api_key=api_key,
    base_url=api_base_url
)

# --- FastAPI Application Instance ---
app = FastAPI(
    title="Project Matching AI Service",
    description="Provides user requirement analysis and project ranking features based on DeepSeek.",
    version="1.0.0"
)

# --- Pydantic Model Definitions ---

class AnalyzeStudentRequest(BaseModel):
    user_input: str = Field(..., description="User's current requirement text", example="I want a project that uses machine learning.")
    # Optional student background info
    student_major: Optional[str] = Field(None, description="Student's major", example="Computer Science")
    student_interests: Optional[str] = Field(None, description="Student's profile interest/research topic text", example="Interested in natural language processing and large language models.")
    student_faculty: Optional[str] = Field(None, description="Student's faculty", example="Faculty of Engineering")

class AnalyzeResponse(BaseModel):
    fields: Optional[List[str]] = Field(None, description="List of matched project fields", example=["Artificial Intelligence", "NLP"])
    keywords: Optional[List[str]] = Field(None, description="Extracted technical keywords", example=["Machine Learning", "LLM"])
    features: Optional[List[str]] = Field(None, description="Specific project features mentioned by the user", example=["Needs data analysis"])

class ProjectInput(BaseModel):
    id: Any = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    field: Optional[str] = Field(None, description="General field the project belongs to (can be broad)")
    project_type: Optional[str] = Field(None, description="Specific type or category of the project", example="Web Application")
    # Added: List of expertise areas from associated supervisor(s)
    supervisor_expertise: Optional[List[str]] = Field(None, description="List of expertise areas of the supervisor(s)", example=["Machine Learning", "Deep Learning"])

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
    """Asynchronously calls the DeepSeek API for conversation using the new client style."""
    try:
        if not client.api_key:
            print("Error: API Key not configured in the client!")
            raise HTTPException(status_code=500, detail="AI service API Key not configured properly")

        print("\n" + "="*50)
        print("Starting DeepSeek API call (v1.0+ style)")
        print(f"Request Messages: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        print(f"API Base URL used by client: {client.base_url}")
        print(f"Expect JSON: {expect_json}")
        print("-"*50)

        response_format_param = {"type": "json_object"} if expect_json else {"type": "text"}

        # Using the client instance for the API call
        response = await client.chat.completions.create(
            model=os.getenv('DEEPSEEK_MODEL', "deepseek-chat"),
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
            response_format=response_format_param
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
                raise HTTPException(status_code=500, detail=f"AI service returned invalid JSON format: {content}")
        else:
            return content

    # Updated exception handling for OpenAI v1.0+
    except AuthenticationError as e:
        print(f"DeepSeek API Authentication Error: {e.status_code} - {e.response} - {e.message}")
        raise HTTPException(status_code=e.status_code or 401, detail=f"DeepSeek API Authentication Failed: {e.message}")
    except APIConnectionError as e:
        print(f"DeepSeek API Connection Error: {e}")
        raise HTTPException(status_code=503, detail="Could not connect to DeepSeek API.")
    except RateLimitError as e:
        print(f"DeepSeek API Rate Limit Exceeded: {e.status_code} - {e.response} - {e.message}")
        raise HTTPException(status_code=e.status_code or 429, detail="Rate limit exceeded for DeepSeek API.")
    except APIStatusError as e: # Catch other API errors (like 4xx, 5xx)
        print(f"DeepSeek API Status Error: {e.status_code} - {e.response} - {e.message}")
        raise HTTPException(status_code=e.status_code or 500, detail=f"DeepSeek API returned an error: {e.message}")
    except OpenAIError as e: # Catch any other OpenAI specific errors
        print(f"OpenAI Library Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred within the OpenAI library: {type(e).__name__}")
    except Exception as e:
        print(f"Unknown error during DeepSeek API call: {str(e)}")
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=f"Internal error processing AI request: {str(e)}")


async def analyze_user_requirements_internal(request_data: AnalyzeStudentRequest) -> Optional[Dict[str, Any]]:
    """Analyzes user requirements, considering student background, extracts keywords and fields (internal implementation)."""
    user_input = request_data.user_input
    print(f"\nStarting user requirement analysis for: {user_input}")
    print(f"Student Background: Major={request_data.student_major}, Interests='{request_data.student_interests}', Faculty={request_data.student_faculty}")

    # Simple keyword check to see if the user is just asking for a list of projects
    ask_keywords = ['what projects', 'which projects', 'all projects', 'show projects', 'list projects', 'view projects']
    normalized_input = user_input.lower()
    if any(keyword in normalized_input for keyword in ask_keywords):
        print("User might be asking for all projects, returning None (indicating no specific requirements extracted)")
        return None # Return None to indicate no specific requirements were extracted

    # Construct the system prompt incorporating background info
    system_prompt = f"""#### Role
- Assistant Name: Project Requirement Analysis Expert
- Primary Task: Analyze student project requirements, extract key information, and match to potential project fields, considering the student's background.

#### Student Background Context (Use this for better understanding)
- Major: {request_data.student_major or 'Not Provided'}
- Stated Interests: {request_data.student_interests or 'Not Provided'}
- Faculty: {request_data.student_faculty or 'Not Provided'}

#### Capabilities
- Requirement Analysis: Accurately understand project interests and needs expressed in the `user_input`, using the student background for context.
- Field Matching: Precisely match requirements to potential project fields (if possible).
- Keyword Extraction: Identify technical keywords within the requirements (from input and background).
- Feature Summarization: Extract explicitly stated project feature requirements from the `user_input`.

#### Reference Project Fields (for reference only; prioritize matching user's text)
  - Healthcare
  - Blockchain
  - Artificial Intelligence
  - Internet of Things (IoT)
  - Big Data
  - Cloud Computing
  - Cybersecurity
  - Web Development
  - Mobile Development
  - Data Science
  - NLP
  - Computer Vision

#### Output Format
Must output valid JSON format. If specific requirements are analyzed, use the following format:
{{
    "fields": ["Field1"],  // Array, 1-2 most relevant fields inferred from input and background
    "keywords": ["Keyword1", "Keyword2"],  // Array, max 3-4 technical keywords from input and background
    "features": ["Feature1"]  // Array, explicitly mentioned feature requirements from user_input
}}
If the user input cannot be analyzed for specific requirements, or is just small talk/greeting, output:
{{
    "fields": [],
    "keywords": [],
    "features": []
}}

#### Matching Rules
1. Use student background to interpret the `user_input` more accurately.
2. Fields: Infer 1-2 relevant fields based on combined info. Reference list is a guide.
3. Keywords: Extract core technical terms from both `user_input` and relevant parts of `Stated Interests`.
4. Features: ONLY extract features explicitly mentioned in the current `user_input`.
5. Brevity: Include only the most core requirement information.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_input # Only send the current user input here
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

    # Prepare project information, including new fields
    projects_for_api = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "description": p.get("description", ""),
            "field": p.get("field", ""), # Keep general field if available
            "project_type": p.get("project_type", ""), # Add project type
            "supervisor_expertise": p.get("supervisor_expertise", []) # Add supervisor expertise
        } for p in projects
    ]


    messages = [
        {
            "role": "system",
            "content": """#### Role
- Assistant Name: Advanced Project Matching Expert
- Primary Task: Score and rank the provided list of projects based on detailed student requirements and comprehensive project information.

#### Capabilities
- Requirement Understanding: Precisely understand student's field interests, technical keywords, and specific project features.
- Project Analysis: Analyze each project's name, description, general field, specific `project_type`, and the `supervisor_expertise`.
- Relevance Scoring: Calculate the matching degree of each project to the student's requirements, providing a score from 0 to 10.
- Ranking: Sort projects based on their scores in descending order.

#### Scoring Rules (Total 10 points) - Apply holistically
1.  **Field/Type Match (0-4 points)**:
    *   Evaluate how well the student's required `fields` match the project's `field` AND `project_type`.
    *   Exact match on specific `project_type` gets high score (e.g., 4 pts).
    *   Match on general `field` or related `project_type` gets moderate score (e.g., 2-3 pts).
    *   Consider semantic similarity (e.g., 'AI' requirement vs 'Machine Learning' project type).
2.  **Keyword Match (0-3 points)**:
    *   Score based on how many required `keywords` are found in the project's `description` OR `supervisor_expertise`.
    *   Explicit mention scores higher than related concepts.
3.  **Supervisor Expertise Match (0-2 points)**:
    *   Award points if the project's `supervisor_expertise` strongly aligns with the student's required `fields` or `keywords`.
    *   This reflects the value of expert guidance in the student's area of interest.
4.  **Feature Match (0-1 point)**:
    *   Award points ONLY if the project explicitly meets specific `features` mentioned in the student's requirements (e.g., 'must use Python', 'needs database').

#### Important Instructions
- **Must** score and rank **every** project in the provided list.
- **Must** output valid JSON format.
- **Must** include `id`, `score`, and `reasoning` fields for each project. `reasoning` should be concise and justify the score based on the rules above (mention which aspects matched well or poorly).

#### Output Format
Must output a valid JSON object with a root key "ranked_projects". The value should be a list containing ALL input projects, each with id, score, and reasoning.
```json
{
    "ranked_projects": [
        {
            "id": "proj_abc",
            "score": 9.5,
            "reasoning": "Excellent match: Project type 'AI/ML' aligns perfectly (4pts). Keywords 'NLP', 'Python' found in description (2pts). Supervisor expertise in 'NLP' is a strong match (2pts). Feature 'needs dataset' met (1pt). Slight bonus for description clarity (0.5pts)."
        },
        {
            "id": "proj_def",
            "score": 6.0,
            "reasoning": "Good match: Related field 'Web Dev' (2pts). Keyword 'JavaScript' found (1pt). Supervisor expertise is less relevant (0.5pts). No specific features requested. Project description is clear (1pt)."
        },
        // ... include scores for all other projects ...
        {
            "id": "proj_xyz",
            "score": 2.0,
            "reasoning": "Poor match: Field 'Blockchain' doesn't align (0pts). No keywords match (0pts). Supervisor expertise not relevant (0pts). Basic score for being a project (2pts)."
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

# --- Endpoint: /analyze-requirements --- 
# Purpose: 
#   Analyzes a student's natural language input, optionally considering their 
#   background information (major, interests, faculty), to extract structured 
#   project requirements (relevant fields, technical keywords, specific features).
# Method: POST
# URL: /analyze-requirements (e.g., http://127.0.0.1:8001/analyze-requirements)
# Request Body (JSON): 
#   - Requires an object matching the AnalyzeStudentRequest model.
#   - `user_input` (string, required): The student's current text input describing their desired project.
#   - `student_major` (string, optional): The student's major (e.g., "Computer Science").
#   - `student_interests` (string, optional): Text describing the student's existing interests (from profile).
#   - `student_faculty` (string, optional): The student's faculty.
#   Example Request Body:
#   {
#     "user_input": "I want to work with large language models for text generation.",
#     "student_major": "Artificial Intelligence",
#     "student_interests": "Previously worked on chatbots and NLP tasks.",
#     "student_faculty": "School of Informatics"
#   }
# Response Body (JSON on success - 200 OK):
#   - Returns an object matching the AnalyzeResponse model.
#   - `fields` (array[string], optional): List of 1-2 inferred relevant project fields.
#   - `keywords` (array[string], optional): List of 3-4 extracted technical keywords.
#   - `features` (array[string], optional): List of specific features explicitly mentioned in the user_input.
#   - Note: If no specific requirements are found, returns empty lists, e.g., {"fields": [], "keywords": [], "features": []}
#   Example Response Body:
#   {
#     "fields": ["Artificial Intelligence", "NLP"],
#     "keywords": ["LLM", "Text Generation", "Chatbot"],
#     "features": []
#   }
# Example curl:
# curl -X POST "http://127.0.0.1:8001/analyze-requirements" \
# -H "Content-Type: application/json" \
# -d '{"user_input": "I want to work with large language models for text generation.", "student_major": "Artificial Intelligence", "student_interests": "Previously worked on chatbots and NLP tasks."}'
@app.post("/analyze-requirements", response_model=AnalyzeResponse, summary="Analyze user requirement text considering student background")
async def analyze_requirements(request: AnalyzeStudentRequest):
    """
    Receives user input text and calls the AI to analyze and extract key project requirement information, considering student background.

    - **user_input**: Natural language text describing the user's project requirements.
    - **student_major**: Student's major.
    - **student_interests**: Student's profile interest/research topic text.
    - **student_faculty**: Student's faculty.

    Returns the structured requirements including fields, keywords, and features.
    If the input doesn't contain specific requirements (e.g., greeting or asking for all projects),
    it will return a response with empty lists.
    """
    analysis_result = await analyze_user_requirements_internal(request)

    # If analysis_result is None (indicating no specific requirements or analysis failure),
    # return a default response with empty lists.
    if analysis_result is None:
        return AnalyzeResponse(fields=[], keywords=[], features=[])

    # Otherwise, populate the response model with the analysis result.
    return AnalyzeResponse(**analysis_result)


# --- Endpoint: /rank-projects ---
# Purpose:
#   Scores and ranks a provided list of projects based on structured student 
#   requirements (output from /analyze-requirements) and detailed project info.
# Method: POST
# URL: /rank-projects (e.g., http://127.0.0.1:8001/rank-projects)
# Request Body (JSON):
#   - Requires an object matching the RankRequest model.
#   - `requirements` (object, optional): The structured requirements object obtained from 
#     /analyze-requirements. If null or omitted, projects might be returned unranked or 
#     based on general relevance without specific scoring.
#     - Contains `fields` (array[string]), `keywords` (array[string]), `features` (array[string]).
#   - `projects` (array[object], required): A list of project objects to be ranked.
#     Each project object should match the ProjectInput model:
#     - `id` (any, required): Unique project identifier.
#     - `name` (string, required): Project name.
#     - `description` (string, optional): Project description.
#     - `field` (string, optional): General project field.
#     - `project_type` (string, optional): Specific project category/type.
#     - `supervisor_expertise` (array[string], optional): List of expertise areas for the project's supervisor(s).
#   Example Request Body:
#   {
#     "requirements": {"fields": ["AI", "NLP"], "keywords": ["Python", "Chatbot"], "features": []},
#     "projects": [
#       {"id": 1, "name": "Customer Service Chatbot", "description": "NLP based chatbot in Python", "field": "AI", "project_type": "AI/ML Application", "supervisor_expertise": ["Natural Language Processing", "Python"]},
#       {"id": 2, "name": "Sales Data Dashboard", "description": "Visualize sales data using React", "field": "Web Development", "project_type": "Web Application", "supervisor_expertise": ["Frontend Development", "React"]}
#     ]
#   }
# Response Body (JSON on success - 200 OK):
#   - Returns an object matching the RankResponse model.
#   - `ranked_projects` (array[object], required): A list of project objects, sorted by relevance score (descending).
#     Each project object matches the RankedProjectOutput model:
#     - `id` (any, required): Unique project identifier.
#     - `score` (float, optional): The calculated relevance score (0-10). Null if ranking failed or requirements were null.
#     - `reasoning` (string, optional): A brief explanation of how the score was derived.
#     - `name`, `description`, `field`, `project_type`, `supervisor_expertise`: Original project details passed in the request.
#   Example Response Body:
#   {
#     "ranked_projects": [
#       {
#         "id": 1,
#         "score": 9.5,
#         "reasoning": "Excellent match: Project type 'AI/ML Application' aligns (4pts). Keywords 'Python', 'Chatbot' found (2pts). Supervisor expertise 'NLP', 'Python' relevant (2pts). No specific features matched (0pts). Clear description (1.5pts).",
#         "name": "Customer Service Chatbot",
#         "description": "NLP based chatbot in Python",
#         "field": "AI",
#         "project_type": "AI/ML Application",
#         "supervisor_expertise": ["Natural Language Processing", "Python"]
#       },
#       {
#         "id": 2,
#         "score": 3.0,
#         "reasoning": "Poor match: Field/Type 'Web Application' doesn't align with 'AI/NLP' (0.5pts). No keywords match (0pts). Supervisor expertise not relevant (0pts). Clear description (1pt).",
#         "name": "Sales Data Dashboard",
#         "description": "Visualize sales data using React",
#         "field": "Web Development",
#         "project_type": "Web Application",
#         "supervisor_expertise": ["Frontend Development", "React"]
#       }
#     ]
#   }
# Example curl:
# curl -X POST "http://127.0.0.1:8001/rank-projects" \
# -H "Content-Type: application/json" \
# -d '{"requirements": {"fields": ["AI", "NLP"], "keywords": ["Python", "Chatbot"], "features": []}, "projects": [{"id": 1, "name": "Customer Service Chatbot", "description": "NLP based chatbot in Python", "field": "AI", "project_type": "AI/ML Application", "supervisor_expertise": ["Natural Language Processing", "Python"]}, {"id": 2, "name": "Sales Data Dashboard", "description": "Visualize sales data using React", "field": "Web Development", "project_type": "Web Application", "supervisor_expertise": ["Frontend Development", "React"]}]}'
@app.post("/rank-projects", response_model=RankResponse, summary="Rank a list of projects based on requirements")
async def rank_projects_endpoint(request: RankRequest):
    """
    Receives structured user requirements and a list of projects, then calls the AI
    to score and rank the projects based on relevance.

    - **requirements**: (Optional) Structured representation of user needs (from /analyze-requirements).
                      If null or empty, projects might be returned unranked or based on general AI understanding.
    - **projects**: List of projects to be ranked. Each project should include id, name, description, field, project_type, and supervisor_expertise.

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
            "field": proj_data.get("field"),
            "project_type": proj_data.get("project_type"),
            "supervisor_expertise": proj_data.get("supervisor_expertise", [])
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
