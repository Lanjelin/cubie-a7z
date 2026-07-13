#!/bin/sh

CLIENT_IF="wlan0"
AP_CONNECTION="cubie-ap"

# Give normal Wi-Fi time to connect
sleep 90

# If wlan0 already has an IPv4 address, do nothing
if ip -4 addr show "$CLIENT_IF" | grep -q "inet "; then
    exit 0
fi

# If NetworkManager says a Wi-Fi client connection is active, do nothing
if nmcli -t -f NAME,TYPE connection show --active | grep -q ":wifi$"; then
    exit 0
fi

# Start fallback AP
nmcli connection up "$AP_CONNECTION"

exit 0
