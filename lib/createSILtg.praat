#clearinfo
form Parameters
	text directory 
	text basename
	text output
endform

# Variables for objects in Menu
sound$ = "Sound " + basename$
text$ = "TextGrid " + basename$

Read from file: directory$ + basename$ + ".wav"

# Create silence tier. Voiced parts carry no interval label
To TextGrid (silences): 100, 0, -25, 0.3, 0.05, "SIL", ""

# Save temporary files
selectObject: text$
Write to text file: output$ + basename$ + ".TextGrid"

# appendInfoLine: basename$+"textgrid created!"