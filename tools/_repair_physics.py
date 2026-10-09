# -*- coding: utf-8 -*-
"""一次性修复 gen_physics_book.py 中 expr 返回常量(0/1) 的概念型 choice 模板：
这些模板会生成“0/1”为正确选项的荒谬题。这里把它们整行替换为正确的 choice_single 题目。
题目保留在 calc 列表内，由 build_section 的 type 透传分支直接加入。"""
import re, io

PATH = 'tools/gen_physics_book.py'
src = open(PATH, encoding='utf-8').read()

# (唯一匹配片段, 替换后的整行题目)
REPL = [
    ("碘锤加热，固态碘直接变成碘蒸气，该过程",
     "      {'type': 'choice_single', 'stem': '碘锤加热，固态碘直接变成碘蒸气，该过程属于', 'options': ['熔化', '升华', '液化', '凝固'], 'answer': 1, 'analysis': '固态直接变为气态是升华，且吸热。', 'kaodian': '升华'}"),
    ("色散中偏折最小的是",
     "      {'type': 'choice_single', 'stem': '光的色散中，偏折程度最小的是', 'options': ['红光', '紫光', '绿光', '蓝光'], 'answer': 0, 'analysis': '红光波长最长，偏折最小。', 'kaodian': '色散'}"),
    ("大于二倍焦距",
     "      {'type': 'choice_single', 'stem': '凸透镜成像中，物距大于二倍焦距时成', 'options': ['倒立放大的实像', '正立放大的虚像', '倒立缩小的实像', '正立缩小的虚像'], 'answer': 2, 'analysis': 'u>2f 成倒立缩小实像（照相机原理）。', 'kaodian': '成像规律'}"),
    ("f<u<2f",
     "      {'type': 'choice_single', 'stem': '凸透镜成像中，物距在一倍与二倍焦距之间（f<u<2f）时成', 'options': ['倒立缩小的实像', '倒立放大的实像', '正立放大的虚像', '正立缩小的虚像'], 'answer': 1, 'analysis': 'f<u<2f 成倒立放大实像（投影仪原理）。', 'kaodian': '成像规律'}"),
    ("近视眼镜的镜片是凹透镜，对光有",
     "      {'type': 'choice_single', 'stem': '近视眼镜的镜片是凹透镜，对光有', 'options': ['会聚作用', '发散作用', '既不会聚也不发散', '反射作用'], 'answer': 1, 'analysis': '凹透镜对光有发散作用，使像后移到视网膜。', 'kaodian': '近视矫正'}"),
    ("质量大的物体比质量小的物体惯性",
     "      {'type': 'choice_single', 'stem': '关于惯性，下列说法正确的是', 'options': ['速度大的物体惯性大', '质量大的物体惯性大', '静止的物体没有惯性', '受力大的物体惯性大'], 'answer': 1, 'analysis': '惯性只与质量有关，质量越大惯性越大。', 'kaodian': '惯性'}"),
    ("1 标准大气压约",
     "      {'type': 'choice_single', 'stem': '1 标准大气压约为', 'options': ['1.0×10^5 Pa', '1.5×10^5 Pa', '2.0×10^5 Pa', '0.5×10^5 Pa'], 'answer': 0, 'analysis': '1 标准大气压≈1.013×10^5 Pa。', 'kaodian': '大气压值'}"),
    ("中间水流速大、压强",
     "      {'type': 'choice_single', 'stem': '两艘船并排高速行驶时容易相撞，是因为中间水流速大、压强', 'options': ['大', '小', '不变', '为零'], 'answer': 1, 'analysis': '中间流速大压强小，外侧压强大将船压向中间。', 'kaodian': '流体压强'}"),
    ("它受到的浮力",
     "      {'type': 'choice_single', 'stem': '木块漂浮在水面上，它受到的浮力与其重力的大小关系是', 'options': ['浮力大于重力', '浮力小于重力', '浮力等于重力', '无法判断'], 'answer': 2, 'analysis': '漂浮时 F浮 = G，浮力等于重力。', 'kaodian': '漂浮'}"),
    ("速度 {v:.0f} m/s 的物体比静止时动能",
     "      {'type': 'choice_single', 'stem': '关于动能，下列说法正确的是', 'options': ['静止的物体没有动能', '速度越小动能越大', '质量越大动能一定越小', '动能只与高度有关'], 'answer': 0, 'analysis': '动能与质量和速度有关，静止物体动能为 0。', 'kaodian': '动能'}"),
    ("物体从 {h:.0f} m 高处自由下落，落地前重力势能",
     "      {'type': 'choice_single', 'stem': '物体从高处自由下落过程中，其重力势能', 'options': ['增大', '减小', '不变', '先增后减'], 'answer': 1, 'analysis': '下落高度减小，重力势能转化为动能而减小。', 'kaodian': '机械能转化'}"),
    ("温度由 {a:.0f}℃ 升到 {b:.0f}℃（b>a），分子热运动",
     "      {'type': 'choice_single', 'stem': '温度越高，分子的无规则运动', 'options': ['越慢', '越快（越剧烈）', '停止', '不变'], 'answer': 1, 'analysis': '温度越高分子热运动越剧烈。', 'kaodian': '温度与分子运动'}"),
    ("质量 {m:.0f} kg 的同一杯 water 从 20℃ 加热到 60℃，内能",
     "      {'type': 'choice_single', 'stem': '同一杯水温度从 20℃ 升高到 60℃，其内能', 'options': ['减小', '增大', '不变', '变为零'], 'answer': 1, 'analysis': '温度升高，分子动能增大，内能增大。', 'kaodian': '内能与温度'}"),
    ("单缸四冲程机转速为",
     "      {'type': 'choice_single', 'stem': '单缸四冲程内燃机，曲轴每转 2 周、完成 4 个冲程中做功', 'options': ['4 次', '2 次', '1 次', '0 次'], 'answer': 2, 'analysis': '一个工作循环 4 冲程做功 1 次。', 'kaodian': '四冲程'}"),
    ("自由下落中重力势能减小，等量减少的是",
     "      {'type': 'choice_single', 'stem': '自由下落过程中重力势能减小，等量减少的是', 'options': ['动能', '内能', '光能', '化学能'], 'answer': 0, 'analysis': '重力势能转化为动能，总量守恒。', 'kaodian': '能量守恒'}"),
    ("两个用毛皮摩擦过的橡胶棒相互靠近会",
     "      {'type': 'choice_single', 'stem': '两个用毛皮摩擦过的橡胶棒相互靠近时会', 'options': ['吸引', '排斥', '无作用', '先吸后斥'], 'answer': 1, 'analysis': '两棒都带负电，同种电荷相互排斥。', 'kaodian': '电荷间作用'}"),
    ("电路中开关闭合、连接正确时形成",
     "      {'type': 'choice_single', 'stem': '电路中开关闭合、连接正确时形成', 'options': ['断路', '短路', '通路', '以上都不是'], 'answer': 2, 'analysis': '闭合且连接正确形成通路，用电器工作。', 'kaodian': '电路状态'}"),
    ("两电阻串联总电阻比任一电阻",
     "      {'type': 'choice_single', 'stem': '两电阻串联后的总电阻比其中任一电阻', 'options': ['小', '大', '相等', '无法确定'], 'answer': 1, 'analysis': '串联总电阻等于各电阻之和，故大于任一。', 'kaodian': '串并联'}"),
    ("两节干电池串联给电路供电，总电压约",
     "      {'type': 'choice_single', 'stem': '两节 1.5 V 干电池串联给电路供电，总电压约为', 'options': ['1.5 V', '3 V', '0.75 V', '4.5 V'], 'answer': 1, 'analysis': '串联电压相加，1.5+1.5 = 3 V。', 'kaodian': '电压'}"),
    ("横截面积越大的导体电阻",
     "      {'type': 'choice_single', 'stem': '长度、材料相同的导体，横截面积越大，其电阻', 'options': ['越大', '越小', '不变', '先大后小'], 'answer': 1, 'analysis': '横截面积越大电阻越小。', 'kaodian': '电阻'}"),
    ("滑片右移使接入电阻丝变长，则电路电流",
     "      {'type': 'choice_single', 'stem': '滑动变阻器滑片右移使接入电阻丝变长，则电路中的电流', 'options': ['变大', '变小', '不变', '先变后不变'], 'answer': 1, 'analysis': '电阻变大，由 I=U/R 电流变小。', 'kaodian': '变阻器'}"),
    ("电阻由 {r1:.0f} Ω 变为 {r2:.0f} Ω（增大），电流",
     "      {'type': 'choice_single', 'stem': '电压不变，电路电阻增大时，电流', 'options': ['增大', '减小', '不变', '先增后减'], 'answer': 1, 'analysis': 'U 不变、R 增大，由 I=U/R 电流减小。', 'kaodian': '电流与电阻'}"),
    ("家庭电路火线与零线间电压为",
     "      {'type': 'choice_single', 'stem': '我国家庭电路中火线与零线之间的电压为', 'options': ['1.5 V', '36 V', '220 V', '380 V'], 'answer': 2, 'analysis': '家庭电路电压 220 V。', 'kaodian': '家庭电路'}"),
]

count = 0
for frag, new_line in REPL:
    pat = re.compile(r"^\s*\{'kind': 'choice'.*?" + re.escape(frag) + r".*?\},\s*$", re.MULTILINE)
    m = pat.search(src)
    if not m:
        print('未匹配到:', frag)
        continue
    src = pat.sub(new_line, src, count=1)
    count += 1

open(PATH, 'w', encoding='utf-8').write(src)
print('已替换 %d 处 broken choice 模板' % count)
