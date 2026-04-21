import threading

PRODUCT_DEFAULTS = dict(
    unit="kg",
    purchase_price="5.00",
    sale_price="10.00"
)

def test_select_for_update_prevents_race_condition(pg_auth_client):
    # Arrange
    response = pg_auth_client.post("/products/", json={
        "name": "test_stock",
        "stock": 10,
        **PRODUCT_DEFAULTS
    })
    product_id = response.json()["id"]

    errors = []
    results = []

    def decrease_stock():
        try:
            r = pg_auth_client.post(f"/products/{product_id}/stock",
                json={"quantity": -1})
            results.append(r.status_code)
        except Exception as e:
            errors.append(e)

    # Act - 10 usuarios simultáneos
    threads = [threading.Thread(target=decrease_stock) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    # Assert
    final = pg_auth_client.get(f"/products/{product_id}").json()
    assert final["stock"] == 0
    assert len(errors) == 0
    assert results.count(200) == 10