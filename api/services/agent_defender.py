import logging
from datetime import datetime, timezone
from api.services.alert import alert_discord

logger = logging.getLogger("audit")

# ─── Umbrales base ─────────────────────────────────────────────────────────────
# Ya no se usan directamente en la decisión final — son los defaults
# que adaptive_thresholds ajusta según contexto.

SUSPICIOUS_PRODUCT_THRESHOLD = 50
SUSPICIOUS_HOUR_START = 2
SUSPICIOUS_HOUR_END = 5

SCORE_WARN = 60       # antes hardcodeado inline
SCORE_BLOCK = 90      # antes hardcodeado inline

# ─── Multiplicador recon → ataque ──────────────────────────────────────────────
RECON_ATTACK_MULTIPLIER = 3.0
RECON_MIN_EVENTS = 2
RECON_WINDOW_SECONDS = 86_400  # 24hs

# Qué paths/métodos en long_history cuentan como señal de recon
RECON_SIGNAL_PATHS = ["/products", "/api/internal", "/admin", "/debug"]
RECON_SIGNAL_METHOD = "GET"

# Qué reglas activas (razones) califican como "ataque activo"
ATTACK_RAZONES = {
    "scraping de productos",
    "modificó stock sin consultar producto",
    "secuencia repetitiva de acciones",
    "modificaciones de stock repetitivas",
}

# ─── Reglas de comportamiento ──────────────────────────────────────────────────

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


# ─── 1. Contexto adaptativo ────────────────────────────────────────────────────

import time

def _is_night_time() -> bool:
    return SUSPICIOUS_HOUR_START <= datetime.now(timezone.utc).hour <= SUSPICIOUS_HOUR_END

async def _load_context(user_id: str, ip: str, redis) -> dict:
    """
    Devuelve multiplicadores y umbrales ajustados según contexto actual.
    Factores: horario nocturno, presión global del sistema, reincidente.
    """
    multiplier = 1.0
    flags = []

    # Horario nocturno → más estricto
    if _is_night_time():
        multiplier *= 0.8
        flags.append("night_hours")

    # Presión global: cuántos bloqueos en las últimas 24hs
    global_blocks_raw = await redis.get("adaptive:global_blocks")
    global_blocks = int(global_blocks_raw) if global_blocks_raw else 0
    if global_blocks >= 50:
        multiplier *= 0.7
        flags.append(f"system_pressure(blocks={global_blocks})")

    # Reincidente: user_id o IP ya fue bloqueado antes
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
        # Umbrales ajustados — si multiplier < 1, los umbrales bajan
        "score_warn": max(30, SCORE_WARN * multiplier),
        "score_block": max(45, SCORE_BLOCK * multiplier),
    }


# ─── 2. Correlación recon → ataque ────────────────────────────────────────────

import json

def _count_recon_events(long_history: list) -> int:
    """
    Cuenta cuántos eventos en long_history son señales de recon
    dentro de la ventana de 24hs.
    """
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
    """
    Si hay recon previo en long_history + ataque activo ahora → multiplica score.
    Returns: (adjusted_score, reason_string | None)
    """
    # ¿Hay ataque activo en esta sesión?
    active_attacks = [r for r in active_razones if r in ATTACK_RAZONES]
    if not active_attacks:
        return base_score, None

    # ¿Hay recon previo suficiente?
    recon_count = _count_recon_events(long_history)
    if recon_count < RECON_MIN_EVENTS:
        return base_score, None

    # Correlación confirmada
    adjusted = base_score * RECON_ATTACK_MULTIPLIER
    reason = (
        f"recon_attack_correlation: recon_events={recon_count} "
        f"attacks={active_attacks} "
        f"score {base_score:.0f}→{adjusted:.0f} (x{RECON_ATTACK_MULTIPLIER})"
    )
    return adjusted, reason


# ─── 3. Decisión y bloqueo ────────────────────────────────────────────────────

async def _block_user(user_id: str, score: float, redis) -> None:
    """Escribe blocked_user en Redis con TTL según severidad del score."""
    if user_id == "anonymous":
        return
    ttl = 60 * 60 * 24 if score >= SCORE_BLOCK else 60 * 60
    await redis.setex(f"blocked_user:{user_id}", ttl, "agent_defender")

async def _increment_global_blocks(redis) -> None:
    await redis.incr("adaptive:global_blocks")
    await redis.expire("adaptive:global_blocks", 86_400)


# ─── Punto de entrada principal ───────────────────────────────────────────────

async def analyze_behavior(
    user_id: str,
    action: dict,
    history: list,
    ip: str = None,
    long_history: list = [],
) -> dict:

    from api.core.redis_client import get_redis
    redis = await get_redis()

    # 1. Contexto adaptativo
    ctx = await _load_context(user_id, ip or "unknown", redis)

    # 2. Reglas sobre historial corto (sin cambios respecto a lo que tenías)
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
    return {
        "decision": "NORMAL",
        "score": final_score,
        "razon": "comportamiento normal",
        "adaptive_flags": ctx["flags"],
    }