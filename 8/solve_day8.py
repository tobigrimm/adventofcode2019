#!/usr/bin/env python3
import sys
import itertools
# hint: 25 pixels wide and 6 pixels tall.

def grouper(iterable, n, fillvalue=None):
    "grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


class SIF:
    def __init__(self, input, width, height):
        self.width = width
        self.height = height
        self.layers = list(grouper(input, width*height))

    def checksum(self):
        mini = min(self.layers, key=lambda t: t.count('0'))
        return mini.count("1") * mini.count("2")

    def render(self):
        output = []
        # calculate final image
        for pixel in range(self.width * self.height):
            for layer in self.layers:
                if layer[pixel] in ("0","1"):
                    # We only care about black and white pixels, so 2 (transparent ones) get ignored
                    # Also only the first pixel that matches on a layer counts, as the first layers are stacked above the later ones
                    output.append(layer[pixel])
                    break
        return list(grouper(output, self.width))


def main(inputfile):
    with open(inputfile) as inputfilehandle:
        inputlines = inputfilehandle.read().strip()
    sif = SIF(inputlines, 25,6)
    print("Part1: checksum is %s" % sif.checksum())
    #assert (len(inputlines) % 25*6) == 0
    print("Part2: Image:")
    for line in sif.render():
        str = "".join(line)
        str= str.replace("0", " ")
        str = str.replace("1", "▮")
        print(str)

if __name__ == "__main__":
    main(sys.argv[1])

