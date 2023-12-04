import os, csv, tgt, subprocess, wave, re
import numpy as np 

# def silence_detect():
# 	return boundary, tag
def read_frames(svm_out):
	rf = open(svm_out,'r')
	lines = rf.readlines()
	rf.close()
	svm_tags, frame_seq = [],[]
	label_order = lines[0].split(' ')[1]
	for i in range(1, len(lines)):
		svm_tags.append(int(lines[i].split(' ')[0]))
		if label_order == '0':
			tmp = [float(lines[i].split(' ')[1])]
			tmp.append(float(lines[i].split(' ')[2][:-1]))
		else:
			tmp = [float(lines[i].split(' ')[2][:-1])]
			tmp.append(float(lines[i].split(' ')[1]))
		frame_seq.append(tmp)
	svm_tags = np.array(svm_tags)
	frame_seq = np.array(frame_seq)
	return svm_tags, frame_seq

def smoothing(prob_seq):
	window_size = 5
	pointer = 0
	smoothing_win_seq = np.append([prob_seq[0], prob_seq[0]],prob_seq,axis=0)
	smoothing_win_seq = np.append(smoothing_win_seq,[prob_seq[-1], prob_seq[-1]], axis=0)
	type_num = len(prob_seq[0])
	smoothed_seq = []
	for i in range(len(prob_seq)):
		tmp = np.zeros(type_num)
		for j in range(len(tmp)):
			tmp[j] = np.mean(smoothing_win_seq[i:i+window_size,j])
		smoothed_seq.append(tmp)
	labeled_seq = np.argmax(smoothed_seq, axis = 1)
	smoothed_seq = np.array(smoothed_seq)
	return smoothed_seq, labeled_seq

def boundary_detect_prob(smooth_prob_seq, svm_tag_seq, wav_dur, boundary_threshold):
	half_window_size = 3
	if len(svm_tag_seq) != len(smooth_prob_seq):
		print('size mismatch error: svm predict sequence')
	smooth_prob_seq = np.array(smooth_prob_seq)
	boundary = [0]
	for i in range(3,len(smooth_prob_seq)-2):
		if svm_tag_seq[i] != svm_tag_seq[i-1]:
			if (sum(svm_tag_seq[i-3:i]) == 3 or sum(svm_tag_seq[i:i+3]) == 3) and sum(svm_tag_seq[i-3:i+3]) == 3:
				tmp = smooth_prob_seq[i-1,0]*9 + smooth_prob_seq[i-2,0]*4 + smooth_prob_seq[i-3,0]
				pre_score = tmp
				tmp = smooth_prob_seq[i,0]*9 + smooth_prob_seq[i+1,0]*4 + smooth_prob_seq[i+2,0]
				post_score = tmp
				if abs(pre_score - post_score) > boundary_threshold:
					boundary.append(i)
				# print('score',abs(pre_score-post_score), 'pre',pre_score, 'post',post_score)
			else:
				continue
	boundary.append(len(smooth_prob_seq)-1)
	smooth_tag_seq = np.argmax(smooth_prob_seq, axis = 1)
	seq_tag = []
	for i in range(len(boundary)-1):
		# if sum(smooth_tag_seq[boundary[i]:boundary[i+1]]) > (boundary[i+1]-boundary[i])/2:
		# 	seq_tag.append(1)
		# else:
		# 	seq_tag.append(0)
		if sum(smooth_prob_seq[boundary[i]:boundary[i+1],0]) > sum(smooth_prob_seq[boundary[i]:boundary[i+1],1]):
			seq_tag.append(0)
		else:
			seq_tag.append(1)
	frame_dur = wav_dur/len(svm_tag_seq)
	boundary = [i*frame_dur for i in boundary]
	# print(boundary)
	return boundary, seq_tag

def svm_discriminate(file, lib_path, tmp_path, tier):
	# prepare input of svm predict
	csvreader = csv.reader(open(tmp_path+file[:-4]+'.csv'))
	frames = []
	for frame in csvreader:
		frame = [float(i) for i in frame]
		frames.append(frame)
	frame_dur = len(frames)/tier.end_time
	wf = open(tmp_path+file[:-4]+'.txt','w')
	for ind in range(len(frames)):
		frame_str = '0 '
		for i in range(len(frames[ind])):
			frame_str += str(i+1)+':'+str(frames[ind][i])+' '
		frame_str = frame_str[:-1] + '\n'
		wf.write(frame_str)
	wf.close()
	# svm predict
	svm_scale = lib_path+'libsvm-3.22/svm-scale'
	svm_predict = lib_path+'libsvm-3.22/svm-predict'
	model = lib_path+'5to10_fold4_model.txt'
	scale = lib_path+'5to10_fold4_scale.txt'
	file_scale = tmp_path+file[:-4]+'_scale.txt'
	file_out = tmp_path+file[:-4]+'_out.txt'
	file_acc = tmp_path+file[:-4]+'_uselessacc.txt'
	os.system(svm_scale+' -r '+scale+' '+tmp_path+file[:-4]+'.txt > '+file_scale)
	os.system(svm_predict+' -b 1 '+file_scale+' '+model+' '+file_out+' > '+file_acc)
	svm_tags, svm_predict_seq = read_frames(file_out)
	# boundary detect
	smoothed_seq, smoothed_tag = smoothing(svm_predict_seq)
	for i in range(4):
		smoothed_seq, smoothed_tag = smoothing(smoothed_seq)
	boundary_threshold = 0.8
	boundary, seg_tag = boundary_detect_prob(smoothed_seq, smoothed_tag, tier.end_time, boundary_threshold)
	wf = open(tmp_path+file[:-4]+'_boundary.txt','w')
	wf.write(str(boundary)+'\n')
	wf.write(str(seg_tag)+'\n')
	wf.write('predict sequence:\n'+str(svm_tags)+'\n')
	wf.write('smoothed sequence:\n'+str(smoothed_tag)+'\n')
	wf.close()
	# silence insert
	for interval in tier: # only iteration interval with 'SIL' tags
		for i in range(1,len(boundary)):
			bound_dis = [interval.start_time-boundary[i-1], boundary[i]-interval.end_time]
			if min(bound_dis) >= 0:
				if max(bound_dis) < 0.25:
					seg_tag[i-1] = 'SIL'
				elif min(bound_dis) < 0.1:
					if bound_dis[0] >= 0.25:
						boundary.insert(i,interval.start_time)
						seg_tag.insert(i,'SIL')
					else:
						boundary.insert(i,interval.end_time)
						seg_tag.insert(i-1, 'SIL')
				break
			elif bound_dis[1] >= 0 and bound_dis[0] < 0:
				if str(seg_tag[i-1]) == '0':
					if abs(bound_dis[0]) < 0.1:
						if bound_dis[1] >= 0.25:
							boundary.insert(i,interval.end_time)
							seg_tag.insert(i-1,'SIL')
						else:
							seg_tag[i-1] = 'SIL'
				elif str(seg_tag[i-2]) == '0':
					if abs(interval.end_time-boundary[i-1]) < 0.25 and interval.start_time-boundary[i-2] <0.25:
						seg_tag[i-2] = 'SIL'
				break
			else:
				continue
	seg_tag = [str(i) for i in seg_tag]
	if len(seg_tag) != (len(boundary)-1) :
		print('segment error!!')
	return boundary, seg_tag

def pph_inform(feature_list, tgfile):
	tg = tgt.read_textgrid(tgfile)
	pph_tier = tg.get_tier_by_name('PPh(L3)')
	segtime = []
	for i in pph_tier._objects:
		segtime.append(i.end_time-i.start_time)
	rf = open(tgfile,'r')
	lines = rf.readlines()
	rf.close()
	tgtext = list(filter(lambda tg:re.match('.*text.*$',tg),lines))
	segtime_inf = []
	for i, v in enumerate(segtime):
		tmp = tgtext[i].split(',')
		inf = []
		for feature in feature_list:
			line_list = list(filter(lambda x:re.match('.*'+feature+'.*$',x),tmp))[0].split(' ')
			index = line_list.index('\"\"'+feature+'\"\"')+2
			inf.append(line_list[index][2:-2])
			#inf.append(list(filter(lambda x:re.match('.*'+feature+'.*$',x),tmp))[0].split(' ')[-1][2:-2])
		segtime_inf.append(inf)
	return segtime, tgtext, segtime_inf

def select_target(t_maxf0, segtime, min_seg_dur):
	try:
		mergetarget = t_maxf0.index('--undefined--')
		if (segtime[mergetarget] > min_seg_dur) and (min(segtime) < min_seg_dur):
			mergetarget = segtime.index(min(segtime))
	except:
		mergetarget = segtime.index(min(segtime))
	# print('target:',mergetarget)
	return mergetarget

def select_adjacent(index, segtime, t_maxf0, z_int):
	if index!=0:
		if (index+1)==len(segtime):
			return index-1
		else:
			adj_index=[index-1, index+1]
			if t_maxf0[index]=='--undefined--': # silence
				for i in adj_index:
					if t_maxf0[i]=='--undefined--':
						return i
				if segtime[adj_index[0]]>=segtime[adj_index[1]]:
					return adj_index[0]
				else:
					return adj_index[1]
			else:
				if abs(float(z_int[adj_index[0]])-float(z_int[index]))<abs(float(z_int[adj_index[1]])-float(z_int[index])):
					return adj_index[0]
				else:
					return adj_index[1]

	else:
		return index+1

def adjust(index, adjacent, segtime):
	segtime[index] = segtime[index]+segtime[adjacent]
	del segtime[adjacent]
	return segtime

def merge_short_seg(segtime_inf, segtime):
	min_seg_dur = 0.2
	if sum(segtime)<1:
		seg_st = [0]
		seg_et = [sum(segtime)]
		return seg_st, seg_et
	else:
		# tg_inform = ['t_min', 't_maxf0', 'z_int', 'z_f0', 'dur', 'dur_all']
		# print(segtime_inf)
		t_maxf0 = [i[1] for i in segtime_inf]
		z_int = [i[2] for i in segtime_inf]
		mergetarget = select_target(t_maxf0, segtime, min_seg_dur)
		min_seg = segtime[mergetarget]
		
		while min_seg < min_seg_dur:
			if (min_seg>min_seg_dur) or (len(segtime)==1):
				print('error in selecting pph merge-target.',mergetarget)
				# print(segtime[mergetarget])
				break
			else:
				adjacent_index = select_adjacent(mergetarget, segtime, t_maxf0, z_int)
				del segtime_inf[mergetarget]
				segtime = adjust(mergetarget, adjacent_index, segtime)
			mergetarget = select_target(t_maxf0, segtime, min_seg_dur)
			min_seg = segtime[mergetarget]			

		seg_st = [0]
		seg_et = []
		for i in range(len(segtime)-1):
			seg_st.append(sum(segtime[:i+1]))
			seg_et.append(sum(segtime[:i+1]))
		seg_et.append(sum(segtime))
		return seg_st, seg_et

def pph_annotate(input_path, file, tmp_path, boundary, seg_tag, seg_index):
	wave_read = wave.open(input_path+file)
	start_sample = int(boundary[seg_index]*16000)
	# print(start_sample)
	end_sample = int(boundary[seg_index+1]*16000)
	# print(end_sample)
	pass_wave_byte = wave_read.readframes(start_sample)
	verbal_wave_byte = wave_read.readframes((end_sample-start_sample))
	wave_read.close()
	verbal_file = file[:-4]+'_seg'+str(seg_index)+'.wav'
	wave_write = wave.open(tmp_path+verbal_file,'wb')
	wave_write.setparams((1,2,16000, len(verbal_wave_byte), 'NONE', 'not compressed'))
	wave_write.writeframesraw(verbal_wave_byte)
	wave_write.close()
	subprocess.run(['./lib/praat-ft-annot', './lib/mod01.praat', tmp_path, verbal_file[:-4], tmp_path])
	subprocess.run(['./lib/praat-ft-annot', './lib/mod02.praat', tmp_path, verbal_file[:-4]])
	subprocess.run(['./lib/praat-ft-annot', './lib/mod03.praat', tmp_path, verbal_file[:-4]])
	subprocess.run(['./lib/praat-ft-annot', './lib/mod05b.praat', tmp_path, verbal_file[:-4]])
	subprocess.run(['./lib/praat-ft-annot', './lib/mod06b.praat', tmp_path, verbal_file[:-4]])
	tg_inform = ['t_min', 't_maxf0', 'z_int', 'z_f0', 'dur', 'dur_all']
	segtime, tgtext, seg_inf = pph_inform(tg_inform, tmp_path+verbal_file[:-4]+'_result.TextGrid')

	st, et = merge_short_seg(seg_inf, segtime)
	for i in range(1,len(st)):
		boundary.insert(seg_index+i,st[i]+boundary[seg_index])
		seg_tag.insert(seg_index+i,'1')
	add_seg = len(st)-1
	return boundary, seg_tag, add_seg

def turn_seg(root,input_path, file):
	lib_path = root + 'lib/'
	tmp_path = root + 'temp/'
	save_path = root + 'textgrid/'
	if not os.path.exists(tmp_path):
		os.makedirs(tmp_path)
	
	# opensmile 384 dim feature with 0.025(0.01) for non functional feature
	# frame size: 0.1(0.05) for functional features
	opensmile_config = lib_path+'IS09_emotion_byframe.conf'
	opensmile_csv = tmp_path+file[:-4]+'.csv'
	try:
		os.remove(opensmile_csv)
	except:
		pass
	os.system('SMILExtract -C '+opensmile_config+' -I '+input_path+file+' -O '+opensmile_csv+' > '+tmp_path+'smile.log')
	rf = open(opensmile_csv,'r')
	lines = rf.readlines()
	rf.close()
	wf = open(opensmile_csv,'w')
	for i in range(391,len(lines)):
		new_line = ''
		splits = lines[i].split(',')
		for i in splits[1:-1]:
			new_line += i + ','
		wf.write(new_line[:-1]+'\n')
	wf.close()
	# silence detect
	createSILtg = lib_path+'createSILtg.praat'
	try:
		# subprocess.run(['./praat', createSILtg, '../'+input_path, file[:-4], '.'+tmp_path])
		subprocess.run([lib_path+'praat', createSILtg, input_path, file[:-4], tmp_path])
	except:
		print('detect silence error:',input_path+file)
	# print('SIL suceed!!!!!!!')
	tg = tgt.read_textgrid(tmp_path+file[:-4]+'.TextGrid')
	tier = tg.get_tier_by_name('silences')
	# libsvm predict
	svm_boundary, svm_tag = svm_discriminate(file, lib_path, tmp_path, tier)
	tgt.io.write_to_file(tg, save_path+file[:-4]+'.TextGrid',format = 'long')
	# print('svm_boundary suceed!!!!!!!')
	svm_boundary[-1] = tier.end_time
	# pph annotate
	ind = 0
	boundary, seg_tag = svm_boundary, svm_tag
	
	while ind < (len(boundary)-1):
		if boundary[ind+1]-boundary[ind] > 1 and seg_tag[ind] == '1':
			boundary, seg_tag, add_seg = pph_annotate(input_path, file, tmp_path, boundary, seg_tag, ind)
			ind += add_seg
		ind += 1
	# print('pph_annotate suceed!!!!!!!')
	
	# write TextGrid file
	
	for i in range(len(tier)-1,-1,-1):
		del tier[i]
	# print(boundary)
	# print(tier.end_time)
	for i in range(len(seg_tag)):
		tier.add_annotation(tgt.Interval(boundary[i],boundary[i+1],seg_tag[i]))
	# tgt.io.write_to_file(tg, tmp_path+file[:-4]+'.TextGrid',format = 'long')
	tgt.io.write_to_file(tg, save_path+file[:-4]+'.TextGrid',format = 'long')
	os.remove(opensmile_csv)
	os.remove(tmp_path+file[:-4]+'.TextGrid')
	os.remove(tmp_path+file[:-4]+'.txt')
	os.remove(tmp_path+file[:-4]+'_boundary.txt')
	os.remove(tmp_path+file[:-4]+'_out.txt')
	os.remove(tmp_path+file[:-4]+'_scale.txt')
	os.remove(tmp_path+file[:-4]+'_uselessacc.txt')
	for i in range(len(seg_tag)):
		if os.path.exists(tmp_path+file[:-4]+'_seg'+str(i)+'.Intensity'):
			os.remove(tmp_path+file[:-4]+'_seg'+str(i)+'.Intensity')
			os.remove(tmp_path+file[:-4]+'_seg'+str(i)+'.wav')
			os.remove(tmp_path+file[:-4]+'_seg'+str(i)+'_result.TextGrid')
			os.remove(tmp_path+file[:-4]+'_seg'+str(i)+'.Pitch')

