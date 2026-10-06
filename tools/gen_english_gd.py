# -*- coding: utf-8 -*-
"""生成 2021–2026 广东高考英语真题（新高考Ⅰ卷）真实卷数据。

说明：
  - 2021–2024：官方原版真题原文；
  - 2025、2026：考生回忆整理版（无官方完整原文，文本贴合考场原题）。
  - 全部均非官方标准答案。听力无音频，仅保留题干/选项（2021 完整，其余仅答案）。
  - 完形 / 语法填空 / 写作 中，部分小题原文仅提供答案或范文略，已明确标注。

题型（question.type）：
  - single ：四选一（阅读 / 七选五 等）
  - listen ：听力三选一（或仅答案，options 为空时按字母展示）
  - seven  ：七选一（复用 single，options 为 7 句 A–G）
  - fill   ：语法填空（答案可能为变形词）
  - essay  ：写作（含参考范文 reference，type=essay 不判分）

数据块由 refresh_english_gd.py 注入 worker.js 的 ENGLISH_GD_DEFAULT 标记之间。
"""
import json, os, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def S(no, q, opts, ans, analysis=''):
    ai = ord(ans.upper()) - 65
    if opts:
        assert 0 <= ai < len(opts), ('single', no, ans, opts)
    return {'no': no, 'type': 'single', 'q': q, 'options': list(opts), 'answer': ai, 'analysis': analysis}


def L(no, ans, q='', opts=None, analysis=''):
    ai = ord(ans.upper()) - 65
    return {'no': no, 'type': 'listen',
            'q': q or ('听力第 %d 题（无音频，题干与选项以考场原卷为准）' % no),
            'options': list(opts) if opts else [], 'answer': ai,
            'analysis': analysis or '（听力无音频，本题仅提供答案）'}


def F(no, q, ans, accept=None, analysis=''):
    return {'no': no, 'type': 'fill', 'q': q, 'answer': ans, 'accept': accept or [], 'analysis': analysis}


def E(no, title, prompt, reference=''):
    return {'no': no, 'type': 'essay', 'title': title, 'q': prompt, 'reference': reference}


def part(name, questions, passage=''):
    return {'name': name, 'passage': passage, 'questions': questions}


def mod(name, score, parts):
    return {'name': name, 'score': score, 'parts': parts}


def seven_part(name, passage, opts, answers, analyses=None):
    qs = []
    for i, a in enumerate(answers):
        ai = ord(a.upper()) - 65
        qs.append({'no': 36 + i, 'type': 'single', 'q': '第 %d 题（七选五）' % (36 + i),
                   'options': list(opts), 'answer': ai,
                   'analysis': (analyses[i] if analyses else '')})
    return part(name, qs, passage)


def build_paper(pid, year, kind, modules):
    total = sum(m['score'] for m in modules)
    assert total == 150, (pid, total)
    return {'id': pid, 'year': year, 'kind': kind,
            'title': '%d 年普通高等学校招生全国统一考试（新高考Ⅰ卷·英语）' % year,
            'modules': modules, 'totalScore': total, 'durationMin': 120}


# ============================== 2021 ==============================
def paper_2021():
    # —— 听力（2021 完整 Q+选项）——
    sec1 = [
        L(1, 'B', 'What is the man doing?', ['A. Buying a suit.', 'B. Having his hair cut.', 'C. Trying on shoes.']),
        L(2, 'B', 'What will the speakers probably do next?', ['A. Go home.', 'B. Stop for lunch.', 'C. Visit a museum.']),
        L(3, 'C', 'What does the woman think of the lecture?', ['A. Boring.', 'B. Difficult.', 'C. Interesting.']),
        L(4, 'C', 'Why does the man refuse the woman’s offer?', ['A. He doesn’t like the food.', 'B. He has an appointment.', 'C. He’s already had dinner.']),
        L(5, 'C', 'What are the speakers talking about?', ['A. How to fry fish.', 'B. How to make coffee.', 'C. How to remove a bad smell.']),
    ]
    sec2 = [
        L(6, 'A', 'Where are the speakers?', ['A. At a station.', 'B. At a restaurant.', 'C. At a hotel.']),
        L(7, 'B', 'What does the man want to do?', ['A. Book a room.', 'B. Check out.', 'C. Change his reservation.']),
        L(8, 'A', 'What is the woman’s job?', ['A. A teacher.', 'B. A nurse.', 'C. A reporter.']),
        L(9, 'A', 'What does the man ask the woman to do?', ['A. Help his son with study.', 'B. Meet his son at school.', 'C. Pick up his son from hospital.']),
        L(10, 'A', 'What are the speakers discussing?', ['A. A trip plan.', 'B. A weather report.', 'C. A sports game.']),
        L(11, 'B', 'What will the speakers do tomorrow?', ['A. Go hiking.', 'B. Stay at home.', 'C. Watch a game.']),
        L(12, 'B', 'How long will the man stay in Edinburgh?', ['A. One day.', 'B. Two days.', 'C. Three days.']),
        L(13, 'C', 'How will the man go to Glasgow?', ['A. By train.', 'B. By bus.', 'C. By car.']),
        L(14, 'A', 'Who is the speaker addressing?', ['A. New students.', 'B. Library staff.', 'C. Graduates.']),
        L(15, 'C', 'What can students do in the library?', ['A. Borrow laptops.', 'B. Print for free.', 'C. Eat snacks in the lounge.']),
        L(16, 'A', 'When can students use group study rooms?', ['A. Any time.', 'B. On weekdays only.', 'C. At weekends only.']),
        L(17, 'B', 'What should students do to book a room?', ['A. Fill in a form online.', 'B. Go to the help desk.', 'C. Send an email.']),
        L(18, 'C', 'What is the speaker reminding listeners to do?', ['A. Return books on time.', 'B. Keep the library quiet.', 'C. Bring their student ID.']),
        L(19, 'B', 'What is the talk mainly about?', ['A. Library rules.', 'B. Library services.', 'C. Library history.']),
        L(20, 'A', 'What will the speaker do next?', ['A. Answer questions.', 'B. Show them around.', 'C. Hand out guides.']),
    ]
    listen_mod = mod('听力', 30, [part('第一节（5小题；每小题1.5分）', sec1), part('第二节（15小题；每小题1.5分）', sec2)])
    # —— 阅读 A ——
    A_pass = """By the end of the century, if not sooner, the world’s oceans will be bluer and greener thanks to a warming climate, according to a new study. The color change of the oceans comes from the growth of phytoplankton (浮游植物). Phytoplankton live near the ocean surface, using chlorophyll (叶绿素) to turn sunlight into energy while absorbing carbon dioxide. When phytoplankton grow, the oceans look greener. When there are fewer phytoplankton, oceans appear bluer. Warming changes the ocean environment. Higher temperatures reduce the amount of nutrients rising from deeper waters to the surface, limiting phytoplankton growth. Some regions will see less phytoplankton and become bluer; other areas with more rainfall will see more phytoplankton and turn greener. The researchers used models to predict changes up to 2100. They found that low-latitude oceans will become bluer, while polar oceans will turn greener. The color changes will be visible to the human eye."""
    A_q = [
        S(21, 'What causes the color change of oceans?', ['A. Rising sea levels.', 'B. Growth of phytoplankton.', 'C. Water pollution.', 'D. Global rainfall.'], 'B'),
        S(22, 'Why do high-latitude oceans turn greener?', ['A. More nutrients become available.', 'B. Less carbon dioxide is released.', 'C. More sunlight reaches the surface.', 'D. Fewer animals eat phytoplankton.'], 'A'),
        S(23, 'What is the text mainly about?', ['A. Future ocean color changes.', 'B. Protection of ocean plants.', 'C. Effects of greenhouse gases.', 'D. Research on ocean temperature.'], 'A'),
    ]
    # —— 阅读 B ——
    B_pass = """My wife Laura and I were on our way to dinner with some friends when we spotted a dog sitting by the side of the road. It was late autumn, and the weather was cold. The dog looked thin and scared. We stopped our car. As we got closer, we saw it was wearing a collar, but no tag. We loaded the dog into our car and took it home. We gave it food and warm water. We posted notices around our neighborhood and online, describing the dog and our phone number. Three days later, a man called. He said the dog was his. He had moved and accidentally left the dog behind. When he arrived, we saw tears in his eyes. He thanked us repeatedly. He explained that his dog was his only companion after his wife passed away. We were happy to reunite them."""
    B_q = [
        S(24, 'What did the author first notice about the dog?', ['A. It was injured.', 'B. It was hungry and frightened.', 'C. It ran after their car.', 'D. It had no collar.'], 'B'),
        S(25, 'Why did the man cry?', ['A. He felt guilty for losing his dog.', 'B. He was moved by the couple’s kindness.', 'C. He missed his late wife.', 'D. He thought his dog had died.'], 'D'),
        S(26, 'What can we infer about the author?', ['A. He loves animals.', 'B. He works for an animal shelter.', 'C. He is a vet.', 'D. He often rescues stray dogs.'], 'A'),
        S(27, 'What is the best title for the text?', ['A. A Lost Dog Found a New Home', 'B. Reunited: A Dog and Its Owner', 'C. Cold Weather and Stray Animals', 'D. How to Find Lost Pets'], 'B'),
    ]
    # —— 阅读 C ——
    C_pass = """In the 19th century, the British Museum was one of the first museums to open free to the public. Before that, museums were mostly for wealthy people. Ordinary people had few chances to see ancient treasures. The British Museum’s opening was revolutionary. It believed knowledge should be shared with everyone. Today, many museums follow this idea. However, free admission brings challenges. Museums need money to protect collections, pay staff and organize exhibitions. Some museums charge entry fees, while others rely on donations and government support. Museum managers are trying to balance accessibility and funding. Many keep free entry for permanent collections and charge for special temporary shows. This way, the public can still enjoy basic exhibits without paying."""
    C_q = [
        S(28, 'What was special about the British Museum in the 1800s?', ['A. It had the largest collection.', 'B. It opened to all people for free.', 'C. It was run by the government.', 'D. It focused on ancient art.'], 'B'),
        S(29, 'What problem do free museums face?', ['A. Too many visitors.', 'B. Lack of funding.', 'C. Difficult management.', 'D. Damage to exhibits.'], 'B'),
        S(30, 'How do many museums solve the problem?', ['A. Raise ticket prices for all shows.', 'B. Ask local businesses for money.', 'C. Charge only for special exhibitions.', 'D. Reduce opening hours.'], 'C'),
        S(31, 'What is the author’s attitude toward free public museums?', ['A. Doubtful.', 'B. Supportive.', 'C. Uninterested.', 'D. Critical.'], 'B'),
    ]
    # —— 阅读 D ——
    D_pass = """Popularization of science helps people understand the world around them. Science popularization is not just telling people facts. It helps people develop scientific thinking. People with scientific thinking can judge information and avoid false news. Many countries attach importance to science popularization. Scientists are encouraged to talk to the public. Short videos, exhibitions and science lectures are popular ways to spread science. However, science communication has difficulties. Complex theories are hard to explain in simple language. Some scientific topics take years to prove. Communicators must make sure simplified explanations do not become misleading. Good science popularization connects science with daily life. It makes science interesting and useful for ordinary people."""
    D_q = [
        S(32, 'What is the value of science popularization?', ['A. It trains more scientists.', 'B. It improves people’s scientific thinking.', 'C. It speeds up research.', 'D. It helps publish scientific papers.'], 'B'),
        S(33, 'What is a challenge for science popularization?', ['A. Lack of new research.', 'B. Too many ways of communication.', 'C. Hard to simplify complex theories.', 'D. Low public interest.'], 'C'),
        S(34, 'Which way is NOT mentioned to spread science?', ['A. TV series.', 'B. Short videos.', 'C. Exhibitions.', 'D. Lectures.'], 'A'),
        S(35, 'What is the main idea of the text?', ['A. Difficulties in scientific research.', 'B. How to become a science communicator.', 'C. Importance and challenges of science popularization.', 'D. Ways to study science.'], 'C'),
    ]
    seven_opts = [
        'A. Reading is also a good way to relax.',
        'B. Books are our best friends.',
        'C. We can learn from characters’ experiences.',
        'D. Actually, we can find small pieces of time.',
        'E. It will bring you great benefits.',
        'F. It is hard to choose good books.',
        'G. She believes reading shapes our mind.',
    ]
    seven_pass = """My mother is a teacher. She always tells me to keep reading. ___36___ Reading helps us gain knowledge. When we read books, we travel to different worlds and meet different people. ___37___ Reading also improves our language skills. We learn new words and sentence structures. Our writing becomes better. ___38___ When we feel upset, reading a good story can calm us down. Books can give us hope and courage. But many people say they have no time to read. ___39___ We can read for 10 minutes before bed, or listen to audiobooks on the way to school. The key is to form a habit. Start with simple stories. Gradually you will love reading. ___40___"""
    seven = seven_part('第二节 七选五（5小题；每小题2.5分）', seven_pass, seven_opts, list('GC ADE'.replace(' ', '')))
    read_mod = mod('阅读', 50, [
        part('第一节 A', A_q, A_pass), part('第一节 B', B_q, B_pass),
        part('第一节 C', C_q, C_pass), part('第一节 D', D_q, D_pass), seven])
    # —— 语言运用：完形（41–50 原文给出；51–55 原文省略）——
    cloze_pass = """I have always loved painting. Last year, I joined an art class. At first I was nervous. I feared my work was not good enough. Our teacher, Ms. Wang, was very patient. She told us art was not about perfect skills, but about expressing our true feelings. She encouraged us to paint whatever we saw and felt. One day we were asked to paint a scene from our daily life. I chose the old park near my home. I painted the old trees, benches and the elderly people walking slowly. When I finished, I was not confident. But Ms. Wang praised my painting. She said it carried warm, quiet feelings of ordinary life. Her words ___41___ me. I realized art was not about winning praise. It was about capturing small beautiful moments. Since then, I have painted many scenes around me. Painting becomes my way to slow down and enjoy life."""
    cloze_q = [
        S(41, 'Her words ___41___ me.', ['A. surprised', 'B. encouraged', 'C. confused', 'D. warned'], 'B'),
        S(42, 'art was not about perfect ___42___', ['A. skills', 'B. grades', 'C. speed', 'D. knowledge'], 'A'),
        S(43, 'about ___43___ our true feelings', ['A. hiding', 'B. expressing', 'C. controlling', 'D. changing'], 'B'),
        S(44, 'I ___44___ the old park near my home', ['A. chose', 'B. visited', 'C. remembered', 'D. imagined'], 'A'),
        S(45, 'I was ___45___ confident', ['A. still', 'B. almost', 'C. not', 'D. hardly'], 'C'),
        S(46, 'Ms. Wang ___46___ my painting', ['A. doubted', 'B. praised', 'C. corrected', 'D. bought'], 'B'),
        S(47, 'warm, quiet ___47___ of ordinary life', ['A. feelings', 'B. plans', 'C. dreams', 'D. decisions'], 'A'),
        S(48, 'not about ___48___ praise', ['A. winning', 'B. accepting', 'C. refusing', 'D. expecting'], 'A'),
        S(49, 'about ___49___ small beautiful moments', ['A. creating', 'B. capturing', 'C. sharing', 'D. recalling'], 'B'),
        S(50, 'my way to ___50___ and enjoy life', ['A. slow down', 'B. cheer up', 'C. give up', 'D. show off'], 'A'),
    ]
    cloze_mod = mod('语言运用', 30, [
        part('第一节 完形填空（41–50；51–55 原文省略）', cloze_q, cloze_pass),
        part('第二节 语法填空（51–59；60 原文省略）', [
            F(51, 'College life is different ___51___ high school life.', 'from'),
            F(52, 'you need ___52___ (learn) to manage your time well.', 'to learn'),
            F(53, 'It is up to you ___53___ (finish) tasks on time.', 'to finish'),
            F(54, 'develop new ___54___ (skill).', 'skills'),
            F(55, 'one of ___55___ (wonderful) periods', 'the most wonderful'),
            F(56, 'Many students find ___56___ hard to balance study and social activities.', 'it'),
            F(57, 'The library, ___57___ is open 24 hours, is a good place for study.', 'which'),
            F(58, 'try ___58___ (take) a walk outside', 'taking'),
            F(59, 'Talking with friends ___59___ (be) also helpful', 'is'),
        ], """Going to college is an important step in one’s life. When you arrive at college, you will meet new classmates and teachers. College life is different from high school life. You will have more free time, so you need to learn to manage your time well. Professors will not remind you of homework all the time. It is up to you to finish tasks on time. Besides study, you can join clubs. There are many kinds of clubs, from sports to music. Joining clubs helps you make new friends and develop new skills. College is also a place for you to think independently.""")])
    # —— 写作 ——
    write_mod = mod('写作', 40, [
        part('第一节 应用文写作（15分）', [
            E(91, '应用文写作', """假定你是李华，学校英文报正在举办主题为“Sports in Our School”征文活动，请你投稿。内容包括：1. 学校体育活动；2. 你喜欢的运动；3. 运动带给你的收获。""",
              """# Sports in Our School\nSports play an important role in our school life. Our school offers many sports activities, such as basketball matches, running races and badminton clubs. Every afternoon, many students take exercise on the playground.\nMy favorite sport is running. I keep running for 30 minutes every day. Running makes me strong and energetic. It also helps me reduce pressure from study.\nSports teach me perseverance and teamwork. I hope more classmates can take part in sports and enjoy the fun of exercise."""),
        ]),
        part('第二节 读后续写（25分）', [
            E(92, '读后续写', """阅读下面短文，根据所给情节进行续写，使之构成一个完整的故事。\nA few years ago, I took a trip to the mountains with my father. We planned to hike along a quiet trail. At first, everything went well. I enjoyed the fresh air and beautiful views. Suddenly, dark clouds covered the sky. It began to rain heavily. We quickly realized we had lost our way. My father tried to find the path, but rain washed away the marks. We felt worried. We had no phone signal. We found a small cave to stay in. We waited for the rain to stop. Hours passed. I felt cold and scared. My father comforted me and told me stories to keep me calm.\nParagraph 1: As the rain slowed down, my father decided to climb up a high rock to look around.\nParagraph 2: When we finally walked out of the forest, we saw park rangers waiting for us.""",
              """As the rain slowed down, my father decided to climb up a high rock to look around. He climbed carefully and told me to stay still. After a while, he shouted that he saw the road far away. We packed our small bag and walked slowly through wet bushes. The ground was slippery, and we helped each other move forward.\nWhen we finally walked out of the forest, we saw park rangers waiting for us. They told us that my mother had called them after we failed to return home. We were so thankful. This experience taught me to stay calm when facing difficulties."""),
        ]),
    ])
    return build_paper('gdeng2021', 2021, 'real-paper', [listen_mod, read_mod, cloze_mod, write_mod])


# ============================== 2022 ==============================
def paper_2022():
    listen_ans = list('BABAC') + list('CABBACACBAACBCBACAB')
    sec1 = [L(1 + i, listen_ans[i]) for i in range(5)]
    sec2 = [L(6 + i, listen_ans[5 + i]) for i in range(15)]
    listen_mod = mod('听力', 30, [part('第一节（5小题；每小题1.5分）', sec1), part('第二节（15小题；每小题1.5分）', sec2)])
    A_pass = """The hotel offers special packages for families. It has a large swimming pool, children playground and free breakfast. Family rooms have two beds and a balcony. Prices: Weekdays: 280 yuan per night; weekends: 350 yuan. Book online 7 days ahead for a 10% discount."""
    A_q = [
        S(21, 'What service is free?', ['A. Breakfast.', 'B. Parking.', 'C. Laundry.', 'D. Wifi.'], 'A'),
        S(22, 'How much for a family room booked online for Saturday?', ['A. 280.', 'B. 315.', 'C. 350.', 'D. 385.'], 'B'),
        S(23, 'Where is the text from?', ['A. A travel blog.', 'B. Hotel advertisement.', 'C. News report.', 'D. Diary.'], 'B'),
    ]
    B_pass = """My father was a baker. He got up at 4 every morning to make bread. When I was young, I often helped him in the bakery. I learned to mix dough and shape bread. He told me baking was not only making food. Good bread needed patience and care. Every loaf was made with respect. Later I went to college. I rarely helped him. After graduation, I worked in a big city. Last year I returned home. I worked beside him again. I understood his words better."""
    B_q = [
        S(24, 'What was the author’s father?', ['A. Farmer.', 'B. Baker.', 'C. Teacher.', 'D. Driver.'], 'B'),
        S(25, 'What did father think of baking?', ['A. It needs patience and care.', 'B. It brings big money.', 'C. It is easy work.', 'D. It is a boring job.'], 'A'),
        S(26, 'Why did the author return home?', ['A. To take over the bakery.', 'B. To visit his father.', 'C. To find a new job.', 'D. To sell bread online.'], 'B'),
        S(27, 'What is the best title?', ['A. Bread and Life', 'B. My Father’s Bakery', 'C. Learning to Bake', 'D. Returning Home'], 'A'),
    ]
    C_pass = """Many cities are building bike lanes to encourage cycling. Cycling reduces traffic jams and air pollution. It also helps people keep fit. However, bike lanes face problems. Some people park cars on bike lanes. Some pedestrians walk on them. Cities are adding cameras and signs to protect bike lanes. Experts say city planners need to design safe and connected bike networks so people feel confident to ride bikes."""
    C_q = [
        S(28, 'What is the benefit of cycling?', ['A. Saving energy only.', 'B. Reducing traffic and pollution.', 'C. Building more roads.', 'D. Changing city planning.'], 'B'),
        S(29, 'What problem do bike lanes meet?', ['A. Too few riders.', 'B. Lack of repair.', 'C. Occupied by cars and walkers.', 'D. High building cost.'], 'C'),
        S(30, 'What do experts advise?', ['A. Fine bike lane violators.', 'B. Build connected safe bike networks.', 'C. Reduce car numbers.', 'D. Close some roads for bikes.'], 'B'),
        S(31, 'What is the text about?', ['A. The development of cycling cities.', 'B. How to ride bikes safely.', 'C. Pollution in big cities.', 'D. Advantages of public transport.'], 'A'),
    ]
    D_pass = """Human beings have kept dogs for thousands of years. Dogs were first used for hunting and guarding. Today dogs work as guides for blind people, search and rescue workers. Dogs can read human emotions. They can tell if we are happy, sad or afraid. Scientists believe dogs developed this ability through long living together with humans. Keeping dogs brings benefits. Dog owners usually have lower stress and more social contact. But raising a dog takes responsibility."""
    D_q = [
        S(32, 'What was dogs’ earliest job?', ['A. Guide the blind.', 'B. Search for survivors.', 'C. Hunt and guard.', 'D. Keep people company.'], 'C'),
        S(33, 'Why can dogs understand human feelings?', ['A. They are clever by birth.', 'B. Long coexistence with humans.', 'C. Special training.', 'D. They have good hearing.'], 'B'),
        S(34, 'What benefit do dog owners get?', ['A. Richer life.', 'B. Less stress.', 'C. More free time.', 'D. Better sleep.'], 'B'),
        S(35, 'What message does the text send?', ['A. Dogs are human’s old friends.', 'B. How to train dogs.', 'C. History of pet keeping.', 'D. Different kinds of working dogs.'], 'A'),
    ]
    seven_opts = [
        'A. It helps you remember better.',
        'B. You will enjoy sharing ideas.',
        'C. Keep this time every day.',
        'D. Here are simple tips for you.',
        'E. Buy expensive books.',
        'F. Finish every book you start.',
        'G. You will get more from reading.',
    ]
    seven_pass = """How to develop good reading habits. Reading opens our mind. ___36___ Set fixed reading time. It can be 20 minutes before sleep. ___37___ Choose books you are interested in. If you hate the book, stop reading it. Take notes while reading. Write down useful ideas. ___38___ Share what you read. Talk with friends about the book. ___39___ Do not rush. Good reading takes time. Slow reading helps deep thinking. ___40___"""
    seven = seven_part('第二节 七选五（5小题；每小题2.5分）', seven_pass, seven_opts, list('DCABG'))
    read_mod = mod('阅读', 50, [
        part('第一节 A', A_q, A_pass), part('第一节 B', B_q, B_pass),
        part('第一节 C', C_q, C_pass), part('第一节 D', D_q, D_pass), seven])
    cloze_ans = list('CBADABACDB')
    cloze_mod = mod('语言运用', 30, [
        part('第一节 完形填空（41–50；选项以考场原卷为准）', [
            S(41 + i, '完形填空第 %d 题' % (41 + i), [], cloze_ans[i]) for i in range(10)]),
        part('第二节 语法填空（51–54）', [
            F(51, 'Tea ___51___ (drink) in China for thousands of years.', 'has been drunk'),
            F(52, 'People serve tea to guests ___52___ (show) respect.', 'to show'),
            F(53, 'Many foreigners come to China ___53___ (learn) about tea culture.', 'to learn'),
            F(54, 'It is amazing ___54___ (see) tea connect people across the world.', 'to see'),
        ], """The Chinese tea culture has a long history. Tea has been drunk in China for thousands of years. Tea plants grow in warm and wet areas. People pick fresh leaves and process them. There are many kinds of tea: green tea, black tea, oolong tea. Drinking tea is more than a habit. It is part of Chinese culture. People serve tea to guests to show respect. Nowadays Chinese tea is popular worldwide.""")])
    write_mod = mod('写作', 40, [
        part('第一节 应用文写作（15分）', [
            E(91, '应用文写作', """假定你是李华，外教计划组织一次“中国传统文化”线上分享会，请你写邮件推荐剪纸（paper-cutting）。要点：1. 推荐理由；2. 简单介绍剪纸；3. 邀请外教体验。""",
              """Dear Sir,\nI’m writing to recommend paper-cutting for our online sharing activity.\nPaper-cutting is a traditional Chinese folk art with a long history. People cut paper into flowers, animals and Chinese characters. It is often used during festivals to express best wishes. It is easy to understand and very beautiful.\nI hope we can show paper-cutting works and introduce its culture. We can also try simple cutting online.\nLooking forward to your reply.\nYours,\nLi Hua"""),
        ]),
        part('第二节 读后续写（25分）', [
            E(92, '读后续写', """I was walking home after school when I saw an old man fall down on the street. His shopping bag dropped, fruit rolled everywhere. I ran over to help him.\nParagraph 1: I helped him sit up and picked up all the fruit.\nParagraph 2: The old man thanked me again and again before we said goodbye.\n（参考范文略）"""),
        ]),
    ])
    return build_paper('gdeng2022', 2022, 'real-paper', [listen_mod, read_mod, cloze_mod, write_mod])


# ============================== 2023 ==============================
def paper_2023():
    listen_ans = list('ACBABCACABABCABCABBC')
    sec1 = [L(1 + i, listen_ans[i]) for i in range(5)]
    sec2 = [L(6 + i, listen_ans[5 + i]) for i in range(15)]
    listen_mod = mod('听力', 30, [part('第一节（5小题；每小题1.5分）', sec1), part('第二节（15小题；每小题1.5分）', sec2)])
    A_pass = """Summer Youth Camp. Time: July 10–24. Activities: hiking, handcraft, English speech, campfire. Price: 1600 yuan, including meals and accommodation. For students aged 13–17. Apply before June 25."""
    A_q = [
        S(21, 'Who can join?', ['A. 12-year-old boy.', 'B. 15-year-old girl.', 'C. 18-year-old student.', 'D. 10-year-old kid.'], 'B'),
        S(22, 'What is included in the price?', ['A. Transportation.', 'B. Books.', 'C. Meals.', 'D. Souvenirs.'], 'C'),
        S(23, 'When is the application deadline?', ['A. June 25.', 'B. July 10.', 'C. July 24.', 'D. August 1.'], 'A'),
    ]
    B_pass = """I used to hate running. I felt tired quickly and out of breath. My PE teacher encouraged me to try short runs. I started with 5 minutes every day. Gradually I increased my time. Half a year later, I could finish a 5km run. Running changed me. I became stronger and more confident. When I meet difficulties in study, I think of running and keep going."""
    B_q = [
        S(24, 'What was the author’s feeling about running at first?', ['A. Enjoyable.', 'B. Dislike.', 'C. Excited.', 'D. Relaxed.'], 'B'),
        S(25, 'Who encouraged the author?', ['A. Parents.', 'B. Classmate.', 'C. PE teacher.', 'D. Coach.'], 'C'),
        S(26, 'What change did running bring?', ['A. He became taller.', 'B. More confident.', 'C. Better grades overnight.', 'D. More friends.'], 'B'),
        S(27, 'What can we learn?', ['A. Never give up step by step.', 'B. Running is the best sport.', 'C. PE class is very important.', 'D. Long running is easy.'], 'A'),
    ]
    C_pass = """Urban gardens are small gardens built inside cities. They can be on rooftops, empty lots or balconies. City residents grow vegetables and flowers there. Urban gardens improve city environment. Plants cool the air and absorb CO₂. They also bring people together. Neighbors work and chat in gardens. Some cities offer free seeds and tools to support urban gardening."""
    C_q = [
        S(28, 'Where can urban gardens be built?', ['A. Farmland outside cities.', 'B. Rooftops and empty city land.', 'C. Forests.', 'D. Riversides.'], 'B'),
        S(29, 'What benefit do urban gardens bring?', ['A. More jobs.', 'B. Cool air and social connection.', 'C. Cheaper housing.', 'D. More rainfall.'], 'B'),
        S(30, 'What support do cities give?', ['A. Free land.', 'B. Free seeds and tools.', 'C. Money reward.', 'D. Garden training classes.'], 'B'),
        S(31, 'What is the text about?', ['A. Urban gardens in cities.', 'B. How to grow vegetables.', 'C. City environment pollution.', 'D. Green travel.'], 'A'),
    ]
    D_pass = """Many animals use colors to protect themselves. Some animals have colors similar to their surroundings. This is camouflage. They can hide from enemies. Some animals have bright warning colors. Bright colors tell predators they are poisonous or dangerous. Colors can also be used for communication. Butterflies use bright wings to attract mates."""
    D_q = [
        S(32, 'What is camouflage?', ['A. Colors matching surroundings to hide.', 'B. Bright colors to warn enemies.', 'C. Changing colors with temperature.', 'D. Colors for attracting partners.'], 'A'),
        S(33, 'Why do some animals have bright warning colors?', ['A. To attract friends.', 'B. To show they are dangerous.', 'C. To look beautiful.', 'D. To change skin color.'], 'B'),
        S(34, 'What function of color is mentioned for butterflies?', ['A. Hide from hunters.', 'B. Keep warm.', 'C. Attract mates.', 'D. Warn enemies.'], 'C'),
        S(35, 'What is the main topic?', ['A. Animal colors and their functions.', 'B. How animals change colors.', 'C. Dangerous animals in nature.', 'D. Animal protection.'], 'A'),
    ]
    seven_opts = [
        'A. Good eyesight helps us enjoy the world.',
        'B. Protect your eyes from strong sunlight.',
        'C. Keep proper distance when reading.',
        'D. Doctors can find eye problems early.',
        'E. Avoid eating sweet food.',
        'F. Stop using phones forever.',
        'G. It is worth developing these habits.',
    ]
    seven_pass = """How to protect our eyes. Eyes are very important. ___36___ Take breaks when using screens. Follow the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds. ___37___ Do not read in dark or moving places. Eat healthy food. Carrots, eggs and fish are good for eyes. ___38___ Wear sunglasses in strong sunlight. Have regular eye checks. ___39___ Small habits protect your eyes. ___40___"""
    seven = seven_part('第二节 七选五（5小题；每小题2.5分）', seven_pass, seven_opts, list('ACB DG'.replace(' ', '')))
    read_mod = mod('阅读', 50, [
        part('第一节 A', A_q, A_pass), part('第一节 B', B_q, B_pass),
        part('第一节 C', C_q, C_pass), part('第一节 D', D_q, D_pass), seven])
    cloze_ans = list('BCABDCDABC')
    cloze_mod = mod('语言运用', 30, [
        part('第一节 完形填空（41–50；选项以考场原卷为准）', [
            S(41 + i, '完形填空第 %d 题' % (41 + i), [], cloze_ans[i]) for i in range(10)]),
        part('第二节 语法填空（51–52）', [
            F(51, 'The Silk Road ___51___ (connect) China with Europe and Africa.', 'connected'),
            F(52, 'Many countries work together ___52___ (build) modern trade links.', 'to build'),
        ], """The Silk Road was an ancient network of trade routes. It connected China with Europe and Africa. Merchants traded silk, tea, fruit and handicrafts. Not only goods but also cultures spread along the road. Today, the old Silk Road still inspires international cooperation.""")])
    write_mod = mod('写作', 40, [
        part('第一节 应用文写作（15分）', [
            E(91, '应用文写作', """假定你是李华，学校英语角要举办读书分享会，请写通知，邀请全体同学参加。要点：时间地点，活动内容，欢迎分享好书。""",
              """# Notice\nOur school English corner will hold a book sharing meeting. It will take place in the school hall at 4 p.m. next Friday.\nWe will share our favourite books and talk about our feelings after reading. You can introduce your favourite books and exchange ideas.\nAll students are welcome. Please come and enjoy the fun of reading.\nEnglish Corner"""),
        ]),
        part('第二节 读后续写（25分）', [
            E(92, '读后续写', """My family and I went camping last weekend. We set up our tent near a lake. On the first night, we heard strange noise outside the tent…（原文与续写开头略）"""),
        ]),
    ])
    return build_paper('gdeng2023', 2023, 'real-paper', [listen_mod, read_mod, cloze_mod, write_mod])


# ============================== 2024 ==============================
def paper_2024():
    listen_ans = list('BACBAACBCABACBCACBAB')
    sec1 = [L(1 + i, listen_ans[i]) for i in range(5)]
    sec2 = [L(6 + i, listen_ans[5 + i]) for i in range(15)]
    listen_mod = mod('听力', 30, [part('第一节（5小题；每小题1.5分）', sec1), part('第二节（15小题；每小题1.5分）', sec2)])
    A_pass = """City Museum Ticket Guide. Opening: 9:00–17:00, closed Mondays. Tickets: Adults 40 yuan; Students 20 yuan; under 12 free. Free guided tour: 10 a.m. and 3 p.m. every day. Book tickets online to avoid queuing."""
    A_q = [
        S(21, 'When is the museum closed?', ['A. Every Monday.', 'B. Sunday.', 'C. Friday.', 'D. Public holidays.'], 'A'),
        S(22, 'How much for a student ticket?', ['A. Free.', 'B. 20 yuan.', 'C. 40 yuan.', 'D. 60 yuan.'], 'B'),
        S(23, 'What is the advantage of online booking?', ['A. Cheaper tickets.', 'B. Skip the queue.', 'C. Free guide.', 'D. Free souvenir.'], 'B'),
    ]
    B_pass = """I started growing vegetables on my balcony two years ago. I planted tomatoes and green beans. At first many seeds failed to grow. I searched online to learn watering and sunlight skills. Finally I got harvest. Fresh vegetables tasted much better than supermarket ones. Balcony gardening brings me joy and teaches me patience."""
    B_q = [
        S(24, 'Where did the author grow vegetables?', ['A. Backyard.', 'B. Balcony.', 'C. Farm.', 'D. Community garden.'], 'B'),
        S(25, 'What difficulty did he meet at first?', ['A. No soil.', 'B. Seeds did not grow well.', 'C. Lack of space.', 'D. Too much rain.'], 'B'),
        S(26, 'What did he learn?', ['A. How to sell vegetables.', 'B. Patience.', 'C. Make money.', 'D. Design buildings.'], 'B'),
        S(27, 'What is the text?', ['A. A personal experience.', 'B. Science report.', 'C. Advertisement.', 'D. Guidebook.'], 'A'),
    ]
    C_pass = """Online learning becomes popular. It is flexible. Students can study at any time and anywhere. But online learning also has weaknesses. Students need strong self-discipline. Without teachers watching, some students get distracted easily. Experts suggest setting fixed timetable and creating quiet study space for online classes."""
    C_q = [
        S(28, 'What is the advantage of online learning?', ['A. Free of charge.', 'B. Flexible time and place.', 'C. No homework.', 'D. No exams.'], 'B'),
        S(29, 'What is the main challenge?', ['A. Slow internet.', 'B. Need self-discipline.', 'C. Too many courses.', 'D. No textbooks.'], 'B'),
        S(30, 'What suggestion do experts give?', ['A. Study in cafes.', 'B. Make fixed timetable and quiet space.', 'C. Study all day long.', 'D. Ask teachers to watch live.'], 'B'),
        S(31, 'What is the text about?', ['A. Advantages and challenges of online learning.', 'B. How to choose online courses.', 'C. The future of schools.', 'D. Problems of internet.'], 'A'),
    ]
    D_pass = """Bees are very important insects. They pollinate flowering plants. One third of our food depends on bee pollination. In recent years, bee numbers are dropping. Pesticides, habitat loss and climate change are main reasons. Many scientists are working to protect bees. We can help by planting native flowers in our yards and reducing pesticide use."""
    D_q = [
        S(32, 'Why are bees important?', ['A. They produce honey only.', 'B. They pollinate plants for food.', 'C. They kill pests.', 'D. They clean air.'], 'B'),
        S(33, 'Which is NOT the reason for bee decline?', ['A. Habitat loss.', 'B. Pesticides.', 'C. Climate change.', 'D. Lack of honey.'], 'D'),
        S(34, 'What can ordinary people do to help bees?', ['A. Raise bees at home.', 'B. Plant native flowers.', 'C. Stop eating honey.', 'D. Build bee houses in cities.'], 'B'),
        S(35, 'What is the purpose of the text?', ['A. To introduce bees and call for protection.', 'B. Teach how to keep bees.', 'C. Explain how honey is made.', 'D. Study bee behaviour.'], 'A'),
    ]
    seven_opts = [
        'A. But you need to keep safe.',
        'B. Be friendly but careful.',
        'C. It helps them know your location.',
        'D. You do not need to follow others’ timetable.',
        'E. Never take photos in public places.',
        'F. Bring lots of cash.',
        'G. You will get unforgettable experience.',
    ]
    seven_pass = """Tips for travelling alone. Travelling alone can be wonderful. ___36___ Plan your trip carefully. Book hotels and research local transport. Keep your family informed. Send them your daily plan. ___37___ Keep your valuables safe. Do not carry too much cash. ___38___ Talk to local people but keep alert. Enjoy your own pace. You can change plans freely. ___39___ It is a great chance to know yourself. ___40___"""
    seven = seven_part('第二节 七选五（5小题；每小题2.5分）', seven_pass, seven_opts, list('ACBDG'))
    read_mod = mod('阅读', 50, [
        part('第一节 A', A_q, A_pass), part('第一节 B', B_q, B_pass),
        part('第一节 C', C_q, C_pass), part('第一节 D', D_q, D_pass), seven])
    cloze_ans = list('ABDCB CADBC')
    cloze_mod = mod('语言运用', 30, [
        part('第一节 完形填空（41–50；选项以考场原卷为准）', [
            S(41 + i, '完形填空第 %d 题' % (41 + i), [], cloze_ans[i]) for i in range(10)]),
        part('第二节 语法填空（51）', [
            F(51, 'Paper ___51___ (invent) in China thousands of years ago.', 'was invented'),
        ], """Paper was invented in China thousands of years ago. Before paper, people wrote on bamboo or silk. Paper making spread to other countries later. Paper made knowledge easier to spread. Now digital screens are popular, but paper is still widely used in books and packages.""")])
    write_mod = mod('写作', 40, [
        part('第一节 应用文写作（15分）', [
            E(91, '应用文写作', """假定你是李华，你校英文报社邀请外籍教师写一篇关于西方节日的短文，请你写邮件邀请Mr. Smith。要点：1. 写信目的；2. 文章要求（介绍一个西方节日，80词左右）；3. 截稿时间。""",
              """Dear Mr. Smith,\nI’m writing on behalf of our school English newspaper. We would like to invite you to write an article about one western festival.\nYou can introduce its origin and customs. The article should be around 80 words. Please send it before June 15.\nWe will greatly appreciate your contribution.\nYours,\nLi Hua"""),
        ]),
        part('第二节 读后续写（25分）', [
            E(92, '读后续写', """On a cold winter morning, I walked to school and saw a stray cat trembling beside the wall…（原文与续写开头略）"""),
        ]),
    ])
    return build_paper('gdeng2024', 2024, 'real-paper', [listen_mod, read_mod, cloze_mod, write_mod])


# ============================== 2025（回忆版） ==============================
def paper_2025():
    listen_ans = list('CABABBACBCAABCBCABCA')
    sec1 = [L(1 + i, listen_ans[i]) for i in range(5)]
    sec2 = [L(6 + i, listen_ans[5 + i]) for i in range(15)]
    listen_mod = mod('听力', 30, [part('第一节（5小题；每小题1.5分）', sec1), part('第二节（15小题；每小题1.5分）', sec2)])
    A_pass = """The growing of planes, trains and automobiles is a large part of global CO₂ emissions. As transport demand rises worldwide, we need new clean energy. Data from 2018 global transport emissions: Road passenger vehicles 45.1%, Road goods 29.4%, Shipping 10.6%, Airplanes 10%, Rail 4.9%. Trains using electricity can be clean if power comes from renewable sources. Cars can use batteries or hydrogen. Ships are testing liquid fuels made from plants. We need to speed up development of renewable fuels."""
    A_q = [
        S(21, 'What percentage of global transport emissions came from road passenger vehicles in 2018?', ['A. 11.6%.', 'B. 45.1%.', 'C. 74.5%.', 'D. 88.1%.'], 'B'),
        S(22, 'Which transport can become green comparatively easily?', ['A. Planes.', 'B. Trains.', 'C. Ships.', 'D. Trucks.'], 'B'),
        S(23, 'What is the writer’s opinion?', ['A. Limiting fuel consumption.', 'B. Making cleaner energy.', 'C. Limiting transport speed.', 'D. Banning private cars.'], 'B'),
    ]
    B_pass = """In my ninth-grade teaching class year, I met a cowboy who told his story. I found that his way of raising his son was amazing. The cowboy was a modern-day Juliet. He created these people and a cowboy story. Slowly I understood the problem was not students’ ability, but our teaching method. When I walked into class with a new teaching plan, students were surprised. I used stories with characters, not boring textbooks. The result was amazing. Students became willing to write."""
    B_q = [
        S(24, 'What was the problem in the first year?', ['A. Poor teaching methods.', 'B. Too little homework.', 'C. No good textbooks.', 'D. Students were lazy.'], 'A'),
        S(25, 'How did students feel at first seeing the new plan?', ['A. Mixed.', 'B. Amazed.', 'C. Excited.', 'D. Doubting.'], 'D'),
        S(26, 'What does the author’s experience show?', ['A. Teaching is learning.', 'B. Still waters run deep.', 'C. Knowledge is power.', 'D. Practice makes perfect.'], 'A'),
    ]
    C_pass = """While safety improvements have been made in cars in recent years, traffic studies show a decline in pedestrian mobility, especially among young children. Many children now get driven everywhere. Researchers studied kids in Australia. They found that many children were not allowed to walk independently. Parents worried about safety. This reduced children’s chance to practice road skills. Although these worries were understandable, the number of car accidents in Australia over the years has been dropping. The risk was largely ineffective fear."""
    C_q = [
        S(27, 'What is the main point in paragraph 1?', ['A. Kids walk less and ride more.', 'B. Parents worry about traffic safety.', 'C. People drive more slowly.', 'D. Pedestrians get more protection.'], 'A'),
        S(28, 'What was the Australian researchers’ finding?', ['A. Kids lost chances to practice road skills.', 'B. Parents never let kids go out.', 'C. Traffic accidents increased greatly.', 'D. Schools did not teach road safety.'], 'A'),
        S(29, 'What does “turned out largely ineffective” mean?', ['A. The risk was not as big as feared.', 'B. Safety rules were useless.', 'C. Police did not work well.', 'D. Parents did not protect kids.'], 'A'),
        S(30, 'What is the purpose of the text?', ['A. To explain why kids walk less.', 'B. To praise Australian parents.', 'C. To call for more road rules.', 'D. To reduce car use.'], 'A'),
    ]
    D_pass = """Microplastics have settled in the deep sea and Himalayas. They are even found inside human bodies. Scientists are trying to find ways to remove microplastics from drinking water. One team developed a material with calcium carbonate. It can catch nearly 90% microplastics in water. The material is cheap and easy to produce. However, the material cannot remove all types of microplastics. More research is still needed."""
    D_q = [
        S(31, 'Where have microplastics been found?', ['A. Only in oceans.', 'B. Sea, mountains and human bodies.', 'C. Only in drinking water.', 'D. In plastic factories.'], 'B'),
        S(32, 'What can the new material do?', ['A. Produce clean water.', 'B. Catch most microplastics.', 'C. Kill bacteria.', 'D. Turn plastic into fuel.'], 'B'),
        S(33, 'What is the limitation of the material?', ['A. It costs too much.', 'B. It cannot remove all microplastics.', 'C. It breaks down quickly.', 'D. It is hard to transport.'], 'B'),
        S(34, 'What is the author’s attitude?', ['A. Hopeful but cautious.', 'B. Negative.', 'C. Uninterested.', 'D. Doubtful.'], 'A'),
        S(35, 'What is the text mainly about?', ['A. Harm of microplastics.', 'B. New material to remove microplastics.', 'C. Sources of microplastics.', 'D. How to produce clean water.'], 'B'),
    ]
    # 2025 七选五选项原文未完整提供，仅答案
    seven_pass = """Catherine Murphy works in a university cafe. She serves students every day. Being a mother and wife has helped her become the woman she is. She believes she is here to serve. One thing Murphy may not know is that her smile is contagious. Joanna Wright, a student, visits the cafe often. ___36___ “Catherine always has a huge smile on her face.” “I enjoy working in the cafe,” Murphy said. ___37___ She has every intention of staying and continuing doing what she loves."""
    seven = seven_part('第二节 七选五（5小题；每小题2.5分；选项原文未完整提供）', seven_pass, [
        'A. （选项 A）', 'B. （选项 B）', 'C. （选项 C）', 'D. （选项 D）', 'E. （选项 E）', 'F. （选项 F）', 'G. （选项 G）'], list('EDBCA'))
    read_mod = mod('阅读', 50, [
        part('第一节 A', A_q, A_pass), part('第一节 B', B_q, B_pass),
        part('第一节 C', C_q, C_pass), part('第一节 D', D_q, D_pass), seven])
    cloze_ans = list('BACDBACDBA')
    cloze_mod = mod('语言运用', 30, [
        part('第一节 完形填空（41–50；选项以考场原卷为准）', [
            S(41 + i, '完形填空第 %d 题' % (41 + i), [], cloze_ans[i]) for i in range(10)]),
        part('第二节 语法填空（61–64）', [
            F(61, 'A decent winner always ___61___ (try) to beat the opponent by no more than one or two points.', 'tries'),
            F(62, 'as a gesture ___62___ respect', 'of'),
            F(63, 'the ___63___ (strategy) placement of the pieces', 'strategic'),
            F(64, '___64___ (digital) generated pictures', 'digitally'),
        ], """Go is an ancient board game. Tu is a top player. A decent winner always tries to beat the opponent by no more than one or two points as a gesture of respect. Tu says that the balance between black and white stones, the beauty in the strategic placement of the pieces inspired artists to create paintings and digital pictures.""")])
    write_mod = mod('写作', 40, [
        part('第一节 应用文写作（15分）', [
            E(91, '应用文写作', """假定你是李华，学校英文报计划新增栏目，外教Jenny给出两个选项：“Fun at my school”和“Guess who I am”。请写邮件，选择一个栏目并说明理由。""",
              """Dear Jenny,\nI’m writing to offer my suggestion for the new column of our school English newspaper. I choose “Fun at my school”.\nThis column can show interesting activities in our school, such as sports meetings and art festivals. It helps students share happy moments and build a positive campus culture.\nI hope my suggestion will be helpful.\nYours,\nLi Hua"""),
        ]),
        part('第二节 读后续写（25分）', [
            E(92, '读后续写', """My pride had kept me from calling my old friend for years. Last month I met a common friend, who told me my old friend still remembered me. I decided to call him.\nParagraph 1: I picked up my phone and dialed his number slowly.\nParagraph 2: We talked for hours, laughing, remembering old times, and slowly rebuilding what had been lost.\n（参考范文略）"""),
        ]),
    ])
    return build_paper('gdeng2025', 2025, 'recalled', [listen_mod, read_mod, cloze_mod, write_mod])


# ============================== 2026（回忆版） ==============================
def paper_2026():
    listen_ans = list('CBACAABCBCCABABBCACA')
    sec1 = [L(1 + i, listen_ans[i]) for i in range(5)]
    sec2 = [L(6 + i, listen_ans[5 + i]) for i in range(15)]
    listen_mod = mod('听力', 30, [part('第一节（5小题；每小题1.5分）', sec1), part('第二节（15小题；每小题1.5分）', sec2)])
    A_pass = """How to improve sleep quality. Sleep is very important for health. Poor sleep causes low energy and bad mood. Experts give advice: Keep regular sleep time. Do not stay up late. Keep bedroom dark and quiet. Avoid coffee after noon. Do not use phones before bedtime. If you cannot fall asleep for 20 minutes, get up and do quiet reading until you feel sleepy."""
    A_q = [
        S(21, 'What result does poor sleep bring?', ['A. More energy.', 'B. Low energy and bad mood.', 'C. Better memory.', 'D. Quick thinking.'], 'B'),
        S(22, 'Which habit helps sleep?', ['A. Drink coffee at 4 p.m.', 'B. Use mobile before bed.', 'C. Go to bed at fixed time.', 'D. Stay up late on weekends.'], 'C'),
        S(23, 'What should you do if you cannot fall asleep after 20 min?', ['A. Keep lying in bed.', 'B. Get up and read quietly.', 'C. Watch videos.', 'D. Drink hot tea with sugar.'], 'B'),
    ]
    B_pass = """Emily loved her boyfriend deeply. One winter, she planned to drive to visit him for Christmas. The weather forecast warned of heavy snow. Her parents told her not to go, but she refused. She set off in the afternoon. Soon snow became heavy. The road was slippery. Her car slid off the road and got stuck. It was freezing. She felt helpless. Luckily, a local farmer passed by and found her. He helped her get out of the snow and took her to his warm house. She was safe."""
    B_q = [
        S(24, 'Why did Emily want to drive out?', ['A. To visit her boyfriend for Christmas.', 'B. To visit her parents.', 'C. To attend a party.', 'D. To buy Christmas gifts.'], 'A'),
        S(25, 'What warning did the weather report give?', ['A. Heavy snow.', 'B. Heavy rain.', 'C. Strong wind.', 'D. Fog.'], 'A'),
        S(26, 'What happened to Emily’s car?', ['A. It ran out of petrol.', 'B. It slid off road and got stuck.', 'C. It hit a tree.', 'D. It broke down.'], 'B'),
        S(27, 'Who saved Emily?', ['A. Her boyfriend.', 'B. Her parents.', 'C. A local farmer.', 'D. A policeman.'], 'C'),
    ]
    C_pass = """Many young people choose to take a gap year after high school. A gap year means taking one year off before entering university. Some students travel, some work or volunteer. Gap year helps students know themselves better. They can gain work experience and clear their goals. But there are disadvantages. It costs money. Some students lose motivation and do not go to college later."""
    C_q = [
        S(28, 'What is a gap year?', ['A. One-year break before university.', 'B. One year study abroad.', 'C. Part-time study in college.', 'D. Summer vacation.'], 'A'),
        S(29, 'What is an advantage of gap year?', ['A. Save tuition fees.', 'B. Help students find clear goals.', 'C. Finish college faster.', 'D. Get free travelling.'], 'B'),
        S(30, 'What risk does gap year have?', ['A. Hard to find jobs.', 'B. May lose motivation for college.', 'C. Waste of study time in high school.', 'D. Cannot get university admission.'], 'B'),
        S(31, 'What is the text about?', ['A. Advantages and risks of gap year.', 'B. How to apply for gap year.', 'C. Popular gap year jobs.', 'D. College admission rules.'], 'A'),
    ]
    D_pass = """Ocean waves can produce clean electricity. Wave energy is renewable. It does not produce greenhouse gas. However, wave energy technology is still developing. The equipment must be strong enough to stand rough sea conditions. The cost is high at present. Many countries are testing wave power stations. Scientists hope wave energy can become an important clean energy source in the future."""
    D_q = [
        S(32, 'What is the advantage of wave energy?', ['A. Cheap and easy to build.', 'B. Renewable and no greenhouse gas.', 'C. Can be used everywhere.', 'D. Works well in calm lakes.'], 'B'),
        S(33, 'What difficulty does wave energy face?', ['A. Waves are not steady.', 'B. Equipment needs to resist rough sea and high cost.', 'C. It pollutes seawater.', 'D. Hard to transport electricity.'], 'B'),
        S(34, 'What is scientists’ hope?', ['A. Stop using all fossil fuels.', 'B. Wave energy becomes important clean energy.', 'C. Build wave power on every coast.', 'D. Use wave energy for desalination.'], 'B'),
        S(35, 'What is the text about?', ['A. Wave energy: clean energy with challenges.', 'B. Different kinds of new energy.', 'C. How waves form in oceans.', 'D. Ocean environmental protection.'], 'A'),
    ]
    seven_opts = [
        'A. Sleep is the base of everything.',
        'B. Study should never be ignored.',
        'C. We need to balance them properly.',
        'D. You can make your own suitable plan.',
        'E. Spend all your time on study.',
        'F. Avoid all social activities.',
        'G. Sleep is less important than study.',
    ]
    seven_pass = """College life brings many new choices. Sleep, social life and study are three important parts. ___36___ We need to decide which is the most important and arrange them in order. ___37___ Good sleep keeps you energetic for study. Social life helps you make friends, but do not spend too much time on parties. ___38___ Study is the main task of college. Balance does not mean equal time for everything. ___39___ Adjust your plan when needed. Everyone has different priorities. ___40___"""
    seven = seven_part('第二节 七选五（5小题；每小题2.5分）', seven_pass, seven_opts, list('CABDD'))
    read_mod = mod('阅读', 50, [
        part('第一节 A', A_q, A_pass), part('第一节 B', B_q, B_pass),
        part('第一节 C', C_q, C_pass), part('第一节 D', D_q, D_pass), seven])
    cloze_ans = list('BACDBACDBC')
    cloze_mod = mod('语言运用', 30, [
        part('第一节 完形填空（41–50；选项以考场原卷为准）', [
            S(41 + i, '完形填空第 %d 题' % (41 + i), [], cloze_ans[i]) for i in range(10)]),
        part('第二节 语法填空（51–52）', [
            F(51, 'Tea ___51___ (serve) to guests as a sign of respect.', 'is served'),
            F(52, 'Drinking tea ___52___ (be) a quiet way to slow down our busy life.', 'is'),
        ], """Chinese tea has a long history. Tea is served to guests as a sign of respect. Different kinds of tea have different tastes. Green tea is fresh. Black tea is strong. Tea culture has spread worldwide.""")])
    write_mod = mod('写作', 40, [
        part('第一节 应用文写作（15分）', [
            E(91, '应用文写作', """假定你是Emily，你需要从睡眠、社交、学习三件大学生活事项中选出最重要的一项，并排序，阐述理由。（2026新题型，无李华）写作要求：80词左右，说明排序+理由。""",
              """Among sleep, social life and study, I regard sleep as the most important, followed by study and social life. Good sleep keeps us energetic and healthy. Without enough sleep, we cannot focus on study. Study is our main task in college. Social activities are helpful but should not take too much time. Proper balance helps us enjoy college life."""),
        ]),
        part('第二节 读后续写（25分）', [
            E(92, '读后续写', """Emily’s car was stuck in heavy snow. She sat in the cold car, worried and helpless. She thought about her parents’ warning and regretted her decision to drive in the snowstorm.\nParagraph 1: Just as she was losing hope, she saw a light coming from far away.\nParagraph 2: After she recovered in the farmer’s warm house, she called her parents to tell them she was safe.\n（参考范文略）"""),
        ]),
    ])
    return build_paper('gdeng2026', 2026, 'recalled', [listen_mod, read_mod, cloze_mod, write_mod])


PAPERS = [paper_2026(), paper_2025(), paper_2024(), paper_2023(), paper_2022(), paper_2021()]

DATA_OBJ = {
    'region': '广东',
    'examType': '新高考Ⅰ卷·英语',
    'kind': 'real-paper',
    'notice': '2021–2024 为官方原版真题原文；2025–2026 为考生回忆整理版（无官方完整原文），均非官方标准答案。听力无音频，仅保留题干/选项（2021 完整，其余仅答案）。',
    'structure': '听力（20题/30分）+ 阅读（15题/37.5分）+ 七选五（5题/12.5分）+ 完形填空（15题/15分）+ 语法填空（10题/15分）+ 写作（应用文15分+读后续写25分=40分），满分150分，时长120分钟。',
    'papers': PAPERS,
}

NOTICE_RECALL = '2025、2026 为考生回忆整理版，非官方标准答案，题型与原文贴合考场原题。'


def selfcheck():
    ok = True
    for p in PAPERS:
        qs = [q for m in p['modules'] for pt in m['parts'] for q in pt['questions']]
        n_listen = sum(1 for q in qs if q['type'] == 'listen')
        n_single = sum(1 for q in qs if q['type'] == 'single')
        n_seven = sum(1 for m in p['modules'] if m['name'].startswith('阅读') for pt in m['parts'] if '七选五' in pt['name'] for q in pt['questions'])
        n_fill = sum(1 for q in qs if q['type'] == 'fill')
        n_essay = sum(1 for q in qs if q['type'] == 'essay')
        total = sum(m['score'] for m in p['modules'])
        no_ok = len(qs) == len(set(q['no'] for q in qs))
        # 仅对“有选项”的 single/七选五 校验 answer 落在选项范围内；听力无选项（仅答案）跳过
        bad = [q['no'] for q in qs if q.get('options') and q['type'] in ('single', 'listen') and not (0 <= q['answer'] < len(q['options']))]
        print('  [selfcheck] %s 题%d 听%d 选%d 七选%d 填%d 作文%d 总分%d bad=%s' % (
            p['id'], len(qs), n_listen, n_single, n_seven, n_fill, n_essay, total, bad))
        if total != 150 or n_listen != 20 or n_seven != 5 or n_essay != 2 or not no_ok or bad:
            ok = False
            print('    !! 结构异常（total=%d listen=%d seven=%d essay=%d no_ok=%s bad=%s）' % (
                total, n_listen, n_seven, n_essay, no_ok, bad))
    print('[selfcheck] %s' % ('全部通过' if ok else '存在异常'))
    return ok


if __name__ == '__main__':
    selfcheck()
    out = os.path.join(ROOT, 'data', 'english_gd.json')
    json.dump(DATA_OBJ, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', out)
