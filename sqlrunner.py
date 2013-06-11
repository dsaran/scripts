#! /usr/bin/env python
"""
This module provides classes to allow user to connect and execute commands on an oracle database from python code.
Existing classes are:
  SqlPlus -> Allow interaction with database using installed sqlplus.

It also provides a way to execute commands from commandline calling the module directly.
Usage:  sqlplus.py <database> <command>

Example: sqlplus.py user/password@TNS 'drop table X;'

Note: This script uses sqlplus instead of the oracle driver as it is intended to run in 
a very restrict environment with very few resources available (i.e. python 2.3 and sqlplus) 

"""
import logging
import subprocess
import tempfile

LOG_FILENAME = '/tmp/sqlrunner.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

log = logging.getLogger('SqlRunner')

class SqlPlus:
    """
    Wrapper for Oracle SQL*Plus to allow user to interact with a database.
    Example:
    >>> sqlplus = SqlPlus()
    >>> sqlplus.begin_transaction(conn_string='user/password@database_host/database_sid')
    >>> sqlplus.execute("update my_table set name='new value' where id=1;")
    >>> sqlplus.commit()
    >>> finish_transaction()
    """

    #
    # Constant definitions
    #
    PROMPT = "SQL>"
    STARTED = "***STARTED***"
    FINISHED = "***FINISHED***"

    sqlplus = None
    conn_string = None
    connected = False

    def __init__(self, app_path=None, silent=False):
        """ Constructs SqlPlus with the given app_path.
            If no app_path is given, the sqlplus executable is expected to be found on PATH.
        """
        self._tempfd, self._tempfile = tempfile.mkstemp()
        self._current_position = 0
        self.output = []
        self.silent = silent
        self.sqlplus = app_path or 'sqlplus'
        self.wrap= True
        self.feedback = False
        self.heading = False
        self.pagesize = 0

    def begin_transaction(self, conn_string=None):
        """ Connects to database
            @param conn_string connection string with format <username>[/<password>][@<connect_identifier>
            valid connection strings are:
                user/pass@host/sid
                user/pass@tns
                user/pass@host (ORACLE_SID needs to be set)
                user/pass (if running on oracle host, ORACLE_SID needs to be set)
        """
        conn_string = conn_string or self.conn_string
        log.debug("Starting transaction with database: " + conn_string)

        if self.silent:
            pipe_output = subprocess.PIPE
            self.process = subprocess.Popen([self.sqlplus + ' /nolog'],# >/tmp/out.log'],
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=self._tempfd,
                                    close_fds=False)
            self.execute_internal("connect " + conn_string, offline=True)

        else:
            pipe_output = None
            self.process = subprocess.Popen([self.sqlplus, '-s', '-L',  conn_string],
                                    # This is necessary since there is a bug running on shell.
                                    # when running on shell the full command line is not send to /bin/sh between quotes
                                    # so the arguments of command line are understood as arguments do 'sh'
                                    shell=False,
                                    stdin=subprocess.PIPE,
                                    stdout=pipe_output,
                                    close_fds=False)


        log.debug("Process PID: " + str(self.process.pid))
        log.info("Transaction started...")
        log.debug("Temporary output file: " + self._tempfile)

        self.connected = True

        # Setup current sqlplus session
        not self.heading and self.execute_internal('set head off')
        self.execute_internal('set pages %d' % self.pagesize )
        not self.feedback and self.execute_internal('set feed off')
        self.wrap and self.execute_internal('set wrap on')
        self.execute_internal('set serverout on')

    def commit(self):
        """ Commit current transaction. """
        self.execute("commit")

    def rollback(self):
        """ Rollback current transaction. """
        self.execute("rollback")

    def execute(self, command):
        """ Executes a command on database.
            @param command the command to execute
        """
        self._validate_connection()

        command = command.strip()

        command = self._strip_semicolon(command)

        if self.silent:
            self.execute_internal("PROMPT %s" % self.STARTED)
            self.execute_internal("PROMPT")

        self.execute_internal(command)

        if self.silent:
            self.execute_internal("PROMPT %s" % self.FINISHED)
            self.execute_internal("PROMPT")

        self._store_output()

    def execute_internal(self, command, offline=False):
        if not offline:
            self._validate_connection()

        if not command.endswith('\n'):
            command = command + '\n'

        self._write_comand(command)

    def _write_comand(self, command):
        log.debug("Writing command '%s'" % repr(command))

        self.process.stdin.write(command)

        self.process.stdin.flush()


    def _store_output(self):
        log.debug("Storing output ...")

        tempfile = open(self._tempfile, 'r')

        log.debug("Current position: " + str(self._current_position))

        tempfile.seek(self._current_position)
        finished = False

        started = False
        while self.silent and not finished:
            lines = tempfile.readlines()
            self._current_position = tempfile.tell()
            for line in lines:
                line = line.strip()
                log.debug("Started: %s | Line: %s" %(str(started), line))
                log.debug("Condition: " +str(line.strip().endswith(self.STARTED)))
                if not started:
                    started = line.endswith(self.STARTED)
                    continue

                if line.endswith(self.FINISHED):
                    finished = True
                    break
                line = self._prepare_output(line)
                if line:
                    self.output.append(line)

        tempfile.close()

    def finish_transaction(self):
        """ Closes the connection with database"""
        self._validate_connection()

        self.execute_internal("exit;\n")

        stdin = self.process.stdin
        if stdin and not stdin.closed:
            stdin.close()
        stdout = self.process.stdout
        if stdout and not stdout.closed:
            stdout.close()

        self.exit_code = self.process.wait()

        self.connected = False

    def _validate_connection(self):
        if not self.connected:
            raise Exception("Not connected")

    def _strip_semicolon(self, command):
        while command.strip().endswith(';'):
            command = command.strip()[:-1]

        if not command.strip().endswith('/'):
            command = command + ";"

        return command

    def _prepare_output(self, line):
        line = line.replace(self.PROMPT, "").strip()
        line = line.replace('\x00','')
        return line.strip()

    def get_output(self):
        return '\n'.join(self.output)


import os
class Popen3:
   """
   This is a deadlock-safe version of popen that returns
   an object with errorlevel, out (a string) and err (a string).
   (capturestderr may not work under windows.)
   Example: print Popen3('grep spam','\n\nhere spam\n\n').out
   """
   def __init__(self,command,input=None,capturestderr=None):
       outfile=tempfile.mktemp()
       command="( %s ) > %s" % (command,outfile)
       if input:
           infile=tempfile.mktemp()
           open(infile,"w").write(input)
           command=command+" <"+infile
       if capturestderr:
           errfile=tempfile.mktemp()
           command=command+" 2>"+errfile
       self.errorlevel=os.system(command) >> 8
       self.out=open(outfile,"r").read()
       os.remove(outfile)
       if input:
           os.remove(infile)
       if capturestderr:
           self.err=open(errfile,"r").read()
           os.remove(errfile)


if __name__ == '__main__':
   import sys
   if len(sys.argv) != 3:
       print "usage: %s <connection_string> <command>" %sys.argv[0]
       sys.exit(1)

   bd = sys.argv[1]
   command = sys.argv[2]

   sqlplus = SqlPlus(silent=True) 
   sqlplus.begin_transaction(bd) 
   sqlplus.execute(command)
   sqlplus.finish_transaction()
   print sqlplus.get_output()

