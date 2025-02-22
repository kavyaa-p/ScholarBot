# main.py
from fastapi import FastAPI

app = FastAPI() # creates fast api instance

@app.get("/") # defining the route. this is a GET endpoint
async def root(): # allows non-blocking, concurrent requests, especially helpful with databases or external API calls
    return {"message": "Hello, World!"}