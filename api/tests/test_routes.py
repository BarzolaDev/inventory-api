PRODUCT_PAYLOAD = {
    "name": "Arroz",
    "stock": 100,
    "purchase_price": "5.00",
    "sale_price": "10.00",
    "unit": "kg"
}


# --- Users ---

def test_register_ok(client):
    response = client.post("/users/register", json={
        "username": "juan",
        "email": "juan@test.com",
        "password": "secret123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "juan@test.com"
    assert "password" not in response.json()


def test_register_duplicate_email(client):
    client.post("/users/register", json={
        "username": "juan",
        "email": "juan@test.com",
        "password": "secret123"
    })
    response = client.post("/users/register", json={
        "username": "otro",
        "email": "juan@test.com",
        "password": "secret123"
    })
    assert response.status_code == 409


def test_login_ok(client):
    client.post("/users/register", json={
        "username": "juan",
        "email": "juan@test.com",
        "password": "secret123"
    })
    response = client.post("/users/login", data={
        "username": "juan@test.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/users/register", json={
        "username": "juan",
        "email": "juan@test.com",
        "password": "secret123"
    })
    response = client.post("/users/login", data={
        "username": "juan@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


# --- Products ---

def test_create_product_ok(auth_client):
    response = auth_client.post("/products/", json=PRODUCT_PAYLOAD)
    assert response.status_code == 201
    assert response.json()["name"] == "Arroz"
    assert response.json()["stock"] == 100


def test_create_product_unauthorized(client):
    response = client.post("/products/", json=PRODUCT_PAYLOAD)
    assert response.status_code == 401


def test_get_products(client):
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_by_id(auth_client):
    created = auth_client.post("/products/", json=PRODUCT_PAYLOAD).json()
    response = auth_client.get(f"/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_product_not_found(client):
    response = client.get("/products/9999")
    assert response.status_code == 404


def test_update_product(auth_client):
    created = auth_client.post("/products/", json=PRODUCT_PAYLOAD).json()
    response = auth_client.patch(f"/products/{created['id']}", json={"name": "Arroz integral"})
    assert response.status_code == 200
    assert response.json()["name"] == "Arroz integral"


def test_update_stock(auth_client):
    created = auth_client.post("/products/", json=PRODUCT_PAYLOAD).json()
    response = auth_client.post(f"/products/{created['id']}/stock", json={"quantity": 50})
    assert response.status_code == 200
    assert response.json()["stock"] == 150


def test_update_stock_insufficient(auth_client):
    created = auth_client.post("/products/", json=PRODUCT_PAYLOAD).json()
    response = auth_client.post(f"/products/{created['id']}/stock", json={"quantity": -9999})
    assert response.status_code == 400


def test_delete_product(auth_client):
    created = auth_client.post("/products/", json=PRODUCT_PAYLOAD).json()
    response = auth_client.delete(f"/products/{created['id']}")
    assert response.status_code == 204


def test_delete_product_not_found(auth_client):
    response = auth_client.delete("/products/9999")
    assert response.status_code == 404
