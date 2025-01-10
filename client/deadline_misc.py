# -*- coding: utf-8 -*-
import re
from collections import  OrderedDict
import  pprint

def extractDeadLineOptions(optionPath):
    lines = ""
    with open(optionPath) as f:
        # print(type(f))
        lines = f.readlines()

    result = OrderedDict()
    # result = {}

    nowParsing = False
    currentKey=""

    for line in lines:
        # lineTmp = line.split()
        lineTmp = line.replace("\n","")
        if lineTmp:
            # line = lineTmp[0]
            line = lineTmp
        else:
            nowParsing = False
            continue

        if not nowParsing:
            m = re.match(r"\[.*\]",line)
            if m:
                m0 = re.search(r"[a-zA-Z]+",line)
                if m0:
                    key =  m0.group(0)
                    result[key] = {}
                    nowParsing = True
                    currentKey = key
        else:
            tmp = line.split("=")
            # print tmp
            result[currentKey][tmp[0]]  = tmp[1]

    requiredOptions = []
    for k,v in result.items():
        if v["Required"] == "true":
            requiredOptions.append(k)
        # print k

    # print requiredOptions

    return result , requiredOptions

if __name__ == '__main__':
    target = "Blender"
    # result,requiredOptions = extractDeadLineOptions("C:/DeadlineRepository10/plugins/" + target +  "/" + target + ".options")
    result,requiredOptions = extractDeadLineOptions("//192.168.20.22/DeadLine/DeadlineRepository10/plugins/" + target +  "/" + target + ".options")
    print 'required = ' + str(requiredOptions)
    pprint.pprint(dict(result))