"""EPUBファイル(ZIP)の読み書き。"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

_HTML_EXT_RE = re.compile(r'\.(xhtml|html|htm)$', re.IGNORECASE)
_XML_ENC_RE = re.compile(rb'<\?xml[^>]*encoding=["\']([^"\']+)["\']', re.IGNORECASE)
_META_ENC_RE = re.compile(rb'<meta[^>]+charset=["\']?([\w-]+)["\']?', re.IGNORECASE)


def is_html_name(name: str) -> bool:
    return bool(_HTML_EXT_RE.search(name))


def decode_html(data: bytes) -> str:
    """charset宣言を尊重してデコード、失敗ならUTF-8フォールバック。"""
    head = data[:512]
    m = _XML_ENC_RE.search(head) or _META_ENC_RE.search(head)
    if m:
        try:
            charset = m.group(1).decode('ascii').lower()
            return data.decode(charset)
        except (LookupError, UnicodeDecodeError):
            pass
    return data.decode('utf-8', errors='replace')


def read_epub(path: Path) -> tuple[list[str], dict[str, bytes]]:
    """ファイル名（順序保持）と内容辞書を返す。"""
    names: list[str] = []
    contents: dict[str, bytes] = {}
    with zipfile.ZipFile(path, 'r') as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            names.append(info.filename)
            contents[info.filename] = zf.read(info.filename)
    if 'mimetype' not in contents:
        raise ValueError('mimetype が見つかりません。EPUBではないかもしれません。')
    return names, contents


def write_epub(path: Path, names: list[str], contents: dict[str, bytes]) -> None:
    """mimetypeを無圧縮で先頭、他はDEFLATEで書き出す。"""
    if 'mimetype' not in contents:
        raise ValueError('mimetype エントリーが必要です')
    with zipfile.ZipFile(path, 'w') as zf:
        info = zipfile.ZipInfo('mimetype')
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, contents['mimetype'])
        for name in names:
            if name == 'mimetype':
                continue
            entry_info = zipfile.ZipInfo(name)
            entry_info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(entry_info, contents[name])
