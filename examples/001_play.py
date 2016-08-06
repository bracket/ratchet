import pyaudio
import wave
import sys

CHUNK = 1024

formats = {
    'paFloat32'      : pyaudio.paFloat32,
    'paInt32'        : pyaudio.paInt32,
    'paInt24'        : pyaudio.paInt24,
    'paInt16'        : pyaudio.paInt16,
    'paInt8'         : pyaudio.paInt8,
    'paUInt8'        : pyaudio.paUInt8,
    'paCustomFormat' : pyaudio.paCustomFormat,
}

formats_i = { v : k for k, v in formats.items() }

def main():
    wf = wave.open('data/001_machjob.wav', 'rb')
    pa = pyaudio.PyAudio()

    format = pa.get_format_from_width(wf.getsampwidth())
    print(formats_i[format])

    stream = pa.open(
        format = format,
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True,
    )

    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    pa.terminate()


if __name__ == '__main__':
    main()
