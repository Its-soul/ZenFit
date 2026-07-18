import logging
import argparse,hashlib
from app.ai.memory.migration import migrate_batch
from app.ai.memory.embeddings import embed_text as legacy_embed
from app.core.qdrant_client import USER_MEMORY_COLLECTION,get_qdrant_client
from qdrant_client.http.models import PointStruct
from app.config import settings

logging.basicConfig(level=logging.INFO); logger=logging.getLogger(__name__)
def seed_development():
    if settings.app_env.lower() not in {"development","test"}:raise RuntimeError("Development seeding is disabled outside development/test")
    user_id="00000000-0000-0000-0000-000000000001";rows=[("User has college Monday mornings.","adherence"),("User missed three Monday morning workouts.","adherence"),("User usually completes evening workouts.","workout")]
    points=[PointStruct(id=hashlib.sha256(text.encode()).hexdigest()[:32],vector=legacy_embed(text),payload={"user_id":user_id,"text":text,"category":category,"source":"development_seed","event_type":"development.memory","importance":.7}) for text,category in rows]
    get_qdrant_client().upsert(collection_name=USER_MEMORY_COLLECTION,points=points,wait=True);print(f"Seeded {len(points)} safe development memories into the old collection")
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--seed-development",action="store_true");args=parser.parse_args()
    if args.seed_development:seed_development()
    offset=None; total={"scanned":0,"already_migrated":0,"newly_migrated":0,"failed":0}
    while True:
        stats,offset=migrate_batch(offset)
        for key in total: total[key]+=stats[key]
        logger.info("Migration batch: %s",stats)
        if offset is None: break
    print(f"Old memories scanned: {total['scanned']}")
    print(f"Already migrated: {total['already_migrated']}")
    print(f"Newly migrated: {total['newly_migrated']}")
    print(f"Failed: {total['failed']}")
if __name__=="__main__": main()
