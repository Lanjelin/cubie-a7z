# Cubie A7Z fan daemon

This directory contains a small PWM fan controller for the Cubie A7Z stock cooling/fan setup.

`cubie-fand` reads thermal zones from `/sys/class/thermal`, ignores `skin_zone`, and writes PWM values to the hwmon device whose `name` is `pwmfan`. The `hwmonN` number is discovered at startup, not hard-coded. It uses a small temperature curve plus hysteresis so the fan does not constantly bounce between speeds.

## Files

| File | Purpose |
| --- | --- |
| `cubie-fand` | Python fan control daemon. |
| `cubie-fand.service` | systemd service unit. |
| `cubie-pwm-fan.dts` / `.dtbo` | Restore the fan device and PWM1 channel 9 routing to PJ27 after the kernel upgrade. |

## Kernel-upgrade recovery

The upgraded base DTB omits the original `pwm-fan` device and routes PWM1 channel 9 to PK5 instead of the fan connector's PJ27. The kernel includes `pwm-fan.ko`, but without the device node there is no fan hwmon interface: the old daemon crashes at startup and the status display shows `--%`.

`cubie-pwm-fan.dts` restores PJ27 active/sleep pinctrl and a `pwm-fan` device using PWM1 channel 9 at a 25,000 ns period (40 kHz). It also keeps `reg_dc1sw1` enabled for the PJ I/O bank, independently of the e-paper overlay. The fan's J6 power pin is fixed 5 V, not `dc1sw1`; that regulator powers the control pin's I/O bank.

The overlay deliberately adds no thermal cooling maps: `cubie-fand` remains the sole temperature-curve controller. The display percentage is PWM duty cycle, not measured RPM; the connector has no tachometer input. The daemon keeps the existing `pwm1_enable=1` behavior and reports enable/write failures instead of silently ignoring them.

References: [original Radxa board DTS](https://github.com/radxa/allwinner-device/blob/device-a733-v1.4.8/configs/cubie_a7z/linux-6.6/board.dts) and [A7Z schematic V1.11, pages 7 and 16](https://dl.radxa.com/cubie/a7z/docs/hw/radxa_cubie_a7z_schematic_v1.11.pdf).

## Install

Run from this checkout's `fan/` directory. Compilation needs no elevation; installation, boot configuration, and reboot require `sudo`.

```bash
dtc -@ -I dts -O dtb -o cubie-pwm-fan.dtbo cubie-pwm-fan.dts
sudo systemctl stop cubie-fand.service
sudo install -d /boot/overlay-user
sudo install -m 0644 cubie-pwm-fan.dtbo /boot/overlay-user/cubie-pwm-fan.dtbo
sudo install -m 0755 cubie-fand /usr/local/sbin/cubie-fand
sudo install -m 0644 cubie-fand.service /etc/systemd/system/cubie-fand.service
sudo systemctl daemon-reload
sudo systemctl enable cubie-fand.service
sudo nano /boot/armbianEnv.txt
```

Append `cubie-pwm-fan` to the existing `user_overlays` line, preserving unrelated tokens. With the existing e-paper power overlay and no other overlays:

```ini
user_overlays=cubie-header-io-power cubie-pwm-fan
```

Keep the e-paper overlay and Wi-Fi configuration unchanged. Do not start the daemon until the new device tree is active:

```bash
sudo reboot
```

After reconnecting, inspect the fan interface and service:

```bash
for h in /sys/class/hwmon/hwmon*; do
    [ "$(cat "$h/name" 2>/dev/null)" = pwmfan ] || continue
    printf '%s: PWM=' "$h"
    cat "$h/pwm1"
    printf 'PWM enable mode='
    cat "$h/pwm1_enable"
done
systemctl status cubie-fand.service --no-pager
journalctl -u cubie-fand.service -b -n 20 --no-pager
```

Expected: one `pwmfan` device, a running daemon, and PWM `128` (about 50%) at temperatures below 45°C. Above that, the curve below applies. Check that the fan physically spins and the status display replaces `--%` with a numeric value.

If the fan interface is absent, inspect kernel logs for PWM probe errors; do not export or directly drive the raw PWM channel while debugging. To roll back, stop/disable `cubie-fand.service`, remove only the `cubie-pwm-fan` token from `user_overlays`, and reboot.

Verification before installation: the compiled overlay applied to the installed base DTB alongside `cubie-header-io-power`; PWM resolves to channel 9 at 40 kHz and both pinctrl states resolve to PJ27. A filesystem-backed daemon smoke run discovered `hwmon7`, ignored an unrelated PWM device, and produced duty transitions `136 → 136 → 128` at `46 → 41 → 40°C`. Physical fan operation and the display readout require post-reboot verification.


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
