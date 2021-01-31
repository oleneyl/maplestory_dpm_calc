from typing import Dict, List, Optional, Tuple

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
    def get_single_potential(
        refMDF: ExMDF, tier: int, number: int, sto: List[List[Optional[List[ExMDF]]]]
    ) -> Tuple[List[ExMDF], ExMDF]:
        retli = []
        enhancement = ExMDF()
        for i in range(number):
            is_first = 0 if i == 0 else 1
            cand = ExMDF()
            ehc = 0
            for mdfCandidate in sto[tier][is_first]:
                if (
                    i >= 2
                    and retli[0].boss_pdamage > 0
                    and retli[1].boss_pdamage > 0
                    and mdfCandidate.boss_pdamage > 0
                ):
                    continue
                _ehc = (refMDF + enhancement + mdfCandidate).get_damage_factor()
                if _ehc > ehc:
                    cand = mdfCandidate
                    ehc = _ehc
            retli.append(cand.copy())
            enhancement = enhancement + cand
        return retli, enhancement

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
        result = {
            "weapon": [],
            "subweapon": [],
            "emblem": [],
        }
        emblem_count = number // 3
        subweapon_count = (number - emblem_count) // 2
        weapon_count = number - subweapon_count - emblem_count

        potential_list, potential_sum = WeaponPotential.get_single_potential(
            target, tier, emblem_count, WeaponPotential.storageEmblem
        )
        result["emblem"] = potential_list
        target += potential_sum

        potential_list, potential_sum = WeaponPotential.get_single_potential(
            target, tier, subweapon_count, WeaponPotential.storageWeapon
        )
        result["subweapon"] = potential_list
        target += potential_sum

        potential_list, potential_sum = WeaponPotential.get_single_potential(
            target, tier, weapon_count, WeaponPotential.storageWeapon
        )
        result["weapon"] = potential_list

        return result
