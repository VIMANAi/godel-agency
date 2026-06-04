"""
Utilidades compartidas para integración con Apify.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from apify_client import ApifyClient


def get_apify_token() -> str | None:
    """Obtiene token de Apify desde variables de entorno estándar."""
    return os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_TOKEN")


def get_actor_id(platform: str) -> str:
    """Mapea plataforma a actor oficial de Apify."""
    actor_by_platform = {
        "instagram": "apify/instagram-comment-scraper",
        "facebook": "apify/facebook-comments-scraper",
    }
    return actor_by_platform.get((platform or "").lower(), "apify/facebook-comments-scraper")


def build_profile_url(target: str, platform: str) -> str:
    """Normaliza target (usuario o URL) a URL de perfil."""
    platform_normalized = (platform or "instagram").lower()
    if target.startswith("http"):
        return target
    if platform_normalized == "instagram":
        return f"https://www.instagram.com/{target}/"
    return f"https://www.facebook.com/{target}/"


def fetch_actor_items(token: str, target: str, platform: str, limit: int, timeout: int = 60) -> List[Dict[str, Any]]:
    """Ejecuta actor de Apify y devuelve items de dataset."""
    if not token:
        raise ValueError("APIFY_API_TOKEN/APIFY_TOKEN no configurado")

    client = ApifyClient(token)
    actor_id = get_actor_id(platform)
    run_input = {
        "directUrls": [build_profile_url(target, platform)],
        "resultsLimit": limit,
    }
    run = client.actor(actor_id).call(run_input=run_input, timeout=timeout)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())
