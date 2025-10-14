## DFD (основной сценарий, prod)

```mermaid
flowchart LR
  subgraph ClientBoundary["Trust Boundary Client"]
    U[Client]
  end

  subgraph EdgeBoundary["Trust Boundary Edge"]
    GW[API Gateway or Ingress - TLS HSTS RL]
  end

  subgraph CoreBoundary["Trust Boundary Core App"]
    APP[FastAPI App]
    USERS[Users API]
    WISHES[Wishes API]
    AUTH[get_current_user X-API-Key]
    ERR[Error Handler]
    SEC[Passlib Argon2id]
  end

  subgraph DataBoundary["Trust Boundary Data"]
    DB[(SQLite app/data/wishlist.db)]
    LOG[(Log sink stdout JSON)]
  end

  U -->|F1 HTTPS| GW
  GW -->|F2 HTTP internal| APP

  APP -->|F2a route| USERS
  APP -->|F2b route| WISHES

  USERS -->|F3 hash password| SEC
  USERS -->|F4 insert user| DB

  WISHES -->|F5 validate X-API-Key| AUTH
  AUTH -->|F5a select user by api_key| DB

  WISHES -->|F6 CRUD wishes| DB

  APP -->|F7 JSON logs no secrets| LOG
  ERR -->|F8 JSON error response| GW
  GW -->|F8 HTTPS to client| U
