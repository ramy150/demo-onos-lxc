import lxc
import sys
import os

LXC_PATH = '/var/lib/lxc/'


def create_container(container_name):
    c = lxc.Container(container_name)
    if c.defined:
        print("Container already exists", file=sys.stderr)
        return False

    if not c.create("download", lxc.LXC_CREATE_QUIET, {"dist": "ubuntu",
                                                       "release": "trusty",
                                                       "arch": "amd64"}):
        print("Failed to create the container rootfs", file=sys.stderr)
        return False
    return True


# List of all the containers
def list_containers():
    try:
        list_all_containers = []
        for container in lxc.list_containers(as_object=True):
            list_all_containers.append(container.name)
        return list_all_containers
    except Exception as exception:
        return exception


# Container status
def containers_status(container_name):
    try:
        c = lxc.Container(container_name)
        if c.state == 'RUNNING' and len(c.get_ips()) == 1:
            print("container is running")
            return c.state, c.get_ips()[0]
        print("container is stopped")
        return c.state, 0
    except Exception as exception:
        return exception


# Start a container after the creation
def start_container(container_name):
    try:
        c = lxc.Container(container_name)
        if not c.defined:
            return False
        if c.start():
            print(c.state)
            return True
        return False
    except Exception as exception:
        return exception


# Get IP address of container
def get_ip_container(container_name):
    try:
        c = lxc.Container(container_name)
        if not c.defined:
            return False
        return c.get_ips()
    except Exception as exception:
        return exception


# attach containers
def container_attach(container_name, command):
    c = lxc.Container(container_name)
    if not c.defined:
        return False
    return c.attach_wait(lxc.attach_run_command, command)


def delete_container(container_name):
    try:
        c = lxc.Container(container_name)
        if not c.defined:
            return False
        c.stop()
        if c.destroy():
            return True
        return False
    except Exception as exception:
        return exception


# Used to clone containers from images or templates
def clone_from_template(template, clone_name):
    c = lxc.Container(template)
    if not c.defined:
        return False
    new_container = c.clone(clone_name)
    return new_container.defined


def modify_configuration_bridge(container_name):
    """
    bridge creation for each container
    :param container_name:
    :return:
    """
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
    os.system(basic_cmd)
