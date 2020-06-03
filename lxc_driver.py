import lxc
import sys


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
