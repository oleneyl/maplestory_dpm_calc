import dpmModule
from dpmModule.util.dpmgenerator import IndividualDPMGenerator
import dpmModule.character.characterTemplateHigh as template
joblist = ["아크메이지불/독", "아크메이지썬/콜", "비숍", "히어로", "팔라딘", "신궁", "윈드브레이커", "소울마스터", "루미너스", "배틀메이지", "메카닉", "메르세데스", "데몬슬레이어", "다크나이트", "와일드헌터", "플레임위자드", "섀도어", "캐논슈터", "미하일", "듀얼블레이드", "카이저", "캡틴", "엔젤릭버스터", "팬텀", "나이트로드", "은월", "바이퍼", "나이트워커", "스트라이커", "에반", "보우마스터", "제로", "키네시스", "일리움", "패스파인더", "카데나", "아크", "블래스터"]

print("전직업 DPM (유니크 / 유니온 6000 기준)")

f = open("result.txt", 'w');
dpmlist = []
for jobname in joblist:
    gen = IndividualDPMGenerator(jobname, template.getU6000CharacterTemplate)
    dpmlist.append((jobname, gen.get_dpm(ulevel = 6000)))
    print(jobname + " 계산 완료")

dpmlist.sort(key=lambda x : x[1], reverse=True)

for (dpmname, dpmvalue) in dpmlist:
    output = dpmname + " " + str(dpmvalue)
    f.write(output)
f.close()
    