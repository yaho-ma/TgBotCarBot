# Telegram Car Bot
It is a bot to help you get a car insurance

# Link to a Bot
@TgBotCarBot

## Technology Stack
- **python-telegram-bot** — for bot
- **mindee** — for processing documents

## Installation and Running

### 1. Clone the Repository
First, clone this repository:

```bash
git clone (https://github.com/yaho-ma/TgBotCarBot)
```

### 2. Set Up Environment Variables
Create a `.env` file and add your keys. TELEGRAM_API_KEY="your_key", MINDEE_API_KEY="your_key"

### 3. Create virtual environmevt
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install dependencies 
```bash
pip install -r requrements.txt
```

### 5. Run Bot
```bash
python main.py
```

# How it works
type /start to start interacting woth bot
or click t.me/TgBotCarBot?start=1

## Process of interaction with user
- User starts the bot with /start
- The bot prompts for a driver's license photo.
- The bot asks for a car photo (showing VIN).
- Mindee API processes the documents.
- The bot generates insurance quotes and asks for user confirmation.
- Once confirmed, the process is completed.






