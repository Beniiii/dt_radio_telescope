import sys
sys.path.append("Modules/")
from UserInterface.controller import Controller


if __name__ == '__main__':
    c = Controller(simobserve, simanalyze, imhead, exportfits)
    c.run()
