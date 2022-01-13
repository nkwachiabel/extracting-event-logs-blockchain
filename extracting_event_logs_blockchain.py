#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Crypto.Hash import keccak
from web3 import Web3


from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from opyenxes.factory.XFactory import XFactory
from opyenxes.factory.XFactoryRegistry import XFactoryRegistry
from opyenxes.extension.XExtension import XExtension
from opyenxes.extension.XExtensionManager import XExtensionManager
from opyenxes.extension.std.XConceptExtension import XConceptExtension
from opyenxes.extension.std.XTimeExtension import XTimeExtension
from opyenxes.extension.std.XOrganizationalExtension import XOrganizationalExtension
from opyenxes.extension.std.XLifecycleExtension import XLifecycleExtension
from opyenxes.extension.std.XCostExtension import XCostExtension
from opyenxes.extension.std.XIdentityExtension import XIdentityExtension


class ExtractingEventLogsBlockchain(object):

    def __init__(process_name, activity_names, ressources, http_provider):
        '''
            Arguments:
                process_name (string): Name of the process.
                activity_names (dictionary): A dictionary where the key is the name of an activity
                    in the process and the value is a function signature.
                ressources (dictionary): A dictionary where the key is the name of an activity
                    in the process and the value is the name of the ressource.
                http_provider (string): A Blockchain node to connect to as a string.
        '''
        self.process_name = process_name
        self.activity_names = activity_names
        self.ressources = ressources
        self.http_provider = http_provider

        self.web3 = self.connect_to_blockchain(http_provider)

        self.function_selectors = self.hash_function_signatures(self.function_signatures)
        self.function_selector_mapping = self.create_function_selector_mapping(self.activity_names, self.function_selectors)

        self.log = {}

        self.set_up_xes_extensions()
        self.log_xes = XFactory.create_log()
        self.add_xes_extensions_to_xes_log()
        self.concept_name.assign_name(element=self.log_xes, name=self.process_name)
        self.lifecycle_extension.assign_model(element=self.log_xes, model="standard")

    def set_up_xes_extensions(self):
        self.concept_extension = XConceptExtension()
        self.time_extension = XTimeExtension()
        self.organizational_extension = XOrganizationalExtension()
        self.lifecycle_extension = XLifecycleExtension()
        self.cost_extension = XCostExtension()
        self.identitity_extension = XIdentityExtension()
        XExtensionManager().register_standard_extensions()

    def add_xes_extensions_to_xes_log(self):
        self.log_xes.get_extensions().add(self.concept_extension)
        self.log_xes.get_extensions().add(self.time_extension)
        self.log_xes.get_extensions().add(self.organizational_extension)
        self.log_xes.get_extensions().add(self.lifecycle_extension)
        self.log_xes.get_extensions().add(self.cost_extension)
        self.log_xes.get_extensions().add(self.identitity_extension)

    def hash_function_signatures(self, function_signatures):
        function_selectors = []

        for function_signature in function_signatures:
            keccak_hash = keccak.new(digest_bits=256)
            byte_string = str.encode(function_signature)
            function_selector = keccak_hash.update(byte_string)
            function_selector = function_selector.hexdigest()
            function_selector = f'0x{function_selector[:8]}'
            function_selectors.append(function_selector)

        return function_selectors

    def connect_to_blockchain(self):
        web3 = Web3(Web3.HTTPProvider(self.http_provider, request_kwargs={'timeout': 60}))
        return web3

    def get_transactions_from_blockchain(self, transaction_hashes, block_numbers):
        if transaction_hashes:
            self.get_transactions_by_transaction_hashes(transaction_hashes)
        else:
            self.get_transactions_from_block_numbers(block_numbers)

    def get_transactions_by_transaction_hashes(self, transaction_hashes):
        self.transactions = []
        for transaction_hash in transaction_hashes:
            transaction = self.web3.eth.getTransaction(transaction_hash)
            self.transactions.append(transaction)

    def get_transactions_from_block_numbers(self, block_numbers):
        self.blocks = []
        for block_number in block_numbers:
            block = self.web3.eth.getBlock(block_number)
            self.blocks.append(block)

    def create_log_from_transactions(self):
        if self.transactions:
            self.process_transactions()
        else:
            self.process_blocks()

    def process_transactions(self):
        for transaction in self.transactions:
            activity_id = transaction["transaction"]["input"][:10]
            activity_name = self.activity_mapping[activity_id]

    def process_blocks(self):
        for block in self.blocks:
            for transactions in block:
                for transaction in transactions:
                    transaction_hash = transaction["hash"].hex()
                    if transaction_hash in self.function_selectors:
                        return 0

    def create_xes_log(self):
        return 0

    def create_function_selector_mapping(self, activity_names, function_selectors):
        function_selector_mapping = {}
        for activity_name, function_signature in activity_names.items():
            return 0
        return function_selector_mapping


if __name__ == '__main__':
    activity_names = {
        "Customer has a problem": "Customer_Has_a_Problem()",
        "Get problem description": "Get_problem_description(int32)",
        "Ask 1st level support": "Ask_1st_level_support(int32)",
        "Explain solution": "Explain_solution()",
        "Ask 2nd level support": "Ask_2nd_level_support()",
        "Provide feedback for account manager": "Provide_feedback_for_account_manager()",
        "Ask developer": "Ask_developer()",
        "Provide feedback for 1st level support": "Provide_feedback_for_1st_level_support()",
        "Provide feedback for 2nd level support": "Provide_feedback_for_2nd_level_support()"
    }

    ressources = {
        "Customer has a problem": "Key Account Manager",
        "Get problem description": "Key Account Manager",
        "Ask 1st level support": "Key Account Manager",
        "Explain solution": "Key Account Manager",
        "Ask 2nd level support": "1st Level Support",
        "Provide feedback for account manager": "1st Level Support",
        "Ask developer": "2nd Level Support",
        "Provide feedback for 1st level support": "2nd Level Support",
        "Provide feedback for 2nd level support": "Software Developer"
    }

    extract_event_log_blockchain = ExtractingEventLogsBlockchain(
        process_name="Incident Management Process",
        activity_names=activity_names,
        ressources=ressources,
        http_provider="https://mainnet.infura.io/v3/2aa2cc2b93984929b4f859479afc4582"
    )
