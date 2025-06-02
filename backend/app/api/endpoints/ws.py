from uuid import UUID
import logging
import asyncio
import time

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_ws_user
from app.services.kafka_service import KafkaService

router = APIRouter(prefix="/ws", tags=["WebSockets"])
logger = logging.getLogger(__name__)

@router.websocket("/notifications/{user_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
    kafka_service: KafkaService = Depends(Provide[ApplicationContainer.services.kafka_service]),
):
    user = await get_ws_user(websocket, user_id)
    if not user:
        logger.warning(f"User authentication failed for WebSocket connection: {user_id}")
        await websocket.close(code=4000)
        return

    try:
        await kafka_service.register_connection(str(user_id), websocket)
        logger.info(f"WebSocket connection established for user {user_id}")

        await websocket.send_json({"type": "connection", "status": "connected", "user_id": str(user_id)})

        heartbeat_task = asyncio.create_task(send_heartbeat(websocket, user_id))

        try:
            while True:
                data = await websocket.receive_text()
                logger.debug(f"Received message from client {user_id}: {data}")

                if data == "pong":
                    logger.debug(f"Received heartbeat response from user {user_id}")

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"Error in WebSocket connection for user {user_id}: {str(e)}")
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

            kafka_service.remove_connection(str(user_id))
            logger.info(f"WebSocket connection removed for user {user_id}")

    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection for user {user_id}: {str(e)}")
        await websocket.close(code=1011)

async def send_heartbeat(websocket: WebSocket, user_id: UUID):
    try:
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_json({"type": "heartbeat", "timestamp": time.time()})
                logger.debug(f"Heartbeat sent to user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to send heartbeat to user {user_id}: {str(e)}")
                break
    except asyncio.CancelledError:
        logger.debug(f"Heartbeat task cancelled for user {user_id}")
        raise