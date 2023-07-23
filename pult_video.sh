# Turn on pult soft with bottom and front video
(
  export PYTHONPATH=$(pwd)

  cd pult
  python3 video.py Front &
  python3 video.py Bottom &
)