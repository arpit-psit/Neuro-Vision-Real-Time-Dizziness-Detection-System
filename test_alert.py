import wave, struct, math

wav = wave.open("test_alert.wav", "w")
wav.setparams((1, 2, 44100, 44100, "NONE", "not compressed"))

for i in range(44100):
    value = int(32767 * math.sin(2 * math.pi * 700 * (i / 44100)))
    wav.writeframes(struct.pack("<h", value))

wav.close()
print("DONE: test_alert.wav created!")