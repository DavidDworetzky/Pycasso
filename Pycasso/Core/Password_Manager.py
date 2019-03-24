import os
import random
import string
from hmac import compare_digest as compare_hash
import hashlib


class Password_Manager:
    def __init__(self, salt=None, rounds=None):
        self.salt = salt
        self.rounds = rounds

    def sha512_hash(self,password):
        return hashlib.sha512(self.salt + password).hexdigest()

    #verifies a hashed password
    def sha512_verify(self,password, hash):
        return self.sha512_hash(password) == hash
