import sys
if "--eng" in sys.argv:
    sys.argv.remove("--eng")
print(sys.argv)


def thing(x, y=2):
    print(x, y)

z = {"y": 6}

thing(2, **z)

