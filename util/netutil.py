# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" General network utilities """

import logging
import os
import paramiko
import select
import socket
import stat
import time


def ssh_connect_or_return(ipaddr, user, passwd, maxretries, remote_port=22):
    """Opens a connection and returns a connection object. If it fails to open
    a connection after a specified number of tries, it returns -1.

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param maxretries: maximum number of times to connect
    :param remote_port: port for ssh connection
    :returns: an ssh connection handle or -1 on failure
    :rtype: paramiko.SSHClient (or -1 when failure)
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type maxretries: int
    :type remote_port: int
    """

    retries = 1

    while retries <= maxretries:
        logging.info(
            '[netutil] Trying to connect to {0}:{1} ({2}/{3})'.
            format(ipaddr, remote_port, retries, maxretries))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ipaddr, port=remote_port,
                        username=user, password=passwd)
            logging.info('[netutil] Connected to {0} '.format(ipaddr))
            return ssh
        except paramiko.AuthenticationException:
            logging.error(
                '[netutil] Authentication failed when connecting to {0}'.
                format(ipaddr))

        except:
            logging.error(
                '[netutil] Could not SSH to {0}, waiting for it to start'.
                format(ipaddr))

        retries += 1
        time.sleep(2)
    # If we exit while without ssh object been returned, then return -1
    logging.info('[netutil] Could not connect to {0}. Returning'
                 .format(ipaddr))
    return None

def ssh_connection_open(ipaddr, user, passwd, remote_port=22):
    """
    :param ipaddr:
    :param user:
    :param passwd
    :param remote_port:
    :returns sftp
    :returns transport_layer
    :rtype
    :rtype
    :type ipaddr:
    :type user:
    :type passwd:
    :type remote_port:
    """
    transport_layer = paramiko.Transport((ipaddr, remote_port))
    transport_layer.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport_layer)

    return (sftp, transport_layer)

def ssh_connection_close(sftp, transport_layer):
    """ Closes an ssh connection"""
    try:
        sftp.close()
        transport_layer.close()
    except:
        pass


def ssh_copy_file_to_target(ipaddr, user, passwd, local_file, remote_file,
                            remote_port=22):

    """Copies local file on a remote machine target.

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param local_file: file from local machine to copy,full location required
    :param remote_file: remote destination, full location required
    i.e /tmp/foo.txt
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type local_file: str
    :type remote_file: str
    :type remote_port: int
    """
    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)
    sftp.put(local_file, remote_file)
    ssh_connection_close(sftp, transport_layer)
    #sftp.close()
    #transport_layer.close()


def copy_directory_to_target(ipaddr, user, passwd, local_path, remote_path,
                             remote_port=22):
    """Copy a local directory on a remote machine.

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param local_path: directory path from local machine to copy, full location
    required
    :param remote_path: remote destination, full location required
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type local_path: str
    :type remote_path: str
    :type remote_port: int
    """

    #  recursively upload a full directory
    if local_path.endswith('/'):
        local_path = local_path[:-1]

    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)
    os.chdir(os.path.split(local_path)[0])
    parent = os.path.split(local_path)[1]

    for walker in os.walk(parent):
        try:
            folder_to_make = os.path.join(remote_path, walker[0])
            sftp.mkdir(folder_to_make)
        except:
            pass
        for curr_file in walker[2]:
            local_file = os.path.join(walker[0], curr_file)
            remote_file = os.path.join(remote_path, walker[0], curr_file)
            sftp.put(local_file, remote_file)
    #sftp.close()
    #transport_layer.close()
    ssh_connection_close(sftp, transport_layer)


def make_remote_file_executable(ipaddr, user, passwd, remote_file,
                                remote_port=22):
    """Makes the remote file executable.

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_file: remote file to make executable
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_file: str
    :type remote_port: int
    """

    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)

    sftp.chmod(remote_file, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    ssh_connection_close(sftp, transport_layer)
    #sftp.close()
    #transport_layer.close()

def create_remote_directory(ipaddr, user, passwd, remote_path, remote_port=22):
    """Opens an ssh connection to a remote machine and creates a new directory.

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_path: maximum number of times to connect
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_path: str
    :type remote_port: int
    """

    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)
    try:
        # Test if remote_path exists
        sftp.chdir(remote_path)
    except IOError:
        # Create remote_path
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)
    ssh_connection_close(sftp, transport_layer)
    #sftp.close()
    #transport_layer.close()


def isdir(path, sftp):
    """Checks if a given remote path is a directory

    :param path: A string with the full path we want to check
    :param sftp: An sftp connection object (paramiko)
    :returns: True if the given path is a directory false otherwise.
    :rtype: bool
    :type path: str
    :type sftp: paramiko.SFTPClient
    """

    try:
        return stat.S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False


def remove_remote_directory(ipaddr, user, passwd, path, remote_port=22):
    """Removes recursively remote directories (removes all files and
    other sub-directories).

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param path: A string with the full path we want to remove
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type path: str
    :type remote_port: int
    """
    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)

    files = sftp.listdir(path=path)

    for file_item in files:
        filepath = os.path.join(path, file_item)
        if isdir(filepath, sftp):
            remove_remote_directory(ipaddr, user, passwd, filepath,
                                    remote_port)
        else:
            sftp.remove(filepath)

    sftp.rmdir(path)
    ssh_connection_close(sftp, transport_layer)
    #sftp.close()
    #transport_layer.close()


def ssh_run_command(ssh_client, command_to_run, prefix='', lines_queue=None,
                    print_flag=True, block_flag=True):
    """Runs the specified command on a remote machine

    :param ssh_client : SSH client provided by paramiko to run the command
    :param command_to_run: Command to execute
    :param prefix: prefix of log message
    :param lines_queue: Queue datastructure to buffer the result of execution
    :param print_flag: Flag that defines if the output of the command will be
    printed on screen
    :param block_flag: Defines if we block execution waiting for the running
    command to return its exit status
    :returns: the exit code of the command to be executed remotely and the
    combined stdout - stderr of the executed command
    :rtype: tuple<int, str>
    :type ssh_client: paramiko.SSHClient
    :type command_to_run: str
    :type prefix: str
    :type lines_queue: queue<str>
    :type print_flag: bool
    :type block_flag: bool
    """

    channel = ssh_client.get_transport().open_session()
    bufferSize = 4*1024
    channel_timeout = 300
    channel.setblocking(1)
    channel.set_combine_stderr(True)
    channel.settimeout(channel_timeout)
    channel.exec_command(command_to_run)
    if not block_flag:
        return 0
    channel_output = ''
    while not channel.exit_status_ready():
        data = ''
        data = channel.recv(bufferSize).decode('utf-8')
        while data is not '':
            channel_output += data
            if print_flag:
                logging.debug('{0} {1}'.format(prefix, data).strip())
            if lines_queue is not None:
                for line in data.splitlines():
                    lines_queue.put(line)
            data = channel.recv(bufferSize).decode('utf-8')

    channel_exit_status = channel.recv_exit_status()
    channel.close()
    return (channel_exit_status, channel_output)


def ssh_delete_file_if_exists(ipaddr, user, passwd, remote_file,
                              remote_port=22):
    """Deletes the file on e remote machine, if it exists

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_file: remote file to remove, full path must be used.
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_file: str
    :type remote_port: int
    """
    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)

    try:
        sftp.remove(remote_file)
        logging.info('[netutil] [delete_file_if_exists]: file {0} removed'.
                     format(remote_file))
    except IOError:
        logging.error(
            '[netutil] [delete_file_if_exists] IOError: The given remote_file '
            'is not valid. Error message: {0}'.format(IOError.strerror))
    except:
        logging.error(
            '[netutil] [delete_file_if_exists] Error: Unknown Error occured '
            'while was trying to remove remote file.')

    transport_layer.close()
    logging.error(
        '[netutil] [ssh_delete_file_if_exists]: transport layer closed')


def copy_remote_directory(ipaddr, user, passwd, remote_path, local_path,
                          remote_port=22):
    """Copy recursively remote directories (Copies all files and
    other sub-directories).

    :param ipaddr: IP address of the remote machine
    :param user: username of the remote user
    :param passwd: password of the remote user
    :param remote_path: A string with the full remote path we want to copy
    :param local_path: A string with the full local path we want to copy
    :param remote_port: port to perform sftp from
    :type ipaddr: str
    :type user: str
    :type passwd: str
    :type remote_path: str
    :type local_path: str
    :type remote_port: int
    """
    (sftp, transport_layer) = ssh_connection_open(ipaddr, user, passwd,
                                                  remote_port=22)

    #transport_layer = paramiko.Transport((ipaddr, remote_port))
    #transport_layer.connect(username=user, password=passwd)
    #sftp = paramiko.SFTPClient.from_transport(transport_layer)

    files = sftp.listdir(path=remote_path)

    for file_item in files:
        remote_filepath = os.path.join(remote_path, file_item)
        if isdir(remote_filepath, sftp):
            if not os.path.exists(os.path.join(local_path, file_item)):
                os.makedirs(os.path.join(local_path, file_item))
            copy_remote_directory(ipaddr, user, passwd, remote_filepath,
                                  os.path.join(local_path, file_item),
                                  remote_port)
        else:
            sftp.get(remote_filepath, os.path.join(local_path, file_item))
    ssh_connection_close(sftp, transport_layer)
    #sftp.close()
    #transport_layer.close()

