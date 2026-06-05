import httpx
import random
import time
import asyncio

BASE_URL = "http://localhost"

NORMAL_ENDPOINTS = [
    ("GET", "/products"),
    ("GET", "/products/1"),
    ("POST", "/auth/login"),
]

ATTACK_ENDPOINTS = [
    ("GET", "/products?id=1' OR '1'='1"),
    ("GET", "/products/../../../etc/passwd"),
    ("GET", "/admin"),
    ("GET", "/products?id=1; DROP TABLE products--"),
]

ATTACK_HEADERS = [
    {"User-Agent": "sqlmap/1.0"},
    {"User-Agent": "nikto/2.1"},
    {"User-Agent": "nmap scripting engine"},
]

async def send_normal(client):
    method, path = random.choice(NORMAL_ENDPOINTS)
    try:
        await client.request(method, f"{BASE_URL}{path}", timeout=3)
    except:
        pass

async def send_attack(client):
    method, path = random.choice(ATTACK_ENDPOINTS)
    headers = random.choice(ATTACK_HEADERS) if random.random() > 0.5 else {}
    try:
        await client.request(method, f"{BASE_URL}{path}", headers=headers, timeout=3)
    except:
        pass

async def main():
    async with httpx.AsyncClient(verify=False) as client:
        print("Generando tráfico... Ctrl+C para parar")
        i = 0
        while True:
            if random.random() > 0.3:  # 70% normal, 30% ataque
                await send_normal(client)
            else:
                await send_attack(client)
            i += 1
            if i % 50 == 0:
                print(f"{i} requests enviados")
            await asyncio.sleep(0.1)

asyncio.run(main())
