# Installing requirements

## Installing Docker or refer to the [official docker website]( https://docs.docker.com/engine/install/ubuntu/)
```
sudo apt-get remove docker docker-engine docker.io containerd runc
```

```
sudo apt-get update
```
```

sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
```

```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

```
sudo apt-key fingerprint 0EBFCD88
```

```
sudo add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

```
sudo apt-get update
```

```
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

```
docker run hello-world
```

## Installing OVS
```
sudo apt update
```

```
sudo apt upgrade
```

```
sudo apt install openvswitch-switch
```

## Installing LXC
```
sudo apt-get install lxc
```

```
sudo apt-get update -y
```

```
apt install python3-pip
```

```
sudo apt-get install -y python3-lxc
```

```
pip3 install docker
```


## Installing LXD

```
pip install pylxd
``` 