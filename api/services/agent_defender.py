import logging
from datetime import datetime
from api.services.alert import alert_discord

logger = logging.getLogger("audit")

SUSPICIOUS_PRODUCT_THRESHOLD = 50
SUSPICIOUS_HOUR_START = 2
SUSPICIOUS_HOUR_END = 5

async def analyze_behavior(user_id: str, action: dict, history: list, ip: str = None) -> dict:

    product_accesses = [
        h for h in history
        if h.get("path", "").startswith("/products") and h.get("method") == "GET"
    ]
    if len(product_accesses) > SUSPICIOUS_PRODUCT_THRESHOLD:
        result = {"decision": "SOSPECHOSO", "razon": f"consultó {len(product_accesses)} productos en una sesión"}
        await alert_discord("AGENTE SOSPECHOSO", user_id, ip or "unknown", result["razon"])
        return result

    if action.get("method") == "POST" and "stock" in action.get("path", ""):
        product_id = action.get("path", "").split("/")[2]
        consulted = any(h.get("path", "") == f"/products/{product_id}" for h in history)
        if not consulted:
            result = {"decision": "SOSPECHOSO", "razon": "modificó stock sin consultar el producto antes"}
            await alert_discord("AGENTE SOSPECHOSO", user_id, ip or "unknown", result["razon"])
            return result

    hour = datetime.utcnow().hour
    if SUSPICIOUS_HOUR_START <= hour <= SUSPICIOUS_HOUR_END:
        if len(history) > 20:
            result = {"decision": "SOSPECHOSO", "razon": f"actividad intensa a las {hour}am UTC"}
            await alert_discord("AGENTE SOSPECHOSO", user_id, ip or "unknown", result["razon"])
            return result

    logger.info("agent_defender_analysis", extra={
        "user_id": user_id,
        "action": str(action),
        "history_length": len(history),
        "method": action.get("method", ""),
        "status_code": 200,
        "duration_ms": 0,
        "ip": ip,
    })

    return {"decision": "NORMAL", "razon": "comportamiento consistente con uso normal de inventario"}
