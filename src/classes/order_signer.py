import os
import sys
from interfaces import Order
directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(directory, "../")))

from web3 import Web3
import utils
import constants
from signer import Signer


class OrderSigner(Signer):
    def __init__(self, network_id, orders_contract_address, domain="IsolatedTrader", version="1.0"):
        super().__init__()
        self.network_id = network_id
        self.contract_address = orders_contract_address;
        self.domain = domain
        self.version = version 

    def get_order_flags(self, order):
        flag = 0 

        if order["reduceOnly"]:
            flag += constants.ORDER_FLAGS["IS_DECREASE_ONLY"] 

        if order["isBuy"]:
            flag += constants.ORDER_FLAGS["IS_BUY"] 
        
        saltBytes = utils.bn_to_bytes8(order["salt"])

        return b''.join([
            "0x".encode('utf-8'), 
            saltBytes[-15:],
            str(flag).encode('utf-8')
            ]).decode().ljust(66, '0')
    
    def get_domain_hash(self):
        """
            Returns domain hash
        """
        return Web3.solidityKeccak(
        [
            'bytes32',
            'bytes32',
            'bytes32',
            'uint256',
            'bytes32'
        ],
        [
            utils.hash_string(constants.EIP712_DOMAIN_STRING),
            utils.hash_string(self.domain),
            utils.hash_string(self.version),
            self.network_id,
            utils.address_to_bytes32(self.contract_address)
        ]
    ).hex()

    def get_order_hash(self, order:Order):
        """
            Returns order hash.
            Inputs:
                - order: the order to be signed
            Returns:
                - str: order hash
        """
        flags = self.get_order_flags(order)
        struct_hash = Web3.solidityKeccak(
            abi_types=[
                'bytes32',
                'bytes32',
                'uint256',
                'uint256',
                'uint256',
                'uint256',
                'bytes32',
                'uint256'
                ],

            values=[
                utils.hash_string(constants.EIP712_ORDER_STRUCT_STRING),
                flags,
                int(order["quantity"]),
                int(order["price"]),
                int(order["triggerPrice"]),
                int(order["leverage"]),
                utils.address_to_bytes32(order["maker"]),
                int(order["expiration"])
            ]
        ).hex()

        return self.get_eip712_hash(self.get_domain_hash(), struct_hash) if struct_hash else "";

    def sign_order(self, order:Order, private_key):
        """
            Used to create an order signature. The method will use the provided key 
            in params(if any) to sign the order.

            Args:
                order (Order): an order containing order fields (look at Order interface)
                private_key (str): private key of the account to be used for signing
    
            Returns:
                str: generated signature
        """
        order_hash = self.get_order_hash(order)
        return self.sign_hash(order_hash, private_key, "01")

    def sign_cancellation_hash(self,order_hash:list):
        """
            Used to create a cancel order signature. The method will use the provided key 
            in params(if any) to sign the cancel order.

            Args:
                order_hash(list): a list containing all orders to be cancelled
                private_key (str): private key of the account to be used for signing
            Returns:
                str: generated signature
        """
        struct_hash = Web3.solidityKeccak(
            abi_types=['bytes32','bytes32','bytes32'],
            values=[
                utils.hash_string(constants.EIP712_CANCEL_ORDER_STRUCT_STRING),
                utils.hash_string("Cancel Orders"),
                Web3.solidityKeccak(
                    abi_types=['bytes32' for i in range(len(order_hash))],
                    values=[hash for hash in order_hash]
                ).hex()
            ]
        ).hex()
        return self.get_eip712_hash(self.get_domain_hash(), struct_hash) if struct_hash else ""





    