from binascii import crc32
from math import sqrt
from Cryptodome import PublicKey
import sympy
import KeyGenerator
import RSA
import zlib
import random

class PNGChunkAnaliser:
    #PNG == Portable Network Graphics
    def __init__(self, FileName=None):
        self.width = 0
        self.height = 0
        self.bit_depth = 0
        self.color_type = 0
        self.FilterType = []
        self.PixelLength = 0
        self.chunks = []
        self.EnChunks = []
        self.pallet = []
        self.functions = {}
        self.FileName = FileName
        self.IdatLocation = 0
        self.PrivateKey = [0,0]
        self.PublicKey = [0,0]
        self.nonce = random.randint(1,20)
        self.Compression = False

        # Gives the functions "names" that match their chunks
        self.functions[b'IHDR'] = self.IHDR_chunk
        self.functions[b'sRGB'] = self.sRGB_chunk
        self.functions[b'gAMA'] = self.gAMA_chunk
        self.functions[b'PLTE'] = self.PLTE_chunk
        self.functions[b'tEXt'] = self.tEXT_chunk

        if FileName != None:
            print(f'File name: {self.FileName}\n')
            self.ReadChunks(self.FileName)
            self.ReadPNG()
            self.CreateCleanCopy("Clean_Image.png")

    def GetDecompressedIDATdata(self):
        if self.Compression:
            print('Decompressing IDAT\'s')
            IDAT_data = b''
            for chunk in self.chunks:
                if chunk[0] == b'IDAT':
                    #d = int.from_bytes(chunk[2], 'big')
                    IDAT_data += chunk[1]
                    #print(type(IDAT_data))

            data = zlib.decompress(IDAT_data)
            self.EnChunks[self.IdatLocation][1] = data
            return data

    def CompressIDATdata(self):
        if self.Compression:
            print('compressing IDAT')
            IDAT_data = self.EnChunks[self.IdatLocation][1]
            data = zlib.compress(IDAT_data)
            self.EnChunks[self.IdatLocation][1] = data

    #only prints the name, effectively a handler for unhandled chunks
    def DefaultChunkHandler(self, index, name, data):
        print(f'{name.decode("utf-8")} Chunk (Unhandled)')

    def ToggleCompression(self, TF):
        self.Compression = TF

    def ReadPNG(self, FileName):
        self.ReadChunks(FileName)
        for index, chunk in enumerate(self.chunks):
            self.functions.get(chunk[0],self.DefaultChunkHandler)(index,chunk[0],chunk[1]) 
            #chunk[0] is the name, chunk[1] is the data

    def ReadPNG(self):
        self.ReadChunks(self.FileName)
        for index, chunk in enumerate(self.chunks):
            self.functions.get(chunk[0],self.DefaultChunkHandler)(index,chunk[0],chunk[1]) 
            #chunk[0] is the name, chunk[1] is the data

    def ReadChunks(self, FileName):
        self.chunks.clear()
        with open(FileName, 'rb') as File:
            # Checking signature
            if File.read(8) != b'\x89PNG\r\n\x1a\n':
                raise Exception('Signature error')
            info = File.read(4)
            while info != b'':
                length = int.from_bytes(info, 'big')
                data = File.read(4 + length)
                crc = File.read(4)
                if int.from_bytes(crc, 'big') != crc32(data):
                    raise Exception('CRC Checkerror')
                #appends chunk name + its data
                self.chunks.append([data[:4], data[4:], info, crc])
                info = File.read(4)

    def IHDR_chunk(self, index, name, data):
        types = {0: 'Grayscale',
            2: 'Truecolor',
            3: 'Indexed-color',
            4: 'Greyscale with alpha',
            6: 'Truecolor with alpha'}

        if index != 0:
            raise Exception('first chunk')
        self.width = int.from_bytes(data[:4], 'big')
        self.height = int.from_bytes(data[4:8], 'big')
        self.bit_depth = int.from_bytes(data[8:9], 'big')
        self.color_type = int.from_bytes(data[9:10], 'big')
        print('IHDR Chunk')
        print(f'  width : {self.width}')
        print(f'  height: {self.height}')
        print(f'  bit depth: {self.bit_depth}')
        print(f'  color type: {types[self.color_type]}')
        print(f'  compression method: {int.from_bytes(data[10:11], "big")}')
        print(f'  filter method: {int.from_bytes(data[11:12], "big")}')
        print(f'  interlace method: {int.from_bytes(data[12:13], "big")}')

    def PLTE_chunk(self, index, name, data):
        print(f'{name.decode("utf-8")} Chunk')
        temp = divmod(len(data), 3)

        if temp[1] != 0:
            raise Exception('pallet')
        for pin in range(temp[0]):
            color = data[pin * 3], data[pin * 3 + 1], data[pin * 3 + 2]
            print(f'  #{color[0]:02X}{color[1]:02X}{color[2]:02X}')
            self.pallet.append(color)

    def gAMA_chunk(self, index, name, data):
        print(f'{name.decode("utf-8")} Chunk')
        print(f'  Image gamma: {int.from_bytes(data, "big")}')

    def tEXT_chunk(self, index, name, data):
        print(f'{name.decode("utf-8")} Chunk')
        txt = data.split(b'\x00')
        print(f'  {txt[0].decode("utf-8")}: {txt[1].decode("utf-8")}')

    def sRGB_chunk(self, index, name, data):
        print(f'{name.decode("utf-8")} Chunk')
        types = {
            0: 'Perceptual',
            1: 'Relatice colorimetric',
            2: 'Saturation',
            3: 'Absolute colorimetric'
            }
        index = int.from_bytes(data, 'big')
        print(f'  Rendering intent: {types[index]}')

    def CreateCleanCopy(self, NewFileName):
        PNG_Header = b'\x89PNG\r\n\x1a\n'
        AncilaryChunks = [
                b'IHDR',
                b'PLTE',
                b'IDAT',
                b'IEND'
            ]

        File = open(NewFileName, 'wb')
        File.write(PNG_Header)

        for chunk in self.chunks:
            if chunk[0] in AncilaryChunks:
                File.write(chunk[2])
                File.write(chunk[0])
                if chunk[0] == b'IDAT':

                    #Byla podjeta proba metody least significant bit
                    #Ktora slozy do usuwania ukrytych informacji w IDAT'ach
                    #program dziala, bo ostatecznie ta czesc nic nie zmienia

                    length = int.from_bytes(chunk[2], 'big')
                    #byte = os.urandom(1)
                    byte = chunk[1][length-1:length]
                    byte = int.from_bytes(byte, 'big')
                    #byte = byte+1
                    #byte = bin(byte)
                    
                    byte = byte.to_bytes(1,'big')
                    
                   # print(f'{byte}\n')
                    File.write(chunk[1][:length-1])
                    File.write(byte)
                else:
                    File.write(chunk[1])
                File.write(chunk[3])

        File.close()

    def Paeth(a, b, c):
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            Pr = a
        elif pb <= pc:
            Pr = b
        else:
            Pr = c
        return Pr

    def DeFilterIDAT(self):
        Data = self.GetDecompressedIDATdata()
        data = []
        DataAfter = []
        #print ([x for x in Data])
        for byte in Data:
           # data.append(byte)
            DataAfter.append(byte)
        PixelLength = 0
        FilterType = 0
        #Match color type with the length of data per pixel
        if self.color_type == 0:
            PixelLength = 1
        elif self.color_type == 2:
            PixelLength = 3
        elif self.color_type == 3 :
            raise Exception('Color indexing is not implemented')
        elif self.color_type == 4 :
            PixelLength = 2
        elif self.color_type == 6 :
            PixelLength = 4
        else: raise Exception("Invalid Color Type")

        RowLength = PixelLength * self.width + 1

        self.PixelLength = PixelLength
        #Defilter
        for j in range(self.height):
            for i in range(RowLength):
                if i == 0:
                    FilterType = DataAfter[i]
                    self.FilterType.append(FilterType)
                    #DataAfter[i] = 0
                    continue
                
                if FilterType == 0:
                    break

                elif FilterType == 1:
                    if i < (RowLength - PixelLength):
                        DataAfter[j*RowLength + PixelLength+i] =  DataAfter[j*RowLength + PixelLength+i] + DataAfter[j*RowLength + i]
                        if DataAfter[j*RowLength + PixelLength+i] > 255: 
                            DataAfter[j*RowLength + PixelLength+i] -= 255

                elif FilterType == 2:
                    if j == 0: break
                    DataAfter[j*RowLength+i] = DataAfter[j*RowLength + i] + DataAfter[(j-1)*RowLength + i]
                    if DataAfter[j*RowLength+i] > 255: 
                        DataAfter[j*RowLength+i] -= 255

                elif FilterType == 3:
                    if j == 0: break
                    if i > PixelLength:
                        a = DataAfter[j*RowLength + i] + DataAfter[j*RowLength + i - PixelLength]
                        b = DataAfter[j*RowLength + i] + DataAfter[(j-1)*RowLength + i]
                        DataAfter[j*RowLength + i] =  (a+b)/2
                        if DataAfter[j*RowLength + i] > 255: 
                            DataAfter[j*RowLength + i] -= 255

                elif FilterType == 4:
                    if j == 0: break
                    if i > PixelLength:
                        a = DataAfter[j*RowLength + i] + DataAfter[j*RowLength + i - PixelLength]
                        b = DataAfter[j*RowLength + i] + DataAfter[(j-1)*RowLength + i]
                        c = DataAfter[j*RowLength + i] + DataAfter[(j-1)*RowLength + i - PixelLength]
                        DataAfter[j*RowLength + PixelLength+i] += Paeth(a,b,c)
                        if DataAfter[j*RowLength + PixelLength+i] > 255: 
                            DataAfter[j*RowLength + PixelLength+i] -= 255

                else: raise Exception('Unknown filter type: ' + str(FilterType))

        #print ([x for x in DataAfter])
        DataAfterBytes = b''
        for i in DataAfter:
            new_bytevalues = i.to_bytes(length=1, byteorder='big')
            #bye = int.to_bytes(i , byteorder='big')
            DataAfterBytes += new_bytevalues
        return DataAfterBytes

    def ReFilterIDAT(self):

        PixelLength = self.PixelLength
        RowLength = PixelLength * self.width + 1
        #Defilter
        for j in range(self.height):
            for i in range(RowLength):
                if i == 0:
                    FilterType = DataAfter[i]
                    self.FilterType.append(FilterType)
                    #DataAfter[i] = 0
                    continue
                
                if FilterType == 0:
                    break

                elif FilterType == 1:
                    if i < (RowLength - PixelLength):
                        DataAfter[j*RowLength + PixelLength+i] =  DataAfter[j*RowLength + PixelLength+i] - DataAfter[j*RowLength + i]
                        if DataAfter[j*RowLength + PixelLength+i] > 255: 
                            DataAfter[j*RowLength + PixelLength+i] -= 255

                elif FilterType == 2:
                    if j == 0: break
                    DataAfter[j*RowLength+i] = DataAfter[j*RowLength + i] - DataAfter[(j-1)*RowLength + i]
                    if DataAfter[j*RowLength+i] > 255: 
                        DataAfter[j*RowLength+i] -= 255

                elif FilterType == 3:
                    if j == 0: break
                    if i > PixelLength:
                        a = DataAfter[j*RowLength + i] - DataAfter[j*RowLength + i - PixelLength]
                        b = DataAfter[j*RowLength + i] - DataAfter[(j-1)*RowLength + i]
                        DataAfter[j*RowLength + i] =  (a+b)/2
                        if DataAfter[j*RowLength + i] > 255: 
                            DataAfter[j*RowLength + i] -= 255

                elif FilterType == 4:
                    if j == 0: break
                    if i > PixelLength:
                        a = DataAfter[j*RowLength + i] - DataAfter[j*RowLength + i - PixelLength]
                        b = DataAfter[j*RowLength + i] - DataAfter[(j-1)*RowLength + i]
                        c = DataAfter[j*RowLength + i] - DataAfter[(j-1)*RowLength + i - PixelLength]
                        DataAfter[j*RowLength + PixelLength+i] += Paeth(a,b,c)
                        if DataAfter[j*RowLength + PixelLength+i] > 255: 
                            DataAfter[j*RowLength + PixelLength+i] -= 255

                else: raise Exception('Unknown filter type: ' + str(FilterType))

        #print ([x for x in DataAfter])
        DataAfterBytes = b''
        for i in DataAfter:
            new_bytevalues = i.to_bytes(length=1, byteorder='big')
            #bye = int.to_bytes(i , byteorder='big')
            DataAfterBytes += new_bytevalues
        return DataAfterBytes

    def CreateSingleIdatChunk(self):
        print('Creating Singlar IDAT\n')
        here = False
        tempchunks = self.chunks.copy()
        #print(id(tempchunks))
        #print(id(self.chunks))
        for chunk in tempchunks:
                if chunk[0] == b'IDAT':
                    if here == False:
                        here = True
                        self.EnChunks.append(chunk)
                    else:
                        len1 = int.from_bytes(self.EnChunks[self.IdatLocation][2], byteorder='big')
                        len2 = int.from_bytes(chunk[2], byteorder='big')
                        len3 = len1 + len2
                        chunkappend = len3.to_bytes(4, byteorder = 'big')

                        self.EnChunks[self.IdatLocation][2] = chunkappend
                        self.EnChunks[self.IdatLocation][1] += chunk[1] 
                else:
                    self.EnChunks.append(chunk)    
                if here == False:
                    self.IdatLocation += 1
        #self.EnChunks[self.IdatLocation][1] = self.DeFilterIDAT()
        self.GenKeys()

    def SetDefilter():
        self.EnChunks[self.IdatLocation][1] = self.DeFilterIDAT()

    def ECB_EnDeCrypt(self,EnCase):
        self.GetDecompressedIDATdata()
        data = self.EnChunks[self.IdatLocation][1]
        NewData = []
        if EnCase == 1:
            print('Beggining ECB encryption')
            for i in range (len(data)):
                Encrypt = int.from_bytes(data[i:i+1],'big')
                Add = RSA.ECB_encrypt(Encrypt, self.PublicKey)
                Add = Add.to_bytes(2, 'big')
                NewData.append(Add)
            self.EnChunks[self.IdatLocation][1] = b''.join(NewData)  # b'': separator
            self.EnChunks[self.IdatLocation][2] = len(NewData).to_bytes(4, 'big')
            print('ECB encrypting complete\n')

        elif EnCase == 0:
            print('Beggining ECB decryption')
            for i in range (0, len(data), 2):
                Decrypt = int.from_bytes(data[i:i+2],'big')
                Add = RSA.ECB_decrypt(Decrypt, self.PrivateKey)
                Add = Add.to_bytes(1, 'big')
                NewData.append(Add)
            self.EnChunks[self.IdatLocation][1] = b''.join(NewData)  # b'': separator
            self.EnChunks[self.IdatLocation][2] = len(NewData).to_bytes(4, 'big')
            print('ECB decrypting complete\n')
        self.CompressIDATdata()

    def CTR_EnDeCrypt(self):
        self.GetDecompressedIDATdata()
        data = self.EnChunks[self.IdatLocation][1]
        NewData = []
        print('Beggining CTR encryption/decryption')
        for i in range(len(data)):
                Encrypt = int.from_bytes(data[i:i+1],'big')
                Add = RSA.CTR_encrypt(Encrypt, self.PublicKey, self.nonce, i)
                AddByte = Add.to_bytes(2,'big')
                NewData.append(AddByte[1:2])
        self.EnChunks[self.IdatLocation][1] = b''.join(NewData)
        print('CTR encryption/decryption complete\n')
        self.CompressIDATdata()
        
    def RSA_EnDeCrypt(self, EnCase):
        self.GetDecompressedIDATdata()
        data = self.EnChunks[self.IdatLocation][1]
        NewData = []
        if EnCase == 1:
            print('Beggining RSA encryption')
            for i in range(len(data)):
                Encrypt = data[i:i+1]
                Add = RSA.RSA_encrypt(Encrypt)
                NewData.append(Add)
            self.EnChunks[self.IdatLocation][1] = b''.join(NewData)
            print('RSA encrypting complete\n')
        if EnCase == 0:
            print('Beggining RSA decryption')
            for i in range (0, len(data), 256):
                Decrypt = data[i:i+256]
                Add = RSA.RSA_decrypt(Decrypt)
                NewData.append(Add)
            self.EnChunks[self.IdatLocation][1] = b''.join(NewData)
            print('RSA decrypting complete\n')
        self.CompressIDATdata()

    def GenKeys(self):
        p = 0
        q = 0
        IDATL = len(self.EnChunks[self.IdatLocation][1])
        print('Generating Keys\n')
        #print(f'IDAT size: {IDATLength}')
        b = sqrt(sqrt(IDATL))
        #while self.PrivateKey[0] < IDATLength or self.PublicKey[0] < IDATLength:
        while p == q :#and p*q<32700:
            p = sympy.randprime(20, b+200)
            q = sympy.randprime(20, b+200)

        Keys = KeyGenerator.KeysG(p,q)
        self.PrivateKey = [Keys[1], Keys[2]]
        self.PublicKey = [Keys[0], Keys[2]]
        
        #print(f'PublicKey: {self.PublicKey}')
        #print(f'PublicKey: {self.PrivateKey}')
        RSA.GenRSA_keys(self.PublicKey, self.PrivateKey)

    def CreateNewPNG(self,NewFileName):
        print(f'Saving image as: {NewFileName}')
        File = open(NewFileName, 'wb')
        File.write(b'\x89PNG\r\n\x1a\n')
        #IdatLS = int.from_bytes(self.EnChunks[self.IdatLocation][2],'big')
        #IdatLC = len(self.EnChunks[self.IdatLocation][2])
        #print(f'IdatLS: {IdatLS}')
        #print(f'IdatLC: {IdatLC}')
        for chunk in self.EnChunks:
            if chunk[0] == b'IDAT':
                length = len(chunk[1]).to_bytes(4,'big')
                File.write(length)
                File.write(chunk[0])
                File.write(chunk[1])
                crcCheck = chunk[0] + chunk[1]
                crc = crc32(crcCheck)
                crcbyte = (crc).to_bytes(4, byteorder='big')
                File.write(crcbyte)
            else:
                File.write(chunk[2])
                File.write(chunk[0])
                File.write(chunk[1])
                crcCheck = chunk[0] + chunk[1]
                crc = crc32(crcCheck)
                crcbyte = (crc).to_bytes(4, byteorder='big')
                File.write(crcbyte)
        File.close()


      
if __name__ == '__main__':
    my_image = 'png_files\\small.png'
    #my_image = 'png_files\\test6.png'
    PNG_Analysis = PNGChunkAnaliser(my_image)

    #PNG_Analysis.DeFilterIDAT()
    PNG_Analysis.CreateCleanCopy('CleanCopy.png')
    PNG_Analysis.CreateSingleIdatChunk()
    #PNG_Analysis.CreateNewPNG('test1.png')


    PNG_Analysis.ECB_EnDeCrypt(1)
    PNG_Analysis.CreateNewPNG('ECB_EN.png')
    PNG_Analysis.ECB_EnDeCrypt(0)
    PNG_Analysis.CreateNewPNG('ECB_DE.png')

    #PNG_Analysis.CTR_EnDeCrypt()
    #PNG_Analysis.CreateNewPNG('CTR_EN.png')
    #PNG_Analysis.CTR_EnDeCrypt()
    #PNG_Analysis.CreateNewPNG('CTR_DE.png')

    #PNG_Analysis.RSA_EnDeCrypt(1)
    #PNG_Analysis.CreateNewPNG('RSA_EN.png')
    #PNG_Analysis.RSA_EnDeCrypt(0)
    #PNG_Analysis.CreateNewPNG('RSA_DE.png')

