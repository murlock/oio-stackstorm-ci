



Note: using openstack SDK through SSH
- connect with SSH to Gateway / Proxy (whatever it is called) with socks proxy enabled
`ssh -D 9998 user@gateway.ip`
- first, you have install proxychains
`apt install proxychains`
- edit `/etc/proxychains.conf` and in `[ProxyList]`, update it to:
`socks4 127.0.0.1 9998`
- now, you can use:
`proxychains openstack network list`
or your Python with Openstack SDK call
