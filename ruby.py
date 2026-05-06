"""ルビタグを括弧形式に変換する。

<ruby>漢字<rt>かんじ</rt></ruby> → 漢字（かんじ）

連続するルビ・1つの<ruby>内の複数<rt>は単語単位にマージする：
  <ruby>吾<rt>わが</rt>輩<rt>はい</rt></ruby>            → 吾輩（わがはい）
  <ruby>名<rt>な</rt></ruby><ruby>前<rt>まえ</rt></ruby> → 名前（なまえ）
"""
from __future__ import annotations

import re

# 連続する<ruby>...</ruby>（間が空白文字のみ）を1グループとしてマッチ。
_GROUP_RE = re.compile(
    r'<ruby\b[^>]*>[\s\S]*?</ruby\s*>(?:\s*<ruby\b[^>]*>[\s\S]*?</ruby\s*>)*',
    re.IGNORECASE,
)
_SINGLE_RUBY_RE = re.compile(r'<ruby\b([^>]*)>([\s\S]*?)</ruby\s*>', re.IGNORECASE)
_RT_RE = re.compile(r'<rt\b[^>]*>([\s\S]*?)</rt\s*>', re.IGNORECASE)
_RP_RE = re.compile(r'<rp\b[^>]*>[\s\S]*?</rp\s*>', re.IGNORECASE)
_RB_OUTER_RE = re.compile(r'<rb\b[^>]*>([\s\S]*?)</rb\s*>', re.IGNORECASE)
_TAG_RE = re.compile(r'<[^>]+>')


def convert(html: str) -> tuple[str, int]:
    """ルビをマージして括弧形式に変換した文字列と、変換件数を返す。"""
    count = 0

    def replace_group(m: re.Match) -> str:
        nonlocal count
        text = m.group(0)
        rubies = list(_SINGLE_RUBY_RE.finditer(text))
        if not rubies:
            return text

        bases: list[str] = []
        rts: list[str] = []
        tail = ''

        for i, ruby_m in enumerate(rubies):
            inner = _RP_RE.sub('', ruby_m.group(2))
            rt_matches = list(_RT_RE.finditer(inner))

            if not rt_matches:
                plain = _TAG_RE.sub('', inner).strip()
                if plain:
                    bases.append(plain)
                continue

            cursor = 0
            for rt_m in rt_matches:
                before = inner[cursor:rt_m.start()]
                base_text = _RB_OUTER_RE.sub(r'\1', before)
                base_text = _TAG_RE.sub('', base_text).strip()
                rt_text = _TAG_RE.sub('', rt_m.group(1)).strip()
                if base_text:
                    bases.append(base_text)
                rts.append(rt_text)
                cursor = rt_m.end()

            ruby_tail = _TAG_RE.sub('', inner[cursor:]).strip()
            if ruby_tail:
                if i == len(rubies) - 1:
                    tail = ruby_tail
                else:
                    bases.append(ruby_tail)

        if not rts:
            joined = ''.join(bases) + tail
            return joined if joined else text

        count += 1
        merged_base = ''.join(bases)
        merged_rt = ''.join(rts)
        if merged_base:
            return f'{merged_base}（{merged_rt}）{tail}'
        return f'（{merged_rt}）{tail}'

    result = _GROUP_RE.sub(replace_group, html)
    return result, count
