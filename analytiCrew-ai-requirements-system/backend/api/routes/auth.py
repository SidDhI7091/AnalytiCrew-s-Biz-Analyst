from fastapi import APIRouter, Depends
from api.dependencies.auth import get_current_user
from firebase.firebase_init import db

router = APIRouter()

from pydantic import BaseModel

class RegisterRequest(BaseModel):
    name: str

@router.post("/register")
def register_user(payload: RegisterRequest, user=Depends(get_current_user)):
    name = payload.name
    user_ref = db.collection("users").document(user["user_id"])
    user_ref.set({
        "name": name,
        "email": user["email"],
        "role": "User",
        "joined_projects": []
    })
    return {"message": "User registered successfully", "uid": user["user_id"]}

