import lxc_driver
import os
import time
import subprocess
import docker


LXC_PATH = '/var/lib/lxc/'


def create_ovs(ovs_name):
    print("Creating the OVS bridge {}".format(ovs_name))
    basic_cmd = 'sudo ovs-vsctl add-br {}'.format(ovs_name)
    os.system(basic_cmd)


def create_link_ovs(ovs_name_1, ovs_name_2, ovs_interface_1, ovs_interface_2, ovs_port):
    print("Attaching the OVS {} to the OVS {}".format(ovs_name_1, ovs_name_2))

    basic_cmd = 'sudo ip link add name {} type veth peer name {}'.format(ovs_interface_1, ovs_interface_2)
    os.system(basic_cmd)

    basic_cmd = "ip link set {} up".format(ovs_interface_1)
    os.system(basic_cmd)

    basic_cmd = "ip link set {} up".format(ovs_interface_2)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-port {0} {1} -- set Interface {1} ofport_request={2}"\
        .format(ovs_name_1, ovs_interface_1, ovs_port)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-port {0} {1} -- set Interface {1} ofport_request={2}"\
        .format(ovs_name_2, ovs_interface_2, ovs_port)
    os.system(basic_cmd)


def attach_ovs_to_sdn(ovs_name):
    print("Attaching the OVS bridge to the ONOS controller")
    client = docker.DockerClient()
    container = client.containers.get("onos")
    ip_add = container.attrs['NetworkSettings']['IPAddress']
    basic_cmd = "ovs-vsctl set-controller {} tcp:{}:6653".format(ovs_name, ip_add)
    os.system(basic_cmd)


def create_lxc_container(container_name, ovs_name, ovs_port, ip_address):
    if lxc_driver.create_container(container_name):
        modify_configuration_bridge(container_name)
        container_bridge_ovs(container_name, ovs_name, ovs_port)
        lxc_driver.container_attach(container_name, ["ip", "addr", "add", "{}/24".format(ip_address), "dev", "eth0"])
        lxc_driver.container_attach(container_name, ["ip", "link", "set", "dev", "eth0", "up"])
        time.sleep(5)
        if not lxc_driver.start_container(container_name):
            return False
        time.sleep(2)

        while len(lxc_driver.get_ip_container(container_name)) != 1:
            print("current_ip: {}".format(lxc_driver.get_ip_container(container_name)))
            print("envisaged_ip: {}".format(ip_address))
            time.sleep(1)
        response = 0
        while response != 256:
            response = lxc_driver.container_attach(container_name, ["ping", "-c", "1", "10.0.0.90"])
        print("end creation of server")
        return True


# bridge creation for each container
def modify_configuration_bridge(container_name):
    """
    bridge creation for each container
    :param container_name:
    :return:
    """
    print("BEGIN modify_configuration_bridge")
    for line in open('{}{}/config'.format(LXC_PATH, container_name), "r"):
        if "lxc.net.0.link" in line:
            with open('{}{}/config'.format(LXC_PATH, container_name), "r") as input_file:
                with open('{}{}/config2'.format(LXC_PATH, container_name), "w") as output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)
                        else:
                            output_file.write('\nlxc.net.0.link =')
                            output_file.write(' ')
                            output_file.write('br{}'.format(container_name))
                            output_file.write('\n')

            basic_cmd = 'rm {}{}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            basic_cmd = 'mv {0}{1}/config2 {0}{1}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
    print("END modify_configuration_bridge")


def container_bridge_ovs(container_name, ovs_name, ovs_port, diff=''):
    """
    Setting container ovs_bridge configurations
    :param container_name:
    :param ovs_name:
    :param ovs_port:
    :param diff:
    :return:
    """

    basic_cmd = 'ip link add name veth{0}Ovs{1} type veth peer name vethOvs{1}{0}'.format(container_name, diff)
    os.system(basic_cmd)

    basic_cmd = "ip link set vethOvs{0}{1} up".format(diff, container_name)
    os.system(basic_cmd)

    basic_cmd = "ip link set veth{0}Ovs{1} up".format(container_name, diff)
    os.system(basic_cmd)

    basic_cmd = "brctl addbr br{0}{1}".format(diff, container_name)
    os.system(basic_cmd)

    basic_cmd = "ifconfig br{0}{1} up".format(diff, container_name)
    os.system(basic_cmd)

    basic_cmd = "brctl addif br{1}{0} veth{0}Ovs{1}".format(container_name, diff)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-port {2} vethOvs{3}{0} -- set Interface vethOvs{3}{0} ofport_request={1}".format(
        container_name, ovs_port, ovs_name, diff)
    print(basic_cmd)
    os.system(basic_cmd)


def set_ip(container_name, ip_address, decision=False, ip_address_2=""):
    """
    IP setting
    :param container_name:
    :param ip_address:
    :param decision:
    :param ip_address_2:
    :return:
    """
    print("BEGIN set_ip")
    for line in open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "r"):
        if "iface eth0 inet dhcp" in line or "auto eth0" in line:
            with open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "r") as input_file:
                with open('{}{}/rootfs/etc/network/interfaces2'.format(LXC_PATH, container_name), "a") as output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)

            basic_cmd = 'rm {}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            basic_cmd = 'mv {0}{1}/rootfs/etc/network/interfaces2 {0}{1}/rootfs/etc/network/interfaces'.format(
                LXC_PATH, container_name)
            os.system(basic_cmd)
    system_ip_configuration(container_name, ip_address, '0')
    if decision:
        system_ip_configuration(container_name, ip_address_2, '1')
    print("END set_ip")


def system_ip_configuration(container_name, ip_address, interface_number):
    """
    IP setting
    :param container_name:
    :param ip_address:
    :param interface_number:
    :return:
    """
    with open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "a") as my_file:
        my_file.write('\nauto eth{}'.format(interface_number))
        my_file.write('\n')
        my_file.write('iface eth{} inet static'.format(interface_number))
        my_file.write('\n    address ')
        my_file.write(str(ip_address))
        my_file.write('\n')
        my_file.write('    netmask 255.255.255.0')
        my_file.write('\n')


if __name__ == '__main__':
    create_ovs("ovs-7")
    create_ovs("ovs-8")
    create_link_ovs("ovs-7", "ovs-8", "int-ovs7", "int-ovs8", 1)
    attach_ovs_to_sdn("ovs-7")
    attach_ovs_to_sdn("ovs-8")
    create_lxc_container("green", "ovs-7", 2, "10.0.0.10")
    create_lxc_container("yellow", "ovs-8", 2, "10.0.0.11")

