# Turn on pult soft with front video
(
  export PYTHONPATH=$(pwd)

  cd pult
  python3 dualshock.py &
  python3 video.py Front &
  python3 video.py Bottom &
)
