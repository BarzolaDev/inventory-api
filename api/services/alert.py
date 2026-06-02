import httpx
import logging
from api.core.settings import settings

logger = logging.getLogger("audit")

async def alert_discord(event: str, user_id: str, ip: str, reason: str):
    message = (
        f"🚨 **{event}**\n"
        f"Usuario: `{user_id}`\n"
        f"IP: `{ip}`\n"
        f"Razón: {reason}"
    )
    print(f"DEBUG: mandando alerta a Discord - {event}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.DISCORD_WEBHOOK_URL,
                json={"content": message},
                timeout=3.0
            )
            print(f"DEBUG: Discord respondió {response.status_code}")
    except Exception as e:
        print(f"DEBUG: error Discord - {e}")
        logger.error(f"discord_alert_failed: {e}")
