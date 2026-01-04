from app.models.chat import Conversation, MessageRequest, ProjectPlan
from app.prompts.system_prompts import WEEKEND_PLANNER_BASIC_PROMPT, WEEKEND_PLANNER_DETAILED_PROMPT, CONVERSATION_PROMPT
from datetime import datetime
from typing import List, Optional, Dict
import uuid
import os
import json
from openai import AsyncOpenAI


class MessageService:
    def __init__(self):
        # In-memory storage (can be replaced with DB)
        # Dict indexed by user_id: {user_id: [Conversation, ...]}
        self.conversations: Dict[str, List[Conversation]] = {}
        # Initialize OpenAI client
        open_api_key = os.getenv("OPENAI_API_KEY")
        print(f"OpenAI API Key: {open_api_key}")
        self.openai_client = AsyncOpenAI(api_key=open_api_key)
    
    def _extract_json_string(self, content: str) -> Optional[str]:
        """Extract JSON string from content that may be wrapped in markdown code blocks"""
        if not content:
            return None
        
        # Try different patterns in order of specificity
        
        # 1. Look for ```json ... ``` pattern
        if '```json' in content:
            json_start = content.find('```json') + 7
            json_end = content.find('```', json_start)
            if json_end != -1:
                return content[json_start:json_end].strip()
        
        # 2. Look for ``` ... ``` (generic code block)
        if '```' in content:
            first_triple = content.find('```')
            # Skip the opening ``` and any language identifier
            json_start = content.find('\n', first_triple) + 1
            json_end = content.find('```', json_start)
            if json_end != -1:
                potential_json = content[json_start:json_end].strip()
                # Verify it starts with { and ends with }
                if potential_json.startswith('{') and potential_json.endswith('}'):
                    return potential_json
        
        # 3. Try to find JSON object by matching braces (more robust)
        # Find first { and matching closing }
        json_start = content.find('{')
        if json_start != -1:
            brace_count = 0
            json_end = json_start
            for i in range(json_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            
            if json_end > json_start:
                return content[json_start:json_end]
        
        return None
    
    async def process_user_message(self, message_data: MessageRequest, user: str) -> Conversation:
        """Process user message and generate bot response"""
        
        # Get mode from message_data, default to 'basic' if not present
        mode = getattr(message_data, 'mode', 'basic')
        
        # Generate AI response with conversation context and mode
        bot_response, project_plan = await self._generate_bot_response(message_data.message, user, mode)
        
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_message=message_data.message,
            bot_response=bot_response,
            project_plan=project_plan,
            timestamp=datetime.now()
        )
        
        # Initialize user conversation list if not present
        if user not in self.conversations:
            self.conversations[user] = []
        
        self.conversations[user].append(conversation)
        return conversation
    
    async def _generate_bot_response(self, user_message: str, user: str, mode: str = 'basic') -> tuple[str, Optional[ProjectPlan]]:
        """Generate a response using OpenAI API and parse the project plan"""
        
        try:
            # Determine if this is a planning request or a conversation
            user_conversations = self.conversations.get(user, [])
            has_existing_plan = any(conv.project_plan for conv in user_conversations)
            
            # Choose the appropriate system prompt based on mode and context
            if has_existing_plan:
                system_prompt = CONVERSATION_PROMPT
            else:
                # Use mode to determine which planning prompt
                if mode == 'detailed':
                    system_prompt = WEEKEND_PLANNER_DETAILED_PROMPT
                else:
                    system_prompt = WEEKEND_PLANNER_BASIC_PROMPT
            
            # Build message history for context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 10 exchanges to keep context manageable)
            for conv in user_conversations[-10:]:
                messages.append({"role": "user", "content": conv.user_message})
                
                # Build assistant response in unified JSON format
                assistant_json = {
                    "message": conv.bot_response,
                    "projectPlan": conv.project_plan.model_dump(by_alias=True) if conv.project_plan else None
                }
                
                messages.append({"role": "assistant", "content": json.dumps(assistant_json)})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Set max_tokens based on prompt type and mode
            if has_existing_plan:
                max_tokens = 2000  # Conversation mode
            else:
                # Planning mode - check mode for token allocation
                max_tokens = 6000 if mode == 'detailed' else 3000  # Double tokens for detailed mode
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7, # Creativity level (0.7-0.9 for planning)
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Parse the unified JSON response format
            project_plan = None
            bot_response = content  # Fallback to raw content if parsing fails
            
            try:
                json_str = self._extract_json_string(content)
                
                if json_str:
                    response_data = json.loads(json_str)
                    
                    # Extract message
                    bot_response = response_data.get('message', content)
                    
                    # Extract project plan if present
                    plan_data = response_data.get('projectPlan')
                    if plan_data:
                        project_plan = ProjectPlan(**plan_data)
                        
            except (json.JSONDecodeError, ValueError) as e:
                # If JSON parsing fails, use the full response as text
                print(f"Failed to parse JSON response: {e}")
                bot_response = content
            
            return bot_response, project_plan
        
        except Exception as e:
            # In case of error, return a fallback message
            return f"Sorry, an error occurred while processing your request: {str(e)}", None
    
    async def get_conversations(self, user: Optional[str] = None) -> List[Conversation]:
        """Get all conversations, optionally filtered by user"""
        if user:
            return self.conversations.get(user, [])
        # Restituisci tutte le conversazioni di tutti gli utenti
        all_conversations = []
        for user_conversations in self.conversations.values():
            all_conversations.extend(user_conversations)
        return all_conversations
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a specific conversation by ID"""
        for user_conversations in self.conversations.values():
            for conv in user_conversations:
                if conv.id == conversation_id:
                    return conv
        return None
    
    async def clear_user_conversations(self, user: str) -> bool:
        """Clear all conversations for a specific user"""
        if user in self.conversations:
            self.conversations[user] = []
            return True
        return False
    
    async def update_task_completion(
        self, 
        conversation_id: str, 
        user: str, 
        time_block_index: int, 
        task_index: int, 
        completed: bool
    ) -> bool:
        """Update the completion status of a specific task in a conversation"""
        user_conversations = self.conversations.get(user, [])
        
        # Find the conversation
        for conv in user_conversations:
            if conv.id == conversation_id and conv.project_plan:
                # Validate indices
                if (0 <= time_block_index < len(conv.project_plan.timeline) and
                    0 <= task_index < len(conv.project_plan.timeline[time_block_index].tasks)):
                    # Update the task completion status
                    conv.project_plan.timeline[time_block_index].tasks[task_index].completed = completed
                    return True
        
        return False


# Singleton instance
message_service = MessageService()
