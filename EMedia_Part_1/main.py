import zlib
import struct
from Fourier_Wav import *
from PNGChunkAnaliser_File import *
import numpy as npf
import matplotlib.pyplot as plt

my_image = 'png_files\\dice.png'
#my_image = 'png_files\\linux.png'
EncryptionFolder = 'EncryptedPNG\\'
#my_image = 'png_files\\smaller.png'

PNG_Analysis = PNGChunkAnaliser(my_image)

DFT_S(my_image)

PNG_Analysis.CreateCleanCopy('CleanCopy.png')

PNG_Analysis.CreateSingleIdatChunk()

PNG_Analysis.ToggleCompression(True)

PNG_Analysis.ECB_EnDeCrypt(1)
PNG_Analysis.CreateNewPNG(EncryptionFolder + 'ECB_EN.png')
PNG_Analysis.ECB_EnDeCrypt(0)
PNG_Analysis.CreateNewPNG(EncryptionFolder + 'ECB_DE.png')

PNG_Analysis.CTR_EnDeCrypt()
PNG_Analysis.CreateNewPNG(EncryptionFolder + 'CTR_EN.png')
PNG_Analysis.CTR_EnDeCrypt()
PNG_Analysis.CreateNewPNG(EncryptionFolder + 'CTR_DE.png')

#PNG_Analysis.ToggleCompression(False)
#PNG_Analysis.RSA_EnDeCrypt(1)
#PNG_Analysis.CreateNewPNG(EncryptionFolder + 'RSA_EN.png')
#PNG_Analysis.RSA_EnDeCrypt(0)
#PNG_Analysis.CreateNewPNG(EncryptionFolder + 'RSA_DE.png')