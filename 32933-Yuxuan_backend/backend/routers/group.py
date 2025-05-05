from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.group import GroupCreate, GroupJoin, GroupApplyProject
from crud.group import create_group, join_group, quit_group, get_group_members, apply_project
from dependencies import get_db
from dependencies.auth import get_current_user

router = APIRouter(
    prefix="/student/groups",
    tags=["Student Groups"]
)

@router.post("/create")
def form_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can form groups.")

    from models.student import Student
    student = db.query(Student).filter(Student.id == current_user["id"]).first()
    if student and student.group_id is not None:
        raise HTTPException(status_code=400, detail="Student already in a group.")

    new_group = create_group(db=db, student_id=current_user["id"], group_name=group_data.group_name)
    return {"group_id": new_group.id, "group_name": new_group.group_name}

@router.post("/join")
def join_group_api(
    join_data: GroupJoin,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can join groups.")

    from models.student import Student
    student = db.query(Student).filter(Student.id == current_user["id"]).first()
    if student and student.group_id is not None:
        raise HTTPException(status_code=400, detail="Already in a group.")

    try:
        group = join_group(db=db, student_id=current_user["id"], group_id=join_data.group_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"group_id": group.id, "group_name": group.group_name}

@router.post("/quit")
def quit_group_api(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can quit groups.")

    try:
        quit_group(db=db, student_id=current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Successfully quit group."}

@router.get("/members")
def get_group_members_api(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view group members.")

    from models.student import Student
    student = db.query(Student).filter(Student.id == current_user["id"]).first()
    if not student or student.group_id is None:
        raise HTTPException(status_code=400, detail="You are not in any group.")

    try:
        members = get_group_members(db=db, group_id=student.group_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"member_ids": members}

@router.post("/apply_project")
def apply_project_api(
    apply_data: GroupApplyProject,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can apply for projects.")

    from models.student import Student
    student = db.query(Student).filter(Student.id == current_user["id"]).first()
    if not student or student.group_id is None:
        raise HTTPException(status_code=400, detail="You are not in any group.")

    try:
        group = apply_project(db=db, group_id=student.group_id, project_id=apply_data.project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": f"Group {group.group_name} applied for project {apply_data.project_id}."}
