from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hello, World!"}



@app.get("/items/")
def read_items():
    return {"items":["kursi1","kursi2","kursi3"]}


@app.get("/items/{item_id}")
def reaf_items(items_id:int):
    return {"item_id":items_id}

@app.get("/users/user_id}")
def get_users(user_id:int):
    return {"item_id":user_id}

@app.put("/items/items_id}")
def update_item(item_id:int,name:str,price:float):
    return {"items_id": item_id, "item_name":name,"item_price":price}


@app.delete("/users/user_id}")
def delete_item(item_id:int):
    return {"message":"u fshie me sukses"}




























