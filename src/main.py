from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aegis9")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AEGIS-9 Trading Engine...")
    yield
    logger.info("Shutting down AEGIS-9...")

app = FastAPI(title="AEGIS-9", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AEGIS-9"}

@app.get("/api/critic/status")
async def critic_status():
    from src.critic.critic_gate import CriticGateAuditor
    auditor = CriticGateAuditor()
    passed, results = auditor.audit_all()
    return {
        "overall_unlocked": passed,
        "modules": {k: {
            "score": v.weighted_total_score,
            "passed": v.passed_9_gate,
            "defects": v.blocking_defects
        } for k, v in results.items()}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)