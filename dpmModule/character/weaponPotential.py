from typing import Dict, List, Optional
from itertools import filterfalse, product, combinations_with_replacement
from functools import reduce

from dpmModule.kernel.core import ExtendedCharacterModifier as ExMDF


class WeaponPotential:
    storageWeapon: List[List[Optional[List[ExMDF]]]] = [
        [None],
        [None],
        [
            [ExMDF(pdamage=6), ExMDF(patt=6), ExMDF(armor_ignore=15)],
            [ExMDF(pdamage=3), ExMDF(att=3)],
        ],
        [
            [ExMDF(boss_pdamage=30), ExMDF(patt=9), ExMDF(armor_ignore=30)],
            [ExMDF(boss_pdamage=20), ExMDF(patt=6), ExMDF(armor_ignore=20)],
        ],
        [
            [ExMDF(boss_pdamage=40), ExMDF(patt=12), ExMDF(armor_ignore=40)],
            [ExMDF(boss_pdamage=30), ExMDF(patt=9), ExMDF(armor_ignore=30)],
        ],
    ]

    storageEmblem: List[List[Optional[List[ExMDF]]]] = [
        [None],
        [None],
        [
            [ExMDF(pdamage=6), ExMDF(patt=6), ExMDF(armor_ignore=15)],
            [ExMDF(pdamage=3), ExMDF(patt=3)],
        ],
        [
            [ExMDF(patt=9), ExMDF(armor_ignore=30)],
            [ExMDF(patt=6), ExMDF(armor_ignore=20)],
        ],
        [
            [ExMDF(patt=12), ExMDF(armor_ignore=40)],
            [ExMDF(patt=9), ExMDF(armor_ignore=30)],
        ],
    ]

    @staticmethod
    def get_potential_list(
        tier: int, number: int, sto: List[List[Optional[List[ExMDF]]]]
    ) -> List[ExMDF]:
        if number <= 0:
            return []
        first_line = sto[tier][0]
        if number == 1:
            return first_line

        other_lines = combinations_with_replacement(sto[tier][1], number - 1)
        combinations = [
            [first, *other] for first, other in list(product(first_line, other_lines))
        ]
        combinations = filterfalse(
            lambda li: all([x.boss_pdamage > 0 for x in li]), combinations
        )
        combinations = filterfalse(
            lambda li: all([x.armor_ignore > 0 for x in li]), combinations
        )

        return [
            {"sum": reduce(lambda x, y: x + y, li), "list": li} for li in combinations
        ]

    @staticmethod
    def get_weapon_pontential(
        mdf: ExMDF, tier: int, number: int
    ) -> Dict[str, List[ExMDF]]:
        """get_weapon_pontential(mdf, tier, number) : return Appropriate weapon potentials.
        This function will return list - of - potential candidate.

        mdf : Base modifier that will refered for optimizing weapon potential.
        tier : Tier of potential. Tier must be 2(Epic), 3(Unique) or 4(Regendry)
        number : Effective option #. number must be in range 0 ~ 9.
        """
        if number < 0 or number > 9:
            raise TypeError("number must be in range 0 ~ 9")
        if tier < 1 or tier > 5:
            raise TypeError("Tier must be 2, 3 or 4.")

        target = mdf.copy()
        emblem_count = number // 3
        subweapon_count = (number - emblem_count) // 2
        weapon_count = number - subweapon_count - emblem_count

        emblem_cand = WeaponPotential.get_potential_list(
            tier, emblem_count, WeaponPotential.storageEmblem
        )
        subweapon_cand = WeaponPotential.get_potential_list(
            tier, subweapon_count, WeaponPotential.storageWeapon
        )
        weapon_cand = WeaponPotential.get_potential_list(
            tier, weapon_count, WeaponPotential.storageWeapon
        )

        combinations = product(emblem_cand, subweapon_cand, weapon_cand)
        best = max(
            combinations,
            key=lambda x: (
                target + x[0]["sum"] + x[1]["sum"] + x[2]["sum"]
            ).get_damage_factor(),
        )

        return {
            "emblem": best[0]["list"],
            "subweapon": best[1]["list"],
            "weapon": best[2]["list"],
        }
