# Memory Samples
To access the memory samples that you can try SCoNDT on mentioned in the paper, you can use this publicly accessible link:

[Download Memory Samples](https://lsumail2-my.sharepoint.com/:f:/g/personal/aalsh25_lsu_edu/EsJYUC6JbOtAk28MXr-DiZMBDOwKTfEunTJ0yzby3pLhhA?e=8JJZw0)


# SCoNDT: SDN Controller Network Discovery Tool

The SDN Controller Network Discovery Tool parses a memory dump of an OpenDaylight (ODL) SDN controller to acquire various information about the network. Specifically, it finds the ID, IP address, and Mac address given by the controller, as well as the time of initial connection and last connection of systems to the network. This tool relies on the Host Tracker service, a component of the L2 switch project. This project must be installed on the ODL controller in order for the network data to be present in memory.

SCoNDT requires Python 2.7.0 or later. To run the tool, use the following command:

python2 SCoNDT.py [inputFileName] [outputFileName]

The input file must be a memory dump of the OpenDaylight SDN controller system. If an outputFileName is not given, the default report will be named Result.html.

Additionally, the command:

python2 SCoNDT.py -h

