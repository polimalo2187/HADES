# scripts/start_data_feeder.py

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "data_feeder.server:app",
        host="0.0.0.0",
        port=9000,
        log_level="info",
    )
