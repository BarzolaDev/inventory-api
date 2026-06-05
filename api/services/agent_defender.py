import logging
import time
import json
from datetime import datetime, timezone
from api.services.alert import alert_discord

logger = logging.getLogger("audit")

# ─── Umbrales base ─────────────────────────────────────────────────────────────
SUSPICIOUS_PRODUCT_THRESHOLD = 50
SUSPICIOUS_HOUR_START = 2
SUSPICIOUS_HOUR_END = 5

SCORE_WARN = 60
SCORE_BLOCK = 90

# ─── Multiplicador recon → ataque ──────────────────────────────────────────────
RECON_ATTACK_MULTIPLIER = 3.0
RECON_MIN_EVENTS = 2
RECON_WINDOW_SECONDS = 86_400  # 24hs

RECON_SIGNAL_PATHS = ["/products", "/api/internal", "/admin", "/debug"]
RECON_SIGNAL_METHOD = "GET"

ATTACK_RAZONES = {
    "scraping de productos",
    "modificó stock sin consultar producto",
    "secuencia repetitiva de acciones",
    "modificaciones de stock repetitivas",
}

# ─── Reglas de comportamiento ──────────────────────────────────────────────────

def _extract_product_id(path: str) -> str | None:
    """Extrae el product_id de un path como /products/123/stock. Retorna None si no aplica."""
    parts = path.split("/")
    # Esperamos al menos: ['', 'products', '<id>', 'stock']
    if len(parts) >= 3:
        return parts[2]
    return None

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
        # FIX: reemplazamos el split()[2] inline por _extract_product_id con guard
        "check": lambda h, a: (
            a.get("method") == "POST"
            and "stock" in a.get("path", "")
            and _extract_product_id(a.get("path", "")) is not None
            and not any(
                x.get("path", "") == f"/products/{_extract_product_id(a.get('path', ''))}"
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


# ─── 1. Contexto adaptativo ────────────────────────────────────────────────────

def _is_night_time() -> bool:
    return SUSPICIOUS_HOUR_START <= datetime.now(timezone.utc).hour <= SUSPICIOUS_HOUR_END

async def _load_context(user_id: str, ip: str, redis) -> dict:
    """
    Devuelve multiplicadores y umbrales ajustados según contexto actual.
    Factores: horario nocturno, presión global del sistema, reincidente.
    """
    multiplier = 1.0
    flags = []

    if _is_night_time():
        multiplier *= 0.8
        flags.append("night_hours")

    global_blocks_raw = await redis.get("adaptive:global_blocks")
    global_blocks = int(global_blocks_raw) if global_blocks_raw else 0
    if global_blocks >= 50:
        multiplier *= 0.7
        flags.append(f"system_pressure(blocks={global_blocks})")

    recidivist = False
    if user_id != "anonymous":
        block_data = await redis.get(f"blocked_user:{user_id}")
        if block_data:
            recidivist = True
    if ip:
        block_data = await redis.get(f"blocked:{ip}")
        if block_data:
            recidivist = True
    if recidivist:
        multiplier *= 0.6
        flags.append("recidivist")

    return {
        "multiplier": multiplier,
        "flags": flags,
        "score_warn": max(30, SCORE_WARN * multiplier),
        "score_block": max(45, SCORE_BLOCK * multiplier),
    }


# ─── 2. Correlación recon → ataque ────────────────────────────────────────────

def _count_recon_events(long_history: list) -> int:
    cutoff = time.time() - RECON_WINDOW_SECONDS
    count = 0
    for entry in long_history:
        ts = entry.get("ts", 0)
        if ts < cutoff:
            continue
        path = entry.get("path", "")
        method = entry.get("method", "")
        if method == RECON_SIGNAL_METHOD and any(path.startswith(p) for p in RECON_SIGNAL_PATHS):
            count += 1
    return count

def _correlate_recon_attack(long_history: list, active_razones: list[str], base_score: float) -> tuple[float, str | None]:
    active_attacks = [r for r in active_razones if r in ATTACK_RAZONES]
    if not active_attacks:
        return base_score, None

    recon_count = _count_recon_events(long_history)
    if recon_count < RECON_MIN_EVENTS:
        return base_score, None

    adjusted = base_score * RECON_ATTACK_MULTIPLIER
    reason = (
        f"recon_attack_correlation: recon_events={recon_count} "
        f"attacks={active_attacks} "
        f"score {base_score:.0f}→{adjusted:.0f} (x{RECON_ATTACK_MULTIPLIER})"
    )
    return adjusted, reason


# ─── 3. Decisión y bloqueo ────────────────────────────────────────────────────

async def _block_user(user_id: str, score: float, redis) -> None:
    if user_id == "anonymous":
        return
    ttl = 60 * 60 * 24 if score >= SCORE_BLOCK else 60 * 60
    await redis.setex(f"blocked_user:{user_id}", ttl, "agent_defender")

async def _increment_global_blocks(redis) -> None:
    await redis.incr("adaptive:global_blocks")
    await redis.expire("adaptive:global_blocks", 86_400)


# ─── Punto de entrada principal ───────────────────────────────────────────────

# FIX: import movido al tope del archivo (ver arriba)
from api.core.redis_client import get_redis

async def analyze_behavior(
    user_id: str,
    action: dict,
    history: list,
    ip: str = None,
    long_history: list = None,  # FIX: default mutable [] → None
) -> dict:

    # FIX: default mutable resuelto acá
    if long_history is None:
        long_history = []

    redis = await get_redis()

    # 1. Contexto adaptativo
    ctx = await _load_context(user_id, ip or "unknown", redis)

    # 2. Reglas sobre historial corto
    total_score = 0
    razones = []
    for rule in RULES:
        try:
            if rule["check"](history, action):
                total_score += rule["score"]
                razones.append(rule["razon"])
        except Exception as e:
            logger.error("rule_error", extra={"error": str(e), "user_id": user_id})

    # 3. Correlación recon → ataque usando long_history
    final_score, correlation_reason = _correlate_recon_attack(long_history, razones, total_score)
    if correlation_reason:
        razones.append(correlation_reason)

    # 4. Decisión con umbrales adaptativos
    score_warn = ctx["score_warn"]
    score_block = ctx["score_block"]

    if final_score >= score_warn:
        decision = "BLOQUEADO" if final_score >= score_block else "SOSPECHOSO"
        razon_str = " + ".join(razones)

        await _block_user(user_id, final_score, redis)
        await _increment_global_blocks(redis)
        await alert_discord(decision, user_id, ip or "unknown", razon_str)

        logger.warning("agent_defender", extra={
            "user_id": user_id,
            "score": final_score,
            "razon": razon_str,
            "ip": ip,
            "action": str(action),
            "adaptive_flags": ctx["flags"],
            "correlation": correlation_reason,
        })
        _log_decision(
            user_id=user_id,
            ip=ip or "unknown",
            action=action,
            score=final_score,
            decision=decision,
            razones=razon_str,
            adaptive_flags=ctx["flags"],
            recon_correlated=bool(correlation_reason),
            history_len=len(history),
            long_history_len=len(long_history),
        )
        return {
            "decision": decision,
            "score": final_score,
            "razon": razon_str,
            "adaptive_flags": ctx["flags"],
        }

    logger.info("agent_defender", extra={
        "user_id": user_id,
        "score": final_score,
        "ip": ip,
        "action": str(action),
    })
    _log_decision(
        user_id=user_id,
        ip=ip or "unknown",
        action=action,
        score=final_score,
        decision="NORMAL",
        razones="comportamiento normal",
        adaptive_flags=ctx["flags"],
        recon_correlated=False,
        history_len=len(history),
        long_history_len=len(long_history),
    )
    return {
        "decision": "NORMAL",
        "score": final_score,
        "razon": "comportamiento normal",
        "adaptive_flags": ctx["flags"],
    }

# ─── Logging a PostgreSQL ─────────────────────────────────────────────────────

from api.db.database import SessionLocal
from api.models.agent_decision import AgentDecision
from datetime import datetime, timezone

def _log_decision(
    user_id: str,
    ip: str,
    action: dict,
    score: float,
    decision: str,
    razones: str,
    adaptive_flags: list,
    recon_correlated: bool,
    history_len: int,
    long_history_len: int,
) -> None:
    try:
        db = SessionLocal()
        record = AgentDecision(
            user_id=user_id,
            ip=ip,
            timestamp=datetime.now(timezone.utc),
            action_method=action.get("method"),
            action_path=action.get("path"),
            score=score,
            decision=decision,
            razones=razones,
            adaptive_flags=",".join(adaptive_flags) if adaptive_flags else "",
            recon_correlated=recon_correlated,
            history_len=history_len,
            long_history_len=long_history_len,
        )
        db.add(record)
        db.commit()
    except Exception as e:
        logger.error("ml_log_error", extra={"error": str(e)})
    finally:
        db.close()
