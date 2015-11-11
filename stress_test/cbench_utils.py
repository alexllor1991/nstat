# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Reusable functions for processes that are cbench related """

import logging
import subprocess
import util.customsubprocess
import util.netutil


def command_exec_wrapper(cmd_list, prefix='', ssh_client=None,
                         data_queue=None):
    """Executes a command either locally or remotely and returns the result

    :param cmd_list: the command to be executed given in a list format of
    command and its arguments
    :param prefix: The prefix to be used for logging of executed command output
    :param ssh_client : SSH client provided by paramiko to run the command
    :param data_queue: data queue where cbench output is posted line by line
    the cbench process will run.
    :returns: The commands exit status
    :rtype: int
    :type cmd_list: list<str>
    :type prefix: str
    :type ssh_client: paramiko.SSHClient
    :type data_queue: multiprocessing.Queue
    """

    if ssh_client == None:
        exit_status = util.customsubprocess.check_output_streaming(cmd_list,
                                                     prefix, data_queue)
    else:
        exit_status, cmd_output = util.netutil.ssh_run_command(ssh_client,
            ' '.join(cmd_list), prefix, data_queue)
    return exit_status


def rebuild_cbench(cbench_build_handler, ssh_client=None):
    """Rebuilds cbench.

    :param cbench_build_handler: filepath to the handler that builds cbench
    :param ssh_client : SSH client provided by paramiko to run the command
    :type cbench_build_handler: str
    :type ssh_client: paramiko.SSHClient
    """

    command_exec_wrapper([cbench_build_handler],
                         '[cbench_build_handler]', ssh_client)



def run_cbench(cbench_run_handler, controller_ip, controller_port, threads,
               sw_per_thread, switches, thr_delay_ms, traf_delay_ms,
               ms_per_test, internal_repeats, hosts, warmup, mode,
               data_queue=None, ssh_client=None):
    """Runs a cbench instance

    :param cbench_run_handler: cbench run handler
    :param controller_ip: controller IP for OpenFlow connection
    :param controller_port: controller port for OpenFlow connection
    :param threads: number of cbench threads
    :param sw_per_thread: number of switches per thread
    :param switches: number of total switches
    :param thr_delay_ms: delay between thread creation (in milliseconds)
    :param traf_delay_ms: delay between last thread creation and traffic
    transmission (in milliseconds)
    :param ms_per_test: test duration of a single cbench loop
    :param internal_repeats: number of cbench loops
    :param hosts: number of simulated hoss
    :param warmup: initial loops to be considered as 'warmup'
    :param mode: cbench mode
    :param data_queue: data queue where cbench output is posted line by line
    the cbench process will run.
    :param ssh_client : SSH client provided by paramiko to run the command
    :type cbench_run_handler: str
    :type controller_ip: str
    :type controller_port: int
    :type threads: int
    :type sw_per_thread: int
    :type switches: int
    :type thr_delay_ms: int
    :type traf_delay_ms: int
    :type ms_per_test: int
    :type internal_repeats: int
    :type hosts: int
    :type warmup: int
    :type mode: int
    :type data_queue: multiprocessing.Queue
    :type ssh_client: paramiko.SSHClient
    """

    cmd_list = [cbench_run_handler,
                controller_ip, str(controller_port), str(threads),
                str(sw_per_thread), str(switches), str(thr_delay_ms),
                str(traf_delay_ms), str(ms_per_test), str(internal_repeats),
                str(hosts), str(warmup), mode]
    command_exec_wrapper(cmd_list, '[cbench_run_handler]', ssh_client,
                         data_queue)

def cleanup_cbench(cbench_clean_handler, ssh_client=None):
    """Shuts down the Generator.

    :param cbench_clean_handler: cleanup handler filepath for cbench.
    :param ssh_client : SSH client provided by paramiko to run the command
    :type cbench_clean_handler: str
    :type ssh_client: paramiko.SSHClient
    """

    command_exec_wrapper([cbench_clean_handler],
                         '[cbench_clean_handler]', ssh_client)


def cbench_thread(cbench_run_handler, controller_ip,
                     controller_port, threads, sw_per_thread, switches,
                     thr_delay_ms, traf_delay_ms, ms_per_test, internal_repeats,
                     hosts, warmup, mode, cbench_node_ip, cbench_node_ssh_port,
                     cbench_node_username, cbench_node_password, succ_msg='',
                     fail_msg='', data_queue=None):

    """ Function executed by cbench thread.

    :param cbench_run_handler: cbench run handler
    :param controller_ip: controller IP
    :param controller_port: controller port
    :param threads: number of cbench threads
    :param sw_per_thread: number of switches per thread
    :param switches: number of total switches
    :param thr_delay_ms: delay between thread creation
    :param traf_delay_ms: delay between last thread creation and traffic
    transmission
    :param ms_per_test: test duration of a single cbench loop
    :param internal_repeats: number of cbench loops
    :param hosts: number of simulated hosts
    :param warmup: initial loops to be considered as 'warmup'
    :param mode: cbench mode
    :param data_queue: data queue where cbench output is posted line by line
    :parar succ_msg: message written to data queue when cbench_thread
    succeeds
    :parar fail_msg: message written to data queue when cbench_thread fails
    :param ssh_client : SSH client provided by paramiko to run the command
    :type cbench_run_handler: str
    :type controller_ip: str
    :type controller_port: int
    :type threads: int
    :type sw_per_thread: int
    :type switches: int
    :type thr_delay_ms: int
    :type traf_delay_ms: int
    :type ms_per_test: int
    :type internal_repeats: int
    :type hosts: int
    :type warmup: int
    :type mode: str
    :type data_queue: multiprocessing.Queue
    :type succ_msg: str
    :type fail_msg: str
    :type ssh_client: paramiko.SSHClient
    """

    logging.info('[cbench_thread] cbench thread started')

    try:
        # Opening connection with cbench_node_ip and returning
        # cbench_ssh_client to be utilized in the sequel
        cbench_ssh_client = \
            util.netutil.ssh_connect_or_return(cbench_node_ip.value.decode(),
                cbench_node_username.value.decode(),
                cbench_node_password.value.decode(), 10,
            int(cbench_node_ssh_port.value.decode()))

        run_cbench(cbench_run_handler.value.decode(),
                   controller_ip.value.decode(),
                   controller_port.value, threads.value,
                   sw_per_thread.value, switches.value, thr_delay_ms.value,
                   traf_delay_ms.value, ms_per_test.value,
                   internal_repeats.value, hosts.value, warmup.value,
                   mode.value.decode(), data_queue, cbench_ssh_client)

        # cbench ended, enqueue termination message
        if data_queue is not None:
            data_queue.put(succ_msg.value.decode(), block=True)
        logging.info('[cbench_thread] cbench thread ended successfully')
    except subprocess.CalledProcessError as err:
        if data_queue is not None:
            data_queue.put(fail_msg.value.decode(), block=True)
        logging.error('[cbench_thread] Exception:{0}'.format(str(err)))
    except:
        logging.error('[cbench_thread] General exception: cbench thread.')

    return
