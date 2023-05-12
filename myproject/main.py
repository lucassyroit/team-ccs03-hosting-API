from fastapi import Depends, FastAPI, HTTPException
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import os
import crud
import models
import schemas
import auth
from database import SessionLocal, engine

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


print("We are in the main.......")
if not os.path.exists('.\sqlitedb'):
    print("Making folder.......")
    os.makedirs('.\sqlitedb')

print("Creating tables.......")
models.Base.metadata.create_all(bind=engine)
print("Tables created.......")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    db_user_username = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if db_user_username:
        raise HTTPException(status_code=406, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return uers


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/password/")
def change_password(password_data: schemas.ChangePassword, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=password_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not auth.verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect previous password")
    if password_data.old_password == password_data.new_password:
        raise HTTPException(status_code=400, detail="Previous and new password are identical")
    new_hashed_password = auth.get_password_hash(password_data.new_password)
    user.hashed_password = new_hashed_password
    db.commit()
    return {"message": "Password changed successfully"}

# @app.post("/token")
#def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #Try to authenticate the user
    #    user = auth.authenticate_user(db, form_data.username, form_data.password)
    #    if not user:
    #        raise HTTPException(
    #           status_code=401,
    #           detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # # Add the JWT case sub with the subject(user)
    # access_token = auth.create_access_token(
    #    data={"sub": user.email}
    # )
     #Return the JWT as a bearer token to be placed in the headers
    #return {"access_token": access_token, "token_type": "bearer"}
