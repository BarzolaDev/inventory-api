"""
Generador v2 - fix: flush Redis por round para evitar acumulacion de score
Uso: python3 traffic_generator.py --host http://localhost:8000 --rounds 200
"""

import asyncio, argparse, random, string, httpx
import redis.asyncio as aioredis

DEFAULT_HOST = "http://localhost:8000"
PRODUCT_IDS = list(range(1, 20))
TEST_USERS = [{"username": f"testuser_{i}", "password": "Test1234!"} for i in range(1, 6)]

def random_ip():
    return f"{random.randint(10,99)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

async def flush_round(r, user_id, ip):
    await r.delete(f"history:{user_id}", f"history_long:{user_id}", f"timing:{ip}", f"blocked:{ip}", f"recon:{ip}")
    if user_id != "anonymous":
        await r.delete(f"blocked_user:{user_id}")

async def get_token(client, host, username, password):
    try:
        r = await client.post(f"{host}/users/login", json={"username": username, "password": password})
        return r.json().get("access_token") if r.status_code == 200 else None
    except:
        return None

async def register_user(client, host, username, password):
    try:
        r = await client.post(f"{host}/users/register", json={"username": username, "password": password})
        return r.status_code in (200, 201)
    except:
        return False

async def req(client, host, method, path, token=None, body=None, ip=None):
    headers = {}
    if token: headers["Authorization"] = f"Bearer {token}"
    if ip: headers["X-Forwarded-For"] = ip
    try:
        fn = getattr(client, method.lower())
        kw = {"headers": headers}
        if body: kw["json"] = body
        r = await fn(f"{host}{path}", **kw)
        return r.status_code
    except:
        return 0

# --- Escenarios ---

async def normal(client, host, token, ip):
    pid = random.choice(PRODUCT_IDS)
    await req(client, host, "GET", "/products/", token, ip=ip)
    await asyncio.sleep(random.uniform(0.4, 1.0))
    await req(client, host, "GET", f"/products/{pid}", token, ip=ip)
    await asyncio.sleep(random.uniform(0.3, 0.8))
    await req(client, host, "POST", f"/products/{pid}/stock", token, {"quantity": random.randint(1,5)}, ip)
    await asyncio.sleep(random.uniform(0.5, 1.2))
    await req(client, host, "GET", "/products/", token, ip=ip)

async def stock_sin_recon(client, host, token, ip):
    # Score 60 → SOSPECHOSO
    pid = random.choice(PRODUCT_IDS)
    await req(client, host, "GET", "/products/", token, ip=ip)
    await asyncio.sleep(0.2)
    await req(client, host, "POST", f"/products/{pid}/stock", token, {"quantity": 99}, ip)

async def secuencia_repetitiva(client, host, token, ip):
    # Score 50 → SOSPECHOSO
    pid = random.choice(PRODUCT_IDS)
    for _ in range(5):
        await req(client, host, "GET", f"/products/{pid}", token, ip=ip)
        await asyncio.sleep(0.2)

async def stock_repetitivo(client, host, token, ip):
    # Score 100+ → BLOQUEADO
    pid = random.choice(PRODUCT_IDS)
    for _ in range(6):
        await req(client, host, "POST", f"/products/{pid}/stock", token, {"quantity": 1}, ip)
        await asyncio.sleep(0.1)

async def scraping(client, host, token, ip):
    # Timing robotico → BLOQUEADO
    for pid in random.choices(PRODUCT_IDS, k=15):
        await req(client, host, "GET", f"/products/{pid}", token, ip=ip)
        await asyncio.sleep(0.04)

async def recon_ataque(client, host, token, ip):
    # Score x3 → BLOQUEADO
    for path in ["/products/", "/products/1", "/products/2", "/products/3"]:
        await req(client, host, "GET", path, token, ip=ip)
        await asyncio.sleep(0.15)
    pid = random.choice(PRODUCT_IDS)
    for _ in range(5):
        await req(client, host, "POST", f"/products/{pid}/stock", token, {"quantity": 50}, ip)
        await asyncio.sleep(0.06)

async def honeypot(client, host, ip):
    path = random.choice(["/api/internal/export", "/admin/users", "/debug/config"])
    await req(client, host, "GET", path, ip=ip)

SCENARIOS = [
    ("NORMAL",               0.15, normal,              False),
    ("STOCK_SIN_RECON",      0.45, stock_sin_recon,     False),
    ("SECUENCIA_REPETITIVA", 0.12, secuencia_repetitiva,False),
    ("STOCK_REPETITIVO",     0.12, stock_repetitivo,    False),
    ("SCRAPING",             0.10, scraping,            False),
    ("RECON_ATAQUE",         0.06, recon_ataque,        False),
    ("HONEYPOT",             0.02, honeypot,            True),
]

async def run(host, rounds, redis_host, redis_port):
    print(f"[*] Host: {host}  Rounds: {rounds}")
    r = aioredis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        print("[*] Registrando usuarios...")
        tokens = {}
        for u in TEST_USERS:
            await register_user(client, host, u["username"], u["password"])
            t = await get_token(client, host, u["username"], u["password"])
            if t:
                tokens[u["username"]] = t
                print(f"    ✓ {u['username']}")
            else:
                print(f"    ✗ {u['username']}")

        usernames = list(tokens.keys()) or ["anonymous"]
        stats = {s[0]: 0 for s in SCENARIOS}
        weights = [s[1] for s in SCENARIOS]

        print(f"[*] Arrancando {rounds} rounds...\n")
        for i in range(rounds):
            username = random.choice(usernames)
            token = tokens.get(username)
            ip = random_ip()

            # flush historial antes de cada round
            await flush_round(r, username, ip)

            idx = random.choices(range(len(SCENARIOS)), weights=weights, k=1)[0]
            name, _, fn, is_honeypot = SCENARIOS[idx]
            stats[name] += 1

            print(f"  [{i+1:03d}/{rounds}] {name:<22} user={username:<20} ip={ip}")

            if is_honeypot:
                await fn(client, host, ip)
            else:
                await fn(client, host, token, ip)

            await asyncio.sleep(random.uniform(0.05, 0.2))

    await r.aclose()
    print("\n[*] Resumen:")
    for name, count in stats.items():
        print(f"    {name:<22} {count}")
    print("\n[✓] Listo.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--rounds", type=int, default=200)
    p.add_argument("--redis-host", default="localhost")
    p.add_argument("--redis-port", type=int, default=6379)
    a = p.parse_args()
    asyncio.run(run(a.host, a.rounds, a.redis_host, a.redis_port))
