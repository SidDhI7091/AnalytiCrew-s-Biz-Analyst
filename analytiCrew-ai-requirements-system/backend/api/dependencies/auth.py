from firebase_admin import auth as firebase_auth, firestore
from fastapi import HTTPException, Header
from firebase.firebase_init import db

def get_current_user(authorization: str = Header(...)):
    try:
        id_token = authorization.split("Bearer ")[-1]
        decoded_token = firebase_auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email")

        # Auto-create user profile if it doesn't exist
        user_ref = db.collection("users").document(uid)
        if not user_ref.get().exists:
            user_ref.set({
                "email": email,
                "name": "",
                "role": "User",
                "joined_projects": []
            })

        return {"user_id": uid, "email": email}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

