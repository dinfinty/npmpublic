import os
import sys
directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(directory, "../")))

from web3 import Web3
import utils
import constants
from interfaces import *
from signer import Signer

class OnboardingSigner(Signer):
    def __init__(self):
        super().__init__()

    def create_signature(self, msg, private_key):
        """
            Signs the message.
            Inputs:
                - msg: the message to be signed
                - private_key: the signer's private key
            Returns:
                - str: signed msg hash
        """
        hash = Web3.sha3(text=msg).hex()
        return self.sign_hash(hash, private_key)

