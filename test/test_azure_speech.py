import os
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig, ResultReason, CancellationReason

TTS_TEXT = '''
Ready to build with Vocode?
'''

output_dir = "./.output"

voice_names = ["en-US-JennyNeural", "en-US-SteffanNeural"]
    

def test_azure_speech_synthesis(voice_name="en-US-JennyNeural", text=TTS_TEXT, filename="output.wav"):
    # Get the subscription key and region from the environment
    speech_config = SpeechConfig(subscription=os.getenv("AZURE_SPEECH_KEY"), region=os.getenv("AZURE_SPEECH_REGION"))

    speech_config.speech_synthesis_voice_name = voice_name

    # Creates a synthesizer with the given settings
    audio_config = AudioConfig(filename=filename)  # Use this to save the synthesized speech to a file
    # use en-US-GuyNeural as voice
    speech_synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Synthesizes the text
    result = speech_synthesizer.speak_text_async(TTS_TEXT).get()

    # Checks result.
    if result.reason == ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized to [{}] for text [{}]".format(filename, text))
    elif result.reason == ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

for voice_name in voice_names:
    test_azure_speech_synthesis(voice_name=voice_name, filename=f"{output_dir}/output_{voice_name}.wav")