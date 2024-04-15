# Turn on pult soft with bottom and front video
(
  export PYTHONPATH=$(pwd)

  cd pult

  python imaginarium.py "192.168.88.101" Bottom BottomLine &
)
