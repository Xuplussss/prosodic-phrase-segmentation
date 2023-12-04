import sys, os, csv, tgt, random, torch, datetime
import numpy as np 
import torch.nn as nn
from lib.preprocess_edit import turn_seg
# from lib.plot import save_segplot
random.seed(2708)
torch.manual_seed(2708)
np.random.seed(2708)


def main(root, input_path):
	temp_path = './temp/'
	lib_path = './lib/'
	# create segment textgrid
	log_file = open('segmentation_log.txt','w')
	log_txt = ''
	for filename in os.listdir(input_path):
		try:
			turn_seg(root,input_path, filename)

			# put segment audio into CNN and seq2seq
			tg = tgt.read_textgrid(temp_path+filename[:-4]+'.TextGrid')
			tier = tg.get_tier_by_name('silences')
			boundary = [i.start_time for i in tier]
			boundary.append(tier[-1].end_time)
			print(boundary)
		except:
			log_txt = log_txt + filename +'\n'
	log_file.write(log_txt)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		# print('Usage:', sys.argv[0], ' please input \'path\' and \'wav file name\'.')
		print('Usage:', sys.argv[0], ' please input \'wav file dict\'.')
		sys.exit(1)
	# print(sys.argv)
	
	root = sys.argv[1]
	audio_path = sys.argv[2] #'/home/xuplus/CHY/CHY/data/small_wav/'
	# wf = open(root+'result.txt','w')
	if audio_path.endswith('.txt'):
		rf = open(audio_path,'r')
		lines = rf.readlines()
		rf.close()
		for filename in lines:
			result_str, boundary = main(root, filename[:-1])
			# if SAVE_PLOT:
			# 	save_segplot('./', filename[:-1], './plot/', boundary)
			wf.write(filename[:-1]+' '+result_str+'\n')
	else:
		print('*************select '+audio_path+'****************')
		main(root, audio_path)
		# wf.write(wav_file+' '+result_str+'\n')
		# if SAVE_PLOT:
		# 		save_segplot('./', wav_file, './plot/', boundary)
		# while True:
		# 	wav_file = input('wav filename:')
		# 	if wav_file.endswith('.wav'):
		# 		try:
		# 			print('*************select '+wav_file+'****************')
		# 			result_str, boundary = main(root, wav_file, device, cnn_sound, cnn_emotion, lstm_seq)
		# 			# if SAVE_PLOT:
		# 			# 	save_segplot('./', wav_file, './plot/', boundary)
		# 			wf.write(wav_file+' '+result_str+'\n')
		# 		except:
		# 			print('wrong input!')
		# 			break
		# 	elif wav_file=='q' or wav_file=='exit':
		# 		break
		# 	else:
		# 		print('input file name like \'./angry_01_B_turn12.wav\'')
	# wf.close()