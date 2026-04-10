from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.timezone import now
import uuid

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .utils import get_chatbot_response


@api_view(['POST'])
@permission_classes([AllowAny])
def start_chat_session(request):
    """Start a new chat session"""
    session_id = str(uuid.uuid4())
    
    session = ChatSession.objects.create(
        session_id=session_id,
        user=request.user if request.user.is_authenticated else None
    )
    
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """Send a message and get chatbot response"""
    session_id = request.data.get('session_id')
    user_message = request.data.get('message', '').strip()
    
    if not session_id or not user_message:
        return Response(
            {'error': 'session_id and message are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Save user message
    user_msg = ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message
    )
    
    # Get conversation history (last 10 messages)
    history = session.messages.all().order_by('-created_at')[:10]
    messages = [
        {'role': msg.role, 'content': msg.content}
        for msg in reversed(history)
    ]
    
    # Get response from ChatGPT
    assistant_response = get_chatbot_response(messages)
    
    # Save assistant response
    assistant_msg = ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=assistant_response
    )
    
    # Update session timestamp
    session.updated_at = now()
    session.save()
    
    return Response({
        'session_id': session_id,
        'user_message': ChatMessageSerializer(user_msg).data,
        'assistant_message': ChatMessageSerializer(assistant_msg).data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chat_history(request):
    """Get chat history for a session"""
    session_id = request.query_params.get('session_id')
    
    if not session_id:
        return Response(
            {'error': 'session_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    messages = ChatMessageSerializer(session.messages.all(), many=True)
    return Response({
        'session_id': session_id,
        'messages': messages.data,
    })
