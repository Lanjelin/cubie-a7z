# Cubie A7Z fan daemon

This directory contains a small PWM fan controller for the Cubie A7Z stock cooling/fan setup.

`cubie-fand` reads thermal zones from `/sys/class/thermal`, ignores `skin_zone`, and writes PWM values to `/sys/class/hwmon/hwmon1/pwm1`. It uses a small temperature curve plus hysteresis so the fan does not constantly bounce between speeds.

## Files

| File | Purpose |
| --- | --- |
| `cubie-fand` | Python fan control daemon. |
| `cubie-fand.service` | systemd service unit. |

## Assumptions

The daemon currently assumes these Armbian sysfs paths:

```text
/sys/class/hwmon/hwmon1/pwm1_enable
/sys/class/hwmon/hwmon1/pwm1
/sys/class/thermal/thermal_zone*
```

Verify them on the board before installing:

```bash
ls /sys/class/hwmon/hwmon1/pwm1_enable /sys/class/hwmon/hwmon1/pwm1
ls /sys/class/thermal/thermal_zone*/type
```

If Armbian exposes the fan under a different `hwmonN`, update `PWM_ENABLE` and `PWM` in `cubie-fand` before installing.

## Install

```bash
sudo install -m 0755 cubie-fand /usr/local/sbin/cubie-fand
sudo install -m 0644 cubie-fand.service /etc/systemd/system/cubie-fand.service
sudo systemctl daemon-reload
sudo systemctl enable --now cubie-fand.service
```

Check service state and logs:

```bash
systemctl status cubie-fand.service
journalctl -u cubie-fand.service -f
```

## Fan curve

The current curve starts at `MIN_PWM = 128` and increases through these temperature/PWM points:

| Temperature | PWM |
| --- | --- |
| 45°C | 136 |
| 50°C | 144 |
| 55°C | 152 |
| 60°C | 160 |
| 70°C | 192 |
| 80°C | 224 |
| 88°C | 255 |

Decrease hysteresis is `5°C`.
