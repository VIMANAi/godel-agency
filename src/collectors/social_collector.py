"""
SAIEL System - Social Media Data Collector
Recoge publicaciones y comentarios de perfiles públicos de Instagram/Facebook.
Soporta un diseño híbrido:
1. Apify API (SaaS) si se provee token.
2. Local Replay: Carga y filtra registros reales existentes en data/raw/ para pruebas rápidas.
3. Scraping directo local (httpx/Playwright) con fallback sintético usando Faker.

Autor: SAIEL Intelligence System
Versión: 2.5 (Dynamic & Hybrid OSINT)
"""

import json
import hashlib
import argparse
import os
from uuid import uuid4
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from faker import Faker

# Cargar variables de entorno
load_dotenv()

class SocialCollector:
    """
    Motor híbrido de recolección de comentarios de redes sociales
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        # Determinar ruta base del proyecto de forma dinámica
        if base_path:
            self.base_path = Path(base_path)
        else:
            env_base = os.getenv("SAIEL_BASE_PATH")
            if env_base:
                self.base_path = Path(env_base)
            else:
                self.base_path = Path(__file__).resolve().parents[2]
                
        self.raw_dir = self.base_path / "data" / "raw"
        self.legacy_raw_dir = self.base_path / "20_00_DATA" / "20_10_RAW"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.legacy_raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Token opcional de Apify
        self.apify_token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_TOKEN")
        self.fake = Faker('es_MX')
        self.ingestion_run_id = f"run_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}"

    def collect_via_apify(self, target: str, platform: str, limit: int) -> List[Dict]:
        """Recolección utilizando la API de Apify"""
        if not self.apify_token or "REDACTED" in self.apify_token or "TU_TOKEN" in self.apify_token:
            print("[Advertencia] APIFY_API_TOKEN/APIFY_TOKEN no configurado. Evitando canal Apify.")
            return []
            
        try:
            from apify_client import ApifyClient
            client = ApifyClient(self.apify_token)
            actor_by_platform = {
                "instagram": "apify/instagram-comment-scraper",
                "facebook": "apify/facebook-comments-scraper",
            }
            actor_id = actor_by_platform.get(platform.lower(), "apify/facebook-comments-scraper")
            
            profile_url = target
            if not target.startswith("http"):
                if platform == "instagram":
                    profile_url = f"https://www.instagram.com/{target}/"
                else:
                    profile_url = f"https://www.facebook.com/{target}/"
                    
            run_input = {
                "directUrls": [profile_url],
                "resultsLimit": limit,
            }
            
            print(f"Llamando a Apify Actor para {target}...")
            run = client.actor(actor_id).call(run_input=run_input, timeout=60)
            
            data = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                published_at = item.get("timestamp", datetime.now().isoformat())
                entity_id = item.get("id", self._make_entity_id(item.get("text", ""), published_at))
                record = {
                    "id": entity_id,
                    "source": platform,
                    "target": target,
                    "candidate": target,
                    "user": item.get("ownerUsername"),
                    "user_id": item.get("ownerId"),
                    "text": item.get("text", ""),
                    "date": published_at,
                    "likes": item.get("likesCount", 0),
                    "shares": item.get("sharesCount", 0),
                    "comments": item.get("commentsCount", 0),
                    "collected_at": datetime.now().isoformat(),
                    "source_platform": platform,
                    "entity_type": "comment",
                    "entity_id": entity_id,
                    "parent_post_id": item.get("postId"),
                    "candidate_id": self._make_candidate_id(target),
                    "candidate_name": target,
                    "reaction_count": item.get("likesCount", 0),
                    "comment_count": item.get("commentsCount", 0),
                    "share_count": item.get("sharesCount", 0),
                    "published_at": published_at,
                    "url": item.get("url"),
                    "ingestion_run_id": self.ingestion_run_id,
                    "is_synthetic": False
                }
                record["raw_hash"] = self._calculate_raw_hash(record)
                data.append(record)
            return data
        except Exception as e:
            print(f"[Error Apify] {e}")
            return []

    def collect_via_replay(self, target: str, platform: str, limit: int) -> List[Dict]:
        """
        Local Replay: Escanea los archivos JSON/JSONL reales existentes en data/raw/
        y extrae una muestra filtrada por candidato para simular recolección real.
        """
        print(f"Iniciando Local Replay para candidato '{target}'...")
        all_comments = []
        
        raw_roots = [self.raw_dir, self.legacy_raw_dir]
        for raw_root in raw_roots:
            if not raw_root.exists():
                continue
            for file_path in raw_root.rglob("*.json*"):
                if file_path.name.endswith(('_processed.json', '_rejected.json')):
                    continue
                if not file_path.is_file():
                    continue
                try:
                    if file_path.suffix == ".json":
                        with open(file_path, "r", encoding="utf-8") as f:
                            records = json.load(f)
                            if isinstance(records, list):
                                for r in records:
                                    cand = r.get("candidate", r.get("candidato", ""))
                                    if self._matches_target(cand, target):
                                        all_comments.append(r)
                    elif file_path.suffix == ".jsonl":
                        with open(file_path, "r", encoding="utf-8") as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                try:
                                    r = json.loads(line)
                                except json.JSONDecodeError:
                                    continue
                                cand = r.get("candidate", r.get("candidato", ""))
                                if self._matches_target(cand, target):
                                    all_comments.append(r)
                except Exception:
                    pass
                
        if all_comments:
            print(f"[Replay] Se encontraron {len(all_comments)} registros históricos.")
            # Limitar y mapear a estructura estándar
            sampled = all_comments[:limit]
            formatted = []
            for item in sampled:
                published_at = item.get("date", item.get("timestamp", datetime.now().isoformat()))
                text = item.get("text", item.get("comment", ""))
                entity_id = item.get("entity_id", item.get("id", self._make_entity_id(text, published_at)))
                formatted.append({
                    "id": item.get("id", item.get("_id", self._make_entity_id(text, published_at))),
                    "source": platform,
                    "target": target,
                    "candidate": target,
                    "user": item.get("user", item.get("ownerUsername")),
                    "user_id": item.get("user_id", item.get("ownerId")),
                    "text": text,
                    "date": published_at,
                    "likes": int(item.get("likes", item.get("likesCount", 0))),
                    "shares": int(item.get("shares", item.get("sharesCount", 0))),
                    "comments": int(item.get("comments", item.get("commentsCount", 0))),
                    "collected_at": datetime.now().isoformat(),
                    "source_platform": platform,
                    "entity_type": item.get("entity_type", "comment"),
                    "entity_id": entity_id,
                    "parent_post_id": item.get("parent_post_id", item.get("postId")),
                    "candidate_id": item.get("candidate_id", self._make_candidate_id(target)),
                    "candidate_name": item.get("candidate_name", target),
                    "reaction_count": int(item.get("likes", item.get("likesCount", 0))),
                    "comment_count": int(item.get("comments", item.get("commentsCount", 0))),
                    "share_count": int(item.get("shares", item.get("sharesCount", 0))),
                    "published_at": item.get("published_at", published_at),
                    "url": item.get("url"),
                    "ingestion_run_id": item.get("ingestion_run_id", self.ingestion_run_id),
                    "is_synthetic": bool(item.get("is_synthetic", False))
                })
                formatted[-1]["raw_hash"] = self._calculate_raw_hash(formatted[-1])
            return formatted
        return []

    def collect_via_local_direct(self, target: str, platform: str, limit: int, allow_synthetic: bool = False) -> List[Dict]:
        """
        Scraping directo local (httpx) de páginas de debate/noticias de Tepic.
        Genera un fallback sintético enriquecido con Faker si hay bloqueos de login.
        """
        print(f"Ejecutando Scraping Directo Local para '{target}'...")
        
        # Intentar scraping ligero de portales locales abiertos
        web_fragments = []
        try:
            # Simulamos consulta a buscador de noticias o posts
            url = f"https://www.google.com/search?q={target}+tepic+nayarit+debate"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = httpx.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # Extraemos algunos snippets como comentarios reales
                soup = BeautifulSoup(response.text, 'html.parser')
                web_fragments = [div.text for div in soup.find_all('div') if len(div.text) > 40][:5]
                if web_fragments:
                    print(f"Scrapeados {len(web_fragments)} fragmentos web reales.")
        except Exception:
            pass
        
        if web_fragments:
            data = []
            for i, text in enumerate(web_fragments[:limit]):
                published_at = (datetime.now() - timedelta(hours=i)).isoformat()
                record = {
                    "id": self._make_entity_id(text, published_at),
                    "source": platform,
                    "target": target,
                    "candidate": target,
                    "user": None,
                    "user_id": None,
                    "text": text,
                    "date": published_at,
                    "likes": 0,
                    "shares": 0,
                    "comments": 0,
                    "collected_at": datetime.now().isoformat(),
                    "source_platform": platform,
                    "entity_type": "post",
                    "entity_id": self._make_entity_id(text, published_at),
                    "parent_post_id": None,
                    "candidate_id": self._make_candidate_id(target),
                    "candidate_name": target,
                    "reaction_count": 0,
                    "comment_count": 0,
                    "share_count": 0,
                    "published_at": published_at,
                    "url": url,
                    "ingestion_run_id": self.ingestion_run_id,
                    "is_synthetic": False
                }
                record["raw_hash"] = self._calculate_raw_hash(record)
                data.append(record)
            return data

        if not allow_synthetic:
            print("[Direct Scraping] Sin datos públicos disponibles y synthetic deshabilitado.")
            return []

        print("[Direct Scraping Fallback] Generando comentarios sociales enriquecidos sintéticos...")
        
        candidatos_contexto = {
            'geraldine': {
                'partido': 'MORENA',
                'positivos': ['Excelente alcaldesa para Tepic', 'Se ven los cambios en la ciudad', 'Gran apoyo a Geraldine', 'Sigue adelante por Tepic'],
                'negativos': ['Tepic sigue lleno de baches', 'Pura publicidad y nada de acción', 'No hay transparencia', 'Falta mucha seguridad en las colonias']
            },
            'adahan': {
                'partido': 'PAN_PRI_PRD',
                'positivos': ['El mejor candidato para levantar Tepic', 'Adahan tiene experiencia', 'Propuestas reales por Nayarit', 'Todo el apoyo de la alianza'],
                'negativos': ['Puro corrupto en esa coalición', 'Ya gobernaron y no hicieron nada', 'No tienen credibilidad', 'Representa al viejo sistema']
            },
            'ivideliza': {
                'partido': 'MC',
                'positivos': ['Movimiento Ciudadano la mejor opción', 'Ivideliza es una mujer de propuestas', 'Tepic necesita una alternativa nueva', 'Gran líder honesta'],
                'negativos': ['MC solo divide el voto', 'No tiene estructura para ganar', 'Pura campaña en redes y nada de calle', 'Falsas promesas de siempre']
            }
        }
        
        # Determinar contexto según el candidato
        cand_key = 'default'
        for k in candidatos_contexto.keys():
            if k in target.lower():
                cand_key = k
                break
                
        data = []
        for i in range(limit):
            # Generar sentiment
            if cand_key != 'default':
                ctx = candidatos_contexto[cand_key]
                sentiment = self.fake.random_element(['pos', 'neg', 'neu'])
                if sentiment == 'pos':
                    text = self.fake.random_element(ctx['positivos'])
                elif sentiment == 'neg':
                    text = self.fake.random_element(ctx['negativos'])
                else:
                    text = f"Hoy el candidato {target} estuvo recorriendo colonias en Tepic."
            else:
                text = f"Comentario número {i} sobre el candidato {target} en Tepic, Nayarit."
                
            # Generar likes/comments aleatorios
            likes = int(self.fake.random_element([0, 1, 5, 20, 150, 950])) # incluye outliers para testear IQR
            comments = int(self.fake.random_element([0, 1, 2, 10, 45]))
            
            data.append({
                "id": self.fake.md5()[:16],
                "source": platform,
                "target": target,
                "candidate": target,
                "user": self.hash_username(self.fake.user_name()) if i % 3 == 0 else self.fake.user_name(), # bots repetidos
                "user_id": self.fake.md5()[:8],
                "text": text,
                "date": (datetime.now() - timedelta(days=i)).isoformat(), # Fechas cronológicas
                "likes": likes,
                "shares": int(likes * 0.1),
                "comments": comments,
                "collected_at": datetime.now().isoformat(),
                "source_platform": platform,
                "entity_type": "comment",
                "entity_id": self._make_entity_id(text, (datetime.now() - timedelta(days=i)).isoformat()),
                "parent_post_id": None,
                "candidate_id": self._make_candidate_id(target),
                "candidate_name": target,
                "reaction_count": likes,
                "comment_count": comments,
                "share_count": int(likes * 0.1),
                "published_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "url": None,
                "ingestion_run_id": self.ingestion_run_id,
                "is_synthetic": True
            })
            data[-1]["raw_hash"] = self._calculate_raw_hash(data[-1])
            
        return data

    def hash_username(self, value: str) -> str:
        """Helper para emular bots de repetición en testeo"""
        return "spammer_bot_tepic"

    def _matches_target(self, candidate_value: Any, target: str) -> bool:
        normalized_target = target.strip().lower()
        if not normalized_target:
            return False
        if candidate_value is None or str(candidate_value).strip() == "":
            return False
        return normalized_target in str(candidate_value).lower()

    def _make_candidate_id(self, candidate_name: str) -> str:
        return hashlib.sha256(candidate_name.strip().lower().encode("utf-8")).hexdigest()[:24]

    def _make_entity_id(self, text: str, published_at: str) -> str:
        value = f"{text}|{published_at}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]

    def _calculate_raw_hash(self, payload: Dict[str, Any]) -> str:
        canon = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()

    def _save_to_raw(self, data: List[Dict], filename: str, platform: str, is_synthetic: bool):
        """Guarda comentarios separando datos reales y sintéticos"""
        data_tier = "synthetic" if is_synthetic else "real"
        output_paths = [
            self.raw_dir / platform / data_tier / filename,
            self.legacy_raw_dir / platform / data_tier / filename,
        ]
        for save_path in output_paths:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✓ Datos de recolección guardados en capas raw ({data_tier}): {output_paths[0]}")

    def collect_social_data(self, target: str, platform: str = "instagram", limit: int = 20, mode: str = "default") -> List[Dict]:
        """
        Orquesta la recolección delegando en el canal correcto según configuración y disponibilidad
        """
        print(f"\n--- INICIANDO CAPA DE RECOLECCIÓN OSINT [Target: {target}] ---")
        data = []
        
        platform = platform.lower().strip()

        # 1. Modo Forzado Replay (útil para no consumir recursos)
        if mode == "replay":
            data = self.collect_via_replay(target, platform, limit)
            
        # 2. Modo Apify SaaS (si tiene token)
        elif self.apify_token and mode in {"default", "apify"}:
            data = self.collect_via_apify(target, platform, limit)
            
        # 3. Fallback / Modo Local Directo (sin synthetic por defecto)
        if not data:
            # Primero intentar Replay de históricos si el modo no es estrictamente local
            if mode == "default":
                data = self.collect_via_replay(target, platform, limit)
            
            # Si no hay datos históricos, intentar raspado local sin synthetic
            if not data:
                allow_synthetic = mode in {"local", "synthetic"}
                data = self.collect_via_local_direct(target, platform, limit, allow_synthetic=allow_synthetic)
                
        # Guardar en data/raw
        if data:
            filename = f"raw_{platform}_{target.lower().replace(' ', '_')}.json"
            synthetic_data = [record for record in data if record.get("is_synthetic", False)]
            real_data = [record for record in data if not record.get("is_synthetic", False)]

            if real_data:
                self._save_to_raw(real_data, filename, platform, is_synthetic=False)
            if synthetic_data:
                self._save_to_raw(synthetic_data, filename, platform, is_synthetic=True)
            
        return data

# --- CLI ENTRYPOINT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collector OSINT de Redes Sociales - SAIEL")
    parser.add_argument("--target", type=str, required=True, help="Nombre del candidato o URL a evaluar")
    parser.add_argument("--source", type=str, default="facebook", help="Plataforma de origen (instagram, facebook)")
    parser.add_argument("--limit", type=int, default=20, help="Cantidad de comentarios a recolectar")
    parser.add_argument("--mode", type=str, default="default", choices=["default", "replay", "apify", "local", "synthetic"], help="Estrategia de recolección")
    
    args = parser.parse_args()
    
    collector = SocialCollector()
    collector.collect_social_data(
        target=args.target,
        platform=args.source,
        limit=args.limit,
        mode=args.mode
    )
