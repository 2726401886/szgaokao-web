# -*- coding: utf-8 -*-
# PET 核心词（剑桥 B1 Preliminary 备考核心词）12 主题 × 20 词 = 240 词
# 音频命名 /audio/pw/pw{group}-w{no}.mp3
import json, os, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
AUD = os.path.join(BASE, "public", "audio", "pw")

GROUPS = [
    ("pw1", "教育与社会", [
        ("education", "/ˌedʒuˈkeɪʃn/", "n.", "教育"), ("society", "/səˈsaɪəti/", "n.", "社会"),
        ("government", "/ˈɡʌvənmənt/", "n.", "政府"), ("public", "/ˈpʌblɪk/", "adj.", "公共的"),
        ("private", "/ˈpraɪvət/", "adj.", "私人的"), ("university", "/ˌjuːnɪˈvɜːsəti/", "n.", "大学"),
        ("degree", "/dɪˈɡriː/", "n.", "学位；程度"), ("research", "/rɪˈsɜːtʃ/", "n.", "研究"),
        ("knowledge", "/ˈnɒlɪdʒ/", "n.", "知识"), ("skill", "/skɪl/", "n.", "技能"),
        ("training", "/ˈtreɪnɪŋ/", "n.", "培训；训练"), ("course", "/kɔːs/", "n.", "课程"),
        ("result", "/rɪˈzʌlt/", "n.", "结果；成绩"), ("grade", "/ɡreɪd/", "n.", "成绩等级"),
        ("pupil", "/ˈpjuːpl/", "n.", "小学生"), ("academy", "/əˈkædəmi/", "n.", "学院"),
        ("scholar", "/ˈskɒlə/", "n.", "学者"), ("tuition", "/tjuˈɪʃn/", "n.", "学费"),
        ("certificate", "/səˈtɪfɪkət/", "n.", "证书"), ("qualification", "/ˌkwɒlɪfɪˈkeɪʃn/", "n.", "资格"),
    ]),
    ("pw2", "科技与媒体", [
        ("technology", "/tekˈnɒlədʒi/", "n.", "技术"), ("computer", "/kəmˈpjuːtə/", "n.", "电脑"),
        ("internet", "/ˈɪntənet/", "n.", "互联网"), ("website", "/ˈwebsaɪt/", "n.", "网站"),
        ("email", "/ˈiːmeɪl/", "n.", "电子邮件"), ("message", "/ˈmesɪdʒ/", "n.", "消息"),
        ("screen", "/skriːn/", "n.", "屏幕"), ("keyboard", "/ˈkiːbɔːd/", "n.", "键盘"),
        ("mobile", "/ˈməʊbaɪl/", "n.", "手机"), ("app", "/æp/", "n.", "应用程序"),
        ("information", "/ˌɪnfəˈmeɪʃn/", "n.", "信息"), ("news", "/njuːz/", "n.", "新闻"),
        ("newspaper", "/ˈnjuːzpeɪpə/", "n.", "报纸"), ("radio", "/ˈreɪdiəʊ/", "n.", "收音机"),
        ("television", "/ˈtelɪvɪʒn/", "n.", "电视"), ("advertisement", "/ədˈvɜːtɪsmənt/", "n.", "广告"),
        ("social", "/ˈsəʊʃl/", "adj.", "社交的；社会的"), ("online", "/ˌɒnˈlaɪn/", "adj.", "在线的"),
        ("download", "/ˌdaʊnˈləʊd/", "v.", "下载"), ("upload", "/ˌʌpˈləʊd/", "v.", "上传"),
    ]),
    ("pw3", "环境与环保", [
        ("environment", "/ɪnˈvaɪrənmənt/", "n.", "环境"), ("pollution", "/pəˈluːʃn/", "n.", "污染"),
        ("climate", "/ˈklaɪmət/", "n.", "气候"), ("energy", "/ˈenədʒi/", "n.", "能源；能量"),
        ("recycle", "/ˌriːˈsaɪkl/", "v.", "回收利用"), ("waste", "/weɪst/", "n.", "浪费；废料"),
        ("rubbish", "/ˈrʌbɪʃ/", "n.", "垃圾"), ("plastic", "/ˈplæstɪk/", "n.", "塑料"),
        ("ocean", "/ˈəʊʃn/", "n.", "海洋"), ("nature", "/ˈneɪtʃə/", "n.", "大自然"),
        ("protect", "/prəˈtekt/", "v.", "保护"), ("reduce", "/rɪˈdjuːs/", "v.", "减少"),
        ("reuse", "/ˌriːˈjuːz/", "v.", "重复使用"), ("global", "/ˈɡləʊbl/", "adj.", "全球的"),
        ("warming", "/ˈwɔːmɪŋ/", "n.", "变暖"), ("resource", "/rɪˈsɔːs/", "n.", "资源"),
        ("wildlife", "/ˈwaɪldlaɪf/", "n.", "野生动物"), ("sustainable", "/səˈsteɪnəbl/", "adj.", "可持续的"),
        ("greenhouse", "/ˈɡriːnhaʊs/", "n.", "温室"), ("carbon", "/ˈkɑːbən/", "n.", "碳"),
    ]),
    ("pw4", "文化与艺术", [
        ("culture", "/ˈkʌltʃə/", "n.", "文化"), ("art", "/ɑːt/", "n.", "艺术"),
        ("painting", "/ˈpeɪntɪŋ/", "n.", "绘画；油画"), ("drawing", "/ˈdrɔːɪŋ/", "n.", "素描"),
        ("sculpture", "/ˈskʌlptʃə/", "n.", "雕塑"), ("concert", "/ˈkɒnsət/", "n.", "音乐会"),
        ("gallery", "/ˈɡæləri/", "n.", "画廊"), ("exhibition", "/ˌeksɪˈbɪʃn/", "n.", "展览"),
        ("traditional", "/trəˈdɪʃənl/", "adj.", "传统的"), ("modern", "/ˈmɒdn/", "adj.", "现代的"),
        ("festival", "/ˈfestɪvl/", "n.", "节日"), ("celebration", "/ˌselɪˈbreɪʃn/", "n.", "庆祝"),
        ("literature", "/ˈlɪtrətʃə/", "n.", "文学"), ("poem", "/ˈpəʊɪm/", "n.", "诗"),
        ("novel", "/ˈnɒvl/", "n.", "小说"), ("drama", "/ˈdrɑːmə/", "n.", "戏剧"),
        ("musician", "/mjuˈzɪʃn/", "n.", "音乐家"), ("composer", "/kəmˈpəʊzə/", "n.", "作曲家"),
        ("performance", "/pəˈfɔːməns/", "n.", "表演"), ("audience", "/ˈɔːdiəns/", "n.", "观众"),
    ]),
    ("pw5", "经济与购物", [
        ("economy", "/ɪˈkɒnəmi/", "n.", "经济"), ("business", "/ˈbɪznəs/", "n.", "商业；生意"),
        ("company", "/ˈkʌmpəni/", "n.", "公司"), ("customer", "/ˈkʌstəmə/", "n.", "顾客"),
        ("product", "/ˈprɒdʌkt/", "n.", "产品"), ("service", "/ˈsɜːvɪs/", "n.", "服务"),
        ("quality", "/ˈkwɒləti/", "n.", "质量"), ("cost", "/kɒst/", "n.", "成本；花费"),
        ("budget", "/ˈbʌdʒɪt/", "n.", "预算"), ("income", "/ˈɪnkʌm/", "n.", "收入"),
        ("profit", "/ˈprɒfɪt/", "n.", "利润"), ("brand", "/brænd/", "n.", "品牌"),
        ("sale", "/seɪl/", "n.", "销售；促销"), ("discount", "/ˈdɪskaʊnt/", "n.", "折扣"),
        ("purchase", "/ˈpɜːtʃəs/", "v.", "购买"), ("payment", "/ˈpeɪmənt/", "n.", "付款"),
        ("receipt", "/rɪˈsiːt/", "n.", "收据"), ("delivery", "/dɪˈlɪvəri/", "n.", "送货"),
        ("currency", "/ˈkʌrənsi/", "n.", "货币"), ("exchange", "/ɪksˈtʃeɪndʒ/", "v.", "兑换；交换"),
    ]),
    ("pw6", "健康与医疗", [
        ("medical", "/ˈmedɪkl/", "adj.", "医疗的"), ("treatment", "/ˈtriːtmənt/", "n.", "治疗"),
        ("patient", "/ˈpeɪʃnt/", "n.", "病人"), ("disease", "/dɪˈziːz/", "n.", "疾病"),
        ("virus", "/ˈvaɪrəs/", "n.", "病毒"), ("infection", "/ɪnˈfekʃn/", "n.", "感染"),
        ("symptom", "/ˈsɪmptəm/", "n.", "症状"), ("surgery", "/ˈsɜːdʒəri/", "n.", "外科手术"),
        ("emergency", "/ɪˈmɜːdʒənsi/", "n.", "紧急情况"), ("fitness", "/ˈfɪtnəs/", "n.", "健康；体能"),
        ("diet", "/ˈdaɪət/", "n.", "饮食"), ("nutrition", "/njuˈtrɪʃn/", "n.", "营养"),
        ("mental", "/ˈmentl/", "adj.", "心理的；精神的"), ("physical", "/ˈfɪzɪkl/", "adj.", "身体的"),
        ("prevent", "/prɪˈvent/", "v.", "预防"), ("recover", "/rɪˈkʌvə/", "v.", "康复"),
        ("prescription", "/prɪˈskrɪpʃn/", "n.", "处方"), ("vaccine", "/ˈvæksiːn/", "n.", "疫苗"),
        ("appointment", "/əˈpɔɪntmənt/", "n.", "预约"), ("insurance", "/ɪnˈʃʊərəns/", "n.", "保险"),
    ]),
    ("pw7", "旅行与冒险", [
        ("adventure", "/ədˈventʃə/", "n.", "冒险"), ("explore", "/ɪkˈsplɔː/", "v.", "探索"),
        ("destination", "/ˌdestɪˈneɪʃn/", "n.", "目的地"), ("flight", "/flaɪt/", "n.", "航班"),
        ("passport", "/ˈpɑːspɔːt/", "n.", "护照"), ("visa", "/ˈviːzə/", "n.", "签证"),
        ("sightseeing", "/ˈsaɪtsiːɪŋ/", "n.", "观光"), ("experience", "/ɪkˈspɪəriəns/", "n.", "经历；体验"),
        ("beach", "/biːtʃ/", "n.", "海滩"), ("island", "/ˈaɪlənd/", "n.", "岛屿"),
        ("desert", "/ˈdezət/", "n.", "沙漠"), ("guide", "/ɡaɪd/", "n.", "导游；指南"),
        ("campsite", "/ˈkæmpsaɪt/", "n.", "露营地"), ("tent", "/tent/", "n.", "帐篷"),
        ("backpack", "/ˈbækpæk/", "n.", "背包"), ("route", "/ruːt/", "n.", "路线"),
        ("expedition", "/ˌekspəˈdɪʃn/", "n.", "远征；探险"), ("voyage", "/ˈvɔɪɪdʒ/", "n.", "航行"),
        ("cruise", "/kruːz/", "n.", "邮轮旅行"), ("landmark", "/ˈlændmɑːk/", "n.", "地标"),
    ]),
    ("pw8", "人际关系", [
        ("relationship", "/rɪˈleɪʃnʃɪp/", "n.", "关系"), ("friendship", "/ˈfrendʃɪp/", "n.", "友谊"),
        ("relative", "/ˈrelətɪv/", "n.", "亲戚"), ("partner", "/ˈpɑːtnə/", "n.", "伙伴"),
        ("colleague", "/ˈkɒliːɡ/", "n.", "同事"), ("trust", "/trʌst/", "v.", "信任"),
        ("respect", "/rɪˈspekt/", "v.", "尊重"), ("support", "/səˈpɔːt/", "v.", "支持"),
        ("argue", "/ˈɑːɡjuː/", "v.", "争论"), ("apologise", "/əˈpɒlədʒaɪz/", "v.", "道歉"),
        ("forgive", "/fəˈɡɪv/", "v.", "原谅"), ("communicate", "/kəˈmjuːnɪkeɪt/", "v.", "交流"),
        ("community", "/kəˈmjuːnəti/", "n.", "社区"), ("together", "/təˈɡeðə/", "adv.", "一起"),
        ("lonely", "/ˈləʊnli/", "adj.", "孤独的"), ("friendly", "/ˈfrendli/", "adj.", "友好的"),
        ("generous", "/ˈdʒenərəs/", "adj.", "慷慨的"), ("honest", "/ˈɒnɪst/", "adj.", "诚实的"),
        ("patient", "/ˈpeɪʃnt/", "adj.", "有耐心的"), ("cooperate", "/kəʊˈɒpəreɪt/", "v.", "合作"),
    ]),
    ("pw9", "工作与职业", [
        ("career", "/kəˈrɪə/", "n.", "职业；生涯"), ("profession", "/prəˈfeʃn/", "n.", "职业"),
        ("employee", "/ɪmˈplɔɪiː/", "n.", "雇员"), ("employer", "/ɪmˈplɔɪə/", "n.", "雇主"),
        ("director", "/dəˈrektə/", "n.", "董事；导演"), ("secretary", "/ˈsekrətri/", "n.", "秘书"),
        ("scientist", "/ˈsaɪəntɪst/", "n.", "科学家"), ("lawyer", "/ˈlɔːjə/", "n.", "律师"),
        ("accountant", "/əˈkaʊntənt/", "n.", "会计师"), ("architect", "/ˈɑːkɪtekt/", "n.", "建筑师"),
        ("designer", "/dɪˈzaɪnə/", "n.", "设计师"), ("journalist", "/ˈdʒɜːnəlɪst/", "n.", "记者"),
        ("opportunity", "/ˌɒpəˈtjuːnəti/", "n.", "机会"), ("promotion", "/prəˈməʊʃn/", "n.", "晋升"),
        ("resign", "/rɪˈzaɪn/", "v.", "辞职"), ("hire", "/ˈhaɪə/", "v.", "雇用"),
        ("dismiss", "/dɪsˈmɪs/", "v.", "解雇"), ("pension", "/ˈpenʃn/", "n.", "养老金"),
        ("colleague", "/ˈkɒliːɡ/", "n.", "同事"), ("workplace", "/ˈwɜːkpleɪs/", "n.", "工作场所"),
    ]),
    ("pw10", "法律与社会", [
        ("law", "/lɔː/", "n.", "法律"), ("legal", "/ˈliːɡl/", "adj.", "合法的"),
        ("illegal", "/ɪˈliːɡl/", "adj.", "非法的"), ("rule", "/ruːl/", "n.", "规则"),
        ("regulation", "/ˌreɡjuˈleɪʃn/", "n.", "规章"), ("crime", "/kraɪm/", "n.", "犯罪"),
        ("criminal", "/ˈkrɪmɪnl/", "n.", "罪犯"), ("police", "/pəˈliːs/", "n.", "警察"),
        ("court", "/kɔːt/", "n.", "法庭"), ("judge", "/dʒʌdʒ/", "n.", "法官"),
        ("justice", "/ˈdʒʌstɪs/", "n.", "正义"), ("rights", "/raɪts/", "n.", "权利"),
        ("freedom", "/ˈfriːdəm/", "n.", "自由"), ("citizen", "/ˈsɪtɪzn/", "n.", "公民"),
        ("responsibility", "/rɪˌspɒnsəˈbɪləti/", "n.", "责任"), ("duty", "/ˈdjuːti/", "n.", "义务"),
        ("safety", "/ˈseɪfti/", "n.", "安全"), ("punishment", "/ˈpʌnɪʃmənt/", "n.", "惩罚"),
        ("evidence", "/ˈevɪdəns/", "n.", "证据"), ("permission", "/pəˈmɪʃn/", "n.", "许可"),
    ]),
    ("pw11", "抽象概念", [
        ("idea", "/aɪˈdɪə/", "n.", "想法；主意"), ("opinion", "/əˈpɪnjən/", "n.", "意见；看法"),
        ("decision", "/dɪˈsɪʒn/", "n.", "决定"), ("choice", "/tʃɔɪs/", "n.", "选择"),
        ("problem", "/ˈprɒbləm/", "n.", "问题"), ("solution", "/səˈluːʃn/", "n.", "解决办法"),
        ("reason", "/ˈriːzn/", "n.", "原因；理由"), ("importance", "/ɪmˈpɔːtns/", "n.", "重要性"),
        ("value", "/ˈvæljuː/", "n.", "价值"), ("success", "/səkˈses/", "n.", "成功"),
        ("failure", "/ˈfeɪljə/", "n.", "失败"), ("challenge", "/ˈtʃælɪndʒ/", "n.", "挑战"),
        ("goal", "/ɡəʊl/", "n.", "目标"), ("plan", "/plæn/", "n.", "计划"),
        ("future", "/ˈfjuːtʃə/", "n.", "未来"), ("luck", "/lʌk/", "n.", "运气"),
        ("courage", "/ˈkʌrɪdʒ/", "n.", "勇气"), ("confidence", "/ˈkɒnfɪdəns/", "n.", "信心"),
        ("effort", "/ˈefət/", "n.", "努力"), ("progress", "/ˈprəʊɡres/", "n.", "进步"),
    ]),
    ("pw12", "学术与语言", [
        ("academic", "/ˌækəˈdemɪk/", "adj.", "学术的"), ("language", "/ˈlæŋɡwɪdʒ/", "n.", "语言"),
        ("grammar", "/ˈɡræmə/", "n.", "语法"), ("vocabulary", "/vəˈkæbjələri/", "n.", "词汇"),
        ("pronunciation", "/prəˌnʌnsiˈeɪʃn/", "n.", "发音"), ("conversation", "/ˌkɒnvəˈseɪʃn/", "n.", "对话"),
        ("translate", "/trænzˈleɪt/", "v.", "翻译"), ("dictionary", "/ˈdɪkʃənri/", "n.", "词典"),
        ("essay", "/ˈeseɪ/", "n.", "文章；短文"), ("report", "/rɪˈpɔːt/", "n.", "报告"),
        ("presentation", "/ˌpreznˈteɪʃn/", "n.", "演示；报告"), ("discuss", "/dɪˈskʌs/", "v.", "讨论"),
        ("explain", "/ɪkˈspleɪn/", "v.", "解释"), ("describe", "/dɪˈskraɪb/", "v.", "描述"),
        ("compare", "/kəmˈpeə/", "v.", "比较"), ("analyse", "/ˈænəlaɪz/", "v.", "分析"),
        ("summarise", "/ˈsʌməraɪz/", "v.", "总结"), ("argument", "/ˈɑːɡjumənt/", "n.", "论点；争论"),
        ("paragraph", "/ˈpærəɡrɑːf/", "n.", "段落"), ("reference", "/ˈrefrəns/", "n.", "参考"),
    ]),
]

def build_payload():
    groups = []
    for gid, title, words in GROUPS:
        wl = [{"id": "%s-w%d" % (gid, i + 1), "word": w, "phonetic": ph.strip("/"), "pos": p, "meaning": m,
               "audio": "/audio/pw/%s-w%d.mp3" % (gid, i + 1)} for i, (w, ph, p, m) in enumerate(words)]
        groups.append({"id": gid, "title": title, "count": len(wl), "words": wl})
    return {"level": "PET", "name": "PET 核心词（B1）", "groups": groups}

def gen():
    os.makedirs(DATA, exist_ok=True)
    p = build_payload()
    with open(os.path.join(DATA, "pet_words.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    md = ["# 小学英语-剑桥PET备考包-核心词表（B1）", "",
          "> 内容由 AI 生成，待创始人人工校对（红线条款）", "",
          "共 12 主题 × 20 词 = 240 词，覆盖剑桥 B1 Preliminary 高频核心词。", ""]
    for g in p["groups"]:
        md.append("## %s（%s）" % (g["title"], g["id"]))
        for w in g["words"]:
            md.append("- %s /%s/ %s %s（%s）" % (w["word"], w["phonetic"].strip("/"), w["pos"], w["meaning"], w["id"]))
        md.append("")
    with open(os.path.join(BASE, "..", "english-edu-company", "03交付素材库", "听说试卷包", "小学英语-剑桥PET备考包-核心词表-B1.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("写入完成：pet_words.json（240 词）+ 素材 md")

def audio():
    os.makedirs(AUD, exist_ok=True)
    import glob
    existing = {os.path.basename(x) for x in glob.glob(os.path.join(AUD, "*.mp3"))}
    plan = []
    for gid, _, words in GROUPS:
        for i, (w, _, _, _) in enumerate(words):
            fn = "%s-w%d.mp3" % (gid, i + 1)
            if fn not in existing:
                plan.append((fn, w))
    print("计划生成:", len(plan))
    for i, (fn, txt) in enumerate(plan, 1):
        if i % 60 == 0: print("[%d/%d]" % (i, len(plan)), end="")
        dst = os.path.join(AUD, fn)
        r = subprocess.run(["edge-tts", "--voice", "en-GB-SoniaNeural", "--text", txt,
                            "--rate=-10%", "--write-media", dst], capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL", fn, r.stderr[-200:])
    print("音频生成完成：%d/%d" % (len(plan), len(plan)))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        audio()
    else:
        gen()
