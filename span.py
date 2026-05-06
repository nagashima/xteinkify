"""<p>タグの直後に空の<span></span>を挿入する。

xteinkリーダーでは段落先頭に自動字下げが当たるため、
原文に既に全角スペースで字下げ済みのEPUBだと二重に下がってしまう。
先頭に空のインライン要素を挿入することで自動字下げを無効化する。
"""
from __future__ import annotations

import re

# <p> または属性付き<p attrs...>。<param>等を除外するため属性は[ \t]始まり。
_P_OPEN_RE = re.compile(r'(<p(?:[ \t][^>]*)?>)', re.IGNORECASE)
_P_DEDUP_RE = re.compile(r'(<p(?:[ \t][^>]*)?>)(?:<span></span>){2,}', re.IGNORECASE)


def insert(html: str) -> tuple[str, int]:
    """<p>直後に<span></span>を挿入した文字列と、挿入件数を返す。"""
    count = 0

    def replace_p(m: re.Match) -> str:
        nonlocal count
        count += 1
        return m.group(1) + '<span></span>'

    result = _P_OPEN_RE.sub(replace_p, html)
    result = _P_DEDUP_RE.sub(r'\1<span></span>', result)
    return result, count
