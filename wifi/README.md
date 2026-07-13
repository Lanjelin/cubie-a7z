# Cubie A7Z Wi-Fi fallback AP

This directory captures the Wi-Fi setup used to keep the Cubie A7Z reachable when normal client Wi-Fi does not come up.

The idea is simple: configure the usual Wi-Fi networks with netplan/NetworkManager, define a disabled fallback access point named `cubie-ap`, then let a systemd timer run a small check after boot. If `wlan0` has no IPv4 address and NetworkManager has no active Wi-Fi client connection, the script starts `cubie-ap`.

## Files

| File | Purpose |
| --- | --- |
| `etc_netplan_30-wifis-dhcp.yaml.example` | Example netplan Wi-Fi config with placeholder SSIDs/passwords. |
| `nmcli_network_priority_ap.example` | Example NetworkManager commands for client priorities and the fallback AP. |
| `wifi-fallback-ap.sh` | Boot-time check that starts `cubie-ap` only when client Wi-Fi failed. |
| `wifi-fallback-ap.service` | oneshot systemd service for the check. |
| `wifi-fallback-ap.timer` | Runs the service after boot. |

The local non-example files are ignored by `.gitignore` because they normally contain real Wi-Fi names and PSKs:

- `etc_netplan_30-wifis-dhcp.yaml`
- `nmcli_network_priority_ap`

## Configure Wi-Fi

Use the examples as templates, then replace all placeholder values locally.

```bash
cp etc_netplan_30-wifis-dhcp.yaml.example etc_netplan_30-wifis-dhcp.yaml
cp nmcli_network_priority_ap.example nmcli_network_priority_ap
```

Install the netplan file if you use this netplan layout:

```bash
sudo install -m 0600 etc_netplan_30-wifis-dhcp.yaml /etc/netplan/30-wifis-dhcp.yaml
sudo netplan apply
```

Run the edited NetworkManager commands to set client priorities and create the fallback AP:

```bash
sh nmcli_network_priority_ap
```

## Install the fallback service

```bash
sudo install -m 0755 wifi-fallback-ap.sh /usr/local/bin/wifi-fallback-ap.sh
sudo install -m 0644 wifi-fallback-ap.service /etc/systemd/system/wifi-fallback-ap.service
sudo install -m 0644 wifi-fallback-ap.timer /etc/systemd/system/wifi-fallback-ap.timer
sudo systemctl daemon-reload
sudo systemctl enable --now wifi-fallback-ap.timer
```

Check timer state and logs:

```bash
systemctl status wifi-fallback-ap.timer
journalctl -u wifi-fallback-ap.service
```

## Manual test

After configuring `cubie-ap`, you can run the check manually:

```bash
sudo /usr/local/bin/wifi-fallback-ap.sh
```

If normal Wi-Fi is already connected, it should exit without changing anything. If no client connection is active, it should bring up `cubie-ap`.
