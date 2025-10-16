# ER Diagram

```mermaid
erDiagram
    users {
        int id PK
        string login UK
        string email UK
        string password_hash
        timestamp created_at
        timestamp updated_at
    }

    posts {
        int id PK
        string title
        text content
        int author_id FK
        timestamp created_at
        timestamp updated_at
    }

    categories {
        int id PK
        string name UK
        text description
        timestamp created_at
    }

    comments {
        int id PK
        text content
        int author_id FK
        int post_id FK
        int parent_comment_id FK
        timestamp created_at
        timestamp updated_at
    }

    subscriptions {
        int subscriber_id PK,FK
        int author_id PK,FK
        timestamp created_at
    }

    user_favorites {
        int user_id PK,FK
        int post_id PK,FK
        timestamp created_at
    }

    post_categories {
        int post_id PK,FK
        int category_id PK,FK
    }

    users ||--o{ posts : "author"
    users ||--o{ comments : "author"
    users ||--o{ subscriptions : "subscriber"
    users ||--o{ subscriptions : "author"
    users ||--o{ user_favorites : "user"
    posts ||--o{ comments : "post"
    posts ||--o{ user_favorites : "post"
    posts }o--o{ categories : "categories"
    comments }o--o| comments : "parent"
