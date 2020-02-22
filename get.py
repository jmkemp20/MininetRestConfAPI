import json

main_data = ""

get_data = '''
{
  "hosts": [
    %s
  ],
  "switches": [
    %s
  ],
  "controller": {
      %s
  },
  "links": [
    %s
  ]
}
'''
host = '''
{
  "name": "%s",
  "interfaces": [
    %s
  ],
  "pid": "%s"
}
'''
switch = '''
{
  "name": "%s",
  "type": "%s",
  "dpid": "%s",
  "listenPort": "%s",
  "connected": "%s",
  "interfaces": [
    %s
  ],
  "pid": "%s"
}
'''
controller = '''
  "name": "%s",
  "type": "%s",
  "ip": "%s",
  "protocol": "%s",
  "port": %s,
  "pid": "%s"
'''
link = '''
{
  "link": "%s",
  "status": "%s"
}
'''
interface = '''
{
  "name": "%s",
  "ip": "%s",
  "EUI-48": "%s"
}
'''

def _get_hosts(net):
    data = ""
    intfaces = ""
    for h in net.hosts:
        for i in h.intfList():
            intfaces += interface % (i.name, i.IP(), i.MAC())
            intfaces += "\n,\n"

        data += host % (h, intfaces[:-2], h.pid)
        data += "\n,\n"
        intfaces = ""
    return data[:-2]

def _get_switches(net):
    data = ""
    intfaces = ""
    for s in net.switches:
        for i in s.intfList():
            intfaces += interface % (i.name, i.IP(), i.MAC())
            intfaces += "\n,\n"
        data += switch % (s.name, s.__class__.__name__, s.dpid, s.listenPort, s.connected(), intfaces[:-2], s.pid)
        data += "\n,\n"
        intfaces = ""
    return data[:-2]

def _get_controller(net):

    data = ""
    for c in net.controllers:
      data += controller % (c.name, c.__class__.__name__, c.IP(), c.protocol, c.port, c.pid)
      data += "\n,\n"
    return data[:-2]

def _get_links(net):
    data = ""
    for l in net.links:
        data += link % (l.__str__(), l.status())
        data += "\n,\n"
    return data[:-2]

# Receives current network JSON as filename
def getJSON(net):
    global main_data
    main_data = get_data % (_get_hosts(net), _get_switches(net), _get_controller(net), _get_links(net))
    return main_data