import parselmouth as pm 
import os, seaborn, tgt
import numpy as np
import matplotlib.pyplot as plt 
plt.switch_backend('agg')
seaborn.set()

def save_plot(wav_path, file, plot_path, pre_emphasize = True):
	f, (axes11, axes21) = plt.subplots(2,1, sharex = True, num = file[2:]+' intensity and pitch')

	snd = pm.Sound(wav_path+file)
	axes11.plot(snd.xs(), snd.values.T)
	axes11.set_xlim([snd.xmin, snd.xmax])
	axes11.set_xlabel("time [s]")
	axes11.set_ylabel("amplitude")

	intensity = snd.to_intensity()
	axes12 = axes11.twinx()
	axes12.plot(intensity.xs(), intensity.values.T, linewidth=2.5, color = 'w')
	axes12.plot(intensity.xs(), intensity.values.T, linewidth=1.5, color = 'y')
	axes12.grid(False)
	axes12.set_ylim(0)
	axes12.set_ylabel("intensity [dB]")

	spectrogram = snd.to_spectrogram()
	if pre_emphasize:
		pre_emphasized_snd = snd.copy()
		pre_emphasized_snd.pre_emphasize()
		spectrogram = pre_emphasized_snd.to_spectrogram(window_length=0.03, maximum_frequency=8000)
	# If desired, pre-emphasize the sound fragment before calculating the spectrogram
	X, Y = spectrogram.x_grid(), spectrogram.y_grid()
	sg_db = 10 * np.log10(spectrogram.values)
	dynamic_range = 70
	axes21.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='OrRd')
	axes21.set_ylim([spectrogram.ymin, spectrogram.ymax])
	axes21.set_xlabel("time [s]")
	axes21.set_ylabel("frequency [Hz]")

	pitch = snd.to_pitch(None, 75.0, 300.0)
	axes22 = axes21.twinx()
	pitch_values = pitch.selected_array['frequency']
	pitch_values[pitch_values==0] = np.nan
	axes22.plot(pitch.xs(), pitch_values, 'o', markersize=1, color='k', linestyle='dashed')
	axes22.grid(False)
	axes22.set_ylim(0, pitch.ceiling)
	# axes22.set_ylabel("fundamental frequency [Hz]")
	axes22.set_ylabel("pitch [Hz]")
	axes22.set_xlim([snd.xmin, snd.xmax])

	# plt.show()
	plt.savefig(plot_path+file[:-4]+".png")

def save_segplot(wav_path, file, plot_path, boundaries, pre_emphasize = True):
	f, (axes11, axes21) = plt.subplots(2,1, sharex = True, num = file[2:]+' intensity and pitch')

	snd = pm.Sound(wav_path+file)
	axes11.plot(snd.xs(), snd.values.T)
	for i in boundaries:
		axes11.plot([i, i],[min(np.array(snd.values.T)), max(np.array(snd.values.T))], color = 'r')
	axes11.set_xlim([snd.xmin, snd.xmax])
	axes11.set_xlabel("time [s]")
	axes11.set_ylabel("amplitude")
	
	intensity = snd.to_intensity()
	axes12 = axes11.twinx()
	axes12.plot(intensity.xs(), intensity.values.T, linewidth=1.5, color='w')
	axes12.plot(intensity.xs(), intensity.values.T, linewidth=1)
	axes12.grid(False)
	axes12.set_ylim(0)
	axes12.set_ylabel("intensity [dB]")
	
	spectrogram = snd.to_spectrogram()
	if pre_emphasize:
		pre_emphasized_snd = snd.copy()
		pre_emphasized_snd.pre_emphasize()
		spectrogram = pre_emphasized_snd.to_spectrogram(window_length=0.03, maximum_frequency=8000)
	# If desired, pre-emphasize the sound fragment before calculating the spectrogram
	X, Y = spectrogram.x_grid(), spectrogram.y_grid()
	sg_db = 10 * np.log10(spectrogram.values)
	dynamic_range = 70
	axes21.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
	axes21.set_ylim([spectrogram.ymin, spectrogram.ymax])
	axes21.set_xlabel("time [s]")
	axes21.set_ylabel("frequency [Hz]")

	pitch = snd.to_pitch(None, 75.0, 300.0)
	axes22 = axes21.twinx()
	pitch_values = pitch.selected_array['frequency']
	pitch_values[pitch_values==0] = np.nan
	axes22.plot(pitch.xs(), pitch_values, 'o', markersize=5, color='b', linestyle='dashed')
	axes22.grid(False)
	axes22.set_ylim(0, pitch.ceiling)
	axes22.set_ylabel("fundamental frequency [Hz]")
	axes22.set_xlim([snd.xmin, snd.xmax])

	# plt.show()
	plt.savefig(plot_path+file[:-4]+".png")

if __name__ == "__main__":

	for file in os.listdir('./'):
		if file.endswith('.wav'):
			tg = tgt.read_textgrid('./'+file[:-4]+'.TextGrid')
			tier = tg.get_tier_by_name('silences')
			boundary = [i.start_time for i in tier]
			boundary.append(tier[-1].end_time)
			save_segplot('./', file, './', boundary)