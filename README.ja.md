# ISEI's Angel Claude Usage Monitor Customize

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![English](https://img.shields.io/badge/English-README-blue.svg)](README.md)

これは [**Maciek-roboblog/Claude-Code-Usage-Monitor**](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) の個人用フォークです。元ツール本体・アーキテクチャ・機能はすべて **Maciek** さん（[@Maciek-roboblog](https://github.com/Maciek-roboblog)）によるものです。このフォークは新機能を追加するものではなく、ターミナルダッシュボードを個人の好み（"Angelcore" ＝淡くマットなパステル調）に配色・レイアウトを作り替え、途中で見つけたレンダリングバグを1件修正したものです。オリジナルのREADMEは [README.upstream.md](README.upstream.md) にそのまま残してあり、`LICENSE`（MIT）も変更していません。

本家ツールが目的なら、活発にメンテナンスされているオリジナルのリポジトリを使ってください。このフォークは今後オリジナルから乖離していきます。このリポジトリは、あくまで「個人的にどうカスタムしたか」（Angelcore配色・超コンパクトなiTerm2ダッシュボード）を記録・共有する目的のものです。

![Dashboard](doc/scnew.png)

---

## オリジナルからの変更点

以下はすべて upstream `claude-monitor` v4.0.0 の上に重ねた変更です。ソースファイル3つを編集し（`upstream/main` ブランチとの `git diff` 参照、または下記の各項目）、[`macos-setup/`](macos-setup/) 配下に新規スクリプトを4つ追加しています。

### 1. Angelcoreカラーテーマ

`src/claude_monitor/terminal/themes.py` — ライト/ダーク背景それぞれの `Theme` テーブルを、upstreamのxterm-256パレットから、彩度を抑えたマットな "Angelcore" パレットに書き換えました。

| 役割 | Hex | 用途 |
|---|---|---|
| `foreground` | `#3F3E4A` | メインテキスト |
| `soft_text` | `#6F7284` | サブテキスト |
| `muted` | `#8A8B98` | 薄字・区切り線・バーの未達部分 |
| `blue` | `#557C9C` | info、Sonnetモデル、max5プラン |
| `cyan` | `#4F8D91` | チャートの線 |
| `lavender` | `#77709F` | ヘッダー、Opusモデル、max20プラン |
| `purple` | `#675D91` | プログレスバーの塗り（使用率段階に関わらず統一） |
| `pink` | `#A66F87` | proプラン |
| `rose` | `#AE6677` | エラー表示 |
| `green` | `#5F856B` | 成功表示 |
| `yellow` | `#927B48` | 警告表示 |

ダークモード用の色は同じ色相を白方向に明るくしたバリエーションです（正確なブレンド比率はファイル参照）。macOSの外観切り替えに追従してもパレットが破綻しないようにしています。

意図的な判断として：upstreamはプログレスバーの「塗り」自体を使用率段階（緑/黄/赤）で色分けしていましたが、このフォークでは塗りを紫で統一し、段階の伝達は🟢🟡🔴の絵文字だけに任せています。理由は、upstream側の「塗り用の段階判定」と「絵文字用の段階判定」が食い違うことがあり（🟡の絵文字なのに赤段階の色のバーが表示される、など）、バグのように見えたためです。塗りを統一することでこの不整合自体を無くしています。

### 2. `--no-header` 超コンパクトモード

`src/claude_monitor/ui/session_display.py` — upstreamの `--no-header` フラグは元々タイトルバナーしか隠していませんでした。冒頭の空行2箇所と、末尾の `⏰ HH:MM:SS 📝 Active session | Ctrl+C to exit` フッターは無条件に出力される仕様でした。このフォークではそれらすべてを同じフラグの条件分岐に含め、`--no-header` を指定すると本当に「先頭の指標行から最後の指標行まで、余白なし」で表示されるようにしました。

### 3. Live表示の重複描画バグ修正

`src/claude_monitor/ui/display_controller.py` — `LiveDisplayManager` はRichの `Live` を `vertical_overflow="visible"` で生成していました。描画内容の高さがターミナルの行数に近い（または一致する）と、最終行の改行出力で実際にターミナルがスクロールしてしまい、`Live` 内部のカーソル位置管理が永久にズレます。以降の更新のたびに、上書きされるはずの古いフレームがscrollbackに残り続けます。ペインの高さを内容ぴったりに詰めた瞬間（まさに `--no-header` が誘発する状況）に顕著になり、上にスクロールすると同じフレームが何十個も積み重なって見えるという症状でした。

`vertical_overflow="crop"` に変更することで、Richがスクロールせずに超過分を単純に切り詰めるようにして解決しました。ペイン高さを内容の行数ときっちり同じにした状態で60回以上の更新を確認し、重複が発生しないことを確認済みです。

### 4. macOS / iTerm2 自動起動セットアップ（`macos-setup/`）

upstreamの機能ではなく、ログイン時に2ペイン構成のiTerm2ウィンドウを開く個人用の自動化レイヤーです。

- **`autolaunch.applescript`** — `~/Library/Application Support/iTerm2/Scripts/AutoLaunch/` に置くと、iTerm2起動のたびに自動実行されます（既に起動中ならスキップ）。1つのウィンドウを2ペインに分割し、サイズを固定：**上ペイン 21行×80列** — ライブダッシュボード（`claude-monitor --plan pro --api --no-header`）を、その21行のコンパクト描画にぴったり収まるサイズに（折り返しなし・見切れなし・上記修正により重複描画も起きない）。**下ペイン 5行** — ステータス表示用の補助スクリプト。
- **`autostart-terminal.sh`** — 同じレイアウトを、AutoLaunchを使わず手動実行できる版。
- **`weekly-status.sh`** — 下ペイン用のスクリプト。`--api` フラグが維持するOAuth使用量キャッシュを読み、**5-hour** と **Weekly** のレート制限バーを表示します（この2つのウィンドウはupstreamのダッシュボードには直接表示されません）。`--api-ttl-seconds 60` と `sleep 60` を組み合わせ、データの鮮度を最大60秒遅延に抑えています（upstreamのデフォルトTTLは180秒）。Anthropic側のエンドポイントが429を返した場合は、既存の `Retry-After` バックオフ処理がそのまま効きます。
- **`combined-monitor.sh`** — ペイン分割をしたくない人向けに、フルダッシュボードと同じ5-hour/Weeklyバーを1ペインにまとめて表示する代替スクリプト。

もし同じ構成を真似る場合の非自明なポイント：iTerm2のAppleScriptで分割済みペインに `set rows to N` を実行すると、実際には「ウィンドウ全体」がリサイズされ、直近にリサイズしたペインのサイズに合わせて拡大し、もう一方のペインはピクセルサイズがそのまま据え置かれます。そのため、小さい方のペインを先に、ダッシュボード側のペインを最後にサイズ指定する必要があります。順序を逆にすると計算が合わなくなります。

---

## インストール

このフォークはPyPIには公開していません。[uv](https://docs.astral.sh/uv/) でこのリポジトリから直接インストールしてください。

```bash
uv tool install git+https://github.com/IIISEIII/Angel-core-Claude-Code-Usage-Monitor.git
```

さらに、iTerm2自動起動レイヤーを使う場合は以下も実行します。

```bash
mkdir -p ~/.claude-monitor
cp macos-setup/weekly-status.sh ~/.claude-monitor/
chmod +x ~/.claude-monitor/weekly-status.sh

mkdir -p ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch
cp macos-setup/autolaunch.applescript ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch/claude-monitor-autolaunch.scpt
```

加えて、名前が **Monitor** のiTerm2プロファイルが必要です（フォント・外観は自由でOK。配色は `claude-monitor` 自体が制御するので、プロファイル側の配色設定には依存しません）。

インストールオプション、`--plan` を含む各種フラグ、機能一覧、トラブルシューティングなど、それ以外はすべてオリジナルの [README.upstream.md](README.upstream.md)（英語）を参照してください。ここで変更した点以外は何も変わっていません。

---

## ライセンス

MIT。upstreamから変更していません。[LICENSE](LICENSE) 参照。Copyright (c) 2025 Maciej（オリジナル作者）、上記カスタマイズ部分 (c) 2026 ISEI。
