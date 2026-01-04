from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from datetime import datetime
from typing import Dict


# In-memory session storage (use Redis in production)
sessions: Dict[str, dict] = {}


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if session cookie exists
        session_id = request.cookies.get("session_id")
        
        # If no session or invalid session, create a new one
        if not session_id or session_id not in sessions:
            session_id = str(uuid4())
            sessions[session_id] = {
                "created_at": datetime.now().isoformat()
            }
        
        # Store session_id in request state for routes to access
        request.state.session_id = session_id
        
        # Process the request
        response: Response = await call_next(request)
        
        # Set/update cookie in response
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,  # Not accessible from JavaScript
            secure=False,   # Set to True in production with HTTPS
            samesite="lax", # CSRF protection
            max_age=86400 * 7  # 7 days
        )
        
        return response


def get_session_id(request: Request) -> str:
    """Get session_id from request state (set by middleware)"""
    return request.state.session_id
