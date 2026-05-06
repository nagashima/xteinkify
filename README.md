# xteinkify

xteinkリーダー向けにEPUBを最適化するCLIツール（Python標準ライブラリのみ）。

## 機能

### 1. ルビ変換
`<ruby>` タグを括弧書きに変換します。連続するルビや複数の `<rt>` は **単語単位にマージ** されます。

変換前:
```html
<p><ruby>吾<rt>わが</rt>輩<rt>はい</rt></ruby>は<ruby>猫<rt>ねこ</rt></ruby>である。<ruby>名<rt>な</rt></ruby><ruby>前<rt>まえ</rt></ruby>はまだない。</p>
```

変換後:
```
吾輩（わがはい）は猫（ねこ）である。名前（なまえ）はまだない。
```

この例には3パターンが含まれます：
- `吾輩（わがはい）` … 1つの `<ruby>` 内に複数の `<rt>` が分割されているケース
- `猫（ねこ）` … 単純な1対1のルビ（マージ不要）
- `名前（なまえ）` … 隣接する別々の `<ruby>` タグが連続しているケース

### 2. 段落字下げ修正
`<p>` タグの直後に空の `<span></span>` を挿入し、xteinkの自動字下げと既存の全角スペースが二重に効く問題を回避します。

変換前:
```html
<p>　吾輩は猫である。</p>
```

変換後:
```html
<p><span></span>　吾輩は猫である。</p>
```

## 必要環境

- Python 3.9 以上（追加パッケージ不要・標準ライブラリのみで完結）

## 使い方

```bash
# 両方適用（デフォルト）
python xteinkify.py book.epub

# ルビ変換のみ
python xteinkify.py book.epub --no-span

# 段落字下げ修正のみ
python xteinkify.py book.epub --no-ruby

# 出力先を指定
python xteinkify.py book.epub -o /path/to/output.epub
```

出力ファイルはデフォルトで入力と同じディレクトリに `<元ファイル名>.xteink.epub` という名前で生成されます。

例:
```
/books/原本/book.epub  → /books/原本/book.xteink.epub
```

## オプション

| オプション | 説明 |
|---|---|
| `-o, --output PATH` | 出力ファイルパス（省略時は自動命名） |
| `--no-ruby` | ルビ変換をスキップ |
| `--no-span` | 段落字下げ修正をスキップ |
| `-q, --quiet` | 詳細ログを抑制 |

## ファイル構成

| ファイル | 役割 |
|---|---|
| `xteinkify.py` | CLIエントリーポイント |
| `ruby.py` | ルビ変換ロジック（マージ対応） |
| `span.py` | span挿入ロジック |
| `epub.py` | EPUB読み書き |

各モジュールは独立しており、ライブラリとしてimportして単体利用も可能です。

```python
import ruby, span
new_html, count = ruby.convert(old_html)
new_html, count = span.insert(old_html)
```

## ライセンス

MIT
