import json
from mininet.net import Mininet
from mininet.node import OVSController, RemoteController, OVSSwitch
from mininet.topo import Topo
from mininet.util import irange, dumpNodeConnections

class EmptyTopo( Topo ):
  def build(self):
    pass


class NetworkConfigurator:

    def __init__(self, initfile, curfile):
        self.net,self.topo,self.data = self.create_net(filename=initfile)
        self.curfile = curfile
        self.save_net()

    def create_net(self, jsondata=None, filename=None):
        data = None
        if (filename != None):
            with open(filename) as f:
                data = json.load(f)
        else:
            data = jsondata

        topo = EmptyTopo()
        myController = None

        for node in data:
            if (node == 'hosts'):
                for i in data[node]:
                    topo.addHost(i)
            elif (node == 'switches'):
                for i in data[node]:
                    topo.addSwitch(i)
            elif (node == 'controller'):
                if (data[node]['type'] == 'RemoteController'):
                    myController = RemoteController(name=data[node]['name'], ip=data[node]['ip_address'], port=data[node]['OF_port'])
                else:
                    myController = OVSController(name=data[node]['name'])
            elif (node == 'links'):
                for i in data[node]:
                    topo.addLink(i['link_one'], i['link_two'])
            else:
                print("error")

        net = Mininet(topo, switch=OVSSwitch, controller=myController, autoSetMacs=True)
        net.start()

        print("Dumping host connections")
        dumpNodeConnections(net.hosts)
        print("Testing network connectivity")
        net.pingAll()

        return net, topo, data

    def restart_net(self):
        pass

    def save_net(self):
        with open(self.curfile, 'w') as f:
            json.dump(self.data, f)

    def update_net(self):
        pass