#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import pickle
from datetime import datetime

from Crypto.Hash import keccak
from web3.auto.infura import w3
from web3 import Web3

# OpyenXES
## XES Serializer
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
## XES Log
from opyenxes.factory.XFactory import XFactory
from opyenxes.factory.XFactoryRegistry import XFactoryRegistry
## XES Log extensions
from opyenxes.extension.XExtension import XExtension
from opyenxes.extension.XExtensionManager import XExtensionManager
from opyenxes.extension.std.XConceptExtension import XConceptExtension
from opyenxes.extension.std.XTimeExtension import XTimeExtension
from opyenxes.extension.std.XOrganizationalExtension import XOrganizationalExtension
from opyenxes.extension.std.XLifecycleExtension import XLifecycleExtension
from opyenxes.extension.std.XCostExtension import XCostExtension
from opyenxes.extension.std.XIdentityExtension import XIdentityExtension


def connect_to_http_provider(
    http_provider="https://mainnet.infura.io/v3/2aa2cc2b93984929b4f859479afc4582",
    timeout=60):
    '''
        Connects to the blockchain node http_provider.

        A w3 object is returned if the connection to the node was successfull.
        An exception is raised if the connection to the node failed.

        Arguments:
            http_provider (string): A unified ressource locator (URL) to a blockchain service, e.g. Infura.
            timeout (int): An integer determining the time period for which the client is alive.

        Returns:
            A web3 http provider object.
    '''
    http_provider = Web3(
        Web3.HTTPProvider(http_provider,
                          request_kwargs={'timeout': timeout}))

    if http_provider.isConnected():
        return http_provider
    else:
        raise Exception(f'Connection to {http_provider} failed!')


def create_function_selector_for_function_signature(function_signature):
    '''
        Creates the function selector for the given function siganture.
        For more details about the function selector see Di Ciccio et al.
        (references are at the of this notebook), and for more examples than
        the one provided below see Mühlberger et al. figure 1 on page 8.

        Argument:
            function_signature (string): A function signature as a string.

        Returns:
            function selector of function_signature.

        Example:
            function signature: Customer_Has_a_Problem()
            function selector: 0xefe73dcb

            >> create_function_selector_for_function_signature('Customer_Has_a_Problem()')
            '0xefe73dcb'
    '''
    keccak_hash = keccak.new(digest_bits=256)

    function_signature = str.encode(function_signature)

    function_signature_hash = keccak_hash.update(function_signature)

    function_signature_hash = function_signature_hash.hexdigest()

    function_selector = '0x' + function_signature_hash[:8]
    return function_selector


def create_activities_dictionary(activity_names, function_signatures, activity_resources):
    '''
        create_activities_dictionary creates a dictionary where the key is the function selector (see above).
        The value of the key is again a dictionary with keys activity_name, function_signature, and
        resource.

        Arguments:
            activity_names (list): A list of activity names.
            function_signatures (list): A list of function signatures.
            activity_resources (list): A list of activity resources.

        Returns:
            acitivites dictionary.

        Example:
            activity name: "Ask 2nd level support"
            function signature: Ask_2nd_level_support()
            activity resource: 1st Level Support

            >> create_activities_dictionary(
                activity_names="Ask 2nd level support",
                function_signatures="Ask_2nd_level_support()",
                activity_resources="1st Level Support")
            {
                '0x63ad6b81': {
                    'activity_name': 'Ask 2nd level support',
                    'function_signature' : Ask_2nd_level_support(),
                    'resouce': '1st Level Support'
                }
            }
    '''
    assert len(activity_names) == len(function_signatures) == len(activity_resources)

    activities_dictionary = {}

    for idx, activity_name in enumerate(activity_names):
        function_selector = create_function_selector_for_function_signature(
            function_signatures[idx])

        activities_dictionary[function_selector] = {
            'activity_name': activity_name,
            'function_signature': function_signatures[idx],
            'resource': activity_resources[idx]
        }

    return activities_dictionary


def get_activity_transactions_from_block_number(activities_dictionary, block_number, http_provider):
    '''
        get_activity_transactions_from_block_number retrieves the given block number and
        searches in the transactions of the retrieved block for transactions that are associated to an activity.
        The result is returned as a list. An empty list is returned if no transaction corresponds
        to an activity.

        Arguments:
            activities_dictionary (dictionary): A dictionary where the keys are function selectors (see above).
                Idially, the dictionary is created with the function create_activities_dictionary from above.
            block_number (int): An integer that specifies the block that should be retrieved.
            http_provider (w3 object): A w3 object that has established a connection to a blockchain node.
                Idially, the object is created with connect_to_http_provider.

        Returns:
            activity_transactions (list): The activity_transactions as a list. Each entry in the list is an
                unprocessed transaction from the blockchain.
    '''
    activity_transactions = []

    block = http_provider.eth.getBlock(block_number, full_transactions=True)
    for transaction in block["transactions"]:
        input_data = transaction["input"]
        function_selector = input_data[:10]
        if function_selector in activities_dictionary:
            # The first 4 bytes are equal to one key in activites. Therefore, the transaction is
            # associated to an activity.
            activity_transactions.append({"block": block, "transaction": transaction})

    return activity_transactions


def get_activity_transactions_from_block_numbers(activities_dictionary, block_numbers, http_provider):
    '''

        Arguments
            activities_dictionary (dictionary): A dictionary where the keys are function selectors (see above).
                Idially, the dictionary is created with the function create_activities_dictionary from above.
            block_number (list): A list of integers that specify the blocks that should be searched for activity
                transactions, i.e. transactions that are associated to activity executions.
            http_provider (w3 object): A w3 object that has established a connection to a blockchain node.
                Idially, the object is created with connect_to_http_provider.

        Returns:
            activity_transactions (list): The activity_transactions as a list. Each entry in the list is an
                unprocessed transaction from the blockchain.

    '''
    activity_transactions = []

    for block_number in block_numbers:
        activity_transactions_from_block = get_activity_transactions_from_block_number(
            activities_dictionary, block_number, http_provider)

        activity_transactions.extend(activity_transactions_from_block)

    return activity_transactions


def create_log_dictionary_from_activity_transactions(activity_transactions, activities_dictionary):
    '''

        Arguments:
            activity_transactions (list): A list of blockchain transactions.
            activities_dictionary (dictionary): A dictionary where the keys are function selectors (see above).
                Idially, the dictionary is created with the function create_activities_dictionary from above.

        Returns:
            A dictionary where the keys are the trace ids and the value is a list. The list is a sequence of dictionaries that describe an activity.
    '''
    log_dic = {}

    for activity_transaction in activity_transactions:
        trace_id = "i" + activity_transaction["transaction"]["to"]
        function_selector = activity_transaction["transaction"]["input"][:10]

        activity = activities_dictionary[function_selector]
        activity_name = activity["activity_name"]
        activity_name_resource = activity["resource"]

        activity_instance_id = activity_transaction["transaction"]["hash"].hex()
        activity_instance_id_time_stamp = activity_transaction["block"]["timestamp"]
        activity_instance_id_block_no = activity_transaction["transaction"]["blockNumber"]
        activity_instance_id_from = activity_transaction["transaction"]["from"]
        activity_instance_id_txh_gas = activity_transaction["transaction"]["gas"]
        activity_instance_id_txh_gas_price = activity_transaction["transaction"]["gasPrice"]
        activity_instance_id_transaction_data = activity_transaction["transaction"]["input"]

        activity = {}
        activity["id"] = function_selector
        activity["name"] = activity_name
        activity["name_resource"] = activity_name_resource
        activity["instance_id"] = "i" + activity_instance_id
        activity["instance_id_time_stamp"] = datetime.fromtimestamp(activity_instance_id_time_stamp)
        activity["instance_id_block_no"] = activity_instance_id_block_no
        activity["instance_id_from"] = activity_instance_id_from
        activity["instance_id_txh_gas"] = activity_instance_id_txh_gas
        activity["instance_id_txh_gas_price"] = activity_instance_id_txh_gas_price
        activity["instance_id_transaction_data"] = activity_instance_id_transaction_data

        if trace_id not in log_dic:
            log_dic[trace_id] = []

        log_dic[trace_id].append(activity)

    return log_dic


def sort_log_dic_by_time(log_dic):
    '''
        sort_log_dic_by_time sorts the log dictionary by time. Specifically, it uses the key
        instance_id_time_stamp created by create_log_dictionary_from_activity_transactions (see above).

        Argument:
            log_dic (dictionary): A dictionary as it is created by
                create_log_dictionary_from_activity_transactions.

        Returns:
            A dictionary that describes a log where the activites are sorted by time.
    '''
    for process_instance, process_instance_activities in log_dic.items():
        log_dic[process_instance] = sorted(
            process_instance_activities, key=lambda k: k["instance_id_time_stamp"])
    return log_dic


def create_xes_log_from_log_dic(log_dic, process_name="Incident Management Process"):
    '''
        create_xes_log_from_log_dic creates and returns a XES log of type <class 'opyenxes.model.XLog.XLog'> from log_dic.

        Arguments:
            log_dic (dictionary): A dictionary
                (as it is created by create_log_dictionary_from_activity_transactions) that contains the log.
            process_name (string): The name of the process.

        Returns:
            A log object of type <class 'opyenxes.model.XLog.XLog'>.
    '''
    concept_name = XConceptExtension()
    time_extension = XTimeExtension()
    organizational_extension = XOrganizationalExtension()
    lifecycle_extension = XLifecycleExtension()
    cost_extension = XCostExtension()
    identitity_extension = XIdentityExtension()
    XExtensionManager().register_standard_extensions()

    log_xes = XFactory.create_log()
    log_xes.get_extensions().add(concept_name)
    log_xes.get_extensions().add(time_extension)
    log_xes.get_extensions().add(organizational_extension)
    log_xes.get_extensions().add(lifecycle_extension)
    log_xes.get_extensions().add(cost_extension)
    log_xes.get_extensions().add(identitity_extension)

    concept_name.assign_name(element=log_xes, name=process_name)
    lifecycle_extension.assign_model(log=log_xes, model="standard")


    for trace_id, _activities in log_dic.items():
        trace = XFactory.create_trace()
        concept_name.assign_name(element=trace, name=trace_id)

        # Not possible because it has to be an UUID
        # identitity_extension.assign_id(element=trace, identity=trace_id)
        _id = XFactory.create_attribute_literal("id", trace_id)
        trace.get_attributes()["id"] = _id

        for activity in _activities:
            event = XFactory.create_event()

            # Activity Instance ID, i.e. the transaction hash
            ## Not possible because it has to be an UUID
            # identitity_extension.assign_id(element=event, identity=activity["instance_id"])
            activity_insance_id = XFactory.create_attribute_literal("id", activity["instance_id"])
            event.get_attributes()["id"] = activity_insance_id

            # Activity ID, i.e. the first 4 bytes of the input data.
            activity_id = XFactory.create_attribute_literal("activity_id", activity["id"])
            event.get_attributes()["activity_id"] = activity_id

            # Activity name
            activity_name = activity["name"]
            concept_name.assign_name(element=event, name=activity_name)

            # Time stampe
            time_extension.assign_timestamp(event=event, date=activity["instance_id_time_stamp"])

            # Organisation attribute
            organizational_extension.assign_resource(event=event, instance=activity["name_resource"])

            # State of the activity
            lifecycle_extension.assign_transition(event=event, transition="complete")


            # Block number
            activity_instance_id_block_no = XFactory.create_attribute_discrete("blockNo", activity["instance_id_block_no"])
            event.get_attributes()["blockNo"] = activity_instance_id_block_no

            # From address
            activity_instance_id_from = XFactory.create_attribute_literal("from", activity["instance_id_from"])
            event.get_attributes()["from"] = activity_instance_id_from

            # Transaction data
            activity_instance_id_transaction_data = XFactory.create_attribute_literal("transactionData", activity["instance_id_transaction_data"])
            event.get_attributes()["transactionData"] =  activity_instance_id_transaction_data


            trace.append(event)

        log_xes.append(trace)

    return log_xes


def write_xes_log_to_disc(log_xes, path='./', file_name='automatic_incident_management'):
    '''
        write_xes_log_to_disc writes the xes_log dictionary to a file in XES format.

        Arguments:
            log_xes (XESLog): A xes log as returned by create_xes_log_from_log_dic.
            path (string): The path to the storing location.
            file_name (string): The file name of thex .xes file.
    '''
    with open(f'{path}{file_name}.xes', "w") as file:
        XesXmlSerializer().serialize(log_xes, file)


def load_activity_transactions_from_pickle(path='activity_transactions.pickle'):
    '''
        load_activity_transactions_from_pickle loads the list activity_transactions from the pickle file specified in path.

        Argument:
            path (string): The path to the directory of the pickle file to be loaded.

        Returns:
            A list of activity_transactions.
    '''
    with open(file=path, mode='rb') as handle:
        activity_transactions = pickle.load(handle)
    return activity_transactions
