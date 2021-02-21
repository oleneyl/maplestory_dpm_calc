def skill_name_by_lang(skill_name: str, lang: str = None) -> str:
    # Preserve the list of modifiers after the skill name
    modifiers = ''
    if '(' in skill_name:
        modifiers = f'({skill_name.split("(", 1)[1]}'
    if lang == 'en':
        return skill_name.split(' | ')[0] + modifiers
    elif ' | ' in skill_name:
        return skill_name.split(' | ', 1)[1]
    return skill_name


def skill_modifier_by_lang(modifier: str, lang: str = None) -> str:
    if lang == 'en':
        return modifier.split(' | ')[0]
    elif ' | ' in modifier:
        return modifier.split(' | ')[1]
    return modifier
