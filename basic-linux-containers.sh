#!/usr/bin/env bash

function create_container() {
echo "Creating the container $1"
sudo lxc-create -t download -n $1 -- -d ubuntu -r $2 -a $3
}

function create_ovs_bridge() {
echo "Creating the OVS bridge $1"
ovs-vsctl add-br $1

}


function attach_container_to_ovs() {
echo "Attaching the namespace $1 to the OVS $2"
ip link add $3 type veth peer name $4
ip link set $3 netns $1
ovs-vsctl add-port $2 $4 -- set Interface $4 ofport_request=$5
ip netns exec $1 ip addr add $6/24 dev $3
ip netns exec $1 ip link set dev $3 up
ip link set $4 up
}


function attach_ovs_to_ovs() {
echo "Attaching the OVS $1 to the OVS $2"
ip link add name $3 type veth peer name $4
ip link set $3 up
ip link set $4 up
ovs-vsctl add-port $1 $3 -- set Interface $3 ofport_request=$5
ovs-vsctl add-port $2 $4 -- set Interface $4 ofport_request=$5
}

function attach_ovs_to_sdn() {
echo "Attaching the OVS bridge to the ONOS controller"
ovs-vsctl set-controller $1 tcp:$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -q  --filter ancestor=onosproject/onos)):6653
}


create_container red trusty amd64
create_container blue trusty amd64

create_ovs_bridge br-1
create_ovs_bridge br-2

attach_ovs_to_ovs br-1 br-2 br-ovs1 br-ovs2 1
attach_container_to_ovs red br-1 veth-red veth-red-br 2 10.0.0.2
attach_container_to_ovs blue br-2 veth-blue veth-blue-br 2 10.0.0.3

attach_ovs_to_sdn br-1
attach_ovs_to_sdn br-2