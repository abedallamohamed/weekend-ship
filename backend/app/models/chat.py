from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    """Base model that serializes to camelCase JSON"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        by_alias=True
    )


class MessageRequest(BaseModel):
    """User message request"""
    message: str = Field(..., min_length=1, description="User message content")
    mode: str = Field(default='basic', description="Planning mode: 'basic' or 'detailed'")


class Task(CamelCaseModel):
    """A single task in the project timeline"""
    task: str
    essential: bool
    estimated_time: str
    completed: bool = False  # Track completion status on client side


class TimeBlock(CamelCaseModel):
    """A time block with associated tasks"""
    time_block: str
    tasks: List[Task]


class ProjectPlan(CamelCaseModel):
    """Structured project plan from AI"""
    project_overview: str
    tech_stack: List[str]
    timeline: List[TimeBlock]
    tips: List[str]


class Conversation(CamelCaseModel):
    """Chat conversation with user message and bot response"""
    id: str
    user_message: str
    bot_response: str
    project_plan: Optional[ProjectPlan] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationResponse(CamelCaseModel):
    """API response for a conversation"""
    id: str
    user_message: str
    bot_response: str
    project_plan: Optional[ProjectPlan] = None
    timestamp: datetime
