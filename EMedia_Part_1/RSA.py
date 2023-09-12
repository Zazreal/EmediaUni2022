from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA


def GenRSA_keys(PubKey,PrivKey):
        new_key = RSA.generate(2048)
        private_RSA = new_key.exportKey("PEM")
        public_RSA = new_key.publickey().exportKey("PEM")

        f = open("private_key.pem", "wb")
        f.write(private_RSA)
        f.close()

        f = open("public_key.pem", "wb")
        f.write(public_RSA)
        f.close()

def ECB_encrypt (Data, PublicKey):
    EncryptedData = pow(Data, PublicKey[0], PublicKey[1])
    return EncryptedData  
    
def ECB_decrypt(Data, PrivateKey):
    DecryptedData = pow(Data, PrivateKey[0], PrivateKey[1])
    return DecryptedData

def CTR_encrypt(Data, PublicKey, nonce, counter):
    EncryptedCounter = pow(nonce+counter, PublicKey[0], PublicKey[1])
    EncryptedData = EncryptedCounter^Data 
    return EncryptedData

def RSA_encrypt(data):
    key = RSA.import_key(open('public_key.pem').read())
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(data)
    return ciphertext 


def RSA_decrypt(data):
    key = RSA.import_key(open('private_key.pem').read())
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.decrypt(data)
    return ciphertext