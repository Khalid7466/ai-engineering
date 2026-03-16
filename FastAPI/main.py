from fastapi import FastAPI

app = FastAPI()

# Define a GET endpoint at the root URL
@app.get("/")
def retrieve_data():
    return {"message": "This is a GET request to the root URL"}

# Define a POST endpoint at the root URL
@app.post("/")
def create_data():
    return {"message": "This is a POST request to the root URL"}

# Define a PUT endpoint at the root URL
@app.put("/")
def update_data():
    return {"message": "This is a PUT request to the root URL"}