# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/console/speech_synthesis_sample.py

import logging
import os
from io import BytesIO
import yaml

import azure.cognitiveservices.speech as speechsdk

from src import config as cfg
from src.data_classes.bilingual_text import BilingualText
from src.tts.ssml_generator import generate_ssml

logging.basicConfig(level=logging.INFO)

UNIVERSAL_VOICE = 'en-US-AvaMultilingualNeural' # Default voice if not specified

class TTS_GEN:
    def __init__(self,
                 voice: str = UNIVERSAL_VOICE,
                 output_format=speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
                 our_dir_path: str = ''):
        speech_config = speechsdk.SpeechConfig(subscription=cfg.SPEECH_KEY, region=cfg.SPEECH_REGION)
        speech_config.set_speech_synthesis_output_format(output_format)
        # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        #  audio_config = speechsdk.audio.AudioOutputConfig(filename="test_azure_tts.mp3")
        speech_config.speech_synthesis_voice_name = voice  # en-US-AvaMultilingualNeural'
        self.speech_config = speech_config
        self.our_dir_path = our_dir_path

    @staticmethod
    def find_voice(lng: str = 'en-US', sex: str = 'Male') -> str:
        with open(cfg.LIST_OF_VOICES_FILE_PATH, 'r') as file:
            dv = yaml.safe_load(file)
            src = dv.get('Source')
            lng_itm = dv['languages'].get(lng)
            if not lng_itm:
                logging.warning(f'language {lng} not found in the list, please check {src}, using voice {UNIVERSAL_VOICE}')
                return UNIVERSAL_VOICE
            voices = lng_itm['voices']
            sex_voices = [v for v in voices
                          if voices[v]['sex'].lower() == sex.lower() or not sex]
            if not sex_voices:
                logging.warning(f'language {lng} for {sex} not found in the list, please check {src}, using voice {UNIVERSAL_VOICE}')
                return voices[0]['name'] if voices else UNIVERSAL_VOICE
            return sex_voices[0]


    def synthesize_audio(self, input_tts: str, is_ssml: bool, audio_config: speechsdk.audio.AudioOutputConfig):
        """
        Common method to synthesize audio using Azure TTS.
        
        Args:
            input_tts (str): The text or SSML input to synthesize into audio.
            is_ssml (bool): Whether the input is SSML or plain text.
            audio_config (speechsdk.audio.AudioOutputConfig): The audio output configuration.
        
        Returns:
            speechsdk.SpeechSynthesisResult: The result of the synthesis process.
   
        """
        logging.info(f'Producing audio for text having len {len(input_tts)} chars')
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        
        # Choose the appropriate synthesis method
        tts_method = speech_synthesizer.speak_ssml_async if is_ssml else speech_synthesizer.speak_text_async
        result = tts_method(input_tts).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.info('Audio synthesis completed successfully.')
            return result
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error("Error details: {}".format(cancellation_details.error_details))
            raise RuntimeError("Speech synthesis failed.")

    def generate_audio_file(self, input_tts: str, is_ssml: bool = False, output_file_name: str = ''):
        """
        Generates audio from the provided text or SSML input and saves it to a file.
        
        Args:
            input_tts (str): The text or SSML input to synthesize into audio.
            is_ssml (bool, optional): If True, treats input_tts as SSML. Defaults to False.
            output_file_name (str, optional): The name of the output audio file. Defaults to ''.
        
        Returns:
            None
        """
        output_file_name = (output_file_name or self.voice) + '.mp3'
        if self.our_dir_path:
            output_file_name = os.path.join(self.our_dir_path, output_file_name)
        
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file_name)
        self.synthesize_audio(input_tts=input_tts, is_ssml=is_ssml, audio_config=audio_config)
        logging.info(f'Wrote audio to file {output_file_name}.')

    def generate_audio_stream(self, input_tts: str, is_ssml: bool = False) -> BytesIO:
        """
        Generates audio from the provided text or SSML input and returns it as a BytesIO stream.
        
        Args:
            input_tts (str): The text or SSML input to synthesize into audio.
            is_ssml (bool, optional): If True, treats input_tts as SSML. Defaults to False.
        
        Returns:
            BytesIO: A BytesIO object containing the synthesized audio data.
        """
        audio_stream = BytesIO()
        audio_config = speechsdk.audio.AudioOutputConfig(stream=speechsdk.audio.PushAudioOutputStream.create_push_stream(audio_stream))
        self.synthesize_audio(input_tts=input_tts, is_ssml=is_ssml, audio_config=audio_config)
        
        # Reset the stream position to the beginning
        audio_stream.seek(0)
        return audio_stream


    def binlingual_to_audio(self, bln: BilingualText,
                            break_time: str = '750ms', output_file_name: str = None):
        """
        Converts a bilingual text to audio using the configured TTS generator.
        Args:
            bilingual_text (BilingualText): The bilingual text to convert to audio.
            source_language_voice (str, optional): The voice for the source language. Defaults to 'tr-TR-AhmetNeural'.
            target_language_voice (str, optional): The voice for the target language. Defaults to 'en-US-AvaNeural'.
            break_time (str, optional): The break time between paragraphs. Defaults to '750ms'.
            skip_if_exists (bool, optional): If True, skips audio generation if the output file already exists. Defaults to False.
        Returns:
            None
        """
        source_language_voice = self.find_voice(lng=bln.source_language)
        target_language_voice = self.find_voice(lng=bln.target_language)
        ssml_output = generate_ssml(
            bilingual_text=bln,
            source_language_voice=source_language_voice,
            target_language_voice=target_language_voice,
            break_time=break_time
        )
        output_file_name = output_file_name or f"{bln.source_language}_{bln.target_language}_{hash(bln)}bilingual_audio"
        self.generate_audio_file(ssml_output, is_ssml=True, output_file_name=output_file_name)
