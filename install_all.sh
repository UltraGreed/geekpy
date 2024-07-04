# Install all sofware to robot
rsync -vIpzrt --exclude .git --exclude venv --exclude .venv --exclude __pycache__ --exclude "*.png" --exclude "*.jpg"  . auv@192.168.88.101:geekpy
