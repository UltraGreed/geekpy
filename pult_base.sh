# Turn on pult soft with front video
(
  export PYTHONPATH=$(pwd)

  cd pult
  python dualshock.py &
  python chart.py &
  python map.py &
  python command.py &
)