from game import Game


# Create a new Game instance
# and start the loop
def main():
    g = Game()
    g.loop()

# Check if this module is being imported or if
# it is being run.  If it is being run, call the
# main function.
if __name__ == '__main__':
    main()
