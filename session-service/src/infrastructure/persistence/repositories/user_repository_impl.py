from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.persistence.models.user_model import UserModel

class UserRepositoryImpl(UserRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        
        if not db_user:
            new_user = UserModel(user_id=user_id)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            print(f"\n[REPO] Usuario creado por defecto: {user_id}\n")
            db_user = new_user
        
        return User(
            user_id=db_user.user_id,
            settings=db_user.settings,
            updated_at=db_user.updated_at.isoformat()
        )
    
    def save(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.user_id == user.user_id).first()
        
        if db_user:
            db_user.settings = user.settings
            db_user.updated_at = user.updated_at
        else:
            db_user = UserModel(
                user_id=user.user_id,
                settings=user.settings,
                updated_at=user.updated_at
            )
            self.db.add(db_user)
        
        self.db.commit()
        self.db.refresh(db_user)
        print(f"\n[REPO] Usuario guardado: {user.user_id}\n")
        
        return User(
            user_id=db_user.user_id,
            settings=db_user.settings,
            updated_at=db_user.updated_at.isoformat()
        )