# -*- coding: utf-8 -*-
"""将增强后的 hchinese_exam.json / htextbook.json 注入 worker.js 的锚点常量。
锚点：
  // === HCHINESE_EXAM_DEFAULT_START ===  ...  // === HCHINESE_EXAM_DEFAULT_END ===
  // === HTEXTBOOK_DEFAULT_START ===       ...  // === HTEXTBOOK_DEFAULT_END ===
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_EXAM = os.path.join(ROOT, 'data', 'hchinese_exam.json')
SRC_BOOK = os.path.join(ROOT, 'data', 'htextbook.json')
WORKER = r'E:/szgaokao.cn/worker/src/worker.js'

def inject(text, start_tag, end_tag, var_name, data):
    s = text.find(start_tag)
    e = text.find(end_tag)
    if s < 0 or e < 0:
        raise SystemExit('锚点未找到: %s / %s' % (start_tag, end_tag))
    # 锚点之间的内容（含两行注释）整体替换
    head = text[:s + len(start_tag)]
    tail = text[e:]
    compact = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    middle = '\nvar %s = %s;\n' % (var_name, compact)
    return head + middle + tail

def main():
    exam = json.load(io.open(SRC_EXAM, encoding='utf-8'))
    book = json.load(io.open(SRC_BOOK, encoding='utf-8'))
    text = io.open(WORKER, encoding='utf-8').read()
    text = inject(text,
                  '// === HCHINESE_EXAM_DEFAULT_START ===',
                  '// === HCHINESE_EXAM_DEFAULT_END ===',
                  'hchinese_exam_default', exam)
    text = inject(text,
                  '// === HTEXTBOOK_DEFAULT_START ===',
                  '// === HTEXTBOOK_DEFAULT_END ===',
                  'htextbook_default', book)
    io.open(WORKER, 'w', encoding='utf-8').write(text)
    # 校验
    print('exam questions 注入字节:', len(json.dumps(exam, ensure_ascii=False)))
    print('book units 注入字节:', len(json.dumps(book, ensure_ascii=False)))
    print('worker.js 新大小(byte):', len(text.encode('utf-8')))
    print('注入完成。')

if __name__ == '__main__':
    main()
