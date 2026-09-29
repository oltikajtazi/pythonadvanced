from fastapi import FastApi
from models import Developer, Project

app = FastApi()

@app.post("/developers/")
def create_developer(developer: Developer):
    return {"messages":"Developer created successfully","developer":developer}

@app.post("/projects/")
def create_project(project:Project):
    return{"[messages":"Project created successfully","project":project}