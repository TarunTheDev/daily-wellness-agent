import logging
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Path to the wellness log JSON file
WELLNESS_LOG_PATH = Path(__file__).parent.parent / "wellness_log.json"


def load_wellness_log():
    """Load the wellness log from JSON file"""
    if WELLNESS_LOG_PATH.exists():
        try:
            with open(WELLNESS_LOG_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Could not decode wellness log, starting fresh")
            return {"check_ins": []}
    return {"check_ins": []}


def save_wellness_log(data):
    """Save the wellness log to JSON file"""
    try:
        with open(WELLNESS_LOG_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("Wellness log saved successfully")
    except Exception as e:
        logger.error(f"Error saving wellness log: {e}")


def get_previous_context():
    """Get context from previous check-ins for the system prompt"""
    log = load_wellness_log()
    check_ins = log.get("check_ins", [])
    
    if not check_ins:
        return "This is the user's first check-in."
    
    # Get the most recent check-in
    latest = check_ins[-1]
    context_parts = [f"Previous check-in on {latest.get('date', 'unknown date')}:"]
    
    if "mood" in latest:
        context_parts.append(f"- Mood: {latest['mood']}")
    if "energy" in latest:
        context_parts.append(f"- Energy level: {latest['energy']}")
    if "objectives" in latest and latest["objectives"]:
        context_parts.append(f"- Goals: {', '.join(latest['objectives'])}")
    
    return "\n".join(context_parts)


class Assistant(Agent):
    def __init__(self) -> None:
        # Get previous check-in context
        previous_context = get_previous_context()
        
        instructions = f"""You are a supportive Health and Wellness Voice Companion. You conduct daily check-ins with users to help them reflect on their well-being and set intentions for the day.

Your role:
- Be warm, supportive, and grounded (not overly enthusiastic)
- NEVER diagnose or provide medical advice
- Keep responses concise and conversational
- Use simple language without complex formatting, emojis, or asterisks

Check-in Flow:
1. FIRST, introduce yourself: "Hi, I'm your Health and Wellness companion. I'm here to help you check in on your well-being and set some intentions for the day."
2. If there's a previous session, reference it naturally (e.g., "Last time we talked, you mentioned feeling low on energy. How does today compare?")
3. If this is the first session, simply ask: "How are you feeling today? What's your mood and energy level like?"
4. Ask what's stressing them or what they're feeling (listen actively)
5. Ask about their intentions or objectives for today (1-3 things they want to accomplish)
6. Offer simple, realistic advice or reflections based on what they shared:
   - Break large goals into smaller steps
   - Encourage short breaks or walks
   - Suggest simple grounding activities
   - Keep suggestions actionable and non-medical
7. Provide a brief recap of what they shared:
   - Summarize their mood
   - List their main 1-3 objectives
   - Ask "Does this sound right?"
8. Once confirmed, use the save_checkin tool to save the session data

Previous Session Context:
{previous_context}

Remember: Always start by introducing yourself, then keep it conversational, supportive, and brief. You're a companion, not a therapist or doctor."""

        super().__init__(
            instructions=instructions,
        )

    @function_tool
    async def save_checkin(
        self, 
        context: RunContext, 
        mood: str, 
        energy: str, 
        objectives: list[str],
        summary: str = ""
    ):
        """Save the daily check-in data to the wellness log.
        
        Use this tool AFTER you have:
        1. Asked about mood and energy
        2. Asked about daily objectives/intentions
        3. Provided advice or reflections
        4. Recapped the session and gotten confirmation from the user
        
        Args:
            mood: The user's self-reported mood (e.g., "good", "tired", "stressed", "energetic")
            energy: The user's energy level (e.g., "high", "medium", "low", "drained")
            objectives: List of 1-3 goals or intentions the user wants to accomplish today
            summary: Optional brief summary of the check-in session
        """
        logger.info(f"Saving check-in - Mood: {mood}, Energy: {energy}, Objectives: {objectives}")
        
        # Load existing log
        log = load_wellness_log()
        
        # Create new check-in entry
        check_in = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "mood": mood,
            "energy": energy,
            "objectives": objectives,
            "summary": summary or f"User reported feeling {mood} with {energy} energy. Goals: {', '.join(objectives)}"
        }
        
        # Add to log
        log["check_ins"].append(check_in)
        
        # Save to file
        save_wellness_log(log)
        
        return f"Check-in saved successfully! I've recorded your mood ({mood}), energy ({energy}), and your {len(objectives)} objectives for today. Have a great day, and I look forward to checking in with you again!"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
