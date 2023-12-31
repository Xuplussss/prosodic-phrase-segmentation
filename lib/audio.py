import scipy.io.wavfile
import numpy as np 
import wave

def wav_len(file):
	wf = wave.open(file,'rb')
	return wf.getnframes()/float(wf.getframerate())

def trim_audio(file, boundary):
	try:
		fstmp, wavtmp = scipy.io.wavfile.read(file)
		
	except ValueError:
		print('read audio error:',file,' has unexpected end.')
	#wavtmp.dtype = int16
	nb_bits = 16
	samples = wavtmp / (float(2**(nb_bits - 1)) + 1.0)
	
	# double_channel to unichaanel
	
	# if samples.shape[1] > 1:
	# 	uni = np.zeros(len(samples))
	# 	for i in range(len(samples)):
	# 		uni[i] = samples[i][0]
		
	# 	samples = uni 
	# unichannel to unichannel
	samples.reshape(samples.shape[0],1)
	# print(samples)
	
	sample_boundary = [int(i*16000) for i in boundary]
	pph_audio = []
	for i in range(len(boundary)-1):
		pph_audio.append(samples[sample_boundary[i]:sample_boundary[i+1]])
	return pph_audio