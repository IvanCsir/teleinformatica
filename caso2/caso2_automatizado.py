#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


class Net:
    def __init__(self, num_redes):
        self.num_redes = num_redes
        self.net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')
        self.r_central = None

    def ip_redes(self):
        hosts = 8
        ip = '192.168.100'
        redes = []
        for redes in range(self.num_redes):
            redes.append(ip + '.' + str(int(hosts * redes)))
        return redes

    def add_switches(self):
        info( '*** Adding controller\n' )    
        info( '*** Add switches\n')
        name = "s" 
        for i in range(self.num_redes):
            self.net.addSwitch(name + '_wan' + str(i + 1), cls=OVSKernelSwitch, failMode='standalone')
            self.net.addSwitch(name + '_lan' + str(i + 1) , cls=OVSKernelSwitch, failMode='standalone')

    def add_router(self):
        r_central = self.net.addHost('r_central', cls=Node, ip='192.168.100.6/29')
        r_central.cmd('sysctl -w net.ipv4.ip_forward=1')

        for i in range(self.num_redes):
            self.net.addHost("r" + str(i+1), cls = Node)
            i.cmd('sysctl -w net.ipv4.ip_forward=1')

    def add_host(self):
        info( '*** Add hosts\n')        
        for i in range(self.num_redes):
            name = "h" + str(i+1)
            ip = "10.0." + str(i+1)
            ip_completa = ip + "254/24"
            self.net.addHost(name, cls=Host, ip = ip_completa, defaultRoute=None)

    def add_links(self):
        pass