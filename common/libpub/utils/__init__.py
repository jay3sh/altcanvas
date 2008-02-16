'''libpub.utils module'''

def encrypt(plain):
    '''
        Encrypt a plain text string.
        Currently a simple ceasar cipher is used.
        @param plain: plaintext string that needs encryption
    '''
    cipher = ''
    for c in plain:
        cipher = cipher + chr(ord(c)+4)
    return cipher

def decrypt(cipher):
    '''
        Decrypt a cipher text.
        Currently a simple ceasar cipher is used.
        @param cipher: encrypted string that needs decryption
    '''
    plain = ''
    for c in cipher:
        plain = plain + chr(ord(c)-4)
    return plain 
