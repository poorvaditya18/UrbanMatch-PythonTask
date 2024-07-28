from sqlalchemy.orm import Session
from pydantic import ValidationError, BaseModel
from utility.exceptions import UserAlreadyExistsException, DatabaseException , UserNotFoundException 
from schemas import EmailValidationModel
import models, schemas

class UserServicesV1():
    
    def __init__(self, db: Session):
        self.db = db

    def validate_user_email(self, email: str) :
        try:
            EmailValidationModel(email=email)
            return True
        except ValidationError:
            return False
    
    def create_user(self,user):
        try:
            existing_user = self.db.query(models.User).filter(models.User.email == user.email).first()
            if existing_user:
                raise UserAlreadyExistsException(user.email)
            
            user_data = models.User(
                name=user.name,
                age=user.age,
                gender=user.gender,
                email=user.email,
                city=user.city,
                interests=user.interests
            )
            self.db.add(user_data)
            self.db.commit()
            self.db.refresh(user_data)
            data = schemas.User.model_validate(user_data).model_dump()
            return data
        except Exception as e:
            raise DatabaseException(f"An unexpected error occurred while creating user:{e}")

    def update_user(self, user_id: int ,data):
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            print(user)
            if not user:
                return None
            
            for key, value in data.items():
                setattr(user, key, value)

            self.db.commit()
            self.db.refresh(user)
            data = schemas.User.model_validate(user).model_dump()
            return data
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"An unexpected error occurred while updating user: {e}")
    
    def get_user(self, user_id: int):
        try:
            db_user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if not db_user:
                return None
            data = schemas.User.model_validate(db_user).model_dump()
            return data
        except Exception as e:
            raise DatabaseException(f"An unexpected error occurred while fetching user: {e}")

    def get_users(self, offset: int, limit: int):
        try:
            users = self.db.query(models.User).offset(offset).limit(limit).all()
            data = [schemas.User.model_validate(user).model_dump() for user in users]
            return data
        except Exception as e:
            raise DatabaseException(f"An unexpected error occurred while fetching users: {e}")

    def delete_user(self,user_id):
        try:
            db_user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if not db_user:
                return None
            
            self.db.delete(db_user)
            self.db.commit()
            data = schemas.User.model_validate(db_user).model_dump()
            return data
        except Exception as e:
            raise DatabaseException(f"An unexpected error occurred while deleting user: {e}")
        
    def find_matches(self, user_id: int, search_parameter : str ):
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                raise UserNotFoundException(f"User with id {user_id} not found")

            if search_parameter == "city":
                matches = self.db.query(models.User).filter(
                    models.User.city == user.city,
                    models.User.id != user.id  # Exclude the user itself
                ).all()

            return [schemas.User.model_validate(match).model_dump() for match in matches]
        except Exception as e:
            raise DatabaseException(f"An unexpected error occurred while finding matches: {e}")