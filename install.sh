# Install all sofware to robot
rsync -vIpzrt --exclude .git --exclude venv --exclude __pycache__ . auv@192.168.88.101:geekpy
