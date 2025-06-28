## Assignment 2

### Pi setup

#### Install system dependencies:

```
$ sudo apt update -y && sudo apt install -y iw tshark
```

When installing tshark, let non-sudo users run it by clicking yes.

### Capturing packets

We assume the pi currently has three network interfaces: `wlan0` which is connected to the internet, `wlan1` which we will use to capture WiFi probe requests on, and `wlan2` which will be used to span the AP. If your setup differs from that, please modify the `capture.sh` script or your execution of it accordingly.
`$ sudo ./capture.sh -m <probe|network> [-o <output_file>] [-f <capture filter>] [-i <interface>] [-c <channel>]`

For the first part of this assignment, we used the capture script with the following parameters to capture WiFi probe requests: `$ sudo ./capture.sh -m probe -i wlan1 -o /tmp/capture-1.pcap -c 1`. We used this script with three connected network dongles, and respectively used channels 1, 6, and 11 with each connected dongle/network interface to capture the probe requests.
For the second part of this assignment, we used the capture script with the following parameters to capture all incoming traffic on the AP: `$ sudo ./capture.sh -m network -i wlan2 -o /tmp/capture.pcap`.

### AP Mode

Make sure you have two wifi dongles connected to the pi, and that you have internet over the network interface `wlan0`. Otherwise, change the script below to accomodate those changes.
`wlan0` is the network interface providing internet to the AP, which is created on the `wlan2` interface. All traffic to the internet will be routed from `wlan2` to `wlan0` with iptables rules.

1. Install necessary packages:

```
$ sudo apt update
$ sudo apt install hostapd dnsmasq netfilter-persistent iptables-persistent
```

2. Stop the hostapd and dnsmasq services (first is for the AP, second is for local DNS and DHCP):

```
$ sudo systemctl stop hostapd
$ sudo systemctl stop dnsmasq
```

3. Configure a static IP for the access point interface (wlan2). Edit the dhcpcd configuration:

`$ sudo nano /etc/dhcpcd.conf`

Add these lines at the end:

```
interface wlan2
static ip_address=192.168.4.1/24
nohook wpa_supplicant
```

4. Configure the DHCP server (dnsmasq): we first make a backup of the existing default configuration.

```
$ sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
```

Edit the config file:
`$ sudo nano /etc/dnsmasq.conf`

Add these lines at the end to configure a static IP address for the AP, and specify the range of IPs leased to the connected stations through DHCP:

```
interface=wlan2
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/gw.wlan/192.168.4.1
```

5. Configure the access point (hostapd):

`$ sudo nano /etc/hostapd/hostapd.conf`

Add these lines at the end to configure the name of the AP created by the machine (rememeber to change the SSID and password, and possibly the interface if you want to use a different one):

```
interface=wlan2
driver=nl80211
ssid=YourNetworkName
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=YourPassword
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

Tell hostapd where to find the configuration:

`$ sudo nano /etc/default/hostapd`

Find the commented-out line `#DAEMON_CONF` and replace it the following path, where we just placed the new AP configuration:

`DAEMON_CONF="/etc/hostapd/hostapd.conf"`

6. Enable IP forwarding:

`$ sudo nano /etc/sysctl.conf`

Uncomment or add the line:

`net.ipv4.ip_forward=1`

7. Configure NAT and routing between the network interfaces `wlan0` and `wlan2` rules, so that incoming traffic on `wlan2` can reach the internet through `wlan0`:

```
$ sudo iptables -A POSTROUTING -t nat -o wlan0 -j MASQUERADE
$ sudo iptables -A FORWARD -i wlan0 -o wlan2 -m state --state RELATED,ESTABLISHED -j ACCEPT
$ sudo iptables -A FORWARD -i wlan2 -o wlan0 -j ACCEPT
```

Save the iptables rules so that they persist upon reboot:

`sudo netfilter-persistent save`

8. Enable and start the services we just modified:

```
$ sudo systemctl unmask hostapd
$ sudo systemctl enable hostapd
$ sudo systemctl enable dnsmasq
$ sudo systemctl start hostapd
$ sudo systemctl start dnsmasq
```

9. And that's it! We can now reboot the pi:

`sudo reboot`

Hopefully, after the restart you should be able to see an AP with the SSID and password we configured on step 5.

### Possible caveats

We have had problems with the network interfaces not receiving any traffic. If that is the case for you as well, try hopping between different channels: our `channel-hopping.sh` script conveniently jumps between channels 1-11 every two seconds. Once you see traffic, feel free to stop the hopping.
