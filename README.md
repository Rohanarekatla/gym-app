
cidrs = [c.strip("*% ") for c in cidrs if '/' in c]

# Sort first by prefix length (shorter subnet mask = larger number), then IP
sorted_cidrs = sorted(cidrs, key=lambda x: (int(x.split('/')[1]), ipaddress.IPv4Network(x).network_address))

for cidr in sorted_cidrs:
    print(cidr)