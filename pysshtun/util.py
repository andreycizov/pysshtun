import enum
import functools
import os
import subprocess
import psutil
import logging

logger = logging.getLogger(__name__)


class Port:
    def __init__(self, hostname, local_addr, local_port, remote_addr, remote_port):
        self.hostname = hostname
        self.local_addr = local_addr
        self.local_port = local_port
        self.remote_addr = remote_addr
        self.remote_port = remote_port

    def notate(self):
        return ':'.join((self.local_addr, self.local_port, self.remote_addr, self.remote_port))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Port<{0.hostname}, {0.local_addr}:{0.local_port}, {0.remote_addr}:{0.remote_port}>'.format(self)


class Host:
    def __init__(self, status, ssh_alias, ports, pid):
        self.status = status
        self.ssh_alias = ssh_alias
        self.ports = ports
        self.pid = pid

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Host<{0.status}, {0.ssh_alias}, {0.ports}, {pid}>'.format(self, pid=self.pid.pid if self.pid else None)


class Status(enum.Enum):
    init = 'INIT'
    started = 'STARTED'
    running = 'RUNNING'
    stopped = 'STOPPED'


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def host_sync_status(host: Host):
    assert host.status in [Status.running, Status.started, Status.init]

    # logger.debug('Syncing host status = {}'.format(host))

    # if host.pid:
    #     print(subprocess.Popen(host.pid).poll())

    if host.status in [Status.init, Status.stopped]:
        pass
    else:
        if host.pid.poll() is None:
            host.status = Status.running
        else:
            host.status = Status.stopped
            host.pid = None

    logger.debug('Synced host status = {}'.format(host))


def host_init(ssh_alias, ports):
    return Host(
        Status.init,
        ssh_alias,
        ports,
        None
    )


def host_start(host: Host):
    assert host.status in [Status.stopped, Status.init]

    port_mappings = functools.reduce(lambda a, b: a + b,
                                     [['-L', x] for x in [x.notate() for x in host.ports]], [])

    opts = ['-o', 'PasswordAuthentication=no', '-o', 'ExitOnForwardFailure=yes', '-o', 'ConnectTimeout=5', '-o', 'IdentitiesOnly=yes']

    args = ['ssh', '-N'] + opts + port_mappings + [host.ssh_alias]

    logger.info('Starting process with args = `{}`'.format(' '.join(args)))

    # host.pid = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    host.pid = subprocess.Popen(args)

    host.status = Status.started


def host_stop(host: Host):
    if host.status is Status.running:
        logger.info('Host {} is being stopped'.format(host))
        host.pid.terminate()


def iptables_rule(rule: Port):
    rule = "OUTPUT -o eth0 -p tcp -d {rule.hostname} --dport {rule.remote_port} -j DNAT --to-destination {rule.local_ad" \
           "dr}:{rule.local_port} -m comment --comment sshtun".format(rule=rule)

    return rule.split(' ')


def iptables_create(rule):
    cmd = ['sudo', 'iptables', '-t', 'nat', '-A'] + rule
    subprocess.check_call(cmd)
    logger.debug('{}'.format(' '.join(cmd)))


def iptables_delete(rule):
    cmd = ['sudo', 'iptables', '-t', 'nat', '-D'] + rule
    subprocess.check_call(cmd)
    logger.debug('{}'.format(' '.join(cmd)))
