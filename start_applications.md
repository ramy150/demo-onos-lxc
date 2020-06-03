## How to access the cluster? using ssh & port! (default user onos password rocks)

```
ssh onos@127.0.0.1 -p 8101  
```
## Activate ONOS applications

### Activating "Host Location Provider" Application

```
app activate org.onosproject.hostprovider
```
### Activating "Host Mobility" Application

```
app activate org.onosproject.mobility
```
### Activating "LLDP Link Provider" Application

```
app activate org.onosproject.lldpprovider
```
### Activating "OpenFlow Agent" Application

```
app activate org.onosproject.ofagent
```
### Activating "OpenFlow Base Provider" Application

```
app activate org.onosproject.openflow-base
```
### Activating "OpenFlow Provider Suite" Application

```
app activate org.onosproject.openflow
```
### Activating "Optical Application" Application

```
app activate org.onosproject.roadm
```
### Activating "Proxy ARP/NDP" Application
```
app activate org.onosproject.proxyarp 
```

### Activating "Reactive Forwarding" Application
```
app activate org.onosproject.fwd
```
