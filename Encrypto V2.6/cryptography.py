import hashlib
import base64
import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import rsa

# SHA-1 hashing function
def generate_sha1_hash(data):
    """
    Generate a SHA-1 hash of the input data for digital signatures
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha1(data).hexdigest()

# AES CTR Mode encryption/decryption
class CTRCipher:
    @staticmethod
    def generate_key():
        """Generate a random 256-bit key for AES encryption"""
        return get_random_bytes(32)
    
    @staticmethod
    def encrypt(data, key):
        """
        Encrypt data using AES in CTR mode
        Returns (ciphertext, nonce) as a tuple
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        cipher = AES.new(key, AES.MODE_CTR)
        ciphertext = cipher.encrypt(data)
        
        # Return Base64 encoded ciphertext and nonce for storage/transmission
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(cipher.nonce).decode('utf-8')
        }
    
    @staticmethod
    def decrypt(encrypted_data, key):
        """
        Decrypt data that was encrypted with AES in CTR mode
        encrypted_data should be a dict with 'ciphertext' and 'nonce' keys
        """
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        
        return plaintext.decode('utf-8')

# RSA encryption/decryption
class RSACipher:
    @staticmethod
    def generate_key_pair():
        """Generate RSA public and private key pair"""
        (pubkey, privkey) = rsa.newkeys(2048)
        return {
            'public_key': pubkey,
            'private_key': privkey
        }
    
    @staticmethod
    def encrypt(data, public_key):
        """Encrypt data using RSA public key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # RSA can only encrypt small chunks of data
        # For larger data, we would typically encrypt a symmetric key with RSA
        # and then encrypt the actual data with that symmetric key
        # and i will not do this why because iam lazy 
        ciphertext = rsa.encrypt(data, public_key)
        return base64.b64encode(ciphertext).decode('utf-8')
    
    @staticmethod
    def decrypt(encrypted_data, private_key):
        """Decrypt data using RSA private key"""
        ciphertext = base64.b64decode(encrypted_data)
        plaintext = rsa.decrypt(ciphertext, private_key)
        return plaintext.decode('utf-8')
    
    @staticmethod
    def sign(data, private_key):
        """Create a digital signature using RSA private key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        signature = rsa.sign(data, private_key, 'SHA-1')
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify(data, signature, public_key):
        """Verify a digital signature using RSA public key"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        signature = base64.b64decode(signature)
        try:
            rsa.verify(data, signature, public_key)
            return True
        except:
            return False

# Hybrid encryption for secure message exchange
def encrypt_message(message, public_key):
    """
    Hybrid encryption: Use AES-CTR for message and RSA for the AES key
    """
    # Generate a random AES key for this message
    aes_key = CTRCipher.generate_key()
    
    # Encrypt the message with AES-CTR
    encrypted_message = CTRCipher.encrypt(message, aes_key)
    
    # Encrypt the AES key with RSA
    encrypted_key = RSACipher.encrypt(aes_key, public_key)
    
    # Generate SHA-1 hash of the original message for integrity
    message_hash = generate_sha1_hash(message)
    
    return {
        'encrypted_message': encrypted_message,
        'encrypted_key': encrypted_key,
        'hash': message_hash
    }

def decrypt_message(encrypted_data, private_key):
    """
    Decrypt a message that was encrypted using hybrid encryption
    """
    # Decrypt the AES key with RSA
    encrypted_key = encrypted_data['encrypted_key']
    aes_key = base64.b64decode(RSACipher.decrypt(encrypted_key, private_key))
    
    # Decrypt the message with AES-CTR
    decrypted_message = CTRCipher.decrypt(encrypted_data['encrypted_message'], aes_key)
    
    # Verify message integrity using SHA-1
    message_hash = generate_sha1_hash(decrypted_message)
    if message_hash != encrypted_data['hash']:
        raise ValueError("Message integrity check failed")
    
    return decrypted_message
