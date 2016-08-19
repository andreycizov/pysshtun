import argparse
import logging

import itertools

import atexit

import time

import sys

from pysshtun.util import host_init, Port, host_stop, iptables_delete, iptables_rule, iptables_create, host_sync_status, \
    Status, host_start


def main():
    parser = argparse.ArgumentParser(description='sshtun')

    parser.add_argument('-P', dest='ports', action='append', default=[])
    parser.add_argument('-t', dest='sleep', default=1, type=float)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(logging.Formatter("[%(asctime)s][%(name)s]\t%(message)s"))
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    args = vars(parser.parse_args())

    hosts = []
    for hostname, host_ports in itertools.groupby(sorted(p.split(':') for p in args['ports']), key=lambda x: x[0]):
        host = host_init(hostname, tuple(Port(*x[1:]) for x in host_ports))
        hosts.append(host)
        logger.info('Created host {}'.format(host))

    iptables_rules = []

    def stop_hosts():
        for host in hosts:
            host_stop(host)

        for rule in iptables_rules:
            iptables_delete(rule)

    for host in hosts:
        for port in host.ports:
            iptables_rules.append(iptables_rule(port))

    for rule in iptables_rules:
        iptables_create(rule)

    atexit.register(stop_hosts)

    while True:
        for host in hosts:
            host_sync_status(host)

            if host.status in [Status.init, Status.stopped]:
                host_start(host)

        logger.debug('Sleeping for {}'.format(args['sleep']))
        time.sleep(args['sleep'])


if __name__ == '__main__':
    main()
