# Turn on pult soft with front video
(
  export PYTHONPATH=$(pwd)

  cd pult

  python dualshock.py &
  python debugger.py &
  python map.py &
)