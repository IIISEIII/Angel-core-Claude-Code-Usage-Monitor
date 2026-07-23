# ISEI's Angel Core Claude Usage Monitor Customize

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![English](https://img.shields.io/badge/English-README-blue.svg)](README.md)

[**Maciek-roboblog/Claude-Code-Usage-Monitor**](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) の個人用フォークでございます。ツール本体の功績はすべて **Maciek** さんに帰するものです。このフォークは新しい機能を何も加えておりません。ダッシュボードの佇まいを、より柔らかくパステルな趣（"Angelcore"）に整え、その過程で見つかった本物の不具合を一つ、静かに直しただけのものです。本家をお探しでしたら、活発にメンテナンスされている[オリジナル](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)がお待ちしております。このリポジトリは、とある個人の作業環境の記録を、同じような手入れをどなたかがされる際のお役に立てばと思い、公開しているものです。オリジナルのREADMEは[README.upstream.md](README.upstream.md)にそのまま残してあり、MITライセンスにも手を加えておりません。

![Dashboard](doc/angelcore-dashboard.png)

---

## 事前にご用意いただくもの

- macOS と [iTerm2](https://iterm2.com) — 自動起動スクリプトはiTerm2専用でございます（`claude-monitor` 本体はどこでも快く動きます）。
- インストール用の [uv](https://docs.astral.sh/uv/)。
- 名前が正確に **Monitor** のiTerm2プロファイル：iTerm2 → 設定 → Profiles → **+** よりご用意ください。見た目はお好みのままで構いません（配色は `claude-monitor` 自身が受け持っており、プロファイルには依存いたしません）。ご参考までに、上のスクリーンショットで用いているフォントは以下の通りです（Profiles → Text タブ）。

  | 設定項目 | 値 |
  |---|---|
  | フォント | JetBrainsMonoNL Nerd Font |
  | スタイル | Medium |
  | サイズ | 8 |
  | 水平方向の間隔 | 100% |
  | 垂直方向の間隔 | 132% |

  Nerd Fontはあれば嬉しい程度のもので、必須ではございません。アイコンはごく普通のUnicode絵文字ですので、等幅フォントであればどれでも構いません。垂直方向132%というゆったりとした間隔が、あの落ち着いた余白を生んでおります。お好みで100%に近づけていただければ、同じ内容がより低いウィンドウに収まります。
- `PATH` に `~/.local/bin` が通っていること。`uv tool install` は `claude-monitor` をそこに置き、セットアップスクリプトもフルパスではなく名前でお呼びしております。通っていなければ、uvがきちんとお知らせしてくれます。

---

## インストール

```bash
uv tool install git+https://github.com/IIISEIII/Angel-core-Claude-Code-Usage-Monitor.git
```

続けて、よろしければiTerm2の自動起動レイヤーもどうぞ。

```bash
mkdir -p ~/.claude-monitor
cp macos-setup/weekly-status.sh ~/.claude-monitor/
chmod +x ~/.claude-monitor/weekly-status.sh

mkdir -p ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch
cp macos-setup/autolaunch.applescript ~/Library/"Application Support"/iTerm2/Scripts/AutoLaunch/claude-monitor-autolaunch.scpt
```

以降は、iTerm2を開くたびに2ペインのウィンドウがお待ちしております。手動での起動は不要でございます。それ以外——インストールオプション、`--plan`、その他のフラグ、機能一覧など——は、すべて[README.upstream.md](README.upstream.md)（英語）をご参照ください。ここで触れた点以外は、何も変わっておりません。

---

## オリジナルからの変更点

ソースファイルを3つ編集し、[`macos-setup/`](macos-setup/) 配下にスクリプトを4つ加えております。

### 色について

`themes.py` — ライト・ダーク両方のテーマテーブルを、upstreamのxterm-256パレットから、もう少し静かな色合いに書き改めました。

| 役割 | Hex | 用途 |
|---|---|---|
| `foreground` | `#3F3E4A` | メインテキスト |
| `soft_text` | `#6F7284` | サブテキスト |
| `muted` | `#8A8B98` | 薄字・区切り線・バーの未達部分 |
| `blue` | `#557C9C` | info、Sonnetモデル、max5プラン |
| `cyan` | `#4F8D91` | チャートの線 |
| `lavender` | `#77709F` | ヘッダー、Opusモデル、max20プラン |
| `purple` | `#675D91` | プログレスバーの塗り |
| `pink` | `#A66F87` | proプラン |
| `rose` | `#AE6677` | エラー表示 |
| `green` | `#5F856B` | 成功表示 |
| `yellow` | `#927B48` | 警告表示 |

ダークモードには、同じ色相を明るくしたものをお使いいただいております。プログレスバーの塗りは使用率段階での色分けをやめ、紫一色に整えました。upstreamでは「バー」の段階判定と「絵文字」の段階判定が時折食い違い、落ち着いた黄色🟡の隣に赤段階の色のバーが並ぶ、ということがございました。その小さな行き違いは静かに解消し、段階をお伝えする役目は絵文字にお任せしております。バーはただ、意見を持たずに埋まってまいります。

### `--no-header`、名は体を表すように

`session_display.py` — upstreamの `--no-header` はタイトルバナーこそ隠しておりましたが、冒頭の空行2つと末尾の「Active session」フッターは、変わらず無条件に出力されておりました。両方とも同じフラグの管理下に置きましたので、`--no-header` は今度こそ名前の通り、最初の行から最後の行まで、余分なものを何も付け加えなくなりました。

### scrollbackにまつわる、ささやかな不具合

`display_controller.py` — こちらは好みの問題ではなく、正真正銘の不具合でございました。`LiveDisplayManager` はRichの `Live` を `vertical_overflow="visible"` にて生成しておりました。ペインの高さを内容ぴったりに整えますと——`--no-header` はまさにそれを誘っております——更新のたびに、ターミナルは一度スクロールを促され、`Live` が自らのカーソル位置を見失ってしまいます。以降は更新のたびに、上書きされるはずだった古いフレームが、scrollbackの中でそっと列をなしてお待ちになる、という次第でございました。`vertical_overflow="crop"` に改め、スクロールではなく単純に切り詰める形に変更いたしました。ペインの高さを内容とぴったり同じにした状態で60回以上の更新を確認し、以後は行き違いが起きないことを確かめております。

### iTerm2まわりの支度

`macos-setup/` — upstreamの機能ではなく、こちらでご用意した自動化でございます。`autolaunch.applescript` はiTerm2の起動時に2ペインのウィンドウを開き、それぞれの描画にぴったり収まる高さに整えます（上段はダッシュボード用に21行、下段はステータス表示用に5行）。`weekly-status.sh` は同じ `--api` の使用量キャッシュを読み、upstreamのダッシュボードには直接現れない **5-hour** と **Weekly** のバーをお見せいたします。確認の間隔はデフォルトの180秒ではなく60秒に整えました。`combined-monitor.sh` は、ペインを分けたくない方向けに、同じ2本のバーを1ペインにまとめたものでございます。

同じような支度をされる方への、ささやかな心得を一つ。iTerm2で分割済みペインの `rows` を変更いたしますと、実のところ「ウィンドウ全体」がリサイズされ、直近に手を加えた方のペインに合わせて広がり、もう一方はそのままの大きさで据え置かれます。ですので、小さい方のペインを先に、ダッシュボード側を最後にお整えください。順序が逆になりますと、計算が思うようには参りません。

---

## ライセンス

MIT。upstreamから変更はございません。[LICENSE](LICENSE) をご参照ください。Copyright (c) 2025 Maciej（オリジナル作者）、上記の変更部分につきましては (c) 2026 ISEI。
