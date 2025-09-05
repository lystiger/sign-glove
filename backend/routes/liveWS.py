"""
WebSocket API for real-time streaming of right-hand sensor data
(no AI prediction involved)
"""

import logging
import asyncio
import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("signglove")

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# ------------------- CONFIG -------------------
RATE_LIMIT_SECONDS = 0.03  # ~30 messages/sec per client
rate_limiter = {}

# ------------------- WEBSOCKET ENDPOINT -------------------
@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    client_ip = websocket.client.host
    await websocket.accept()
    logger.info(f"WebSocket connected: {client_ip}")

    try:
        while True:
            data_text = await websocket.receive_text()

            # Rate limiting
            current_time = time.time()
            last_time = rate_limiter.get(client_ip, 0)
            if current_time - last_time < RATE_LIMIT_SECONDS:
                continue
            rate_limiter[client_ip] = current_time

            try:
                payload = json.loads(data_text)
                right_values = payload.get("right", [])
                timestamp = payload.get("timestamp", time.time())

                if not right_values:
                    await websocket.send_json({"error": "No right-hand sensor data provided"})
                    continue

                # Simply forward the smoothed sensor values
                response = {
                    "timestamp": timestamp,
                    "right": right_values
                }

                await websocket.send_json(response)

            except json.JSONDecodeError:
                logger.warning(f"{client_ip}: invalid JSON received")
            except Exception as e:
                logger.error(f"{client_ip}: streaming error: {e}")
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_ip}")
        rate_limiter.pop(client_ip, None)
    except Exception as e:
        logger.error(f"WebSocket error ({client_ip}): {e}")
        await websocket.close()
