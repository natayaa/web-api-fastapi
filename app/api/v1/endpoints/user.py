from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse

from models.schemas.user import UserCreate, UserPublic
from models.orm.users import User, UserProfile
# Database 
from db.session import get_db, AsyncSession

user_endpoint = APIRouter(tags=["User Information"])

#
@user_endpoint.post("/users", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create new user with profile"""
    try:
        # Hash password properly
        hashed_password = user_data.password
        
        # Create user with profile
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role="user",
            is_active=True,
            profile=UserProfile(
                first_name="",  # Set defaults or get from request
                last_name="",
            )
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # Convert to Pydantic model
        return UserPublic.model_validate(db_user)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )