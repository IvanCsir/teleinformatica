#!/usr/bin/python.
# -*- coding: utf-8 -*-


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
        redes_list = []
        for redes in range(self.num_redes):
            redes_list.append(ip + '.' + str(int(hosts * redes)))
        return redes_list

    def add_switch(self):
        info( '*** Adding controller\n' )    
        info( '*** Add switches\n')
        name = "s" 
        for i in range(self.num_redes):
            self.net.addSwitch(name + str(i + 1) + '_wan' , cls=OVSKernelSwitch, failMode='standalone')
            self.net.addSwitch(name + str(i + 1) + '_lan' , cls=OVSKernelSwitch, failMode='standalone')

    def add_router(self):
        self.r_central = self.net.addHost('r_central', cls=Node, ip='192.168.100.6/29')
        self.r_central.cmd('sysctl -w net.ipv4.ip_forward=1')

        for i in range(self.num_redes):
            nombre = "r" + str(i+1)
            r = self.net.addHost(nombre, cls = Node)
            r.cmd('sysctl -w net.ipv4.ip_forward=1')

    def add_host(self):
        info( '*** Add hosts\n')        
        for i in range(self.num_redes):
            name = "h" + str(i+1)
            ip = "10.0." + str(i+1)
            ip_completa = ip + ".254/24"
            self.net.addHost(name, cls=Host, ip = ip_completa, defaultRoute=None)

    def add_links(self):
        redes = self.ip_redes()
        for i in range(self.num_redes):
            switch_wan = self.net.get("s" + str(i + 1) + '_wan')
            router = self.net.get("r" + str(i + 1))
            switch_lan = self.net.get("s" + str(i + 1) + '_lan')
            hosts = self.net.get("h" + str(i+1))


            self.net.addLink(self.r_central, switch_wan)
            self.net.addLink(switch_wan,router)
            self.net.addLink(router, switch_lan)
            self.net.addLink(switch_lan,hosts)

    def crear_red(self):
        info('* Starting network\n')
        self.net.build()

        info( '*** Starting controllers\n')
        for controller in self.net.controllers:
            controller.start()

        info( '*** Starting switches\n')
        for i in self.net.switches:
            i.start([])

    def config(self, redes_list):
        info('* Post configure switches and hosts\n')

        for i in range(self.num_redes):
            r = self.net.get("r" + str(i + 1))
            h = self.net.get("h" + str(i + 1))
            red = redes_list[i].rsplit('.', 1)
            ip = red[0] + '.' + str(int(red[1]) + 6)
            r_central_eth = 'r_central-eth' + str(i)
            self.r_central.setIP(ip, prefixLen=29, intf=r_central_eth)
            ip2 = red[0] + '.' + str(int(red[1]) + 1)
            eth0 = 'r' + str(i + 1) + '-eth0'
            ip_lan = '10.0.' + str(i + 1) + '.1'
            red_host = '10.0.' + str(i + 1) + '.0/24'
            eth1 = 'r' + str(i + 1) + '-eth1'
            r.setIP(ip2, prefixLen=29, intf=eth0)
            r.setIP(ip_lan, prefixLen=24, intf=eth1)
            cmd = 'ip route add ' + red_host + ' via ' + ip2
            self.r_central.cmd(cmd)
            cmd1 = 'ip route add 10.0.0.0/18 via ' + ip
            r.cmd(cmd1)
            cmd2 = 'ip route add 192.168.100.0/24 via ' + ip
            r.cmd(cmd2)
            cmd3 = 'ip route add 10.0.0.0/18 via ' + ip_lan
            h.cmd(cmd3)
            cmd4 = 'ip route add 192.168.100.0/24 via ' + ip_lan
            h.cmd(cmd4)

    def start(self):

        redes_list = self.ip_redes()
        self.ip_redes()
        self.add_switch()
        self.add_router()
        self.add_host()
        self.add_links()
        self.crear_red()
        self.config(redes_list)
        CLI(self.net)
        self.net.stop()

def main():
    while True:
        while True:
            cant_redes = int(input("¿Cuantas redes quiere crear? Menor o igual a 32: "))
            break
        if cant_redes > 0 and cant_redes < 33:
            break
        else:
            print("Ingrese una cantidad menor a 32 redes")
    caso2 = Net(cant_redes)
    caso2.start()

if __name__ == '__main__':
    setLogLevel('info')
    main()
