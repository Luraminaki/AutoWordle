#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Mon Apr 15 15:25:51 2024

@author: Luraminaki
@rules: https://en.wikipedia.org/wiki/Wordle
'''

#===================================================================================================
import time
import uuid

#pylint: disable=wrong-import-position, wrong-import-order
from modules import helpers, wordle
#pylint: enable=wrong-import-position, wrong-import-order
#===================================================================================================

__version__ = '0.1.0'


def init_lang_launcher(config: dict) -> helpers.LangLauncher:
    return helpers.LangLauncher(config['dict_path'], config['exhaustive'], config['word_lenght'])


def create_game_session(lang_launcher: helpers.LangLauncher, game_mode: int, max_tries: int=6) -> dict[str, dict[str, str | wordle.Wordle | int | list[str]]]:
    sesion_uuid = str(uuid.uuid4())
    return {sesion_uuid: {'game_session': wordle.Wordle(lang_launcher),
                          'game_mode': game_mode,
                          'max_tries': max_tries,
                          'current_tries': 0,
                          'guesses': [],
                          'patterns': [],
                          'created_timestamp': int(time.time()),
                          'last_active_timestamp': int(time.time())}}


def reset_game_session(game_session: dict[str, str | wordle.Wordle | int | list[str]], game_mode: int, max_tries: int=6) -> None:
    game_session['game_session'].reset()
    game_session['game_mode'] = game_mode
    game_session['max_tries'] = max_tries
    game_session['current_tries'] = 0
    game_session['guesses'] = []
    game_session['patterns'] = []
    game_session['last_active_timestamp'] = int(time.time())


def get_session_stats(game_session: dict[str, str | wordle.Wordle | int | list[str]]) -> dict[str, str | int | list[str]]:
    return {'game_mode': game_session['game_mode'],
            'max_tries': game_session['max_tries'],
            'current_tries': game_session['current_tries'],
            'guesses': game_session['guesses'],
            'patterns': game_session['patterns'],
            'created_timestamp': game_session['created_timestamp'],
            'last_active_timestamp': game_session['last_active_timestamp']}


def get_word_to_guess(game_session: dict[str, str | wordle.Wordle | int | list[str]]) -> str:
    return ''.join(chr(ord_letter) for ord_letter in game_session['game_session'].word)


def get_guess_stats(game_session: dict[str, str | wordle.Wordle | int | list[str]], word: str, pattern: str) -> dict | dict[str, list[tuple[tuple[int], float]] | set[int] | dict[str, int] | list[list[tuple[tuple[int], float]]] | float]:
    if game_session['game_mode'] == helpers.GAME_MODE_PLAY:
        return {}

    pool = game_session['game_session'].submit_guess_and_pattern(word, pattern)
    game_session['game_session'].letter_extractor = helpers.update_letter_extractor(game_session['game_session'].letter_extractor,
                                                                                    helpers.build_letter_extractor(tuple(ord(letter) for letter in word),
                                                                                                                   tuple(int(p) for p in pattern)))
    pool_letters, pool_letters_dupes = helpers.gather_pool_letters(pool)
    suggestions = helpers.build_suggestion(game_session['game_session'].language_launcher.words_information,
                                           pool_letters,
                                           pool_letters_dupes,
                                           game_session['game_session'].letter_extractor)

    if game_session['game_mode'] == helpers.GAME_MODE_SOLVE:
        game_session['guesses'].append(word)
        game_session['patterns'].append(helpers.pattern_to_emoji(pattern))
        game_session['last_active_timestamp'] = int(time.time())

    return {'pool_words': pool,
            'pool_letters': pool_letters,
            'pool_letters_dupes': pool_letters_dupes,
            'elimination_suggestions': suggestions,
            'information': game_session['game_session'].information}


def submit_guess(game_session: dict[str, str | wordle.Wordle | int | list[str]], word: str) -> tuple | tuple[int] | None:
    if game_session['current_tries'] >= game_session['max_tries']:
        return None

    pattern = game_session['game_session'].submit_guess((ord(letter) for letter in word))

    if not pattern or pattern is None:
        return None

    game_session['guesses'].append(word)
    game_session['patterns'].append(helpers.pattern_to_emoji(pattern))
    game_session['current_tries'] = game_session['current_tries'] + 1
    game_session['last_active_timestamp'] = int(time.time())

    return pattern
