from . import ItemKernel as it

# 장갑은 아무도 안씀
#Glove = it.Item(stat_main = 12, stat_sub = 12, att = 15)
# 신발 업횟 2
Shoes = it.Item(name="타일런트 슈즈", stat_main = 50, stat_sub = 50, att = 30, level = 150)
# 망토 업횟 2
Cloak = it.Item(name="타일런트 클록", stat_main = 50, stat_sub = 50, att = 30, level = 150)
# 벨트 업횟 1
Belt = it.Item(name="타일런트 벨트", stat_main = 50, stat_sub = 50, att = 25, level = 150)

# get_surprise_enhance_list_direct 사용 (150제)