import os
import re
import sys


def getfiles(folder):
    files = {}
    for path, _, filenames in os.walk(folder):
        for filename in filenames:
            with open(os.path.join(path, filename)) as file:
                files[
                    os.path.relpath(os.path.join(path, filename), start=folder)
                    ] = set(re.findall(r'require ‘(.+)’', file.read()))
    return files


def sortfiles(files):
    def tarjan(graph, whitelist, graylist, blacklist, vertex, trace):
        if vertex in blacklist:
            return
        if vertex in graylist:
            cycle = trace[trace.index(vertex):]
            cycle.append(vertex)
            sys.exit(f"Cyclic dependency found: {' - '.join(cycle)}")
        if vertex in whitelist:
            whitelist.remove(vertex)
            trace.append(vertex)
            graylist.append(vertex)
            for next in graph[vertex]:
                tarjan(graph, whitelist, graylist, blacklist, next, trace)
            graylist.remove(vertex)
            blacklist.append(vertex)

    whitelist = [x for x in files.keys()]
    graylist = []
    blacklist = []
    trace = []
    while whitelist:
        tarjan(files, whitelist, graylist, blacklist, whitelist[0], trace)
    return blacklist


def concat(folder, filelist):
    with open(os.path.join(folder, 'concat.txt'), 'w') as output:
        for file in filelist:
            with open(os.path.join(folder, file)) as input:
                output.write(input.read())


if __name__ == "__main__":

    rootfolder = os.getcwd()
    if len(sys.argv) > 2:
        sys.exit("Too many arguments, not more than one was expected")
    elif len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            rootfolder = os.path.abspath(sys.argv[1])
        else:
            sys.exit("Argument is expected to be folder")

    concat(rootfolder, sortfiles(getfiles(rootfolder)))
