import sys, os, csv, tgt, random, torch, datetime
import numpy as np 
from lib.preprocess import turn_seg
from lib.audio import trim_audio


def main(input_path, wav_file):
	# temp_path = './temp/'
	turn_seg(input_path, wav_file)

	


if __name__ == "__main__":
	if len(sys.argv) < 2:
		# print('Usage:', sys.argv[0], ' please input \'path\' and \'wav file name\'.')
		print('Usage:', sys.argv[0], ' please input \'wav file list\'.')
		sys.exit(1)
	# print(sys.argv)
	
	file_path = sys.argv[1]
	filelist = os.listdir(file_path)
	for filename in filelist:
		if filename.endswith('.wav'):
			main(file_path, filename)
	