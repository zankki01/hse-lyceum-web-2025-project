from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from storage import Storage, Post, User 
from datetime import datetime
import uvicorn

app = FastAPI()
storage = Storage()

def dt_to_str(dt: datetime) -> str:
    return dt.isoformat()

templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    posts = storage.list_posts()
    users = storage.list_users()
    posts_with_authors = []
    for post in posts:
        author = storage.get_user(post.author_id)
        post_data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author_id': post.author_id,
            'author_login': author.login if author else 'Unknown'
        }
        posts_with_authors.append(post_data)

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "posts": posts_with_authors, 
        "users": users
    })  

def dt_to_str(dt: datetime) -> str:
    return dt.isoformat()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/users/create", response_class=HTMLResponse)
async def create_user_form(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

@app.post("/users/create")
async def create_user_form_submit(
    login: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    user_id = len(storage.users) + 1
    current_time = dt_to_str(datetime.utcnow())
    payload = {
        "id": user_id,
        "login": login,
        "email": email,
        "password": password,
        "createdAt": current_time,
        "updatedAt": current_time,
    }
    storage.add_user(payload)
    return RedirectResponse("/", status_code=303)

@app.get("/posts/create", response_class=HTMLResponse)
async def create_post_form(request: Request):
    users = storage.list_users()
    return templates.TemplateResponse("create_post.html", {"request": request, "users": users})

@app.post("/posts/create")
async def create_post_form_submit(
    title: str = Form(...),
    content: str = Form(...),
    author_id: str = Form(...),
):
    print(f"Received data: title={title}, content={content}, author_id={author_id}")

    try:
        author_id = int(author_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="author_id must be an integer")
    
    print(f"Converted author_id: {author_id}")
    if not author_id:
        raise HTTPException(status_code=400, detail="Author ID is required")

    created_at = updated_at = datetime.utcnow().isoformat()
    payload = {
        "title": title,
        "content": content,
        "author_id": author_id,
        "createdAt": created_at,
        "updatedAt": updated_at
    }
    print(f"Payload for add_post: {payload}")
    try:
        storage.add_post(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    return RedirectResponse("/", status_code=303)

@app.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(request: Request, user_id: int):
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@app.post("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form_submit(
    user_id: int,
    login: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_at = datetime.utcnow().isoformat()
    updated_data = {"login": login, "email": email, "password": password, "updatedAt": updated_at}
    success = storage.update_user(user_id, updated_data)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update user")

    return RedirectResponse(f"/users/{user_id}", status_code=303)

@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_form(request: Request, post_id: int):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})

@app.post("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_form_submit(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    updated_at = datetime.utcnow().isoformat()
    updated_data = {"title": title, "content": content, "updatedAt": updated_at}
    success = storage.update_post(post_id, updated_data)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update post")

    return RedirectResponse(f"/posts/{post_id}", status_code=303)

@app.post("/posts/{post_id}/delete")
async def delete_post(post_id: int):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    success = storage.delete_post(post_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete post")

    return RedirectResponse("/", status_code=303)

@app.post("/users/{user_id}/delete")
async def delete_user(user_id: int):
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    success = storage.delete_user(user_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete user")

    return RedirectResponse("/", status_code=303)

@app.get("/users", response_class=HTMLResponse)
async def list_users(request: Request):
    users = storage.list_users()
    return templates.TemplateResponse("list_users.html", {"request": request, "users": users})

@app.get("/users/{user_id}", response_class=HTMLResponse)
async def view_user(request: Request, user_id: int):
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    all_posts = storage.list_posts()
    user_posts = [post for post in all_posts if post.author_id == user_id]
    
    return templates.TemplateResponse("view_user.html", {
        "request": request, 
        "user": user,
        "posts": user_posts
    })

@app.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int):
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    author = storage.get_user(post.author_id)

    return templates.TemplateResponse("view_post.html", {
        "request": request, 
        "post": post, 
        "author": author
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
