from rpg_adventure_game import Game, setup_game

if __name__ == '__main__':
    game = Game(*setup_game())
    game.run()