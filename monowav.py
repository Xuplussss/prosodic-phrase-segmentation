from pydub import AudioSegment
import wave
import sys
import os

data_path = sys.argv[1]
# ========== 轉單通道音檔 =============

new_path = data_path.split('/')[:-1]
mono_path = ''
for i in new_path:
    mono_path = mono_path + i + '/'
revi_path = ''
for i in new_path:
    revi_path = revi_path + i + '/'
mono_path += 'mono/'
revi_path += 'revised/'
for filename in os.listdir(data_path):
    if filename.endswith('wav'):
        wave_s = wave.open(data_path+filename,mode='rb')
        sound = AudioSegment.from_wav(data_path+filename)
        if wave_s.getnchannels() == 2:
            print(filename, 'is not mono')
            sound = sound.set_channels(1)
            sound = sound.set_frame_rate(16000)
        sound.export(mono_path+filename, format="wav")
        os.system('sox '+str(mono_path)+str(filename)+' -b 16 -e signed-integer '+str(revi_path)+str(filename))
# ========== 列出音檔資訊 =============
# wav_info_file = open('wav_information.txt','w')
# wav_info = ''
# for i in os.listdir(data_path):
#     if i.endswith('wav'):
#         wave_s = wave.open(data_path+filename,mode='rb')
#         wav_info = wav_info + '========== ' + str(i) + ' ==========\n'
#         wav_info = wav_info + 'channels: ' + str(wave_s.getnchannels()) + '\n'
#         wav_info = wav_info + 'sample rate: ' + str(wave_s.getframerate()) + '\n'
#         wav_info = wav_info + 'number of frame: ' + str(wave_s.getnframes()) + '\n'
#         wav_info = wav_info + 'sample width: ' + str(wave_s.getsampwidth()) + '\n'
#         wav_info = wav_info + '====================\n'
#         wave_s.close()
        
# wav_info_file.write(wav_info)
