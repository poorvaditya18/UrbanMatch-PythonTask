from fastapi import FastAPI,Request,Depends,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine, Base
import schemas
from typing import List
from services.user_services import UserServicesV1
from utility.helper_functions import Utility
from utility.exceptions import UserAlreadyExistsException, DatabaseException, UserNotFoundException
app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@app.post("/v1/users/", response_model=schemas.User)
async def create_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    request_body = await request.json()
    required_keys = ["name", "age", "gender", "email", "city" ,"interests"]
    Utility.check_required_keys(request_body, required_keys)
    user_service_obj = UserServicesV1(db)
    if not user_service_obj.validate_user_email(user.email):
        return JSONResponse({"status_code": 400, "error": "Invalid email format"})
    try:
        data = user_service_obj.create_user(user)
        if data is None:
            return JSONResponse({"status_code": 500, "error": "Not able to create user."})
    except UserAlreadyExistsException as e:
        return JSONResponse({"status_code": 400, "error": str(e)})
    except DatabaseException as e:
        return JSONResponse({"status_code": 500, "error": str(e)})
    return JSONResponse({"status_code":201, "data":data})

@app.get("/v1/users/", response_model=List[schemas.User])
def get_users(offset: int = Query(0, ge=0), limit: int = Query(10, ge=1), db: Session = Depends(get_db)):
    user_service = UserServicesV1(db)
    try:
        users = user_service.get_users(offset, limit)
        return JSONResponse({"status_code": 200, "data": users})
    except DatabaseException as e:
        return JSONResponse({"status_code": 500, "error": str(e)})

@app.get("/v1/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserServicesV1(db)
    try:
        user = user_service.get_user(user_id)
        if user is None:
            return JSONResponse({"status_code": 404, "error": "User not found"})
        return JSONResponse({"status_code": 200, "data": user})
    except DatabaseException as e:
        return JSONResponse({"status_code": 500, "error": str(e)})

@app.put("/v1/users/{user_id}", response_model=schemas.User)
async def update_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    request_body = await request.json()
    user_service_obj = UserServicesV1(db)
    try:
        data = user_service_obj.update_user(user_id, request_body)
        if data is None:
            return JSONResponse({"status_code": 404, "error": "User not found"})
    except DatabaseException as e:
        return JSONResponse({"status_code": 500, "error": str(e)})
    return JSONResponse({"status_code": 200, "data": data})

@app.delete("/v1/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_service = UserServicesV1(db)
    data = user_service.delete_user(user_id)
    if data is None:
        return JSONResponse({"status_code": 404, "error": "User not found"})
    return JSONResponse({"status_code": 200, "data":data})

@app.get("/v1/users/{user_id}/matches", response_model=List[schemas.User])
def find_matches(user_id: int, based_on: str = Query(...), db: Session = Depends(get_db)):
    """
    Find matches for a user based on a search parameter
    """
    user_service = UserServicesV1(db)
    try:
        matches = user_service.find_matches(user_id, based_on)
        return JSONResponse({"status_code": 200, "data": matches})
    except UserNotFoundException as e:
        return JSONResponse({"status_code": 404, "error": str(e)})
    except Exception as e:
        return JSONResponse({"status_code": 500, "error": str(e)})