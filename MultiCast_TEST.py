import socket

multicast_address = 'ff05::113d:6fdd:2c17:a643:ffe2:1bd1:3cd2'
port = 12345

# Create a UDP socket for IPv6
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Optionally set multicast options for IPv6
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 255)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 1)

message = b'Hello, multicast!'

# Send the message to the multicast address and port
sock.sendto(message, (multicast_address, port))