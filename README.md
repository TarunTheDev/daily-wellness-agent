# Health & Wellness Voice Companion

A supportive AI voice agent that conducts daily check-ins to help users reflect on their well-being and set intentions for the day. Built with LiveKit Agents, Murf Falcon TTS, Google Gemini, and Deepgram.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **Daily Check-ins**: Conversational voice interface for mood and energy assessment
- **Goal Setting**: Help users identify and articulate 1-3 daily objectives
- **Supportive Guidance**: Provides practical, non-medical advice and reflections
- **Session Persistence**: Saves check-in data to JSON for continuity across sessions
- **Previous Context**: References past check-ins to maintain conversation continuity
- **Real-time Voice**: Ultra-fast TTS with Murf Falcon and accurate STT with Deepgram
- **Modern UI**: Beautiful, responsive web interface built with Next.js

## 🎯 What It Does

The Health & Wellness Voice Companion:

1. **Introduces itself** and welcomes the user warmly
2. **References previous sessions** for continuity (e.g., "Last time you mentioned feeling stressed...")
3. **Asks about mood and energy** to understand current well-being
4. **Explores daily goals** - helps users set 1-3 achievable objectives
5. **Offers practical advice** like breaking goals into steps, taking breaks, or simple grounding activities
6. **Recaps the session** and confirms understanding before saving
7. **Persists data** in `wellness_log.json` for future reference

## 🏗️ Architecture

```
health-wellness-companion/
├── backend/              # LiveKit Agents backend
│   ├── src/
│   │   ├── agent.py     # Main agent logic with health companion
│   │   └── __init__.py
│   ├── wellness_log.json # Check-in data storage
│   ├── .env.local       # Environment variables
│   └── pyproject.toml   # Python dependencies
├── frontend/            # Next.js web interface
│   ├── app/
│   ├── components/
│   ├── .env.local
│   └── package.json
└── livekit-server.exe   # LiveKit server (Windows)
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with pnpm
- **LiveKit Server** ([Download for your platform](https://docs.livekit.io/home/self-hosting/local/))

### 1. Clone the Repository

```bash
git clone https://github.com/TarunTheDev/daily-wellness-agent.git
cd daily-wellness-agent
```

### 2. Set Up Backend

```bash
cd backend

# Install dependencies
pip install -e .

# Configure environment variables
# Edit .env.local with your API keys:
# - LIVEKIT_URL=ws://127.0.0.1:7880
# - LIVEKIT_API_KEY=devkey
# - LIVEKIT_API_SECRET=secret
# - GOOGLE_API_KEY=your_google_ai_key
# - MURF_API_KEY=your_murf_api_key
# - DEEPGRAM_API_KEY=your_deepgram_key
```

### 3. Set Up Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Configure .env.local with LiveKit credentials
```

### 4. Run the Application

**Terminal 1 - Start LiveKit Server:**
```bash
# Windows
.\livekit-server.exe --dev

# Linux/Mac
livekit-server --dev
```

**Terminal 2 - Start Backend Agent:**
```bash
cd backend
python src/agent.py dev
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
pnpm dev
```

**Open in browser:** `http://localhost:3000`

## 🔑 API Keys Required

### Google AI (Gemini)
- Get your key from [Google AI Studio](https://aistudio.google.com/apikey)
- Used for: Language understanding and conversation

### Murf AI (Falcon TTS)
- Get your key from [Murf AI](https://murf.ai/)
- Used for: Ultra-fast text-to-speech

### Deepgram
- Get your key from [Deepgram](https://deepgram.com/)
- Used for: Speech-to-text transcription

## 💡 Usage Example

1. **Connect to the agent** via the web interface
2. **Start speaking** - the agent will introduce itself
3. **Have a conversation** about your mood, energy, and daily goals
4. **Receive supportive advice** tailored to your situation
5. **Confirm the recap** - the agent will save your check-in
6. **Check the data** in `backend/wellness_log.json`

### Sample Conversation Flow

```
Agent: "Hi, I'm your Health and Wellness companion. I'm here to help you 
check in on your well-being and set some intentions for the day. Last time 
we talked, you mentioned feeling stressed with medium energy. How does today 
compare?"

User: "I'm feeling much better today, pretty energetic actually."

Agent: "That's wonderful to hear! What's your energy level like on a scale 
you're comfortable with?"

User: "I'd say about 8 out of 10."

Agent: "Great! So what are 1 to 3 things you'd like to accomplish today?"

User: "Finish my presentation, go to the gym, and call my mom."

Agent: "Those sound like solid goals. For the presentation, consider breaking 
it into outline, slides, and practice. And scheduling specific times for the 
gym and call can help ensure they happen. Let me recap: You're feeling much 
better and energetic with an 8 out of 10 energy level. Your objectives are 
to finish your presentation, go to the gym, and call your mom. Does this 
sound right?"

User: "Yes, that's perfect."

Agent: "Check-in saved successfully! I've recorded your mood, energy, and 
your 3 objectives. Have a great day!"
```

## 📊 Data Storage

Check-ins are stored in `backend/wellness_log.json`:

```json
{
  "check_ins": [
    {
      "date": "2025-11-24",
      "time": "09:30:00",
      "mood": "much better and energetic",
      "energy": "8 out of 10",
      "objectives": [
        "finish presentation",
        "go to the gym",
        "call mom"
      ],
      "summary": "User feeling much better and energetic with 8/10 energy. Goals: finish presentation, go to the gym, call mom."
    }
  ]
}
```

## 🛠️ Technology Stack

- **Backend Framework**: [LiveKit Agents](https://docs.livekit.io/agents/) (Python)
- **LLM**: Google Gemini 2.5 Flash
- **TTS**: Murf AI Falcon (Matthew voice, Conversation style)
- **STT**: Deepgram Nova-3
- **Frontend**: Next.js 15 with React 19
- **UI Components**: Radix UI, Tailwind CSS
- **Real-time Communication**: LiveKit WebRTC

## 🎨 Customization

### Changing the Agent's Persona

Edit the system prompt in `backend/src/agent.py`:

```python
instructions = f"""You are a supportive Health and Wellness Voice Companion...
[Customize the instructions here]
"""
```

### Changing the Voice

Modify the TTS configuration in `backend/src/agent.py`:

```python
tts=murf.TTS(
    voice="en-US-emily",  # Change voice
    style="Calm",         # Change style
    ...
)
```

Available Murf voices: Check [Murf AI Documentation](https://murf.ai/api/docs)

### Adjusting Data Fields

Modify the `save_checkin` function in `backend/src/agent.py` to add or remove fields.

## 📝 Development

### Running Tests

```bash
cd backend
pytest
```

### Code Style

The project uses:
- Python: `ruff` for linting and formatting
- TypeScript: `eslint` and `prettier`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is based on MIT-licensed templates from LiveKit. See LICENSE files in backend and frontend directories.

## 🙏 Acknowledgments

- Built for the **Murf AI Voice Agents Challenge**
- Based on [LiveKit Agent Starter Templates](https://github.com/livekit-examples)
- Powered by [Murf Falcon TTS](https://murf.ai/) - the fastest TTS API

## 🔗 Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [Murf AI Documentation](https://murf.ai/api/docs)
- [Google Gemini API](https://ai.google.dev/)
- [Deepgram Documentation](https://developers.deepgram.com/)

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for the AI Voice Agents Challenge by Murf AI**
