from pydantic import BaseModel

class TrainInput(BaseModel):
    db_path: str
class AddToTraining(BaseModel):
    db_path: str
    user_query: str
    sql_query: str
class AskInput(BaseModel):
    user_query: str
    db_path: str
    history: list
