# Turn on robot software
(
  export PYTHONPATH=$(pwd)

#  python robot/physoptic.py &
  python3 robot/zed.py bottom 24827734 True &
  python3 robot/zed.py front 16909428 False &
)
