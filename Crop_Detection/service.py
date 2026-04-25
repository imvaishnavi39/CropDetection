import os
import json
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
import google.generativeai as genai


class AgricultureChatbotService:
    """
    Advanced chatbot service for CropCare AI using Gemini API.
    Specializes in agriculture, crop care, and plant disease support.
    Features session-based memory, natural conversation, and expert guidance.
    """

    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")

        genai.configure(api_key=api_key)

        # Use Gemini Flash for fast responses
        self.model_name = "gemini-1.5-flash"

        # Advanced system prompt for agriculture expertise
        self.system_prompt = """
        You are AgriBot, an expert agricultural assistant for CropCare AI. You specialize in crop care, plant diseases, farming practices, and agricultural guidance.

        Your personality:
        - Friendly, knowledgeable, and approachable like a trusted farm advisor
        - Professional yet warm, like a seasoned agronomist
        - Patient and encouraging, especially for new farmers
        - Practical and actionable in all advice
        - Always emphasize safety and consulting local experts for critical decisions

        Your expertise areas:
        - Crop disease identification and treatment
        - Pest management and integrated pest control
        - Soil health and fertility management
        - Irrigation techniques and water conservation
        - Fertilizer recommendations and nutrient management
        - Seed selection and crop rotation strategies
        - Weather impact assessment and climate-smart farming
        - Organic farming practices and sustainable agriculture
        - Harvest timing and post-harvest handling
        - Market trends and price guidance

        Response guidelines:
        - Use natural, conversational language like ChatGPT
        - Provide detailed, accurate information with practical steps
        - Include specific recommendations with dosages, timings, and methods
        - Ask follow-up questions to gather more context when helpful
        - Use markdown formatting for clarity (headings, bullets, bold, tables)
        - Personalize responses using user's name and context when available
        - For disease identification: explain symptoms, causes, treatment, prevention
        - Always recommend professional consultation for serious issues
        - Stay current with modern agricultural practices and technology

        Memory context: You have access to conversation history and user preferences.
        Use this to provide personalized, contextual advice.

        Safety first: Never give medical advice for humans, only agricultural guidance.
        """

        # Memory cache key prefix
        self.memory_prefix = "chatbot_memory_"

    def initialize_chat(self, session_id: str) -> Dict[str, Any]:
        """
        Initialize or reset chat session memory.
        """
        memory_key = f"{self.memory_prefix}{session_id}"
        initial_memory = {
            'messages': [],
            'user_name': None,
            'crop_type': None,
            'farm_type': None,
            'language': 'en',
            'problems_discussed': [],
            'recommendations_given': [],
            'last_activity': time.time()
        }
        cache.set(memory_key, initial_memory, timeout=86400)  # 24 hours
        return initial_memory

    def get_memory(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve chat session memory.
        """
        memory_key = f"{self.memory_prefix}{session_id}"
        memory = cache.get(memory_key)
        if not memory:
            memory = self.initialize_chat(session_id)
        return memory

    def remember_user_data(self, session_id: str, key: str, value: Any) -> None:
        """
        Store user data in session memory.
        """
        memory = self.get_memory(session_id)
        memory[key] = value
        memory['last_activity'] = time.time()
        cache.set(f"{self.memory_prefix}{session_id}", memory, timeout=86400)

    def clear_memory(self, session_id: str) -> None:
        """
        Clear chat session memory.
        """
        memory_key = f"{self.memory_prefix}{session_id}"
        cache.delete(memory_key)

    def format_response(self, text: str) -> str:
        """
        Format response text (basic cleanup).
        """
        return text.strip()

    def _extract_user_info(self, message: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and remember user information from messages.
        """
        message_lower = message.lower()

        # Extract name
        if "my name is" in message_lower or "i am" in message_lower:
            # Simple name extraction - could be improved with NLP
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ["name", "am"] and i + 1 < len(words):
                    name = words[i + 1].strip(".,!")
                    if name and len(name) > 1:
                        memory['user_name'] = name.title()
                        break

        # Extract crop type
        crop_keywords = ["wheat", "rice", "tomato", "potato", "corn", "maize", "soybean", "cotton"]
        for crop in crop_keywords:
            if crop in message_lower:
                memory['crop_type'] = crop.title()
                break

        return memory

    def _build_context_prompt(self, memory: Dict[str, Any]) -> str:
        """
        Build context prompt from memory for personalized responses.
        """
        context_parts = []

        if memory.get('user_name'):
            context_parts.append(f"User's name: {memory['user_name']}")

        if memory.get('crop_type'):
            context_parts.append(f"Primary crop discussed: {memory['crop_type']}")

        if memory.get('farm_type'):
            context_parts.append(f"Farm type: {memory['farm_type']}")

        if memory.get('problems_discussed'):
            context_parts.append(f"Previous problems: {', '.join(memory['problems_discussed'])}")

        if memory.get('recommendations_given'):
            context_parts.append(f"Previous recommendations: {', '.join(memory['recommendations_given'])}")

        recent_messages = memory.get('messages', [])[-5:]  # Last 5 messages
        if recent_messages:
            context_parts.append("Recent conversation:")
            for msg in recent_messages:
                context_parts.append(f"- {msg['role']}: {msg['content'][:100]}...")

        return "\n".join(context_parts) if context_parts else "No previous context available."

    def get_chat_response(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Get chatbot response using Gemini API with memory context.
        """
        if not message or not message.strip():
            return {"reply": "Please type a message and I'll help you with your agricultural questions!", "error": None}

        try:
            # Get or initialize memory
            memory = self.get_memory(session_id)

            # Extract user info from message
            memory = self._extract_user_info(message, memory)

            # Build context
            context_prompt = self._build_context_prompt(memory)

            # Prepare full prompt
            full_prompt = f"""
{self.system_prompt}

CONTEXT FROM PREVIOUS CONVERSATION:
{context_prompt}

USER MESSAGE: {message}

Please provide a helpful, detailed response as AgriBot. Remember to be conversational, practical, and use markdown formatting when appropriate.
"""

            # Generate response using Gemini
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(full_prompt)

            reply = response.text.strip() if response.text else "I apologize, but I couldn't generate a response. Please try again."

            # Update memory
            memory['messages'].append({"role": "user", "content": message})
            memory['messages'].append({"role": "assistant", "content": reply})
            memory['last_activity'] = time.time()

            # Keep only last 20 messages to prevent memory bloat
            memory['messages'] = memory['messages'][-20:]

            # Save updated memory
            cache.set(f"{self.memory_prefix}{session_id}", memory, timeout=86400)

            return {"reply": self.format_response(reply), "error": None}

        except genai.types.generation_types.BlockedPromptException:
            return {"reply": "I apologize, but I cannot respond to that type of query. Please ask about agriculture, crop care, or plant diseases.", "error": "blocked_prompt"}

        except genai.types.generation_types.StopCandidateException:
            return {"reply": "I need more information to provide a complete answer. Could you please provide more details about your agricultural question?", "error": "incomplete_response"}

        except Exception as e:
            error_type = type(e).__name__
            if "quota" in str(e).lower():
                return {"reply": "I'm currently experiencing high demand. Please try again in a few minutes.", "error": "quota_exceeded"}
            elif "timeout" in str(e).lower() or "deadline" in str(e).lower():
                return {"reply": "The response is taking longer than expected. Please try rephrasing your question.", "error": "timeout"}
            else:
                return {"reply": "I encountered an issue processing your request. Please try again.", "error": f"api_error_{error_type}"}


# Global service instance
chatbot_service = AgricultureChatbotService()


# Django view integration functions
def initialize_chat_view(request):
    """
    Django view to initialize chat session.
    """
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    memory = chatbot_service.initialize_chat(session_id)
    return JsonResponse({"status": "initialized", "session_id": session_id})


def get_chat_response_view(request):
    """
    Django view to get chat response.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = request.session.session_key

        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        response = chatbot_service.get_chat_response(message, session_id)
        return JsonResponse(response)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)


def clear_chat_memory_view(request):
    """
    Django view to clear chat memory.
    """
    session_id = request.session.session_key
    if session_id:
        chatbot_service.clear_memory(session_id)
    return JsonResponse({"status": "memory_cleared"})


# AJAX/Fetch frontend example (to be added to base.html)
/*
JavaScript example for frontend integration:

async function sendChatMessage(message) {
    try {
        const response = await fetch('/chatbot/message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (data.error) {
            console.error('Chat error:', data.error);
            return 'Sorry, I encountered an error. Please try again.';
        }

        return data.reply;
    } catch (error) {
        console.error('Network error:', error);
        return 'Network error. Please check your connection and try again.';
    }
}

// Typing effect function
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.innerHTML = '';

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Usage example
const message = "How do I treat tomato blight?";
sendChatMessage(message).then(reply => {
    const chatBubble = document.createElement('div');
    chatBubble.className = 'chat-bubble';
    document.getElementById('chat-messages').appendChild(chatBubble);
    typeWriter(chatBubble, reply);
});
*/

# Suggestions to improve ChatGPT-like behavior:
"""
1. Implement streaming responses for real-time typing effect
2. Add conversation starters and suggested questions
3. Include emoji reactions and visual elements
4. Add voice input/output capabilities
5. Implement multi-language support
6. Add image analysis integration for disease photos
7. Include weather API integration for location-based advice
8. Add user feedback collection for response quality
9. Implement conversation summarization for long chats
10. Add integration with agricultural databases for up-to-date info
"""