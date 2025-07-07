Need to add to FE options to define format for audio output. 
Default is None, - no audio is generated.
Other options from AudioOutputFormat class.
If "bilingual" option is selected by user, BE part should leverage binlingual_to_audio to write audio data to file and give the link to this file to FE part. Use hash of BilingualText as name of audio file and 