import logging
from datetime import datetime, timezone
from api.services.alert import alert_discord

logger = logging.getLogger("audit")

SUSPICIOUS_PRODUCT_THRESHOLD = 50
SUSPICIOUS_HOUR_START = 2
SUSPICIOUS_HOUR_END = 5

RULES = [
    {
        "check": lambda h, a: len([
            x for x in h
            if x.get("path", "").startswith("/products") and x.get("method") == "GET"
        ]) > SUSPICIOUS_PRODUCT_THRESHOLD,
        "score": 40,
        "razon": "scraping de productos"
    },
    {
        "check": lambda h, a: (
            a.get("method") == "POST"
            and "stock" in a.get("path", "")
            and len(a.get("path", "").split("/")) > 2
            and not any(
                x.get("path", "") == f"/products/{a.get('path','').split('/')[2]}"
                for x in h
            )
        ),
        "score": 60,
        "razon": "modificó stock sin consultar producto"
    },
    {
        "check": lambda h, a: (
            SUSPICIOUS_HOUR_START <= datetime.now(timezone.utc).hour <= SUSPICIOUS_HOUR_END
            and len(h) > 20
        ),
        "score": 30,
        "razon": "actividad nocturna intensa"
    },
    {
        "check": lambda h, a: (
            len(h) >= 4 and
            len(set(
                f"{x.get('method')}:{x.get('path')}" for x in h[:4]
            )) <= 2
        ),
        "score": 50,
        "razon": "secuencia repetitiva de acciones"
    },
    {
        "check": lambda h, a: (
            a.get("method") == "POST"
            and "stock" in a.get("path", "")
            and sum(
                1 for x in h
                if x.get("method") == "POST" and "stock" in x.get("path", "")
            ) >= 5
        ),
        "score": 40,
        "razon": "modificaciones de stock repetitivas"
    },
]

async def analyze_behavior(user_id: str, action: dict, history: list, ip: str = None, long_history: list = []) -> dict:
    total_score = 0
    razones = []

    for rule in RULES:
        try:
            if rule["check"](history, action):
                total_score += rule["score"]
                razones.append(rule["razon"])
        except Exception as e:
            logger.error("rule_error", extra={"error": str(e), "user_id": user_id})

    if total_score >= 60:
        if user_id != "anonymous":
            from api.core.redis_client import get_redis
            r = await get_redis()
            ttl = 60 * 60 * 24 if total_score >= 90 else 60 * 60
            await r.setex(f"blocked_user:{user_id}", ttl, "agent_defender")

        # Castigo por user_id — independiente de IP
        if user_id != "anonymous":
            import redis as redis_lib
            from api.core.redis_client import get_redis
            r = await get_redis()
            ttl = 60 * 60 * 24 if total_score >= 90 else 60 * 60
            await r.setex(f"blocked_user:{user_id}", ttl, "agent_defender")

        decision = "BLOQUEADO" if total_score >= 90 else "SOSPECHOSO"
        razon = " + ".join(razones)
        await alert_discord(decision, user_id, ip or "unknown", razon)
        logger.warning("agent_defender", extra={
            "user_id": user_id,
            "score": total_score,
            "razon": razon,
            "ip": ip,
            "action": str(action),
        })
        return {"decision": decision, "score": total_score, "razon": razon}

    logger.info("agent_defender", extra={
        "user_id": user_id,
        "score": total_score,
        "ip": ip,
        "action": str(action),
    })
    return {"decision": "NORMAL", "score": total_score, "razon": "comportamiento normal"}