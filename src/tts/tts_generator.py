# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/console/speech_synthesis_sample.py

from enum import StrEnum
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

class AudioOutputFormat(StrEnum):
    bilingual = "bilingual"
    bilingual_and_repeat_source_slowly = "bilingual_and_repeat_source_slowly"
    source_language = "source_language"
    target_language = "target_language"

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

    def generate_audio_file(
            self, input_tts: str, is_ssml: bool = False,
            output_file_name: str = '', skip_if_exists: bool = False):
        """
        Generates audio from the provided text or SSML input and saves it to a file.
        
        Args:
            input_tts (str): The text or SSML input to synthesize into audio.
            is_ssml (bool, optional): If True, treats input_tts as SSML. Defaults to False.
            output_file_name (str, optional): The name of the output audio file. Defaults to ''.
            skip_if_exists (bool, optional): If True, skips audio generation if the output file already exists.
                Defaults to False.
        
        Returns:
            None
        """
        output_file_name = (output_file_name or self.voice) + '.mp3'
        if self.our_dir_path:
            output_file_name = os.path.join(self.our_dir_path, output_file_name)
        
        # Skip if the file already exists and skip_if_exists is True
        if skip_if_exists and os.path.exists(output_file_name):
            logging.info(f'File {output_file_name} already exists, skipping generation.')
            return
        
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
        # Create a temporary file to store the audio
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # Generate audio to the temporary file
            audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_filename)
            self.synthesize_audio(input_tts=input_tts, is_ssml=is_ssml, audio_config=audio_config)
            
            # Read the temporary file into a BytesIO object
            audio_data = BytesIO()
            with open(temp_filename, 'rb') as f:
                audio_data.write(f.read())
            
            # Reset the stream position to the beginning
            audio_data.seek(0)
            return audio_data
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def generate_audio_file_from_multiple_inputs(
            self, input_ttss: list, is_ssml: bool = False,
            output_file_name: str = '', skip_if_exists: bool = False):
        """
        Generates audio from multiple text or SSML inputs and concatenates them into a single file.
        
        Args:
            input_ttss (list): A list of text or SSML inputs to synthesize into audio.
            is_ssml (bool, optional): If True, treats inputs as SSML. Defaults to False.
            output_file_name (str, optional): The name of the output audio file. Defaults to ''.
            skip_if_exists (bool, optional): If True, skips audio generation if the output file already exists.
                Defaults to False.
        
        Returns:
            None
        """
        # Process output filename
        output_file_name = (output_file_name or self.voice) + '.mp3'
        if self.our_dir_path:
            output_file_name = os.path.join(self.our_dir_path, output_file_name)
        
        # Skip if the file already exists and skip_if_exists is True
        if skip_if_exists and os.path.exists(output_file_name):
            logging.info(f'File {output_file_name} already exists, skipping generation.')
            return

        try:
            # Create a BytesIO object to store the concatenated audio
            merged_audio = BytesIO()
            
            # Process each input and add it to the merged audio
            for i, input_tts in enumerate(input_ttss):
                logging.info(f'Processing audio segment {i + 1}/{len(input_ttss)}')
                
                # Generate audio for this segment
                audio_stream = self.generate_audio_stream(input_tts=input_tts, is_ssml=is_ssml)
                
                # Add to merged audio
                merged_audio.write(audio_stream.read())
            
            # Reset position to beginning
            merged_audio.seek(0)
            
            # Write merged audio to the output file
            with open(output_file_name, 'wb') as output_file:
                output_file.write(merged_audio.read())
                
            segments_count = len(input_ttss)
            logging.info(f'Successfully wrote concatenated audio from {segments_count} segments '
                         f'to file {output_file_name}.')
            
        except Exception as e:
            logging.error(f"Failed to generate concatenated audio file: {str(e)}")
            raise RuntimeError(f"Audio concatenation failed: {str(e)}")

    def get_ssml_only(self, bln: BilingualText, break_time: str = '750ms',
                      aof: AudioOutputFormat = AudioOutputFormat.bilingual) -> str:
        """
        Generates SSML for a bilingual text without creating audio.
        Args:
            bln (BilingualText): The bilingual text to generate SSML for
            break_time (str): The break time between paragraphs, default is '750ms'
            aof (AudioOutputFormat): Audio output format, determines which languages are included
        Returns:
            str: Generated SSML string
        """
        source_language_voice = self.find_voice(lng=bln.source_language)
        target_language_voice = (
            self.find_voice(lng=bln.target_language)
            if aof in (
                AudioOutputFormat.bilingual,
                AudioOutputFormat.bilingual_and_repeat_source_slowly,
                AudioOutputFormat.target_language
            )
            else None
        )
        ssml_output = generate_ssml(
            bilingual_text=bln,
            source_language_voice=source_language_voice,
            target_language_voice=target_language_voice,
            break_time=break_time,
            repeat_slowly=(aof == AudioOutputFormat.bilingual_and_repeat_source_slowly)
        )
        return ssml_output

    def binlingual_to_audio(self, bln: BilingualText,
                            break_time: str = '750ms',
                            output_file_name: str = None,
                            aof: AudioOutputFormat = AudioOutputFormat.bilingual):
        """
        Converts a bilingual text to audio using the configured TTS generator.
        Args:
            bilingual_text (BilingualText): The bilingual text to convert to audio.
            source_language_voice (str, optional): The voice for the source language. Defaults to 'tr-TR-AhmetNeural'.
            target_language_voice (str, optional): The voice for the target language. Defaults to 'en-US-AvaNeural'.
            break_time (str, optional): The break time between paragraphs. Defaults to '750ms'.
            skip_if_exists (bool, optional): If True, skips audio generation if the output file already exists.
                Defaults to False.
        Returns:
            None
        """
        source_language_voice = (
            self.find_voice(lng=bln.source_language)
            if aof in (
                AudioOutputFormat.bilingual,
                AudioOutputFormat.bilingual_and_repeat_source_slowly,
                AudioOutputFormat.source_language
            )
            else None
        )
        target_language_voice = (
            self.find_voice(lng=bln.target_language)
            if aof in (
                AudioOutputFormat.bilingual,
                AudioOutputFormat.bilingual_and_repeat_source_slowly,
                AudioOutputFormat.target_language
            )
            else None
        )
        ssml_output = generate_ssml(
            bilingual_text=bln,
            source_language_voice=source_language_voice,
            target_language_voice=target_language_voice,
            break_time=break_time,
            repeat_slowly=(aof == AudioOutputFormat.bilingual_and_repeat_source_slowly)
        )
        output_file_name = output_file_name or f"{bln.source_language}_{bln.target_language}_{hash(bln)}bilingual_audio"
        self.generate_audio_file(ssml_output, is_ssml=True, output_file_name=output_file_name)
