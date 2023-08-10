from base import network, message
from base.message import ImageLink

def main():
    net = network.Net(1.0/4.0)

    while net.receive():
        file = "simulation/000.png"
        if net.id == "Timer":
            net.send(ImageLink(
                "Bottom",
                file,
                "000.png",
                0
            ))        

if __name__=="__main__":
    main()