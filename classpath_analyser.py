#!/usr/bin/env python
# Version: $Id: classpath_analyser.py 489 2010-05-14 13:40:30Z dsaran $
"""
This script searches for duplicated classes inside jar files on the given directory.
   usage: classpath_analyser.py [directory]
   if no [directory] is given it searches for jars on the current directory (recursively)
"""
import sys
try:
    from path import path as Path
except ImportError:
    print "[ERROR] This script needs the Jason Orendorff's path module to work"
    print "Download it from http://www.jorendorff.com/articles/python/path"
    sys.exit(1)

def get_jar_content(jar):
    from zipfile import ZipFile
    import re
    matcher = re.compile('(?P<classname>.*)\.class')
    zip = ZipFile(jar)
    files = zip.namelist()
    classes = []
    for file in files:
        m = matcher.match(file)
        if m:
            classname = m.groupdict()['classname'].replace('/', '.')
            classes.append(classname)
    return classes

directory = '.'
if len(sys.argv) == 2:
    directory = sys.argv[1]

libdir = Path(directory)
print " * Looking for duplicated classes at " + directory

jars = [jar for jar in libdir.walk("*.jar")]

classes = {}
for jar in jars:
    class_list = get_jar_content(jar)

    for classname in class_list:
        if not classes.has_key(classname):
            classes[classname] = []
        classes[classname].append(jar.basename())

duplicated_jars = {}
duplicated_classes = []
for cl in sorted(classes):
    found_in = len(classes[cl])
    if found_in > 1:
        message = "%d occurrences of class %s:" % (found_in, cl)
        message = message.ljust(80) + repr(classes[cl])
        duplicated_classes.append(message)
        for jar in classes[cl]:
            duplicated_jars[jar] = classes[cl]


print "------- JARs com classes repetidas -------\n"
for jar in duplicated_jars:
    print "- " + jar
    for j in duplicated_jars[jar]:
        if j != jar:
            print "   - " + j

print "\n------- Todas as classes repetidas -------\n"
print '\n'.join(duplicated_classes)

