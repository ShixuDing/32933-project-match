from sqlalchemy.orm import Session
from models.group import Group
from models.student import Student

def create_group(db: Session, student_id: int, group_name: str):
    new_group = Group(
        group_name=group_name,
        member_ids=[student_id]
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        student.group_id = new_group.id
        db.commit()

    return new_group

def join_group(db: Session, student_id: int, group_id: int):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group does not exist.")

    if student_id in group.member_ids:
        raise ValueError("Student already in the group.")

    group.member_ids.append(student_id)
    db.commit()

    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        student.group_id = group.id
        db.commit()

    return group

def quit_group(db: Session, student_id: int):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or student.group_id is None:
        raise ValueError("Student is not in any group.")

    group = db.query(Group).filter(Group.id == student.group_id).first()
    if group:
        group.member_ids.remove(student_id)
        db.commit()

    student.group_id = None
    db.commit()

def get_group_members(db: Session, group_id: int):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group does not exist.")
    return group.member_ids

def apply_project(db: Session, group_id: int, project_id: int):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group does not exist.")

    group.project_id = project_id
    db.commit()
    return group
