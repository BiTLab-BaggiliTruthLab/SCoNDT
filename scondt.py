# Software-Defined Networking Controller Network Discovery Tool (SCoNDT)
# Script to extract data from the memory dump of a SDN controller and generate potential network topologies
# Authors: Christian Facundus, Adam Kardorff


import sys
import subprocess as sp
from datetime import datetime
import pandas as pd
from timeit import default_timer


class Host:
    """A host object"""
    id = int
    ip = str
    macAddress = str
    firstSeen = int
    lastSeen = int

class User:
    """A user object"""
    username = str
    hashedPassword = str

def generate_report(df, df2, fileName): 
    """Generates an HTML report from the information gathered"""
    
    if fileName is not "":
        if fileName[-5:] != ".html":
            fileName = fileName + ".html"
    else:
            fileName = "Result.html"

    hfile = open(fileName, "w")
    df.drop_duplicates(subset=None, keep="first", inplace=True)
    df = df.sort_values(by=['ID'])
    html = df.to_html(index=False)
    hfile.write(html)

    hfile.write("\n<br>\n<br>\n")
    df2.drop_duplicates(subset=None, keep="first", inplace=True)
    html2 = df2.to_html(index=False)
    hfile.write(html2)
    hfile.close()
    return fileName


def get_strings(file_path):
    """Returns matched data (grep) from strings on file"""
    strings = sp.Popen(['strings', file_path], stdout=sp.PIPE)
    grep = sp.Popen(['grep', '{\"hashedPassword\":\|\"host-tracker-service:addresses\":'], stdin=strings.stdout, stdout=sp.PIPE)
    strings.stdout.close()
    strings.stdout.close()
    search = grep.communicate()[0]
    return search


def parse_host_string(string):
    """Parses a string for host data and returns a filled host object"""
    # "id":6,"mac":"00:00:00:00:00:07","last-seen":1667335188392,"ip":"10.1.1.7","first-seen":1667335188392
    # ^ string to parse; 5 elements separated by ,
    host = Host
    split = string.split(',')

    for i in split:
        if i[:4] == "\"id\"":
            id = i[5:]
            host.id = int(id)
        elif i[:5] == "\"mac\"":
            host.macAddress = i[7:-1]
        elif i[:11] == "\"last-seen\"":
            host.lastSeen = i[12:]
        elif i[:4] == "\"ip\"":
            host.ip = i[6:-1]
        elif i[:12] == "\"first-seen\"":
            host.firstSeen = i[13:]
    return host

def flush_host_data(host):
    """Flushes data of a host object"""
    temp = Host
    temp.id = -1
    temp.ip = ""
    temp.macAddress = ""
    temp.firstSeen = 0
    temp.lastSeen = 0


def parse_user_string(string):
    """Parses a string for username and hashed password data and returns a filled user object"""
    # "userName":"root","uid":0,"gid":0,"homeDirectory":"/root","shell":"/bin/bash","privileged":{"hashedPassword":["$6$3M0TY4hV0GQT..k4$j3YoGWswueW4FAW6LB6ZydlAlnOdFOhy3EeHjHpB7US1CGOll4oFWwFEpqcQ10ZXucjHYzy3Nmfj2JPhw5bwB0"]},"passwordChangeNow":false,"lastPasswordChangeUSec":1645488000000000,"passwordChangeMaxUSec":8639913600000000,"passwordChangeWarnUSec":604800000000}
    # ^ string to parse, 10 elements separated by ,
    user = User
    split = string.split(',')
    for i in split:
        if i[:10] == "\"userName\"":
            user.username = i[12:-1]
        if i[:29] == "\"privileged\":\"hashedPassword\"":
            user.hashedPassword = i[33:-1]
    return user

def flush_user_data(user):
    """Flushes data of a user object"""
    temp = User
    temp.user = ""
    temp.hashedPassword = ""

def cleanTimeStamp(timeStamp):
    """Takes an integer and converts it to a timestamp"""
    try: 
        return datetime.fromtimestamp(int(timeStamp)/1000.0)
    except:
        return "Timestamp Not Available"

def helpPage():
    print("")
    print('='*100)
    print("")
    #PUT HELP PAGE MESSAGE HERE

    print("Thank you for using SCoNDT!")
    print("In order to use SCoNDT, please enter the file path to a memory sample as the first argument, and the file name for your report as the second argument")
    
    print("")
    print('='*100)


if __name__ == "__main__":
    full_runtime_start = default_timer()
    if sys.argv[1] == "-h":
        helpPage()
        sys.exit(0)
    try:
        file_path = sys.argv[1]
    except:
        print("No file path given\n--------------------")
    else:
        file_path = sys.argv[1]
        print("Reading from: " + file_path)

    try:
        name = sys.argv[2]
    except:
        name = "Result"

    get_strings_timer_start = default_timer()
    search = get_strings(file_path)
    get_strings_timer_end = default_timer() - get_strings_timer_start
    index = 0
    fulls = ""
    host = Host
    user = User
    df = pd.DataFrame(columns=['ID', 'IP', 'Mac Address', 'First Seen', 'Last Seen'])
    userDF = pd.DataFrame(columns = ['Username', 'HashedPassword'])
    # print("\nhosts:\n" + search)


    splitHosts = search.split("\"host-tracker-service:addresses\":")
    parse_hosts_timer_start = default_timer()
    for j in splitHosts:
        # print("j:\n" + j)
        j = j.replace('[','')
        j = j.replace('{','')
        j = j.replace('}','')
        select = j.split(']')
        for i in select:
            hostString = i
            # print(hostString)
            if hostString[0:4] == "\"id\"":
                host = flush_host_data(host)
                host = parse_host_string(hostString)
                firstSeen = cleanTimeStamp(host.firstSeen)
                lastSeen = cleanTimeStamp(host.lastSeen)
                hostData = [host.id, host.ip, host.macAddress, firstSeen, lastSeen]
                df.loc[len(df)] = hostData
    parse_hosts_timer_end = default_timer() - parse_hosts_timer_start

    splitUsers = search.split("\n")
    parse_users_timer_start = default_timer()
    for userString in splitUsers:
        if userString[:11] == "{\"userName\"":
            userString = userString.replace('{','')
            userString = userString.replace('}','')
            userString = userString.replace('[','')
            userString = userString.replace(']','')
            user = flush_user_data(user)
            user = parse_user_string(userString)
            userData = [user.username, user.hashedPassword]
            userDF.loc[len(userDF)] = userData
    parse_users_timer_end = default_timer() - parse_users_timer_start

    generate_report_timer_start = default_timer()
    fileName = generate_report(df, userDF, name)
    generate_report_timer_end = default_timer() - generate_report_timer_start
    full_runtime_end = default_timer() - full_runtime_start
    print("SCoNDT total runtime: %.4f" % full_runtime_end + " s")
    print("Time get strings: %.4f" % get_strings_timer_end + " s")
    print("Time to parse hosts: %.4f" % parse_hosts_timer_end + " s")
    print("Time to parse users: %.4f" %parse_users_timer_end + " s")
    print("Time to generate report: %.4f" %generate_report_timer_end + " s")
    print("Report Generated in " + fileName)