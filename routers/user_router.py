from fastapi import APIRouter
from models.user import User
from services.user_service_ghost import UserServiceGhost

router = APIRouter(prefix="/users", tags=["User"])
service = UserServiceGhost()

@router.get("/")
def list_users():
    return service.list()

@router.get("/{item_id}")
def get_user(item_id: int):
    return service.get(item_id)

@router.post("/")
def create_user(item: User):
    return service.create(item)

@router.patch("/{item_id}")
def update_user(item_id: int, item: User):
    return service.update(item_id, item)

@router.delete("/{item_id}")
def delete_user(item_id: int):
    return service.delete(item_id)    