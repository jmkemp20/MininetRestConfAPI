# Imports for MiniNet
from mininet.net import Mininet
from mininet.node import OVSController, OVSSwitch
from mininet.topo import Topo
from mininet.util import irange, dumpNodeConnections
from mininet.clean import Cleanup
# Imports for Server
import BaseHTTPServer
import SocketServer
# Imports for utilities
#import time
import json

net = None
topo = None

'''
    Custom Mininet Topology, 1 switch and n hosts
'''
class SingleSwitchTopo( Topo ):
  # Single switch connected to n hosts
  def build(self, n=2):
    switch = self.addSwitch('s1')
    # Python's range(N) generates 0..N-1
    for h in range(n):
      host = self.addHost('h%s' % (h + 1))
      self.addLink(host, switch)


class EmptyTopo( Topo ):
  def build(self):
    pass


'''
    Custom Request Handler for HTTP GET, POST, and DELETE commands
'''
class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def _set_headers(self):
    self.send_response(200)
    self.send_header("Content-type", "text/json")
    self.end_headers()
    
  def _get_hosts(self):
    global net
    #<Host h1: h1-eth0: 10.0.0.1 pid=14476>
    host = '''
    {
      "name": %s,
      "interfaces": [
        %s
      ],
      "pid": %s
    }
    '''
    intface = '''
    {
      "name": %s,
      "ip": %s,
      "EUI-48": %s
    }
    '''
    data = ""
    intfaces = ""
    for h in net.hosts:
      for i in h.intfList():
        intfaces += intface % (i.name, i.IP(), i.MAC())
        intfaces += "\n,\n"
      
      data += host % (h, intfaces[:-2], h.pid)
      data += "\n,\n"
      intfaces = ""
    return data[:-2]
    
  def _get_switches(self):
    global net
    switch = '''
    {
      "name": %s,
      "type": %s,
      "dpid": %s,
      "listenPort": %s,
      "connected": %s
      "interfaces": [
        %s
      ],
      "pid": %s
    }
    '''
    intface = '''
    {
      "name": %s,
      "ip": %s,
      "EUI-48": %s
    }
    '''
    data = ""
    intfaces = ""
    for s in net.switches:
      for i in s.intfList():
        intfaces += intface % (i.name, i.IP(), i.MAC())
        intfaces += "\n,\n"
      data += switch % (s.name, s.__class__.__name__, s.dpid, s.listenPort, s.connected(), intfaces[:-2], s.pid)
      data += "\n,\n"
      intfaces = ""
    return data[:-2]
  
  def _get_controllers(self):
    global net
    controller = '''
    {
      "name": %s,
      "type": %s,
      "ip": %s,
      "protocol": %s,
      "port": %s,
      "pid": %s
    }
    '''
    data = ""
    for c in net.controllers:
      data += controller % (c.name, c.__class__.__name__, c.IP(), c.protocol, c.port, c.pid)
      data += "\n,\n"
    return data[:-2]
    
  def _get_links(self):
    global net
    link = '''
    {
      "link": %s,
      "status": %s
    }
    '''
    data = ""
    for l in net.links:
      data += link % (l.__str__(), l.status())
      data += "\n,\n"
    return data[:-2]
  
    
  def _execute_request(self):
    data = '''
    {
      %s,
      %s,
      %s,
      %s
    }
    '''
    hosts = '''
    {
      "hosts": [
        %s
      ]
    } 
    ''' % self._get_hosts()
    switches = '''
    {
      "switches": [
        %s
      ]
    }
    ''' % self._get_switches()
    controllers = '''
    {
      "controllers": [
        %s
      ]
    }
    ''' % self._get_controllers()
    links = '''
    {
      "links": [
        %s
      ]
    }
    ''' % self._get_links()
    
    if (self.path == '/'):
      return data % (hosts, switches, controllers, links)
    elif (self.path == '/hosts'):
      return hosts
    elif (self.path == '/switches'):
      return switches
    elif (self.path == '/controllers'):
      return controllers
    elif (self.path == '/links'):
      return links
    else:
      return "ERROR DATA NOT FOUND FROM %s" % self.path
    
    #return data % (hosts, switches, controllers, links)
    #return self._get_switches()
    
  def do_GET(self):
    self._set_headers()
    ret = self._execute_request()
    self.wfile.write(ret);
    
  def do_POST(self):
    global topo
    global net
  
    content_length = int(self.headers['Content-length'])
    post_data = json.loads(self.rfile.read(content_length))
    print(post_data)
    self._set_headers()
    
    print(self.path[0:6])
    
    if (self.path[0:5] == '/host'):
      print('host')
      savedTopo = topo
      try: # Check if host field is available
        name = post_data["name"]
        savedTopo.addHost(name)
        try: # Switch link specified
          switch = post_data["switch"]
          savedTopo.addLink(name, switch)
        except: # No switch link specified
          pass
        try:
          res = restart_net(savedTopo)
        except:
          print("Error restarting network /host")
      except:
        print("No Host name specified /host")
        
      self.wfile.write("Done creating host %s with %s%% of packets dropped after pingAll()" % (name, res)) 
      
    elif (self.path[0:7] == '/switch'):
      print('switch')
      savedTopo = topo
      try:
        name = post_data["name"]
        savedTopo.addSwitch(name)
        try:
          res = restart_net_switch(savedTopo)
        except:
          print("Error restarting network /switch")
      except:
        print("No Switch name specified")
       
      self.wfile.write("Done creating switch %s" % name)
      
    elif (self.path[0:5] == '/link'):
      print('link')
      savedTopo = topo
      try:
        link1 = post_data["link_one"]
        link2 = post_data["link_two"]
        savedTopo.addLink(link1, link2)
        try:
          res = restart_net(savedTopo)
        except:
          print("Error restarting network /link")
      except:
        print("Invalid link specification /link")
   
      self.wfile.write("Done creating link between %s and %s, with %s%% of packets dropped after pingAll()" % (link1, link2, res))
      
    elif (self.path[0:4] == '/new'):
      net.stop()
      net = None
      topo = None
      
      cleanup = Cleanup.cleanup
      
      topo = EmptyTopo()
      
      for node in post_data:
        if (node == 'hosts'):
          for i in post_data[node]:
            topo.addHost(i)
        elif (node == 'switches'):
          for i in post_data[node]:
            topo.addSwitch(i)
        elif (node == 'controllers'):
          print("not created")
        elif (node == 'links'):
          for i in post_data[node]:
            topo.addLink(i['link_one'], i['link_two'])
        else:
          print("error")
          
      net = Mininet(topo, controller=OVSController, autoSetMacs=True)
      net.start()
      
      print ("Dumping host connections")
      dumpNodeConnections(net.hosts)
      print ("Testing network connectivity")
      res = net.pingAll()
      
      print('bulk new')
      self.wfile.write("Done creating bulk data, with %s%% of packets dropped after pingAll()" % (res)) 
    elif (self.path[0:1] == '/'):
      savedTopo = topo
      for node in post_data:
        if (node == 'hosts'):
          for i in post_data[node]:
            savedTopo.addHost(i)
        elif (node == 'switches'):
          for i in post_data[node]:
            savedTopo.addSwitch(i)
        elif (node == 'controllers'):
          print("not created")
        elif (node == 'links'):
          for i in post_data[node]:
            savedTopo.addLink(i['link_one'], i['link_two'])
        else:
          print("error")
      res = restart_net(savedTopo)
      print('bulk')
      self.wfile.write("Done creating bulk data, with %s%% of packets dropped after pingAll()" % (res)) 
    else:
      print("ERROR POSTING DATA TO %s" % self.path)
    
  def do_DELETE(self):
    self._set_headers()
    global topo
    global net
    net.stop()
    net = None
    topo = None
    cleanup = Cleanup.cleanup
    topo = EmptyTopo()
    net = Mininet(topo, controller=OVSController, autoSetMacs=True)
    net.start()
    
    self.wfile.write("Successfully deleted the entire Network, use the normal POST request to add on")
    
  
def run_mininet():
  global net
  global topo
  # "Create and test a simple network"
  topo = SingleSwitchTopo(n=4)
  net = Mininet(topo, controller=OVSController, autoSetMacs=True)
  net.start()
  print ("Dumping host connections")
  dumpNodeConnections(net.hosts)
  print ("Testing network connectivity")
  net.pingAll()
  #net.stop()
  
def restart_net( sTopo ):
  global net
  global topo
  print("Saved the topology")
  print("Stopping the network")
  net.stop()
  net = None
  topo = sTopo
  print("Stopped the network")
  print("Starting new network")
  net = Mininet(topo, controller=OVSController, autoSetMacs=True)
  net.start()
  print ("Dumping host connections")
  dumpNodeConnections(net.hosts)
  print("Testing network connectivity")
  ping = net.pingAll()
  print("Done restarting")
  print("Waiting for all switches to connect...")
  net.waitConnected()
  print("Done")
  return ping
  
def restart_net_switch( sTopo ):
  global net
  global topo
  print("Saved the topology")
  print("Stopping the network")
  net.stop()
  net = None
  topo = sTopo
  print("Stopped the network")
  print("Starting new network")
  net = Mininet(topo, controller=OVSController, autoSetMacs=True)
  net.start()
  print("Done restarting")
  print("Waiting for all switches to connect...")
  net.waitConnected()
  print("Done")
    
  
def run_api_server(handler=MyRequestHandler, addr="", port=8000):
  server_address = (addr, port)
  httpd = SocketServer.TCPServer(server_address, handler)
  
  print("Starting httpd server on %s:%s" % (addr, port))
  httpd.serve_forever()
  

if __name__ == "__main__":
  run_mininet()
  run_api_server()
  