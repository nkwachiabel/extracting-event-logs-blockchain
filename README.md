# Extracting Event Logs for Process Mining from Data Stored on the Blockchain

This GitLab repository contains the software implementation of the approach explained in
Roman Mühlberger, Stefan Bachhofner, Claudio Di Ciccio, Luciano García-Bañuelos and Orlenys López-Pintado: Extracting Event Logs for Process Mining from Data Stored on the Blockchain.
Accepted for presentation at the Second Workshop on Security and Privacy-enhanced Business Process Management (SPBP’19), September 2nd, 2019, Vienna, Austria.
To appear in the Proc. of BPM Workshops 2019.

## BibTeX Entry
Please cite this research if you use it in any form with the following BibTeX key.
By doing so, you not only support the research but also the effort of making this repository public.
```
@InProceedings{Muehlberger.etal/SPBP2019:ExtractingEventLogsfromBlockchain,
    author    = {M{\"u}hlberger, Roman and Bachhofner, Stefan and Di Ciccio, Claudio and Garc{\’i}a-Ba{\~n}uelos, Luciano and L{\’o}pez-Pintado, Orlenys},
    title     = {Extracting Event Logs for Process Mining from Data Stored on the Blockchain},
    booktitle = {Business Process Management Workshops - {BPM} 2019 International Workshops, Vienna, Austria, September 2, 2019},
    year      = {2019},
    editor    = {Dijkman, Remco and Di Francescomarino, Chiara, and Zdun, Uwe},
    series    = {Lecture Notes in Business Information Processing},
    publisher = {Springer},
    year      = {2019},
    keywords  = {Ethereum; Process Discovery; Process Monitoring; Process Conformance}
}
```

# About the Software

## How you can use this software

First, make sure that you have the following two python packages installed.
- [web3](https://web3py.readthedocs.io/en/stable/quickstart.html)
- [opyenxes](https://opyenxes.readthedocs.io/en/latest/installation.html)

Second, set the Application Programming Interface (API) Key in your environemnt. In this research, we connected to a node in the public Ethereum network provided by Infura. In oder to obtain an Infura API Key, please go to https://www.infura.io to create an API key. 
```sh
export INFURA_API_KEY="YOUR_API_KEY"
```
[Infura](https://infura.io/) is a company that offers access to the Ethereum blockchain via their API. In short, the company runs their own modified Ethereum blockchain node which allows them to collect data. You have to create an account at Infura if you want to use their services. After you have created an account you have to create an API Key. Please see [their documentation](https://infura.io/docs/gettingStarted/makeRequests.md) for furhter details.


Then, you either clone this repository or download it as a zip. Once you have the repository in a directory, you have to copy the folder extracting_event_logs_blockchain in your project
direcotry. Finally, you insert the following two code lines at the top of your script
```py
from __future__ import absolute_import

from extracting_event_logs_blockchain import utils
```

Now, you use the provided functions.
```py
# activity_names, function_signatures, and activity_resources are defined somewhere above.

activities_dictionary = utils.create_activities_dictionary(
    activity_names=activity_names,
    function_signatures=function_signatures,
    activity_resources=activity_resources
)

http_provider = utils.connect_to_http_provider()

....
```

## Getting help
You can either open the ```*.py``` you are interested in and have a look at the code and the documentation, or you use pythons ```help()``` function to see the docstring.

```py
from extracting_event_logs_blockchain import utils

help(utils.get_activity_transactions_from_block_number)
```

## Explanation of Files and Directories
[**extracting_event_logs_blockchain**](https://gitlab.com/MacOS/extracting-event-logs-from-process-data-on-the-blockchain/blob/paper/extracting_event_logs_blockchain/utils.py)

The software that was written to scrape the blockchain. See below for instructions on how you can use the software.

[**incident_management_process.ipynb**](https://gitlab.com/MacOS/extracting-event-logs-from-process-data-on-the-blockchain/blob/paper/incident_management_process.ipynb)

The use case that was presented in the paper.

[**incident_management_process.xes**](https://gitlab.com/MacOS/extracting-event-logs-from-process-data-on-the-blockchain/blob/paper/incident_management_process.xes)

The log file in eXtensible Event Stream (XES) that is producted by the software for the presented use case.

[**figures**](https://gitlab.com/MacOS/extracting-event-logs-from-process-data-on-the-blockchain/tree/paper/figures)

The figures that are used in the jupyter notebook.

[**activity_transactions.pickle**](https://gitlab.com/MacOS/extracting-event-logs-from-process-data-on-the-blockchain/blob/paper/activity_transactions.pickle)

The activity transactions of the scrapped process as a Python list. In the jupyter notebook, you can choose if you want to load this file or retrieve the data
from an Ethereum node.


# Paper

## Resources
Paper (preprint): [https://easychair.org/publications/preprint/cW8l](https://easychair.org/publications/preprint/cW8l)

Presentation slides: [https://easychair.org/smart-slide/slide/zBS5](https://easychair.org/smart-slide/slide/zBS5)

## Abstract
The integration of business process management with blockchains across
organisational borders provides a means to establish transparency of execution and
auditing capabilities. To enable process analytics, though, non-trivial extraction and
transformation tasks are necessary on the raw data stored in the ledger. In this paper,
we describe our approach to retrieve process data from an Ethereum blockchain ledger
and subsequently convert those data into an event log formatted according to the IEEE
Extensible Event Stream (XES) standard. We show a proof-of-concept software artefact
and its application on a data set produced by the smart contracts of a process execution
engine stored on the public Ethereum blockchain network.

## Authors
[Roman Mühlberger](https://www.xing.com/profile/Roman_Muehlberger)

[Stefan Bachhofner](https://scholar.google.com/citations?hl=de&user=-WZ0YuUAAAAJ)

[Claudio Di Ciccio](https://scholar.google.at/citations?user=OBwQoWsAAAAJ&hl=en&oi=ao)

[Luciano García-Bañuelos](https://scholar.google.com/citations?user=ly9UiYMAAAAJ&hl=de)

[Orlenys López-Pintado](https://scholar.google.com/citations?user=nP1fb3sAAAAJ&hl=en)
