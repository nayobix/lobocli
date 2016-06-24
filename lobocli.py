#!/usr/bin/env python2.7

__author__ = "Boyan Vladinov"
__copyright__ = "Copyright 2016"
__license__ = "GPL"

import sys
import os
import os.path
import argparse
import logging
import serial
import time

import luacommands as luacmd

_log = logging.getLogger('lobocli.py')
logging.basicConfig()

def parseOptions(args = None):
    parser = argparse.ArgumentParser(description = '''
Lobo CLI''', epilog = '''
    Command line tool for emw3165 operations - file read/write/ver and so on
    Implemented for MICO Lobo wifimcu modification

    Usage: lobocli.py [--option] command

    ''',
    formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('command', nargs='*', default = ['none'],
    help = '''
    Commands: [default: none]:
       ver
       info
       mem
       reboot
    ''')

    parser.add_argument('--serial', default = '/dev/ttyUSB0',
    help = '''Serial port. Default: /dev/ttyUSB0''')

    parser.add_argument('--baud', default = '115200',
    help = '''Baud rate. Default: 115200''')

    parser.add_argument('--uploadfile', default = None,
    help = '''File upload.''')

    parser.add_argument('--readfile', default = None,
    help = '''File read.''')

    parser.add_argument('-d', '--debug', action = 'store_true', default = False,
    help = 'Debug mode')

    return parser.parse_args(args)


def checkPython():
    if sys.version_info[:2] == (2,7):
        pass
    else:
        print 'Python version 2.7.x needed!'
        exit(1)

def printAndExit(message):
    print ''
    print '[Lobo CLI]: %s' % message
    print ''
    exit(1)

def myprint(message):
    print ''
    print '[Lobo CLI]: %s' % message
    print ''

def replaceString(string):
    newstr = string
    newstr = newstr.replace("/", r'\/')
    newstr = newstr.replace("'", r"\'")
    newstr = newstr.replace("\"", r"\"")
    newstr = newstr.strip();

    return newstr

def openSerial(args = None):
    try:
        ser = serial.Serial(
    	    port = args.serial,
	    baudrate = args.baud
            )
        if ser == None and not ser.isOpen() == True:
            printAndExit("Serial port %s opened already" % args.serial)

        ser.flushInput()
        ser.flushOutput()
    except Exception, e:
        printAndExit("Serial port open %s exception: %s" % (args.serial, str(e)))

    _log.debug("Serial port %s opened" % args.serial)

    return ser

def closeSerial(ser):

    if not ser == None and ser.isOpen() == True:
        try:
            ser.close()
            _log.debug("Serial port %s closed" % ser.port)
        except Exception, e:
            printAndExit("Serial port close %s exception: %s" % (ser.port, str(e)))

def readSerial(ser):
    out = ''
    data = ''

    while ser.inWaiting() > 0 or not '/>' in out:
        out += ser.read(1).decode("utf-8")

    #Remove all command lines, and get just the answer
    for line in out.splitlines():
        if not '/>' in line and not '>>' in line:
            data += line
            data += "\n"

    return data

def uploadSerial(ser, src, dst):
    cmd = luacmd.FILE_ARG["write_open"] % (dst)
    execCommand(ser, cmd, True)

    fh = open(src, "r")
    fileCount = 0
    for line in fh.readlines():
        newline = replaceString(line)
        _log.debug("uploadSerial line: %s" % newline)
        cmd = luacmd.FILE_ARG["write_data"] % (newline)
        execCommand(ser, cmd, True)

    cmd = luacmd.FILE_ARG["write_close"]
    execCommand(ser, cmd, True)

def execCommand(ser, command, justWrite):

    bytearr = bytearray(command.encode('utf-8'))
    ser.write(bytearr)

    #Give some time content to be written to the console
    time.sleep(0.1)

    if justWrite == True:
        return

    #let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)

    data = readSerial(ser)

    if data != '':
        print ">> " + data

def execCommands(ser, args):

    #All commands without arguments
    for cmd in args.command:
        execCmd = None

        if "none" == cmd:
            continue
        elif luacmd.MCU.has_key(cmd) == True:
            execCmd = luacmd.MCU[cmd]
        elif luacmd.FILE.has_key(cmd) == True:
            execCmd = luacmd.FILE[cmd]

        if execCmd:
            myprint("Executing: %s" % cmd)
            execCommand(ser, execCmd, False)
        elif execCmd != "none":
            myprint("Undefined command: %s" % cmd)

    #All commands with arguments
    if args.readfile:
        readFile = args.readfile
	command = luacmd.FILE_ARG["read"] % (readFile, readFile)
	for execCmd in command.splitlines():
            _log.debug("Executing: %s" % execCmd)
            execCommand(ser, execCmd+"\n", True)
        execCommand(ser, "", False)

    if args.uploadfile:
        srcFile = args.uploadfile
        dstFile = srcFile
        if dstFile == None:
            dstFile = srcFile
        uploadSerial(ser, srcFile, dstFile)
        _log.debug("Executing: %s" % execCmd)
        myprint("Upload complete!")

if __name__ == '__main__':

    #Check and parse
    checkPython()
    opts = parseOptions()

    if opts.debug:
	    logging.getLogger('lobocli.py').setLevel(logging.DEBUG)

    _log.debug('Opts: %s' % str(opts))

    ser = openSerial(opts)

    execCommands(ser, opts)

    closeSerial(ser)

    exit(0)
