import pytest



# Tests for products

def test_create_product(client):
    response = client.post("/products/", json={

        "name": "test",

        "price": 1.0,

    })
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] is not None
    

def test_read_products(client):
    # Create one first
    client.post("/products/", json={
        
        "name": "test2",
        
        "price": 2.0,
        
    })
    
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_read_product(client):
    # Create one
    create_res = client.post("/products/", json={

        "name": "test3",

        "price": 3.0,

    })
    item_id = create_res.json()["id"]
    
    response = client.get(f"/products/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id

def test_update_product(client):
    # Create one
    create_res = client.post("/products/", json={

        "name": "test4",

        "price": 4.0,

    })
    item_id = create_res.json()["id"]
    
    # Update
    response = client.patch(f"/products/{item_id}", json={

        "name": "updated",

        "price": 5.0,

    })
    assert response.status_code == 200

def test_delete_product(client):
    # Create one
    create_res = client.post("/products/", json={

        "name": "test6",

        "price": 6.0,

    })
    item_id = create_res.json()["id"]
    
    response = client.delete(f"/products/{item_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_res = client.get(f"/products/{item_id}")
    assert get_res.status_code == 404