import sys
import logging
from collections import deque
from itertools import chain

_log = logging.getLogger(__name__)
_log.setLevel(logging.WARNING)


def main() -> int:
    n_persons, women_pref, men_pref = _parse_input()
    result = _compute_stable_matching(n_persons, women_pref, men_pref)
    _display_results(result)

    return 0


def _parse_input() -> tuple[int, list[list[int]], list[list[int]]]:
    n_persons = int(input())
    women_pref, men_pref = _parse_preference_lists(n_persons)
    women_pref_inverted = _invert_index(women_pref)
    _log.warning(
        f"Obtained input preferences\n"
        f"{women_pref=}\n{men_pref=}\n{women_pref_inverted=}"
    )
    return n_persons, women_pref_inverted, men_pref


def _parse_preference_lists(n_persons: int) -> tuple[list[list[int]], ...]:
    women_pref= [None] * n_persons
    men_pref = [None] * n_persons

    for _ in range(2 * n_persons):
        # remove spaces for list constructor
        input_ = input()
        raw_input = input_.split(" ")

        person_id, *preferences = raw_input

        if not preferences:
            # empty preference list input
            preferences = []

        # convert into ints
        person_id = int(person_id)
        preferences = _to_int(preferences)

        # first occurrence of an index is a woman
        if not women_pref[person_id - 1]:
            women_pref[person_id - 1] = [person_id, *preferences]
        else:
            men_pref[person_id - 1] = [person_id, *preferences]

    # fill values to have all pref lists to be same length
    """max_length = max(
        [
            len(pref) for pref in chain(women_pref, men_pref)
        ]
    )
    _log.warning(f"Max length is {max_length}")"""

    return women_pref, men_pref


def _to_int(preferences: list[list[str]]) -> list[list[int]]:
    return [int(person) for person in preferences]


def _invert_index(women_pref):
    _log.warning(f"{women_pref=}")
    women_pref_inverted = []
    for woman_pref in women_pref:
        if len(woman_pref) > 1:
            woman_index, *preferences = woman_pref
            inverted_preferences = [woman_index]
            index = 1
            for index, _ in enumerate(preferences):
                if index + 1 in preferences:
                    inverted_preferences.append(
                        preferences.index(index + 1) + 1
                    )
                else:
                    continue
        else:
            # no preferences
            inverted_preferences = woman_pref

        # update
        women_pref_inverted.append(inverted_preferences)

    _log.warning(
        f"Inverting preference list:"
        f"\n\tOriginal: {women_pref}"
        f"\n\tInverted: {women_pref_inverted}"
    )
    return women_pref_inverted


def _compute_stable_matching(
    n_persons: int,
    women_pref: list[list[int]],
    men_pref_original: list[list[int]]
):
    # deque to allow for popleft and appending
    men_left = deque(men_pref_original)

    # updated preferences for men, as to not start from beginning when re-matching pairs
    men_pref_progress = [None] * n_persons

    # at index `i` you find the (index of the) man paired with woman `ì`; initially None
    paired_women = [None] * n_persons

    while men_left:
        # <pseudocode>:
        # get the next man
        # get the next woman in his preference list
        # if she is not paired
        #   create pair
        # if she is paired
        #   check if she prefers this man, if so
        #       remove old pairing
        #       add removed man to men_left
        #       create this new pair
        # else:
        #   put man back in man_left (to try next woman in his list next time around

        man_index, *man_pref = men_left.popleft()
        _log.warning(f":Begin: fetched man {man_index}, preferences {man_pref}")

        # allow for pop_left
        man_pref = deque(man_pref)

        this_woman = man_pref.popleft()
        _log.warning(f"proposing to woman {this_woman}")

        if not paired_women[this_woman - 1]:  # because index == women_id - 1
            paired_women[this_woman - 1] = man_index
            _log.warning(f"Unpaired woman {this_woman}: {paired_women=}")

        elif _prefers_man_over_current_man(women_pref, paired_women, this_woman, man_index):
            # extract currently paired man and his preference list
            current_paired_man = paired_women[this_woman - 1]
            current_paired_man_index_and_pref = men_pref_progress[current_paired_man - 1]
            _log.warning(
                f"-> Woman {this_woman} prefers man {man_index} over "
                f"man {current_paired_man}: switching."
            )

            paired_women[this_woman - 1] = man_index
            men_left.append(current_paired_man_index_and_pref)

        else:
            _log.warning(f"Could not pair man {man_index}: appending to back to list")
            men_left.append([man_index, *man_pref])

        # Update progress
        _log.warning(f"Updating progress with: {[man_index, *man_pref]}")
        men_pref_progress[man_index - 1] = [man_index, *man_pref]
        _log.warning(f"Current progress: {men_pref_progress}")

        _log.warning(f"Current paired women: {paired_women}")
        _log.warning(f"Current men left: {men_left}")
    return paired_women


def _prefers_man_over_current_man(
    women_pref: list[list[int]],
    paired_women: list[int],
    next_woman: int,
    man_index: int,
) -> bool:
    # the first index is the index of the woman: remove this
    this_woman_pref = women_pref[next_woman - 1][1:]
    current_man = paired_women[next_woman - 1]

    # at index `i` we find the rank of man `i`
    result = this_woman_pref[man_index - 1] < this_woman_pref[current_man - 1]
    _log.warning(f"# Proposing to woman with preferences {this_woman_pref}:"
                 f"\nRank of current man {current_man}: "
                 f"{this_woman_pref[current_man - 1]}\nRank of this man {man_index}: "
                 f"{this_woman_pref[man_index - 1]}\n and "
                 f"{this_woman_pref[man_index - 1]} {'' if result else '!'}< {this_woman_pref[current_man - 1]}")

    return result

def _display_results(result: list[int]) -> None:
    for preferred_man in result:
        print(preferred_man)


if __name__ == "__main__":
    sys.exit(main())