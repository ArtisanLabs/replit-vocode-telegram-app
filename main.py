import inspect
import io
import logging
import os
import pickle
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Type, Union

from pydantic import BaseModel
from pydub import AudioSegment
from replit import db
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from vocode.turn_based.agent import ChatGPTAgent
from vocode.turn_based.synthesizer import (
    AzureSynthesizer,
    BaseSynthesizer,
    CoquiSynthesizer,
    CoquiTTSSynthesizer,
    ElevenLabsSynthesizer,
    PlayHtSynthesizer,
    RimeSynthesizer,
    StreamElementsSynthesizer,
)
from vocode.turn_based.transcriber import BaseTranscriber, WhisperTranscriber

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Synthesizer class must be one of the following (do not change without adding support):
supported_classes = [
    CoquiSynthesizer,
    StreamElementsSynthesizer,
    ElevenLabsSynthesizer,
    PlayHtSynthesizer,
    AzureSynthesizer,
    CoquiTTSSynthesizer,
    RimeSynthesizer,
]

##############################################
## CONFIGURATION START
##############################################
# Required environment variables containing API key: OPENAI_API_KEY, TELEGRAM_BOT_KEY, 
# and your Vocode synthesizers classes corresponding API key variable

# Your chosen synthesizer provider's corresponding Vocode turn_based class instance
SYNTH = AzureSynthesizer(voice_name="en-US-JennyMultilingualV2Neural")

# Instructions to the language model responsible for generating response transcript.
SYSTEM_PROMPT = (
  "You are having a voice-to-voice conversation with a user. "
  "Always pretend you are a real human. Do not avoid or decline "
  "to answer questions because you are not human."
)

##############################################
## CONFIGURATION END
##############################################


# key=synth class, value=attribute that chooses the provider voice
voice_attr_of: Dict[Type[BaseSynthesizer], str] = {
    ElevenLabsSynthesizer: "voice_id",
    PlayHtSynthesizer: "voice",
    StreamElementsSynthesizer: "voice",
    AzureSynthesizer: "voice_name",
    CoquiSynthesizer: "voice_id",
    CoquiTTSSynthesizer: "speaker",
    RimeSynthesizer: "speaker",
}
assert set(voice_attr_of.keys()) == set(
    supported_classes
), "supported_classes must match the keys of voice_attr_of!"

assert (
    type(SYNTH) in voice_attr_of
), "Synthesizer class must be one of the supported ones!"
# Check voice_attr_of is correct by asserting all classes have their
# corresponding value as a parameter in the init function
for key, value in voice_attr_of.items():
    assert value in inspect.signature(key.__init__).parameters


# Define a Voice model with id, name and description fields
class Voice(BaseModel):
  id: Optional[str] = None # Optional id for the voice
  name: Optional[str] = None # Optional name for the voice
  description: Optional[str] = None # Optional description for the voice

# Array of tuples (synthesizer's voice id, nickname, description if text to voice)
DEFAULT_VOICES: List[Voice] = [Voice(id=None, name="Azure default", description=None)]

# Define a Chat model with voices, current_voice and current_conversation fields
class Chat(BaseModel):
    voices: List[Voice] = DEFAULT_VOICES # List of available voices for the chat
    current_voice: Voice = DEFAULT_VOICES[0] # Current voice for the chat
    current_conversation: Optional[bytes] = None # Current conversation as a pickled object


class VocodeBotResponder:
    def __init__(
        self,
        transcriber: BaseTranscriber,
        system_prompt: str,
        synthesizer: BaseSynthesizer
    ) -> None:
        self.transcriber = transcriber
        self.system_prompt = system_prompt
        self.synthesizer = synthesizer
        self.db: Dict[int, Chat] = defaultdict(Chat)


    def get_agent(self, chat_id: int) -> ChatGPTAgent:
        # Get current voice name and description from DB
        user = self.db[chat_id]
        voice_name = user.current_voice.name
        voice_description = user.current_voice.description

        # Augment prompt based on available info
        prompt = self.system_prompt
        if voice_description is not None or voice_name is not None:
            prompt += (
              " Pretend to be {0}. This is a demo of Coqui's voice creation tool, "
              "so your responses are fun, always in character, and relevant to that"
              "voice description."
            ).format(
                voice_description if voice_description else voice_name
            )

        # Load saved conversation if it exists
        convo_string = self.db[chat_id].current_conversation
        agent = ChatGPTAgent(
            system_prompt=prompt,
            model_name="gpt-4-0613",
            max_tokens=512,
            memory=pickle.loads(convo_string) if convo_string else None,
        )

        return agent

    # input can be audio segment or text
    async def get_response(
        self, chat_id: int, input: Union[str, AudioSegment]
    ) -> Tuple[str, AudioSegment]:
        # If input is audio, transcribe it
        if isinstance(input, AudioSegment):
            input = self.transcriber.transcribe(input)
    
        # Get agent response
        agent = self.get_agent(chat_id)
        agent_response = agent.respond(input)
    
        user = self.db[chat_id]
        voice_id = user.current_voice.id
        voice_description = user.current_voice.description
    
        # If we have a Coqui voice prompt, use that. Otherwise, 
        # set ID as synthesizer expects.
        if voice_description is not None and isinstance(
            self.synthesizer, 
          CoquiSynthesizer
        ):
            self.synthesizer.voice_prompt = voice_description
        elif voice_id is not None:
            setattr(self.synthesizer, voice_attr_of[type(self.synthesizer)], voice_id)
    
        # Synthesize response
        # TODO make async
        synth_response = self.synthesizer.synthesize(agent_response)
    
        # Save conversation to DB
        self.db[chat_id].current_conversation = pickle.dumps(agent.memory)
    
        return agent_response, synth_response

    async def handle_telegram_start(
      self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
      assert update.effective_chat, "Chat must be defined!"
      start_text = (
        "We're robot YC Partners that scale, here to help you Make "
        "Something People Want 24/7. Introduce yourself to Garry Tan \n\n"
        "use /help to talk to someone else."
      )

      await context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)

    async def handle_telegram_message(
      self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
      assert update.effective_chat, "Chat must be defined!"
      chat_id = update.effective_chat.id
      # Accept text or voice messages
      if update.message and update.message.voice:
          user_telegram_voice = await context.bot.get_file(
              update.message.voice.file_id
          )
          bytes = await user_telegram_voice.download_as_bytearray()
          # convert audio bytes to numpy array
          input = AudioSegment.from_file(
              io.BytesIO(bytes), format="ogg", codec="libopus"  # type: ignore
          )
      elif update.message and update.message.text:
          input = update.message.text
      else:
          # No audio or text, complain to user.
          await context.bot.send_message(
              chat_id=update.effective_chat.id,
              text=(
                  "Sorry, I only respond to commands, voice, or text messages. "
                  "Use /help for more information."
              ),
          )
          return
      # Get audio response from LLM/synth and reply
      agent_response, synth_response = await self.get_response(int(chat_id), input)
      out_voice = io.BytesIO()
      synth_response.export(out_f=out_voice, format="ogg", codec="libopus")  # type: ignore
      await context.bot.send_message(
          chat_id=update.effective_chat.id, text=agent_response
      )
      await context.bot.send_voice(chat_id=str(chat_id), voice=out_voice)

    async def handle_telegram_help(
      self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
      help_text = (
          "Hello! I'm your voice chatbot. Here's how you can interact with me:\n"
          "- Send me a voice message, and I'll reply with a voice message.\n"
          "- Use /help to display this help message again.\n"
      )
      assert update.effective_chat, "Chat must be defined!"
      # if isinstance(self.synthesizer, CoquiSynthesizer): 
      #     help_text += (
      #       "\n- Use /create <voice_description> to create a new Coqui "
      #       "voice from a text prompt and switch to it. "
      #     )
      await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

    async def handle_telegram_unknown_cmd(
      self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
      assert update.effective_chat, "Chat must be defined!"
      await context.bot.send_message(
          chat_id=update.effective_chat.id,
          text=(
              "Sorry, I didn\'t understand that command. Use "
              "/help to see available commands"
          )
      )

if __name__ == "__main__":
    transcriber = WhisperTranscriber()
    print("the db", db)
    voco = VocodeBotResponder(transcriber, SYSTEM_PROMPT, SYNTH, db)
    application = ApplicationBuilder().token(
    os.environ["TELEGRAM_BOT_KEY"]).build()
    application.add_handler(CommandHandler("start", voco.handle_telegram_start))
    application.add_handler(
    MessageHandler(~filters.COMMAND, voco.handle_telegram_message))
    # application.add_handler(
    #   CommandHandler("create", voco.handle_telegram_create_voice))
    application.add_handler(
    CommandHandler("voice", voco.handle_telegram_select_voice))
    application.add_handler(
    CommandHandler("list", voco.handle_telegram_list_voices))
    application.add_handler(CommandHandler("who", voco.handle_telegram_who))
    application.add_handler(CommandHandler("help", voco.handle_telegram_help))
    application.add_handler(
    MessageHandler(filters.COMMAND, voco.handle_telegram_unknown_cmd))
    application.run_polling()