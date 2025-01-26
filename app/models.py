from .app import db
from azure.identity import ClientSecretCredential
from azure.keyvault.keys.crypto import KeyWrapAlgorithm, CryptographyClient
import os
import hashlib
from Crypto.Cipher import AES

class SecureFeedback(db.Model):
    __tablename__ = 'secure_feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.LargeBinary)
    contact_number = db.Column(db.LargeBinary)
    encrypted_feedback = db.Column(db.LargeBinary)
    dek = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

class CustomerFeedback:
    def __init__(self, email, contact_number, feedback):
        self.email = email
        self.contact_number = contact_number
        self.feedback = feedback

class SecurityHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityHelper, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        vault_uri = os.getenv("AZURE_KEY_VAULT_URI")

        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.cryptography_client = CryptographyClient(vault_uri, credential)

    def generate_dek(self, email):
        """
        Generates a data encryption key (DEK) using the provided email address to
        create a unique DEK. The DEK is a SHA-256 hash of the email address.
        
        :param email: The email address used to generate the DEK.
        :return: The generated DEK.
        """
        return hashlib.sha256(email.encode()).digest()

    def generate_encrypted_dek(self, email):
        """
        Generates an encrypted data encryption key (DEK) using the provided email
        to create a unique DEK, and then encrypts the DEK using the Key Vault-managed
        key encryption key (KEK).

        :param email: The email address used to generate the DEK.
        :return: The encrypted data encryption key (DEK).
        """
        dek = self.generate_dek(email)
        wrap_result = self.cryptography_client.wrap_key(KeyWrapAlgorithm.rsa_oaep, dek)
        return wrap_result.encrypted_key

    def encrypt(self, input_data, encrypted_dek):
        """
        Encrypts the input data using the provided encrypted data encryption key (DEK).

        :param input_data: The string that needs to be encrypted.
        :param encrypted_dek: The encrypted data encryption key used to encrypt the input data.
        :return: The encrypted input_data, which is the nonce (16 bytes), tag (16 bytes), and ciphertext.
        """
        decrypted_dek = self.cryptography_client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, encrypted_dek).key
        return self._encrypt_data_with_dek(input_data, decrypted_dek)

    def decrypt(self, input_data, encrypted_dek):
        """
        Decrypts the input data using the provided encrypted data encryption key (DEK).

        :param input_data: The encrypted data to be decrypted.
        :param encrypted_dek: The encrypted data encryption key used to decrypt the input data.
        :return: The decrypted data as a string.
        """
        decrypted_dek = self.cryptography_client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, encrypted_dek).key
        return self._decrypt_data_with_dek(input_data, decrypted_dek)

    def _encrypt_data_with_dek(self, input_data, dek):
        """
        Encrypt input_data with dek using AES-GCM.

        :param input_data: The string that needs to be encrypted
        :param dek: The data encryption key
        :return: The encrypted input_data, which is the nonce (16 bytes), tag (16 bytes), and ciphertext
        """
        cipher = AES.new(dek, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(input_data.encode())
        return cipher.nonce + tag + ciphertext

    def _decrypt_data_with_dek(self, input_data, dek):
        """
        Decrypt input_data with dek using AES-GCM.

        :param input_data: The encrypted bytes that needs to be decrypted
        :param dek: The data encryption key
        :return: The decrypted input_data as a string
        """
        nonce, tag, ciphertext = input_data[:16], input_data[16:32], input_data[32:]
        cipher = AES.new(dek, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()


