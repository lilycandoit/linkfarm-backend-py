from flask_socketio import join_room, leave_room
from extensions import socketio
from flask import request

@socketio.on('join')
def on_join(data):
    """
    Allows a farmer to join a private room based on their farmer_id.
    This allows us to send real-time notifications to specific farmers.
    """
    farmer_id = data.get('farmer_id')
    if farmer_id:
        room = f"farmer_{farmer_id}"
        join_room(room)
        print(f"📡 [SOCKET] SID: {request.sid} JOINED ROOM: {room}")
    else:
        print(f"⚠️ [SOCKET] SID: {request.sid} attempted JOIN without farmer_id")

@socketio.on('leave')
def on_leave(data):
    """Allows a farmer to leave their private room."""
    farmer_id = data.get('farmer_id')
    if farmer_id:
        room = f"farmer_{farmer_id}"
        leave_room(room)
        print(f"📡 Client {request.sid} left room: {room}")

@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected: {request.sid}")
