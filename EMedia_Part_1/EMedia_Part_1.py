
#pip install numpy
#pip install matplotlib?
import zlib
import struct
from spectrum import *


my_image = 'png_files\\anaconda.png'
f = open(my_image, 'rb')

PngSignature = b'\x89PNG\r\n\x1a\n'
if f.read(len(PngSignature)) != PngSignature:
    raise Exception('Invalid PNG Signature')

chunks = []

while True:
    chunk_type, chunk_data = read_chunk(f)
    chunks.append((chunk_type, chunk_data))
    if chunk_type == b'IEND':
        break


_, IHDR_data = chunks[0] # IHDR is always the first chunk
width, height, bitd, colort, compm, filterm, interlacem = struct.unpack('>IIBBBBB', IHDR_data)

if compm != 0:
    raise Exception('invalid compression method')
if filterm != 0:
    raise Exception('invalid filter method')
if colort != 6:
    raise Exception('we only support truecolor with alpha')
if bitd != 8:
    raise Exception('we only support a bit depth of 8')
if interlacem != 0:
    raise Exception('we only support no interlacing')

print ("width = ", width)
print ("height = ", height)
print ("bit depth = ", bitd)
print ("color type = ", colort)
print ("compression method = ", compm)
print([chunk_type for chunk_type, chunk_data in chunks])

entries = []
#for chunk in chunks:
#    if chunk[0] == b'PLTE':
        

Recon = []
bytesPerPixel = 4
stride = width * bytesPerPixel

IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in chunks if chunk_type == b'IDAT')
IDAT_data = zlib.decompress(IDAT_data)


i = 0
for r in range(height): # for each scanline
    filter_type = IDAT_data[i] # first byte of scanline is filter type
    i += 1
    for c in range(stride): # for each byte in scanline
        Filt_x = IDAT_data[i]
        i += 1
        if filter_type == 0: # None
            Recon_x = Filt_x
        elif filter_type == 1: # Sub
            Recon_x = Filt_x + Recon_a(r, c)
        elif filter_type == 2: # Up
            Recon_x = Filt_x + Recon_b(r, c)
        elif filter_type == 3: # Average
            Recon_x = Filt_x + (Recon_a(r, c) + Recon_b(r, c)) // 2
        elif filter_type == 4: # Paeth
            Recon_x = Filt_x + PaethPredictor(Recon_a(r, c), Recon_b(r, c), Recon_c(r, c))
        else:
            raise Exception('unknown filter type: ' + str(filter_type))
        Recon.append(Recon_x & 0xff) # truncation to byte



import matplotlib.pyplot as plt
import numpy as np
import os

"""make_wav(my_image)
my_image.removeprefix('png_files"\"')
wav = ".wav"
wav_image = my_image+wav
graph_spectrogram(wav_image)
os.remove(wav_image)

pylab.figure(num=None, figsize=(10, 6))
pylab.title(my_image)
plt.imshow(np.array(Recon).reshape((height, width, 4)))
plt.show()"""

print("Entering Colors\n")
Colors(my_image)
