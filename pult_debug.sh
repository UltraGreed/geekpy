# Turn on pult soft with front video
(
  export PYTHONPATH=$(pwd)

  cd pult
  python command.py &
  python chart.py &
  python map.py &
)