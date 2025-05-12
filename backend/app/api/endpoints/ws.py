from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_ws_user
from app.services.kafka_service import KafkaService

router = APIRouter(prefix="/ws", tags=["WebSockets"])

@router.websocket("/notifications/{user_id}")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
    kafka_service: KafkaService = Depends(Provide[ApplicationContainer.services.kafka_service]),
):
    # Authenticate user
    user = await get_ws_user(websocket, user_id)
    if not user:
        await websocket.close(code=4000)
        return
    
    # Register connection
    await kafka_service.register_connection(str(user_id), websocket)
    
    try:
        # Keep connection open
        while True:
            # Wait for any client messages (could be used for ping/pong)
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Clean up on disconnect
        kafka_service.remove_connection(str(user_id)) 