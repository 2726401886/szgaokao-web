# -*- coding: utf-8 -*-
"""补：给已替换的 choice_single 行补上列表所需的尾逗号；并替换 2 处之前未匹配到的 broken 模板。"""
import re

PATH = 'tools/gen_physics_book.py'
src = open(PATH, encoding='utf-8').read()

# 1) 给形如  {'type': 'choice_single', ...}  且行尾没有逗号 的行补逗号
pat = re.compile(r"^(\s*\{'type': 'choice_single'.*?\}\s*)$", re.MULTILINE)
src, n_comma = pat.subn(lambda m: m.group(1).rstrip() + ',', src)
print('补逗号 %d 处' % n_comma)

# 2) 未匹配到的 2 处 broken 模板（用真实片段）
EXTRA = [
    ("近视镜片为凹透镜，对光有",
     "      {'type': 'choice_single', 'stem': '近视眼镜的镜片是凹透镜，对光有', 'options': ['会聚作用', '发散作用', '既不会聚也不发散', '反射作用'], 'answer': 1, 'analysis': '凹透镜对光有发散作用，使像后移到视网膜。', 'kaodian': '近视矫正'},"),
    ("其惯性比",
     "      {'type': 'choice_single', 'stem': '关于惯性，下列说法正确的是', 'options': ['速度大的物体惯性大', '质量大的物体惯性大', '静止的物体没有惯性', '受力大的物体惯性大'], 'answer': 1, 'analysis': '惯性只与质量有关，质量越大惯性越大。', 'kaodian': '惯性'},"),
]
for frag, new_line in EXTRA:
    p = re.compile(r"^\s*\{'kind': 'choice'.*?" + re.escape(frag) + r".*?\},\s*$", re.MULTILINE)
    if p.search(src):
        src = p.sub(new_line, src, count=1)
        print('已替换:', frag)
    else:
        print('仍未匹配:', frag)

open(PATH, 'w', encoding='utf-8').write(src)
print('done')
