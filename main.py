from typing import Optional
from fastapi import FastAPI,status,HTTPException,Response
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time



app=FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published : bool = True
   
while True:
    try:
        conn=psycopg2.connect(host="localhost", database="freecodecamp",user="postgres",
                            password="Ayush@04",cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Database connection successful")
        break
    except Exception as e:
        print("Connection to database failed")
        print(e)
        time.sleep(2)


@app.get("/")
async def root():
    return {
        "message":"Hello World"
    }


@app.get("/posts")
async def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts=cursor.fetchall()
    return {"data":posts}


@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING * """,
                   (post.title,post.content,post.published))
    new_post=cursor.fetchone()
    conn.commit()
    return {"newpost":new_post}


@app.get("/posts/{id}")
async def get_post(id: int):
    cursor.execute(""" SELECT * FROM posts WHERE id= %s""",(str(id)))
    post=cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} not found")
    return {"post_detail":post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int):
    cursor.execute("""DELETE FROM posts where id=%s returning *""",(str(id),))
    deleted_post=cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No post with id: {id}")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
async def update_post(id:int,post:Post):
    cursor.execute(""" UPDATE posts set title=%s,content=%s,published=%s where id=%s returning *""",
                   (post.title,post.content,post.published,str(id)))
    updated_post=cursor.fetchone()
    conn.commit()
    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail=f"no post with id:{id}")
    return {"updates post":updated_post}