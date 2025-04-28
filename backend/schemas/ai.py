from fastapi import APIRouter, Depends
from schemas.ai import AnalyzeRequest, AnalyzeResponse, RankRequest, RankResponse, RankedProjectOutput
from services.ai_service import analyze_user_requirements_internal, rank_projects_internal

router = APIRouter(
    prefix="/ai",
    tags=["AI Project Matching"]
)

@router.post("/analyze-requirements", response_model=AnalyzeResponse)
async def analyze_requirements(request: AnalyzeRequest):
    analysis_result = await analyze_user_requirements_internal(request.user_input)
    if analysis_result is None:
        return AnalyzeResponse(fields=[], keywords=[], features=[])
    return AnalyzeResponse(**analysis_result)

@router.post("/rank-projects", response_model=RankResponse)
async def rank_projects_endpoint(request: RankRequest):
    requirements_dict = request.requirements.model_dump() if request.requirements else None
    projects_dict_list = [p.model_dump() for p in request.projects]
    ranked_projects_list = await rank_projects_internal(requirements_dict, projects_dict_list)

    validated_ranked_projects = [
        RankedProjectOutput(**{
            "id": p.get("id"),
            "score": p.get("score"),
            "reasoning": p.get("reasoning"),
            "name": p.get("name", "Unknown"),
            "description": p.get("description"),
            "field": p.get("field")
        })
        for p in ranked_projects_list if p.get("id") is not None
    ]

    return RankResponse(ranked_projects=validated_ranked_projects)
