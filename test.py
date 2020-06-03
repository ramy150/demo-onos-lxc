from pylxd import Client
from signal import signal, SIGPIPE, SIG_DFL
import time
import os

def test(container_name, ovs_name, ip_address):
    signal(SIGPIPE, SIG_DFL)
    client = Client()
    if not client.profiles.exists(ovs_name):
        client.profiles.create(
            ovs_name,
            config={'environment.http_proxy': 'http://[fe80::1%eth0]:13128', 'user.network_mode': 'link-local'},
            devices={'eth0': {'name': 'eth0', 'nictype': 'bridged', 'parent': ovs_name, 'type': 'nic'}})
    config = {
        'name': container_name,
        'source':
            {
                'type': 'image',
                "mode": "pull",
                "server": "https://cloud-images.ubuntu.com/daily",
                "protocol": "simplestreams",
                'alias': 'bionic/amd64'
            },
        'profiles': [ovs_name]}
    container = client.containers.create(config, wait=True)
    container.start()
    while client.containers.get(container_name).status != 'Running':
        print("waiting")
        time.sleep(1)
    time.sleep(5)
    basic_cmd = "lxc exec {} -- ip addr add {}/24 dev eth0".format(container_name, ip_address)
    os.system(basic_cmd)
    basic_cmd = "lxc exec {} -- ip link set dev eth0 up".format(container_name)
    os.system(basic_cmd)


test("lxd5", "br-ovs", "10.0.0.25")