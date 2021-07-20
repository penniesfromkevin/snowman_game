#!/usr/bin/env python3
"""Do you want to build a snowman?
"""
import argparse
import os
import random
import sys

import pygame


SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FRAME_RATE = 30

IMAGE_PATH = 'images'
SOUND_PATH = 'sounds'

GUTTER_LEFT = 60
GUTTER_RIGHT = SCREEN_WIDTH - GUTTER_LEFT
GUTTER_BOTTOM = 70

SPEED_MIN = 6
SPEED_MAX = 16
SPEED_BUMP = 3  # How many snowmen must be built to increase speed by 1

SNOWMEN_MAX = 2  # How many completed snowmen to keep on screen at one time
CLUTTER = 2  # How many extra "legs" that can be on the screen at one time
MISSES_MAX = 10

POINTS = 50
PIECES = {
    'heads': [
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'head-1',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.9,
                    },
                ],
            },
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'head-2',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.9,
                    },
                ],
            },
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'head-3',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.9,
                    },
                ],
            },
        ],
    'arms': [
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'torso-1',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.8,
                    },
                {
                    'name': 'arms-1',
                    'x_offset': -46,
                    'y_offset': -40,
                    'ratio': 0.8,
                    },
                ],
            },
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'torso-1',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.8,
                    },
                {
                    'name': 'arms-2',
                    'x_offset': -45,
                    'y_offset': -55,
                    'ratio': 0.8,
                    },
                ],
            },
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'torso-2',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.8,
                    },
                {
                    'name': 'arms-3',
                    'x_offset': -78,
                    'y_offset': -55,
                    'ratio': 0.8,
                    },
                ],
            },
        ],
    'legs': [
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'legs-1',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.9,
                    },
                ],
            },
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'legs-2',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.9,
                    },
                ],
            },
        {
            'images': [
                {  # first one is always the hit-box image
                    'name': 'legs-3',
                    'x_offset': 0,
                    'y_offset': 0,
                    'ratio': 0.9,
                    },
                ],
            },
        ],
    }
SOUND_FILES = (  # name, file_name
    'block_break',
    'coin',
    'dont_you_dare',
    'pause',
    )
BACKGROUNDS = (
    'snowy_bench',
    'anna_elsa',
    'elsa',
    )


class ImageStore():
    """Image store.
    """
    def __init__(self, path, ext='png'):
        """Initialize the store.

        Args:
            path: Path to image files.
            ext: File extension image files.
        """
        self._store = {}
        self._path = path
        self._ext = ext

    def get(self, name):
        """Get image object.

        If the image does not exist in the store, this will also try to
        add it first, but it is better to pre-add images as there is
        less delay.

        Args:
            name: Name of image to get.

        Returns:
            Image object, or None if object could not be found.
        """
        if name in self._store:
            image = self._store[name]
        else:
            image = self.add(name)
        return image

    def add(self, name):
        """Add image object to the store.

        Args:
            name: Name of image to add.

        Returns:
            Image object, or None if object could not be loaded.
        """
        image_path = os.path.join(self._path, '%s.%s' % (name, self._ext))
        image_object = pygame.image.load(image_path).convert_alpha()
        self._store[name] = image_object
        return image_object


class SoundStore():
    """Sound store.
    """
    def __init__(self, path, ext='wav'):
        """Initialize the store.

        Args:
            path: Path to sound files.
            ext: File extension of sound files.
        """
        self._store = {}
        self._path = path
        self._ext = ext

    def play(self, name):
        """Play sound object.

        If the sound does not exist in the store, this will also try to
        add it first, but it is better to pre-add sounds as there is
        less delay.

        Args:
            name: Name of sound to play.
        """
        if not name in self._store:
            self.add(name)
        self._store[name].play()

    def add(self, name):
        """Add sound object to the store.

        Args:
            name: Name of sound to add.

        Returns:
            sound object, or None if object could not be loaded.
        """
        sound_path = os.path.join(self._path, '%s.%s' % (name, self._ext))
        sound_object = pygame.mixer.Sound(sound_path)
        self._store[name] = sound_object
        return sound_object


class Piece(pygame.sprite.Sprite):
    """Player class.
    """
    def __init__(self, pieces_possible, speed=SPEED_MIN):
        """Initialize player.

        Args:
            pieces: List of possible piece types
        """
        super().__init__()
        self.piece = random.choice(pieces_possible)
        piece = random.choice(PIECES[self.piece])
        if speed > SPEED_MAX:
            speed = SPEED_MAX
        self.speed = speed
        self.images = piece['images']
        self.hit_ratio = self.images[0]['ratio']
        self.image = IMAGES.get(self.images[0]['name'])
        self.width, self.height = self.image.get_size()

        self.x_inc = 0
        self.y_inc = speed

        self.x_pos = random.randint(GUTTER_LEFT, GUTTER_RIGHT)
        self.y_pos = -self.height // 2

        # Fetch the rectangle object that has the dimensions of the image
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.rect.center = self.x_pos, self.y_pos

        if self.piece == 'legs':
            self.limit = SCREEN_HEIGHT - random.randint(self.height // 2,
                                                        self.height)
        else:
            self.limit = SCREEN_HEIGHT - GUTTER_BOTTOM  # self.height
        self.status = None  # 'stuck', 'gone'

    def get_input(self):
        """Get input from the user (keyboard)
        """
        game_over = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                elif event.key == pygame.K_p:
                    pause_game()
                elif event.key in (pygame.K_SPACE, pygame.K_DOWN):
                    self.y_inc = SPEED_MAX
                elif event.key == pygame.K_LEFT:
                    self.direction = 'left'
                    self.x_inc = -self.speed * 2
                elif event.key == pygame.K_RIGHT:
                    self.direction = 'right'
                    self.x_inc = self.speed * 2

            elif event.type == pygame.KEYUP:
                if self.x_inc < 0 and event.key == pygame.K_LEFT:
                    self.x_inc = 0
                elif self.x_inc > 0 and event.key == pygame.K_RIGHT:
                    self.x_inc = 0
                elif event.key in (pygame.K_SPACE, pygame.K_DOWN):
                    self.y_inc = self.speed
        return game_over

    def display(self):
        """Draw the character image on the game board.
        """
        rect_new = self.image.get_rect(center=(self.x_pos, self.y_pos))
        for layer in self.images:
            image = IMAGES.get(layer['name'])
            x_pos = rect_new[0] + layer['x_offset']
            y_pos = rect_new[1] + layer['y_offset']
            SCREEN.blit(image, (x_pos, y_pos))

    def update(self):
        """Update Player.
        """
        if self.x_pos < GUTTER_LEFT:
            self.x_pos = GUTTER_LEFT
        elif self.x_pos > GUTTER_RIGHT:
            self.x_pos = GUTTER_RIGHT
        if self.piece in PIECES:
            slow_zone = (4 - list(PIECES.keys()).index(self.piece)) * GUTTER_BOTTOM
            if self.y_inc and self.y_pos > SCREEN_HEIGHT - slow_zone:
                self.y_inc = self.speed
        self.x_pos += self.x_inc
        self.y_pos += self.y_inc
        self.rect.center = (self.x_pos, self.y_pos)
        self.display()


def parse_args():
    """Parse user arguments and return as parser object.

    Returns:
        Parser object with arguments as attributes.
    """
    parser = argparse.ArgumentParser(description='Test basic functionality.')
    parser.add_argument(
        '-c', '--centipede', action='store_true',
        help='Enable centipede mode (multiple arms).')
    parser.add_argument(
        '-i', '--infinite', action='store_true',
        help='Enable infinite mode (misses do not count).')
    parser.add_argument(
        '-s', '--speed', action='store_true',
        help='Enable speed increases.')
    args = parser.parse_args()
    return args


def show_stats(score, snowmen, misses):
    """Show stats
    """
    stats = GAME_FONT.render(
        '%s: %06d (%s)' % (snowmen, score, misses), True, (0, 0, 0))
    SCREEN.blit(stats, (0, 0))


def show_text(text, timer=-1, size=48, color=(240, 240, 0), py_key='any'):
    """Display text on screen for a given amount of time
    """
    text_pic = GAME_FONT.render(text, 1, color)
    text_width, text_height = text_pic.get_size()
    text_position = ((SCREEN_WIDTH - text_width) // 2,
                     (SCREEN_HEIGHT - text_height) // 2)
    SCREEN.blit(text_pic, text_position)
    pygame.display.flip()
    wait_for_keypress(py_key, timer)


def wait_for_keypress(py_key='any', timer=-1):
    """Waits for a keypress.

    Args:
        py_key: Pygame constant keyboard key referemce.
        timer: Amount of time to wait, in seconds.  -1 is infinite.
    """
    pygame.event.clear()
    while timer != 0:
        pygame.time.wait(1000)
        CLOCK.tick(10)
        if timer > 0:
            timer -= 1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if py_key in ('any', event.key):
                    timer = 0


def pause_game():
    """Pause the game until the pause key is pressed again.
    """
    SOUNDS.play('pause')
    show_text('Paused', py_key=pygame.K_p)


def end_game():
    """End the game.
    """
    pygame.mixer.music.stop()
    SOUNDS.play('dont_you_dare')
    show_text('Game Over!')


def main():
    """The game itself.
    """
    exit_code = 0
    # To play music, simply select and play
    pygame.mixer.music.load('sounds/snowman.wav')
    pygame.mixer.music.play(-1, 0.0)
    for sound in SOUND_FILES:
        SOUNDS.add(sound)

    pieces = pygame.sprite.Group()
    player = None

    score = misses = 0
    current = {
        'heads': 0,
        'arms': 0,
        'legs': 0,
        'snowmen': 0,
        }
    connected = {}  # All snowman pieces that have been connected
    heads = []  # How many completed heads there are

    game_over = False
    while not game_over:
        SCREEN.fill((240, 240, 255))
        background = BACKGROUNDS[(current['snowmen']//5) % len(BACKGROUNDS)]
        SCREEN.blit(IMAGES.get('background/%s' % background), (0, 0))

        if not player:
            if ARGS.centipede:
                piece_types = ['arms'] * 2
            else:
                piece_types = []
            if current['legs'] - current['heads'] < CLUTTER:
                piece_types.append('legs')

            if ARGS.centipede:
                if current['legs'] > current['heads']:
                    times = current['legs'] - current['heads']
                    piece_types.extend(['heads'] * times)
                if current['legs'] == current['heads']:
                    piece_types.extend(['legs'] * 2)
            else:
                if current['legs'] > current['arms']:
                    times = current['legs'] - current['arms']
                    piece_types.extend(['arms'] * times)
                if current['arms'] > current['heads']:
                    times = current['arms'] - current['heads']
                    piece_types.extend(['heads'] * times)
            if ARGS.speed:
                speed = SPEED_MIN + current['snowmen'] // SPEED_BUMP
            else:
                speed = SPEED_MIN
            player = Piece(piece_types, speed)
            current[player.piece] += 1

        game_over = player.get_input()

        hits = pygame.sprite.spritecollide(
            player, pieces, False,
            pygame.sprite.collide_circle_ratio(player.hit_ratio))
        for piece in hits:
            if (
                    (player.piece == 'heads' and piece.piece == 'arms')
                    or (player.piece == 'arms' and piece.piece == 'legs')
                    or (ARGS.centipede
                        and player.piece == 'arms' and piece.piece == 'arms')
                ):
                SOUNDS.play('coin')
                player.status = 'stuck'
                piece.piece = 'connected'
                connected[player] = piece
                score += POINTS
                break
        pieces.update()
        player.update()
        if player.status == 'stuck' or (
                player.piece == 'legs' and player.y_pos > player.limit):
            player.x_inc = player.y_inc = 0
            if player.piece == 'legs':
                connected[player] = None
                pieces.add(player)
            elif player.piece == 'heads':
                heads.append(player)
                pieces.add(player)
                current['snowmen'] += 1
                if len(heads) > SNOWMEN_MAX:
                    head = heads[0]
                    heads.remove(head)
                    while head:
                        head, head_old = connected[head], head
                        pieces.remove(head_old)
            else:
                pieces.add(player)
            player = None
        elif player.piece != 'legs' and player.y_pos > player.limit:
            SOUNDS.play('block_break')
            current[player.piece] -= 1
            misses += 1
            score -= POINTS
            player = None

        if not ARGS.infinite and misses >= MISSES_MAX:
            game_over = True
        show_stats(score, current['snowmen'], misses)
        CLOCK.tick(FRAME_RATE)
        pygame.display.flip()

    print(current)
    end_game()
    return exit_code


if __name__ == '__main__':
    ARGS = parse_args()
    pygame.init()
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)
    CLOCK = pygame.time.Clock()
    GAME_FONT = pygame.font.Font(None, 48)
    IMAGES = ImageStore(IMAGE_PATH, 'png')
    SOUNDS = SoundStore(SOUND_PATH, 'wav')
    EXIT_STATUS = main()
    pygame.quit()
    sys.exit(EXIT_STATUS)
