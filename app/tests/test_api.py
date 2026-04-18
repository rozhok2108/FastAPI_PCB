import pytest
from httpx import AsyncClient
from app.models import UserRole
from app.tests.conftest import API_PREFIX  

pytestmark = pytest.mark.asyncio



async def register_user(client: AsyncClient, email: str, password: str, role: str):
    """Регистрирует пользователя и возвращает ответ"""
    return await client.post(
        f"{API_PREFIX}/auth/register",
        json={"email": email, "password": password, "role": role}
    )


async def login_user(client: AsyncClient, email: str, password: str) -> str:
    """Логинит пользователя и возвращает токен"""
    resp = await client.post(
        f"{API_PREFIX}/auth/login",
        json={"email": email, "password": password}
    )
    assert resp.status_code == 200, f"Login failed: {resp.status_code} - {resp.text}"
    return resp.json()["access_token"]


async def get_auth_headers(client: AsyncClient, email: str, password: str) -> dict:
    """Возвращает заголовки с авторизацией для запросов"""
    token = await login_user(client, email, password)
    return {"Authorization": f"Bearer {token}"}



async def test_register_and_login(client):
    """Проверка регистрации и получения токена"""
    resp = await register_user(client, "test@example.com", "pass123", "client")
    assert resp.status_code == 200, f"Register failed: {resp.status_code} - {resp.text}"
    
    resp = await client.post(
        f"{API_PREFIX}/auth/login",
        json={"email": "test@example.com", "password": "pass123"}
    )
    assert resp.status_code == 200, f"Login failed: {resp.status_code} - {resp.text}"
    data = resp.json()
    assert "access_token" in data, f"Token not in response: {data}"
    assert data["token_type"] == "bearer"


async def test_guest_view_services(client):
    """Гость может просматривать услуги (публичный эндпоинт)"""
    resp = await client.get(f"{API_PREFIX}/services/")
    assert resp.status_code == 200, f"Get services failed: {resp.status_code} - {resp.text}"
    data = resp.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"


async def test_client_create_order(client, db_session):
    """Клиент может создать заказ после авторизации"""
    await register_user(client, "c@test.com", "123", "client")
    headers_client = await get_auth_headers(client, "c@test.com", "123")
    
    await register_user(client, "m@test.com", "123", "manager")
    headers_manager = await get_auth_headers(client, "m@test.com", "123")
    
    service_resp = await client.post(
        f"{API_PREFIX}/services/",
        json={"name": "SMD Assembly", "price": 100},
        headers=headers_manager
    )
    assert service_resp.status_code == 200, f"Create service failed: {service_resp.text}"
    service_id = service_resp.json().get("id")
    assert service_id is not None, "Service ID not returned"
    
    order_resp = await client.post(
        f"{API_PREFIX}/orders/",
        json={"description": "PCB v1", "service_ids": [service_id]},
        headers=headers_client
    )
    assert order_resp.status_code == 200, f"Create order failed: {order_resp.text}"
    order_data = order_resp.json()
    assert order_data["description"] == "PCB v1"
    assert "client_id" in order_data


async def test_engineer_update_status(client, db_session):
    """Инженер может менять статус заказа на 'in_progress'"""
    await register_user(client, "client@test.com", "123", "client")
    await register_user(client, "manager@test.com", "123", "manager")
    await register_user(client, "engineer@test.com", "123", "engineer")
    
    headers_client = await get_auth_headers(client, "client@test.com", "123")
    headers_manager = await get_auth_headers(client, "manager@test.com", "123")
    headers_engineer = await get_auth_headers(client, "engineer@test.com", "123")
    
    service = await client.post(
        f"{API_PREFIX}/services/",
        json={"name": "Debug", "price": 50},
        headers=headers_manager
    )
    service_id = service.json()["id"]
    
    order = await client.post(
        f"{API_PREFIX}/orders/",
        json={"description": "Fix bug", "service_ids": [service_id]},
        headers=headers_client
    )
    order_id = order.json()["id"]
    
    patch_resp = await client.patch(
        f"{API_PREFIX}/orders/{order_id}",
        json={"engineer_id": 3, "status": "accepted"},  
        headers=headers_manager
    )
    assert patch_resp.status_code == 200, f"Assign engineer failed: {patch_resp.text}"
    
    status_resp = await client.patch(
        f"{API_PREFIX}/orders/{order_id}",
        json={"status": "in_progress"},
        headers=headers_engineer
    )
    assert status_resp.status_code == 200, f"Update status failed: {status_resp.text}"
    assert status_resp.json()["status"] == "in_progress"


async def test_admin_delete_user(client, db_session):
    """Админ может удалять пользователей"""
 
    await register_user(client, "admin@test.com", "123", "admin")
    headers_admin = await get_auth_headers(client, "admin@test.com", "123")
    
    await register_user(client, "victim@test.com", "123", "client")
    
    users_resp = await client.get(f"{API_PREFIX}/users/", headers=headers_admin)
    assert users_resp.status_code == 200, f"Get users failed: {users_resp.text}"
    
    users = users_resp.json()
    victim = next((u for u in users if u["email"] == "victim@test.com"), None)
    assert victim is not None, "Victim user not found"
    victim_id = victim["id"]
    
    delete_resp = await client.delete(
        f"{API_PREFIX}/users/{victim_id}",
        headers=headers_admin
    )
    assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
    
    users_after = await client.get(f"{API_PREFIX}/users/", headers=headers_admin)
    emails = [u["email"] for u in users_after.json()]
    assert "victim@test.com" not in emails, "User was not deleted"
