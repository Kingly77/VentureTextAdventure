import logging

from rpg_adventure_game import Game
from game.game_world_initializer import setup_game


def main():
    game = Game(*setup_game())
    game.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
