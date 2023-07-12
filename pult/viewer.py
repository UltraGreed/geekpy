import cv2
import sys

from base.network import Net
from base.message import ImageLink


def main(provider):
    net = Net()

    while net.receive():
        if net.id != "ImageLink":
            continue

        link: ImageLink = net.id
        if link.obj != provider:
            continue

        img = cv2.imread(link.path)
        cv2.imshow(provider, img)
        cv2.keyWait(100)
    cv2.destroyAllWindow()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise "Specify the image provider name"
    main(sys.argv[1])
