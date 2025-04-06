from fastapi import FastAPI, HTTPException
import uvicorn

from models import TrainInput, AddToTraining, AskInput
from train import train_from_a_db, add_data_to_training
from ask import vanna_ask

app = FastAPI()

@app.get('/')
def health_check():
    try:
        return "Health check success"
    except Exception as e:
        return "Error: ", e
    
@app.post('/train')
async def train(input:TrainInput):
    try:
        print("received training db file path: ", input.db_path)
        result = train_from_a_db(input.db_path)
        return {"success":1, "message":result} 
    except Exception as e:
        return f"Error: {e}"
    
@app.post('/add_to_training')
async def add_to_training(input: AddToTraining):
    try:
        print("received training db file path: ", input.db_path)
        print("received user query to be trained: ", input.user_query)
        print("received corresponding sql_query to be trained: ", input.sql_query)
        result = add_data_to_training(input.db_path, input.user_query, input.sql_query)
        return {"success":1, "message":result} 
    except Exception as e:
        return f"Error: {e}"
    
@app.post('/ask')
async def train(input:AskInput):
    try:
        print("received user query: ", input.user_query)
        print("received training db file path: ", input.db_path)
        result = vanna_ask(input.user_query, input.db_path, input.history)
        return {"success":1, "message":result} 
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error":str(e)}) 
    
if __name__=="__main__":
    uvicorn.run(app=app,host='0.0.0.0',port=5050)
