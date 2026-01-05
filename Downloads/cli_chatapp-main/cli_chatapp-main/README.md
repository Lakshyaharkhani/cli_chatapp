# Redis CLI Chat Application

A simple but powerful CLI chat application using Upstash Redis for persistent messaging.

## Features

- ✅ **Single Chat Room** - One unified chat space for all users
- ✅ **Custom Usernames** - Choose any username when joining
- ✅ **Message History** - View last 20 messages with timestamps
- ✅ **Interactive Mode** - Easy-to-use command interface
- ✅ **Background Streaming** - Real-time message updates while typing
- ✅ **Timestamps** - Each message includes exact timestamp
- ✅ **Colorized Output** - Beautiful terminal UI with colors

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

The `.env` file is already configured with your Upstash credentials:

```
UPSTASH_REDIS_REST_URL="https://glad-coyote-12496.upstash.io"
UPSTASH_REDIS_REST_TOKEN="ATDQAAIncDJkMGMyZGE3MTViYjI0NWMyYmU2YzA0NWY2OWViNDM0YXAyMTI0OTY"
```

### 3. Run the Application

```bash
python chat.py
```

## How to Use

1. **Start the app** and enter your username
2. **Send messages** - Just type and press Enter
3. **View history** - Type `/history` to see recent messages
4. **Get help** - Type `/help` for command list
5. **Exit** - Type `/quit` or press Ctrl+C

## Commands

| Command | Description |
|---------|-------------|
| `/history` | Display last 20 messages |
| `/help` | Show help menu |
| `/quit` | Exit the application |
| Any text | Send a message |

## Message Format

Each message stores:
- **Username** - Who sent it
- **Message** - The actual message content
- **Timestamp** - When it was sent (YYYY-MM-DD HH:MM:SS)

## How It Works

- Messages are stored in Upstash Redis using a list (LPUSH)
- Background thread checks for new messages every 1 second
- New messages appear in real-time while you're typing
- Message history persists as long as Redis storage is available

## Technical Stack

- **Python 3.x**
- **Upstash Redis** (REST API)
- **Requests** - HTTP library for Redis communication
- **Threading** - Background message streaming
- **Colorama** - Terminal colors
- **python-dotenv** - Environment variable management

## Example Session

```
============================================================
Welcome to Redis Chat CLI!
============================================================

Enter your username: Alice

--- New message(s) received ---
[2026-01-02 10:30:45] Bob: Hey everyone!
[2026-01-02 10:31:12] Charlie: Hello!

>>> Hi there!
✓ Message sent

--- New message(s) received ---
[2026-01-02 10:31:20] Bob: Hi Alice!
>>>
```

Enjoy chatting! 🚀
