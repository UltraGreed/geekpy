# Turn on pult soft with front video
(
  export PYTHONPATH=$(pwd)

  cd pult
  python3 chart.py &
  python3 map.py &
)