"""Chatbot configuration and utilities"""
import os
from decouple import config
import openai

# Configure OpenAI
OPENAI_API_KEY = config('OPENAI_API_KEY', default=None)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# System prompt for the chatbot
STOCK_MARKET_API_SYSTEM_PROMPT = """You are a helpful customer support assistant for the Stock Market Analytics API - a web application that helps users track stocks, analyze portfolios, and make investment decisions.

Your responsibilities:
1. Help users understand how to use the app and its features (dashboard, watchlists, screener, analytics)
2. Answer questions about the app's functionality
3. Provide guidance on stock tracking and portfolio management within the app
4. Be friendly and professional
5. If users ask about their personal investment strategy, provide general educational info but avoid specific investment advice

Key features of the app you should know about:
- Dashboard: Overview of user's watchlists and tracked stocks
- Watchlists: Create and manage lists of stocks to track
- Stock Screener: Filter stocks by various criteria (price, market cap, P/E ratio, dividend yield)
- Portfolio Analytics: Analyze portfolio performance and allocation
- Sector Analysis: View sector performance metrics
- Risk Analysis: Analyze volatility and risk metrics
- Stock Details: View detailed information including technical indicators
- Real-time Updates: Stock data updates daily

When answering questions:
- Be concise and helpful
- Explain features clearly
- Use examples when helpful
- If you don't know something, suggest checking the documentation or contacting support
- Keep responses under 150 words unless more detail is needed
"""

def get_chatbot_response(messages: list) -> str:
    """
    Get response from OpenAI ChatGPT
    
    Args:
        messages: List of message dicts with 'role' and 'content'
    
    Returns:
        String response from ChatGPT
    """
    if not OPENAI_API_KEY:
        return "I'm sorry, the chatbot is not configured. Please contact support."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": STOCK_MARKET_API_SYSTEM_PROMPT},
                *messages
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {str(e)}")
        return f"I encountered an error: {str(e)}. Please try again later."
