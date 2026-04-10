# Stock Market API Chatbot Setup Guide

## Introduction

This guide explains how to set up and configure the OpenAI GPT-powered chatbot widget for your Stock Market Analytics application.

## ✅ What's Included

The chatbot includes:
- **Floating chat widget** - Bottom-right corner of every page
- **Customer support** - Answers questions about the app and stocks
- **Chat history** - Stores conversations for reference
- **OpenAI GPT-3.5 Turbo** - Advanced language understanding
- **Responsive design** - Works on mobile and desktop

## 🚀 Quick Setup (4 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

The `openai>=1.3.0` package should now be installed.

### Step 2: Get OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Sign up or log in with your account
3. Click "Create new secret key"
4. Copy the API key

### Step 3: Configure Environment Variables

Add to your `.env` file:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

Or set it as an environment variable:

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

**Windows CMD:**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### Step 4: Create Database Tables

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🔄 Restart Django Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 - you should see the **💬** chat button in the bottom-right corner!

---

## 📝 How to Use the Chatbot

### For Users

1. **Click the chat button** (💬) in the bottom-right corner
2. **Type your question** about the app or stocks
3. **Get instant responses** from the AI chatbot
4. **Continue the conversation** - the chatbot remembers context

### Example Conversations

- "How do I create a watchlist?"
- "What does the stock screener do?"
- "How do I analyze my portfolio?"
- "What are technical indicators?"
- "How do I add stocks to my dashboard?"

---

## 🛠️ Configuration

### Customize the Chatbot System Prompt

Edit [chatbot/utils.py](chatbot/utils.py) to change the chatbot's personality or information:

```python
STOCK_MARKET_API_SYSTEM_PROMPT = """
You are a helpful customer support assistant...
"""
```

### Change Chat Colors

Edit [static/css/chatbot.css](static/css/chatbot.css):

```css
:root {
  --chatbot-primary: #cc5500;      /* Orange */
  --chatbot-secondary: #3498db;    /* Blue */
  --chatbot-success: #27ae60;       /* Green */
  --chatbot-danger: #e74c3c;        /* Red */
}
```

### Change Model

In [chatbot/utils.py](chatbot/utils.py), change the model:

```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Change to gpt-4 for better quality (more expensive)
    ...
)
```

---

## 📊 Monitoring Chats

### Django Admin

View all chats at http://127.0.0.1:8000/admin/chatbot/

- See all chat sessions
- View message history
- Track user engagement

### API Endpoints

#### Start a Chat Session
```bash
POST /api/chatbot/start/
```

Response:
```json
{
  "id": 1,
  "session_id": "uuid-here",
  "messages": [],
  "created_at": "2026-04-10T10:00:00Z"
}
```

#### Send a Message
```bash
POST /api/chatbot/send/
Content-Type: application/json

{
  "session_id": "uuid-here",
  "message": "How do I create a watchlist?"
}
```

#### Get Chat History
```bash
GET /api/chatbot/history/?session_id=uuid-here
```

---

## 💰 OpenAI Pricing

**GPT-3.5 Turbo** (recommended for this app):
- **Input:** $0.50 per 1M tokens
- **Output:** $1.50 per 1M tokens

**Estimated costs:**
- 100 chats/day = ~$0.50-$1.00/month
- 1000 chats/day = ~$5-$10/month
- 10000 chats/day = ~$50-$100/month

**Money-saving tips:**
- Start with free tier ($5 credits)
- Set rate limits if needed
- Use gpt-3.5-turbo (cheaper than gpt-4)

---

## 🐛 Troubleshooting

### "Chatbot is not configured"

**Problem:** You see this error message

**Solution:** 
- Check `OPENAI_API_KEY` is set correctly
- Restart Django server after setting the key
- Verify the key in `.env` file or environment variables

### Chatbot doesn't respond

**Problem:** Messages sent but no response

**Solutions:**
1. **Check internet connection** - API calls need internet
2. **Verify OpenAI account** - Make sure you have credits
3. **Check logs** - Look for error messages in terminal
4. **Verify API key** - Test at https://platform.openai.com/account/api-keys

### Widget not showing

**Problem:** Chat button doesn't appear on page

**Solutions:**
1. **Check static files** - Run `python manage.py collectstatic`
2. **Clear browser cache** - Press `Ctrl+Shift+Delete`
3. **Verify settings** - Check `DEBUG = True` in settings.py
4. **Check browser console** - Look for JavaScript errors (F12)

---

## ✨ Advanced Features

### Custom Context

Make the chatbot smarter by including user-specific info:

```python
# In chatbot/views.py
user_info = f"User: {request.user.username}"
if request.user.is_authenticated:
    watchlist_count = Watchlist.objects.filter(user=request.user).count()
    user_info += f"\nWatchlists: {watchlist_count}"
```

### Rate Limiting

Prevent abuse by adding rate limits:

```python
# In requirements.txt
djangorestframework-simplejwt>=5.3.0
django-ratelimit>=4.1.0

# In views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='POST')
def send_message(request):
    ...
```

### Multilingual Support

Translate chatbot responses:

```python
from django.utils.translation import gettext as _

message = _("Welcome to the Stock Market API")
```

---

## 📚 Resources

- **OpenAI Docs:** https://platform.openai.com/docs/
- **Django Tutorial:** https://docs.djangoproject.com/
- **Chat API Reference:** https://platform.openai.com/docs/api-reference/chat

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Get OpenAI API key
3. ✅ Set environment variables
4. ✅ Run migrations
5. ✅ Start Django server
6. ✅ Test chatbot on your app
7. 🎉 Deploy to production!

---

## Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review Django debug output (usually shows helpful errors)
3. Test API endpoints with curl or Postman
4. Check OpenAI API status at https://status.openai.com/

---

**Last Updated:** April 10, 2026  
**Version:** 1.0  
**Status:** ✅ Ready for Production
