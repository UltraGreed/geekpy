modprobe can
modprobe can-raw
modprobe mttcan
ip link set can0 up type can bitrate 500000
ip link set can1 up type can bitrate 500000

echo 392 > /sys/class/gpio/export
echo 394 > /sys/class/gpio/export
echo 395 > /sys/class/gpio/export
echo 396 > /sys/class/gpio/export

sleep 0.2

echo out > /sys/class/gpio/gpio392/direction
echo out > /sys/class/gpio/gpio394/direction
echo out > /sys/class/gpio/gpio395/direction
echo out > /sys/class/gpio/gpio396/direction
