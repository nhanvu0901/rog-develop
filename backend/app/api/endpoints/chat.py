from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from backend.app.schemas.chat import ChatMessage, ChatResponse
from backend.app.services.chat_service import process_chat_message

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message and return a response
    """
    try:
        answer_msg = await process_chat_message(message.text)
        return ChatResponse(response=answer_msg)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """
    Handle WebSocket chat connections
    """
    await websocket.accept()
    while True:
        try:
            # Receive message from client
            received_text = await websocket.receive_text()
            message = ChatMessage.model_validate_json(received_text)
            # Process message
            answer_msg = await process_chat_message(message.text)
            
            # Send response back to client
            response = ChatResponse(response=answer_msg)
            await websocket.send_text(response.json())
            
        except WebSocketDisconnect:
            print("Client disconnected")
            break
        except Exception as e:
            # Send error message to client before closing
            error_response = ChatResponse(response=f"Error: {str(e)}")
            await websocket.send_text(error_response.json())
            break
                