# Turn on pult soft with bottom and front video
(
  export PYTHONPATH=$(pwd)

  cd pult
  python3 recieve.py Front &
  python3 recieve.py Bottom &
)