import socket

from Crypto.Hash import SHA256

from keepassc.helper import cbc_encrypt, cbc_decrypt, get_key

class Connection(object):
    def __init__(self, password = None, keyfile = None):
        self.seed1 = None
        self.seed2 = None
        self.rounds = None
        self.vec = None
        self.password = password
        self.keyfile = keyfile
        self.masterkey = get_key(self.password, self.keyfile)
        self.final_key = None

    def create_hash(self, msg):
        """Create hash to verify decrypted message"""

        sha_obj = SHA256.new()
        sha_obj.update(msg)
        return sha_obj.digest()

    def verify_decryption(self, msg, test_hash):
        """Verify decryption"""

        sha_obj = SHA256.new()
        sha_obj.update(msg)
        # Test if decrypted data is correct
        return (test_hash == sha_obj.digest())

    def encrypt_msg(self, msg):
        test_hash = self.create_hash(msg)
        msg = cbc_encrypt(msg, self.final_key, self.vec)
        return msg+test_hash

    def decrypt_msg(self, msg):
        decrypted_msg = cbc_decrypt(self.final_key, msg[:-32], self.vec)
        if self.verify_decryption(decrypted_msg, msg[-32:]) is True:
            return decrypted_msg
        else:
            return False

    def receive(self, conn):
        """Receive a message"""

        data = b''
        while True:
            received = conn.recv(16)
            if b'END' in received:
                data += received[:received.find(b'END')]
                break
            else:
                data += received
                if data[-3:] == b'END':
                    data = data[:-3]
                    break
        return data

    def sendmsg(self, sock, msg):
        """Send message"""

        sock.sendall(self.encrypt_msg(msg) + b'END')
