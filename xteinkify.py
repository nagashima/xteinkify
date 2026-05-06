#!/usr/bin/env python3
"""xteinkify - xteinkリーダー向けEPUB変換CLI。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import epub
import ruby
import span


def build_output_path(input_path: Path, custom: Path | None) -> Path:
    if custom is not None:
        return custom
    stem = input_path.stem
    return input_path.with_name(f'{stem}.xteink.epub')


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='xteinkify',
        description='xteinkリーダー向けにEPUBを最適化（ルビ変換・段落字下げ修正）',
    )
    parser.add_argument('input', type=Path, help='変換対象のEPUBファイル')
    parser.add_argument(
        '-o', '--output', type=Path, default=None,
        help='出力ファイルパス（省略時は入力と同じディレクトリに .xteink サフィックス）',
    )
    parser.add_argument('--no-ruby', action='store_true', help='ルビ変換をスキップ')
    parser.add_argument('--no-span', action='store_true', help='段落字下げ修正(span挿入)をスキップ')
    parser.add_argument('-q', '--quiet', action='store_true', help='詳細ログを抑制')
    args = parser.parse_args()

    if not args.input.exists():
        print(f'エラー: ファイルが見つかりません: {args.input}', file=sys.stderr)
        return 1

    convert_ruby = not args.no_ruby
    add_span = not args.no_span
    if not convert_ruby and not add_span:
        print('エラー: --no-ruby と --no-span を両方指定すると何も変換しません', file=sys.stderr)
        return 1

    output_path = build_output_path(args.input, args.output)
    if output_path.resolve() == args.input.resolve():
        print('エラー: 入力ファイルを上書きすることはできません', file=sys.stderr)
        return 1
    if '.xteink.' in args.input.name:
        print('INFO: 入力ファイル名に ".xteink." が含まれています（再変換として処理します）',
              file=sys.stderr)

    print(f'読み込み中: {args.input}')
    names, contents = epub.read_epub(args.input)

    html_count = 0
    ruby_total = 0
    span_total = 0
    warnings: list[str] = []

    for name in names:
        if not epub.is_html_name(name):
            continue
        html_count += 1
        try:
            text = epub.decode_html(contents[name])
        except Exception as e:
            warnings.append(f'{name}: デコード失敗 ({e})')
            continue

        rc = sc = 0
        if convert_ruby:
            text, rc = ruby.convert(text)
            ruby_total += rc
        if add_span:
            text, sc = span.insert(text)
            span_total += sc

        contents[name] = text.encode('utf-8')

        if not args.quiet:
            print(f'  {name}: ruby={rc}, span={sc}')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f'書き出し中: {output_path}')
    epub.write_epub(output_path, names, contents)

    print()
    print('=== 変換結果 ===')
    print(f'HTMLファイル数: {html_count}')
    if convert_ruby:
        print(f'ルビ変換: {ruby_total}件')
    if add_span:
        print(f'span挿入: {span_total}件')
    if warnings:
        print()
        print('警告:')
        for w in warnings:
            print(f'  WARN: {w}')
    print(f'出力: {output_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
