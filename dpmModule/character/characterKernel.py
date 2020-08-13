from ..kernel.core import CharacterModifier, InformedCharacterModifier
from ..kernel.core import ExtendedCharacterModifier as EXMDF
from ..item import ItemKernel as ik
from ..item.ItemKernel import Item
from ..status.ability import Ability_tool, Ability_grade
from ..kernel.graph import GlobalOperation, initialize_global_properties, _unsafe_access_global_storage
from ..kernel import policy
from functools import reduce

MDF = CharacterModifier
'''Clas AbstractCharacter : Basic template for build specific User. User is such object that contains
- Items
- Buff Skill Wrappers
- Damage Skill Wrappers
- Some else Modifiers.
'''

class AbstractCharacter():
    #TODO : get/set :: use decorator? could be...
    def __init__(self, modifierlist = [], level = 230, buff_rem = 0, summonRemain = 0, cooltimeReduce = 4):
        #Initialize Items
        self.level = level
        self.basic_character_modifier = CharacterModifier(stat_main = 18 + level * 5, stat_sub = 4, crit = 5)
        self.potential_modifier = CharacterModifier()
        self.itemlist = {}
        for md in modifierlist:
            self.basic_character_modifier = self.basic_character_modifier + md
        self.static_character_modifier = self.basic_character_modifier.copy()

        self.buff_rem = buff_rem
        self.summonRemain = summonRemain
        self.cooltimeReduce = cooltimeReduce
        
        self._property_ignorance = 0
        
        self.about = ""
        self.add_summary("레벨 %d" % level)
        
        self._modifier_cache = None

    def unsafe_change_level(self, level):
        level_delta = level - self.level
        self.add_summary(f"레벨 강제 변경 : {self.level} -> {level}")
        self.level = level
        self.basic_character_modifier += CharacterModifier(stat_main = level_delta * 5)        

    def add_summary(self, txt):
        self.about += "\n" + txt
    
    def add_property_ignorance(self, val):
        self._property_ignorance += val
        
    def get_property_ignorance(self):
        return self._property_ignorance
        
    def get_property_ignorance_modifier(self):
        return MDF(pdamage_indep = self.get_property_ignorance()) + MDF(pdamage_indep = -50)

    def apply_modifiers(self, li):
        '''Be careful! This function PERMANENTLY change character's property.
        You must sure that this function call is appropriate.
        '''
        for mdf in li:
            self.static_character_modifier += mdf
            self.basic_character_modifier += mdf
    
    def generate_modifier_cache(self):
        self._modifier_cache = self.get_static_modifier() + self.get_potential_modifier() + self.get_property_ignorance_modifier()
    
    def get_modifier(self):
        if self._modifier_cache is None:
            return self.get_static_modifier() + self.get_potential_modifier() + self.get_property_ignorance_modifier()
        else:
            return self._modifier_cache
    
    def get_buffed_modifier(self):
        mod = self.get_static_modifier() + self.get_potential_modifier() + self.get_property_ignorance_modifier()
        return mod
        
    def get_static_modifier(self):
        return self.static_character_modifier.copy()
        
    def get_potential_modifier(self):
        return self.potential_modifier.copy()
        
    def remove_item_modifier(self, item):
        basic, ptnl = item.get_modifier()
        self.potential_modifier = self.potential_modifier - ptnl
        self.static_character_modifier = self.static_character_modifier - basic

    def add_item_modifier(self, item):
        basic, ptnl = item.get_modifier()
        self.potential_modifier = self.potential_modifier + ptnl
        self.static_character_modifier = self.static_character_modifier + basic        
        
    def add_item_with_id(self, _id, item):
        if _id in self.itemlist:
            self.remove_item_modifier(self.itemlist[_id])
        self.itemlist[_id] = item            
        self.add_item_modifier(self.itemlist[_id])
        
    def add_items_with_id(self, _dict):
        for _id in _dict:
            self.add_item_with_id(_id, _dict[_id])



class JobGenerator():
    '''class JobGenerator : Template for job generator.
    JobGenerator Is Abstract Class : yuo mus re-Implement this class in usage.AbstractSkill
    
    - Functions that you must re - implement
    
    .generate(chtr : ck.AbstractCharacter, combat : bool = False , vlevel : int = 0, vEnhance : list = [0,0,0]) : 
        This function generate given chtr's graph and returns schedule.
    
    .apply_complex_options(self, chtr) : apply other setting values etc ) 
    
    - Values that you must re-  implement
    
    .buffrem : Boolean, option that this character will use bufrem property in union, card, etc.
    .jobtype : str, int, dex, luk. 사용하는 스탯의 종류를 명시해야 합니다. You must specify which type of stat this job uses.
    .vEnhanceNum : 5차 강화 스킬의 총 개수입니다.
    .vSkillNum : 5차 스킬의 총 개수입니다.
    
    from . import globalSkill
    self.preEmptiveSkills = 2
    globalSkill.maple_heros(chtr.level), globalSkill.useful_sharp_eyes(), globalSkill.useful_wind_booster()
    globalSkill.soul_contract()
    
    미하일까지..
    '''
    def __init__(self, vEhc = None):
        self.buffrem = False
        self.vEnhanceNum = 10
        self.vSkillNum = 3 + 3
        self.preEmptiveSkills = 0
        self.jobname = None
        self.jobtype = "str" #재상속 하도록 명시할 필요가 있음.
        self._passive_skill_list = [] #각 생성기가 자동으로 그래프 생성 시점에서 연산합니다.
        self.constructedSchedule = None
        self.combat = False
        self.chtr = None
        self.ability_list = Ability_tool.get_ability_set(None, None, None)
        self._use_critical_reinforce = False
            
    def apply_complex_options(self, chtr):
        return

    def get_ruleset(self):
        return

    def get_predefined_rules(self, rule_type):
        ruleset = self.get_ruleset()
        if ruleset is None:
            return []
        else:
            return ruleset.get_rules(rule_type)

    def get_total_modifier_optimization_hint(self):
        return self.get_modifier_optimization_hint() + CharacterModifier(armor_ignore = 20)

    def get_modifier_optimization_hint(self):
        '''
        Modifier optimization에서 사용될 Modifier Hint를 기입합니다.
        
        '''
        return CharacterModifier()
    
    def apply_specific_schedule(self, graph):
        return
    
    def build(self, chtr, combat = False, storage_handler=None):
        initialize_global_properties()

        base_element, all_elements = self.generate(self.vEhc, chtr, combat = combat)

        GlobalOperation.assign_storage()
        GlobalOperation.attach_namespace()
        GlobalOperation.save_storage()
        if storage_handler is not None:
            storage_handler(_unsafe_access_global_storage())
        GlobalOperation.convert_to_static()

        collection = GlobalOperation.export_collection()

        graph = policy.StorageLinkedGraph(base_element,
            collection.get_storage(), accessible_elements=all_elements)
        graph.build(chtr)
        
        return graph
    
    def generate(self, vEhc, chtr : AbstractCharacter, combat : bool = False):
        raise NotImplementedError
    
    def build_passive_skill_list(self):
        self._passive_skill_list = self.get_passive_skill_list()
        return

    def get_passive_skill_list(self):
        raise NotImplementedError("You must fill get_passive_skill_list function.")
        return 
    
    def build_not_implied_skill_list(self):
        notImpliedBuffList = self.get_not_implied_skill_list()
        self._passive_skill_list += notImpliedBuffList
        return
    
    def get_not_implied_skill_list(self):
        raise NotImplementedError('You must fill get_not_implied_skill_list function.')
        return []
    
    def get_passive_skill_modifier(self):
        passive_modifier = CharacterModifier()
        for _mdf in self._passive_skill_list:
            passive_modifier += _mdf        
        return passive_modifier
    
    def package_bare(self, chtr, v_builder, useFullCore = False, vEnhanceGenerateFlag = None):
        self.vEhc = v_builder.build_enhancer(chtr, self)
        self.chtr = chtr
        
        # Since given character specification already imply both option; ignore these two.

        self.build_not_implied_skill_list()
        chtr.apply_modifiers([self.get_passive_skill_modifier()])
        
        graph = self.build(chtr)
        graph.set_v_enhancer(self.vEhc)
        
        return graph
        
    def package(self, chtr, v_builder, combat : bool = False, 
                    vlevel : int = 0,
                    ulevel : int = 4000,
                    weaponstat = [3,6],
                    log = False,
                    vEnhanceGenerateFlag = None,
                    ability_grade = Ability_grade(4,1),
                    storage_handler=None ):
        '''Packaging function
        '''
        self.vEhc = v_builder.build_enhancer(chtr, self)
        self.combat = combat
        self.chtr = chtr
        
        self.build_passive_skill_list()
        self.build_not_implied_skill_list()
        
        #어빌리티 적용
        adjusted_ability = Ability_tool.adjusted_ability(ability_grade, self.ability_list[0], self.ability_list[1], self.ability_list[2])
        chtr.apply_modifiers([self.get_passive_skill_modifier()])
        chtr.apply_modifiers([adjusted_ability])
        
        #성향 적용
        personality = Personality.get_personality(100)
        chtr.apply_modifiers([personality])
        
        self.chtr.buff_rem = self.chtr.buff_rem + adjusted_ability.buff_rem + personality.buff_rem
        self.chtr.add_property_ignorance(personality.prop_ignore)
        
        graph = self.build(chtr, combat = combat, storage_handler=storage_handler)

        def log_modifier(modifier, name):
            if log:
                print("\n---" + name + "---")
                print(modifier.log())

        def log_character(chtr):
            if log:
                print("\n---basic CHTR---")
                print(chtr.get_modifier().log())

        def log_buffed_character(chtr):
            if log:
                print("\n---final---")
                buffed = graph.get_default_buff_modifier() + chtr.get_modifier()
                print(buffed.log())

        # refMDF는 상시 - 시전되는 버프에 관련된 정보를 담고 있습니다.
        def get_reference_modifier(chtr):
            return graph.get_default_buff_modifier() + chtr.get_modifier() + self.get_total_modifier_optimization_hint()

        log_character(chtr)
        log_buffed_character(chtr)

        # 무기 소울
        refMDF = get_reference_modifier(chtr)
        if refMDF.crit < 88:
            weapon_soul_modifier = CharacterModifier(crit = 12)
        else:
            weapon_soul_modifier = CharacterModifier(patt = 3)
        log_modifier(weapon_soul_modifier, "weapon soul")
        chtr.apply_modifiers([weapon_soul_modifier])
        log_buffed_character(chtr)
        
        # 도핑
        doping = Doping.get_full_doping()
        log_modifier(doping, "doping")
        chtr.apply_modifiers([doping])
        log_buffed_character(chtr)

        # 유니온 공격대원
        unionCard = Card.get_card(self.jobtype, ulevel, True)[0]
        log_modifier(unionCard, "union card")
        chtr.apply_modifiers([unionCard])
        self.chtr.buff_rem = self.chtr.buff_rem + 20 #메카닉 벞지 적용
        log_buffed_character(chtr)

        # 링크 스킬
        refMDF = get_reference_modifier(chtr)
        link = LinkSkill.get_link_skill_modifier(refMDF, self.jobname)
        log_modifier(link, "link")
        chtr.apply_modifiers([link])
        log_buffed_character(chtr)

        # 하이퍼 스탯
        refMDF = get_reference_modifier(chtr)
        hyperstat = HyperStat.get_hyper_modifier(refMDF, chtr.level, critical_reinforce = self._use_critical_reinforce)
        log_modifier(hyperstat, "hyper stat")
        chtr.apply_modifiers([hyperstat])
        log_buffed_character(chtr)

        # 유니온 점령
        refMDF = get_reference_modifier(chtr)
        union, unionBuffRem = Union.get_union(refMDF, ulevel, buffrem = self.buffrem, critical_reinforce = self._use_critical_reinforce)
        log_modifier(union, "union")
        chtr.apply_modifiers([union])
        chtr.buff_rem += unionBuffRem #유니온 벞지 적용
        log_buffed_character(chtr)

        # 무기류 잠재능력
        refMDF = get_reference_modifier(chtr)
        weaponli = WeaponPotential.get_weapon_pontential(refMDF, weaponstat[0], weaponstat[1])
        for index, wp in enumerate(weaponli):
            log_modifier(wp, "weapon " + str(index + 1))
        chtr.set_weapon_potential(weaponli)
        log_buffed_character(chtr)
        
        ## 기타 옵션 적용
        self.apply_complex_options(chtr)
        #그래프를 다시 빌드합니다.
        graph = self.build(chtr, combat = combat, storage_handler=storage_handler)
        graph.set_v_enhancer(self.vEhc)

        log_character(chtr)
        log_buffed_character(chtr)
        
        return graph


class ItemedCharacter(AbstractCharacter):
    def __init__(self, modifierlist = [], level = 230):
        super(ItemedCharacter, self).__init__(modifierlist, level)
        
        #6 items for armor
        self.itemlist["head"] = Item()
        self.itemlist["glove"] = Item()
        self.itemlist["top"] = Item()
        self.itemlist["bottom"] =Item()
        self.itemlist["shoes"] = Item()
        self.itemlist["cloak"] = Item()

        #13 items for accessory
        
        self.itemlist["eye"] = Item()
        self.itemlist["face"] = Item()
        self.itemlist["ear"] = Item()
        self.itemlist["belt"] = Item()
        self.itemlist["ring1"] = Item()
        self.itemlist["ring2"] = Item()
        self.itemlist["ring3"] = Item()
        self.itemlist["ring4"] = Item()
        self.itemlist["shoulder"] = Item()
        self.itemlist["pendant1"] = Item()
        self.itemlist["pendant2"] = Item()
        self.itemlist["pocket"] = Item()
        self.itemlist["badge"] = Item()
        
        # 3 items for weapon
        
        self.itemlist["weapon"] = Item()
        self.itemlist["subweapon"] = Item()
        self.itemlist["emblem"] = Item()
        
        #2 items for else
        
        self.itemlist["medal"] = Item()
        self.itemlist["heart"] = Item()
        self.itemlist["title"] = Item()
        self.itemlist["pet"] = Item()
        
    def set_weapon_potential(self, li):
        if len(li) > 9: 
            raise TypeError("무기 잠재능력은 최대 9개입니다.")
        itemOrder = ["weapon", "subweapon", "emblem"]    
        
        for i in range(3):
            ptnl = CharacterModifier()
            for j in range((len(li) - i - 1) // 3):
                ptnl  = ptnl + li[i+j*3]
                
            item = self.itemlist[itemOrder[i]].copy()
            item.set_potential(ptnl)
            self.add_item_with_id(itemOrder[i], item)
            
class Union():
    peoples = [0, 9, 10, 11, 12, 13, 
                18, 19, 20, 21, 22,
                27, 28, 29, 30, 31,
                36, 37, 38, 39, 40]
    
    maxSlot = [6,13,21,30,40]
    #hierarchy : 공 - 주스텟 - 보공 - 방무 - 크확 - 크뎀 - 벞지
    #links : 연결가능한 경로 제공.
    #기본적으로 보공과 방무를 연결합니다. 6칸씩 버림.(12칸)

    initial_state = [6,6,1,1,0,0,0]
    initial_state_with_buff_rem = [6,5,1,0,0,0,6]

    def __init__(self, mdf, buff_rem, slots, ulevel):
        self.mdf = mdf
        self.buff_rem = buff_rem
        self.slots = slots
        self.ulevel = ulevel

    def as_dict(self):
        return {"mdf" : self.mdf.as_dict(),
                "buffrem" : self.buff_rem,
                "slots" : self.slots,
                "ulevel" : self.ulevel}

    @staticmethod
    def get_apt_slot(ulevel, maplem = True):
        '''get_apt_slot(ulevel, maplem = True) : Return Apt union slot.
        유니온 캐릭터는 2000레벨부터 300레벨당 200짜리가 1개씩 증가합니다. 기본적으로 하나를 가집니다.
        점령 가능한 개수는 아래와 같습니다.
        '''
        numOf200 = min((ulevel - 2000) // 300 + 1, Union.peoples[ulevel//500])
        _else = (ulevel - numOf200 * 200) // 140
        return numOf200 * 4 + min(_else, Union.peoples[ulevel//500] - numOf200) * 3 + (maplem * 3)
    
    #TODO :: -1을 리턴하지 않도록,
    @staticmethod
    def get_union_object(mdf, ulevel, buffrem = False, asIndex = False, slot = None):
        mdf, buffrem = Union.get_union(mdf, ulevel, buffrem = buffrem, asIndex = asIndex, slot = slot)
        return Union(mdf, buffrem, -1, ulevel)
        
    @staticmethod
    def get_union(mdf, ulevel, buffrem = False, asIndex = False, slot = None, critical_reinforce = False):
        '''get_union(mdf, ulevel, buffrem = False, asIndex = False) : return optimized MDF value.
        return value : (MDF, buffremain) tuple.
        '''
        if slot is None:
            slots = Union.get_apt_slot(ulevel)
        else:
            slots = slot
        maxvalue = Union.maxSlot[min((ulevel-2000) // 1000, 4)]
        
        if buffrem:
            state = [i for i in Union.initial_state_with_buff_rem]
            while state[6] < maxvalue and slots > 0:
                state[6] += 1
                slots -= 1
        else:
            state = [i for i in Union.initial_state]
        
        while slots > 0:
            idx = -1
            eff = 0
            for i in range(6):
                _state = [j for j in state]
                _state[i] = min(_state[i] + 1, maxvalue)
                _eff = Union._get_union_increment_from_state(mdf, _state, critical_reinforce = critical_reinforce)
                if _eff > eff:
                    idx = i
                    eff = _eff
            if idx == -1:
                if (Union._get_union_from_state(state) + mdf).armor_ignore < 66.7:
                    idx = 3
                else:
                    for i in range(6):
                        _state = [j for j in state]
                        _state[i] = min(_state[i] + 1, maxvalue)
                        _eff = Union._get_union_increment_from_state(mdf, _state, critical_reinforce = critical_reinforce)
                        print(_state, _eff)
                        if _eff > eff:
                            idx = i
                            eff = _eff                
                    print("Current state : %s\nslots : %d\n" % (str(state), slots))
                    raise ArithmeticError("Something gonna wrong")
            state[idx] += 1
            slots -= 1
        
        if asIndex:
            return state
        else:
            if state[3] > 100:
                print(state)
                raise ValueError("something gonna wrong")
            return Union._get_union_from_state(state), state[6]
    
    @staticmethod
    def _get_union_increment_from_state(mdf, state, critical_reinforce = False):
        mdfCopy = mdf + Union._get_union_from_state(state)
        if critical_reinforce:
            mdfCopy += MDF(crit_damage = max(0, mdfCopy.crit)*0.125)
        return mdfCopy.get_damage_factor()

    @staticmethod
    def _get_union_from_state(state):
        return (MDF(att = state[0]) + MDF(stat_main = 5 * state[1]) + \
                            MDF(boss_pdamage = state[2]) + MDF(armor_ignore = state[3]) + \
                            MDF(crit = state[4]) + MDF(crit_damage = state[5] * 0.5))
        
        
class LinkSkill():
    DemonSlayer = InformedCharacterModifier("링크(데몬슬레이어)", boss_pdamage = 15)
    DemonAvenger = InformedCharacterModifier("링크(데몬어벤져)", pdamage = 10)
    Ark = InformedCharacterModifier("링크(아크)", pdamage = 11)
    Illium = InformedCharacterModifier("링크(일리움)", pdamage = 12)
    Cadena = InformedCharacterModifier("링크(카데나)", pdamage = 12) #optional
    AdventureMage = InformedCharacterModifier("링크(모법)", pdamage=9, armor_ignore=9)
    AdventureRog = InformedCharacterModifier("링크(모도)", pdamage=18/2)
    Adele = InformedCharacterModifier("링크(아델)", pdamage=2, boss_pdamage=4)
    Luminous = InformedCharacterModifier("링크(루미너스)", armor_ignore = 15)
    Zero = InformedCharacterModifier("링크(제로)", armor_ignore = 10)
    Hoyoung = InformedCharacterModifier("링크(호영)", armor_ignore = 10)
    Zenon = InformedCharacterModifier("링크(제논)", pstat_main = 10, pstat_sub = 10)
    AdventurePirate = InformedCharacterModifier("링크(모해)", stat_main = 70, stat_sub = 70)
    Cygnus = InformedCharacterModifier("링크(시그너스)", att = 25)
    Phantom = InformedCharacterModifier("링크(팬텀)", crit = 15)
    AdventureArcher = InformedCharacterModifier("링크(모궁)", crit = 10)
    Kinesis = InformedCharacterModifier("링크(키네시스)", crit_damage = 4)
    Angelicbuster = InformedCharacterModifier("링크(엔젤릭버스터)")   #Skill
    Michael = InformedCharacterModifier("링크(미하일)") # Util skill
    Mercedes = InformedCharacterModifier("링크(메르세데스)")    #Exp
    Aran = InformedCharacterModifier("링크(아란)")    #Exp
    Evan = InformedCharacterModifier("링크(에반)")    #Exp
    Eunwol = InformedCharacterModifier("링크(은월)") # Util
    Kaiser = InformedCharacterModifier("링크(카이저)") # HP
    Registance = InformedCharacterModifier("링크(레지스탕스)") #Util
    AdventureWarrior = InformedCharacterModifier("링크(모전)")   #Skill

    jobdict = {
        "아크메이지불/독" : AdventureMage,
        "아크메이지썬/콜" : AdventureMage,
        "비숍" : AdventureMage,
        "히어로" : AdventureWarrior,
        "팔라딘" : AdventureWarrior,
        "다크나이트" : AdventureWarrior,
        "보우마스터" : AdventureArcher,
        "패스파인더" : AdventureArcher,
        "신궁" : AdventureArcher,
        "나이트로드" : AdventureRog,
        "섀도어" : AdventureRog,
        "듀얼블레이드" : AdventureRog,
        "캡틴" : AdventurePirate,
        "바이퍼" : AdventurePirate,
        "캐논슈터" : AdventurePirate,
        "소울마스터" : Cygnus,
        "플레임위자드" : Cygnus,
        "윈드브레이커" : Cygnus,
        "나이트워커" : Cygnus,
        "스트라이커" : Cygnus,
        "미하일" : Michael,
        "아란" : Aran,
        "에반" : Evan,
        "루미너스" : Luminous,
        "메르세데스" : Mercedes,
        "팬텀" : Phantom,
        "은월" : Eunwol,
        "메카닉" : Registance,
        "배틀메이지" : Registance,
        "와일드헌터" : Registance,
        "블래스터" : Registance,
        "제논" : Zenon,
        "데몬어벤져" : DemonAvenger,
        "데몬슬레이어" : DemonSlayer,
        "카이저" : Kaiser,
        "엔젤릭버스터" : Angelicbuster,
        "카데나" : Cadena,
        "일리움" : Illium,
        "아크" : Ark,
        '아델' : Adele,
        "제로" : Zero,
        "키네시스" : Kinesis,
        "호영" : Hoyoung
    }

    @staticmethod
    def get_link_skill_modifier(refMDF, job_name):
        def append_link(links, new_link):
            return [link for link in links if link.name != new_link.name] + [new_link]
        
        def get_mdf(links):
            return reduce(lambda x, y: x+y, links)

        links = [LinkSkill.Registance, LinkSkill.Angelicbuster]
        links = append_link(links, LinkSkill.jobdict[job_name])

        # TODO: 미하일링크 사용시 이쪽에 사용 직업들 추가

        if job_name in ["소울마스터", "카데나", "제로", "블래스터", "배틀메이지", "스트라이커", "나이트워커"]:
            links = append_link(links, LinkSkill.Illium)

        if (refMDF + get_mdf(links)).armor_ignore < 90:
            links = append_link(links, LinkSkill.Luminous)
        if (refMDF + get_mdf(links)).armor_ignore < 85:
            links = append_link(links, LinkSkill.Zero)
        if (refMDF + get_mdf(links)).armor_ignore < 85:
            links = append_link(links, LinkSkill.Hoyoung)

        if (refMDF + get_mdf(links)).crit < 90:
            links = append_link(links, LinkSkill.Phantom)
        if (refMDF + get_mdf(links)).crit < 90:
            links = append_link(links, LinkSkill.AdventureArcher)

        link_priority = [LinkSkill.DemonSlayer, LinkSkill.AdventureMage, LinkSkill.Cadena,
                        LinkSkill.Kinesis, LinkSkill.Ark, LinkSkill.DemonAvenger,
                        LinkSkill.AdventureRog, LinkSkill.Zenon, LinkSkill.Cygnus,
                        LinkSkill.Adele, LinkSkill.AdventurePirate]
        for link in link_priority:
            if len(links) < 13:
                links = append_link(links, link)
            
        return get_mdf(links)

class Card():
    '''
    10/20/40/80/100
    힘캐 : 8
    법캐 : 7
    덱 : 4
    럭 : 5
    5/10/15/20
    공마 : 1
    
    1/2/3/4/5
    크리율 : 2
    
    4/6/8/10/12
    소환수 : 1
    
    250/500/100/2000/2500
    체력 : 2
    
    아란 : 피회복
    에반 : 마나회복
    메르 : 쿨감 2/3/4/5/6
    팬텀 : 메획 1/2/3/4/5
    
    1/2/3/5/6
    크뎀 : 1
    방무 : 1
    보공 : 1
    
    0.8/1.6/2.4/3.2/4 뎀증
    와헌
    
    벞지 5/10/15/20/25
    메카
    
    제논 : 힘덱럭 5/10/20/40/50
    
    제로 : 경치
    '''
    #주스텟 / 부스텟 / 크리 / 공마 / 크뎀 / 보공 / 방무 / 총뎀 / 제논
    CList = [[MDF(stat_main_fixed = i) for i in [10,20,40,80,100]],
            [MDF(stat_sub_fixed = i) for i in [10,20,40,80,100]],
            [MDF(crit = i) for i in [1,2,3,4,5]],
            [MDF(att = i) for i in [5,10,15,20, None]],
            [MDF(crit_damage = i) for i in [1,2,3,5,6]],
            [MDF(armor_ignore = i) for i in [1,2,3,5,6]],
            [MDF(boss_pdamage = i) for i in [1,2,3,5,6]],
            [MDF(pdamage = i) for i in [0.8,1.6,2.4,3.2,4]],
            [MDF(stat_main_fixed = i, stat_sub_fixed = i) for i in [5,10,20,40,50]]]
    
    priority = {
        "str" : {
            "order" : [2,4,5,6,7,0,8,1],
            "max" : [8,4,2,1,1,1,1,1,1]
        },
        "dex" : {
            "order" : [2,4,5,6,7,0,8,1],
            "max" : [4,8,2,1,1,1,1,1,1]
        },
        "int" : {
            "order" : [2,4,5,6,7,0,8,1],
            "max" : [7,5,2,1,1,1,1,1,1]
        },
        "luk" : {
            "order" : [2,4,5,6,7,0,8,1],
            "max" : [5,4,2,1,1,1,1,1,1]
        }
    }
        
    
    @staticmethod
    def get_apt_slot(ulevel, maplem = True):
        '''get_apt_slot(ulevel, maplem = True) : Return Apt union slot.
        유니온 캐릭터는 2000레벨부터 300레벨당 200짜리가 1개씩 증가합니다. 기본적으로 하나를 가집니다.
        점령 가능한 개수는 아래와 같습니다.
        
        리턴 값 타입 : 200레벨의 수, 140레벨의 수
        '''
        numOf200 = min((ulevel - 2000) // 300 + 1, Union.peoples[ulevel//500])
        _else = (ulevel - numOf200 * 200) // 140
        return [numOf200, min(_else, Union.peoples[ulevel//500] - numOf200) + (maplem * 1)]
    
    #TODO define Character Cards
    @staticmethod
    def get_card(jobtype, ulevel, maplem = True):
        '''get_card : 캐릭터카드 효과를 리턴합니다.
        리턴 형태 : Modifier, (벞지), (소환수), (쿨감)
        '''
        if jobtype not in ["str", "dex", "int", "luk"]:
            raise TypeError("jobtype must str, dex, int or luk, get:"+str(jobtype))
        retmdf = MDF()
        card_4, card_3 = Card.get_apt_slot(ulevel, maplem = maplem)
        order = [i for i in Card.priority[jobtype]["order"]]
        lefts = [i for i in Card.priority[jobtype]["max"]]
        currentorder = 0
        while card_4 + card_3 > 0:
            if currentorder >= len(order):
                break
            idx = order[currentorder]
            if lefts[idx] == 0:
                currentorder += 1
                continue
            if card_4 > 0:
                retmdf += Card.CList[idx][3]
                card_4 -= 1
            else:
                retmdf += Card.CList[idx][2]
                card_3 -= 1
            lefts[idx] -= 1
        
        if maplem:
            retmdf += Card.CList[3][2]
        return (retmdf, )
    

class WeaponPotential():
    storageWeapon = [[None],[None], 
                        [[MDF(pdamage=6), MDF(patt = 6), MDF(armor_ignore = 15)], [MDF(pdamage=3), MDF(att=3)]],
                        [[MDF(boss_pdamage=30), MDF(patt = 9), MDF(armor_ignore = 30)], 
                            [MDF(boss_pdamage=20), MDF(patt = 6), MDF(armor_ignore = 20)]],
                        [[MDF(boss_pdamage=40), MDF(patt = 12), MDF(armor_ignore = 40)], 
                            [MDF(boss_pdamage=30), MDF(patt = 9), MDF(armor_ignore = 30)]]]
                            
    storageEmblem = [[None],[None], 
                        [[MDF(pdamage=6), MDF(patt = 6), MDF(armor_ignore = 15)], [MDF(pdamage=3), MDF(patt=3)]],
                        [[MDF(patt = 9), MDF(armor_ignore = 30)], 
                            [MDF(patt = 6), MDF(armor_ignore = 20)]],
                        [[MDF(patt = 12), MDF(armor_ignore = 40)], 
                            [MDF(patt = 9), MDF(armor_ignore = 30)]]]
                                
    @staticmethod
    def get_weapon_pontential(mdf, tier, number):
        '''get_weapon_pontential(mdf, tier, number) : return Appropriate weapon potentials.
        This function will return list - of - potential candidate.
        
        mdf : Base modifier that will refered for optimizing weapon potential.
        tier : Tier of potential. Tier must be 2(Epic), 3(Unique) or 4(Regendry)
        number : Effective option #. number must be in range 0 ~ 9.
        '''
        if number<0 or number>9:
            raise TypeError("number must be in range 0 ~ 9")
        if tier < 1 or tier > 5:
            raise TypeError("Tier must be 2, 3 or 4.")
            
        target = mdf.copy()
        enhancement = MDF()
        retli = []
        for i in range(number):
            if i < 3: j = 0
            else: j = 1
            
            if i%3==0: sto = WeaponPotential.storageEmblem
            else: sto = WeaponPotential.storageWeapon
            
            cand = MDF()
            ehc = 0
            for mdfCandidate in sto[tier][j]:
                _ehc = (target + enhancement + mdfCandidate).get_damage_factor()
                if _ehc > ehc:
                    cand = mdfCandidate
                    ehc = _ehc
            retli.append(cand.copy())
            enhancement = enhancement + cand
        
        return retli

class HyperStat():
    requirement = [1,2,4,8,10,15,20,25,30,35,50,65,80,95,110,9999]
    enhancement = [[MDF(stat_main_fixed = 30) for i in range(16)],
                    [MDF(stat_sub_fixed = 30) for i in range(16)],
                    [MDF(crit = 1) for i in range(5)] + [MDF(crit=2) for i in range(11)],
                    [MDF(crit_damage = 1) for i in range(16)],
                    [MDF(armor_ignore = 3*(i+1)) - MDF(armor_ignore = 3*i) for i in range(16)],
                    [MDF(pdamage = 3) for i in range(16)],
                    [MDF(boss_pdamage = 3) for i in range(5)] + [MDF(boss_pdamage = 4) for i in range(11)],
                    [MDF(att = 3) for i in range(16)] ]
    def __init__(self, mdf, level):
        self.mdf = mdf
        self.level = level
    
    def as_dict(self):
        return {"mdf" : self.mdf.as_dict(),
                "level" : self.level}
    
    @staticmethod
    def get_point(level):
        '''get_point(level) : return hyperstat point of given level.
        '''
        delta = level-140
        return delta*3 + (delta//10) * (delta//10 - 1) * 5 + (delta//10) * (delta % 10)
    
    @staticmethod
    def get_hyper_object(mdf, level):    
        mdf = HyperStat.get_hyper_modifier(mdf, level)
        return HyperStat(mdf, level)
    
    @staticmethod
    def get_hyper_index(mdf, level, isIndex = True, critical_reinforce = False):
        '''get_hyper_index(mdf, level) : return enhancement index for matching enhancement type.
        '''
        hyper_size = 8
        idxList = [0 for i in range(hyper_size)]
        point_left = HyperStat.get_point(level)
        mdfSum = MDF()
        while True:
            not_enough = True
            fix_enhance = (mdf + mdfSum).get_damage_factor()
            #print(point_left, idxList, fix_enhance)
            val = -1
            ehc = 0
            for i in range(hyper_size):
                enhanced_mdf = HyperStat.enhancement[i][idxList[i]] + mdf + mdfSum
                if critical_reinforce:
                    enhanced_mdf += MDF(crit_damage = max(0, enhanced_mdf.crit) * 0.125)
                _ehc = ((enhanced_mdf).get_damage_factor() - fix_enhance) / \
                            HyperStat.requirement[idxList[i]]
                if _ehc >= ehc and HyperStat.requirement[idxList[i]] < point_left:
                    ehc = _ehc
                    val = i
                if HyperStat.requirement[idxList[i]] < point_left:
                    not_enough = False
            if not_enough:
                break
            if val == -1:
                if (mdf + mdfSum).armor_ignore < 66.7:
                    val = 4
                else:
                    print(point_left)
                    print(idxList)
                    print((mdf+mdfSum).log())
                    raise TypeError("Something gonna wrong")
                
            point_left -= HyperStat.requirement[idxList[val]]
            mdfSum = mdfSum + HyperStat.enhancement[val][idxList[val]]
            idxList[val] += 1
            
        if isIndex:
            return idxList
        else:
            return mdfSum
    
    @staticmethod
    def get_hyper_modifier(mdf, level, critical_reinforce = False):
        return HyperStat.get_hyper_index(mdf, level, isIndex = False, critical_reinforce = critical_reinforce)

class Doping():
    dopingListAtt = {"길드의 축복" : MDF(att = 20),
                    "우뿌" : MDF(att = 30),
                    "익스레드/블루" : MDF(att = 30),
                    "MVP 버프" : MDF(att = 30)}

    dopingListStat = {"향상된 10단계 물약" : MDF(stat_main = 30)}
    
    dopingListDamage = {"매칭" : MDF(boss_pdamage = 10),
                        "노블레스(뎀퍼)" : MDF(pdamage = 30),
                        "노블레스(보공)" : MDF(boss_pdamage = 28),
                        "반빨별" : MDF(boss_pdamage = 20)}
                        
    dopingListArmor = {"고관비" : MDF(armor_ignore = 20)}
                        
    dopingListCritDamage = {"노블레스(크뎀)" : MDF(crit_damage = 30)}
                        
    @staticmethod
    def get_full_doping():
        retMdf = MDF()
        
        for name in Doping.dopingListAtt:
            retMdf = retMdf + Doping.dopingListAtt[name]
        for name in Doping.dopingListStat:
            retMdf = retMdf + Doping.dopingListStat[name]
        for name in Doping.dopingListDamage:
            retMdf = retMdf + Doping.dopingListDamage[name]
        for name in Doping.dopingListArmor:
            retMdf = retMdf + Doping.dopingListArmor[name]
        for name in Doping.dopingListCritDamage:
            retMdf = retMdf + Doping.dopingListCritDamage[name]
        
        return retMdf

class Personality():
    @staticmethod
    def get_personality(avg_level):
        return EXMDF(armor_ignore = (avg_level // 5) * 0.5, buff_rem = (avg_level // 10) * 1, prop_ignore = 0.5 * (avg_level // 10))


def testonly():            
    test = MDF(armor_ignore = 80, pdamage = 100, stat_main = 1000, att = 100)
    for i in range(140, 220, 5):
        print("level" + str(i))
        print(HyperStat.get_hyper_index(test, i))