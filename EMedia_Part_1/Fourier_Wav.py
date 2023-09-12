#!/usr/bin/python
import numpy as np
import cv2
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import wave
from array import array
import pylab


def DFT(image_filename, subplotpos):
    # Read and process image   
    image = plt.imread(image_filename)
    plt.subplot(subplotpos)
    plt.imshow(image)

    # Convert to grayscale
    image = image[:, :, :3].mean(axis=2)
    plt.set_cmap("gray")

    #fourier transform
    ft = np.fft.ifftshift(image)
    ft = np.fft.fft2(ft)
    ft = np.fft.fftshift(ft)  

    plt.axis("off")
    subplotpos=subplotpos+1
    plt.subplot(subplotpos)
    plt.imshow(np.log(abs(ft)))
    plt.axis("off")

def DFT_S(image_filename):
    img = plt.imread(image_filename)
    #fourier transform
    image = cv2.imread(image_filename, 0)
    ft = np.fft.fft2(image)
    ft_s = np.fft.fftshift(ft)
    fourier_mag = np.asarray(np.log(abs(ft_s)), dtype=np.uint8)
    fourier_phase = np.asarray(np.angle(ft_s), dtype=np.uint8)

    f1 = plt.figure(5)

    plt.subplot(221), plt.imshow(img)
    plt.title('Input Image'), plt.xticks([]), plt.yticks([])

    plt.subplot(222), plt.imshow(image, cmap='gray')
    plt.title('GrayScale'), plt.xticks([]), plt.yticks([])

    plt.subplot(223), plt.imshow(fourier_mag, cmap='gray')
    plt.title('FFT'), plt.xticks([]), plt.yticks([])

    plt.subplot(224), plt.imshow(fourier_phase, cmap='gray')
    plt.title('FFT Angle'), plt.xticks([]), plt.yticks([])

    plt.show()

def Colors(image_filename):

    # read the image from file
    a = 321
    img = cv2.imread(image_filename)
    b,g,r = cv2.split(img)       # get b,g,r
    rgb_img = cv2.merge([r,g,b])

    # separate the image into different colors
    x,y,z = np.shape(img)
    red = np.zeros((x,y,z),dtype=int)
    green = np.zeros((x,y,z),dtype=int)
    blue = np.zeros((x,y,z),dtype=int)
    for i in range(0,x):
        for j in range(0,y):        
            green[i][j][1]= rgb_img[i][j][1]       
            blue[i][j][0] = rgb_img[i][j][0]
            red[i][j][2] = rgb_img[i][j][2]


    # save the images as files
    cv2.imwrite("red.png", red)
    cv2.imwrite("blue.png", blue)
    cv2.imwrite("green.png", green)

    # read the saved images to make fourier transforms of them
    pylab.figure(num=0, figsize=(8, 8))
    DFT("red.png",a)
    DFT("green.png",a+2)
    DFT("blue.png",a+4)
    plt.show()


    #def get_wav_info(wav_file):
    #    wav = wave.open(wav_file, 'r')
    #    frames = wav.readframes(-1)
    #    sound_info = pylab.fromstring(frames, 'int16')
    #    frame_rate = wav.getframerate()
    #    wav.close()
    #    return sound_info, frame_rate

    #def make_wav(image_filename):
#    # Make a WAV file having a spectrogram resembling an image
#    # Load image
#    image = mpimg.imread(image_filename)
#    image = np.sum(image, axis = 2).T[:, ::-1]
#    image = image**3 # ???
#    w, h = image.shape

#    # Fourier transform, normalize, remove DC bias
#    data = np.fft.irfft(image, h*2, axis=1).reshape((w*h*2))
#    data -= np.average(data)
#    data *= (2**15-1.)/np.amax(data)
#    data = array("h", np.int_(data)).tobytes()

#    # Write to disk
#    output_file = wave.open(image_filename+".wav", "w")
#    output_file.setparams((1, 2, 44100, 0, "NONE", "not compressed"))
#    output_file.writeframes(data)
#    output_file.close()
#    print ("Wrote %s.wav" % image_filename)

#def graph_spectrogram(wav_file):
#    sound_info, frame_rate = get_wav_info(wav_file)
#    pylab.figure(num=None, figsize=(10, 6))
#    pylab.subplot(111)
#    pylab.title('spectrogram of %r' % wav_file)
#    pylab.specgram(sound_info, Fs=frame_rate)
#    pylab.savefig('spectrogram.png')