import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    login: str
    email: str
    password: str
    createdAt: str
    updatedAt: str


class Post(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    createdAt: str
    updatedAt: str


def dt_to_str(dt: datetime) -> str:
    return dt.isoformat()


class Storage:
    def __init__(self, filename: str = "data.json"):
        self.filename = Path(filename)
        self.users: List[User] = []
        self.posts: List[Post] = []
        self.user_id_counter = 1
        self.post_id_counter = 1
        self.load_from_file()

    def add_user(self, user_data: dict):
        user_data["id"] = self.user_id_counter
        user_data["createdAt"] = dt_to_str(datetime.utcnow())
        user_data["updatedAt"] = dt_to_str(datetime.utcnow())
        user = User(**user_data)
        self.users.append(user)
        self.user_id_counter += 1
        self.save_to_file()

    def get_user(self, user_id: int) -> Optional[User]:
        return next((u for u in self.users if u.id == user_id), None)

    def update_user(self, user_id: int, new_data: dict) -> bool:
        user = self.get_user(user_id)
        if user:
            user_dict = user.dict()
            user_dict.update(new_data)
            user = User(**user_dict)
            self.users = [u if u.id != user_id else user for u in self.users]
            self.save_to_file()
            return True
        return False

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user:
            self.users = [u for u in self.users if u.id != user_id]
            self.save_to_file()
            return True
        return False

    def add_post(self, post_data: dict):
        print(f"Received post data: {post_data}")
        author_id = post_data.get("author_id", None)
        if author_id is None:
            print("Error: author_id is missing in the post data.")
            raise ValueError("author_id is required")

        try:
            post_data["author_id"] = int(author_id)
        except ValueError:
            print(f"Error: Invalid author_id '{author_id}'")
            raise ValueError(
                f"Invalid author_id '{author_id}', must be an integer."
            )
        post_data["id"] = self.post_id_counter
        post_data["createdAt"] = dt_to_str(datetime.utcnow())
        post_data["updatedAt"] = dt_to_str(datetime.utcnow())
        print(f"Post data before creating Post object: {post_data}")
        try:
            post = Post(**post_data)
        except Exception as e:
            print(f"Error creating post: {e}")
            raise ValueError(f"Invalid data for post: {post_data}")
        self.posts.append(post)
        self.post_id_counter += 1
        self.save_to_file()

    def get_post(self, post_id: int) -> Optional[Post]:
        return next((p for p in self.posts if p.id == post_id), None)

    def update_post(self, post_id: int, new_data: dict) -> bool:
        post = self.get_post(post_id)
        if post:
            post_dict = post.dict()
            post_dict.update(new_data)
            post = Post(**post_dict)
            self.posts = [p if p.id != post_id else post for p in self.posts]
            self.save_to_file()
            return True
        return False

    def delete_post(self, post_id: int) -> bool:
        post = self.get_post(post_id)
        if post:
            self.posts = [p for p in self.posts if p.id != post_id]
            self.save_to_file()
            return True
        return False

    def list_users(self) -> list:
        return self.users

    def list_posts(self) -> list:
        return self.posts

    def save_to_file(self):
        data = {
            "users": [user.dict() for user in self.users],
            "posts": [post.dict() for post in self.posts],
        }
        with self.filename.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self):
        if not self.filename.exists() or self.filename.stat().st_size == 0:
            return

        try:
            with self.filename.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.users = [User(**user) for user in data.get("users", [])]
                self.posts = [Post(**post) for post in data.get("posts", [])]
                if self.users:
                    self.user_id_counter = (
                        max(user.id for user in self.users) + 1
                    )
                if self.posts:
                    self.post_id_counter = (
                        max(post.id for post in self.posts) + 1
                    )
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON. The file may be corrupted.")
            self.users = []
            self.posts = []
