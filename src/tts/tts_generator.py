# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/console/speech_synthesis_sample.py

import logging
import os

import yaml
import azure.cognitiveservices.speech as speechsdk

from src import config as cfg


class TTS_GEN:
    def __init__(self,
                 voice: str = 'en-US-AvaMultilingualNeural',
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
            lng_itm = dv['languages'][lng]
            if not lng_itm:
                print(f'language {lng} not found in the list, please check {src}')
                return
            voices = lng_itm['voices']
            sex_voices = [v for v in voices
                          if voices[v]['sex'] == sex or not sex]
            if not sex_voices:
                print(f'language {lng} for {sex} not found in the list, please check {src}')
                return
            return sex_voices[0]

    def generate_audio(self, tts: str, file_name: str = '', skip_if_exists=False):
        file_name = file_name or self.voice
        file_name = file_name + '.mp3'
        if self.our_dir_path:
            file_name = os.path.join(self.our_dir_path, file_name)
        if os.path.exists(file_name) and skip_if_exists:
            logging.warning(f'file {file_name} exists. skipping')
            return
        logging.info(f'producing audio for text having len {len(tts)} chars')
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=file_config)

        result = speech_synthesizer.speak_text_async(tts).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.info(f'wrote audio to file {file_name}.')
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
