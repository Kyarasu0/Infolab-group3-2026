# 1-Frontend

学習の状況・シナリオの比較・実験の実行と記録を見るための、1枚の画面です(React + Vite + TypeScript)。
見た目は、KyarasuDailyTracker(元は Idisclosure#3)と同じ、濃い青緑の背景・シアンの文字・Makinas フォントです。

## 起動
`machine-learning/start.sh` でバックエンドと一緒に起動するのが簡単です(初回は `setup.sh`)。
フロントだけ起動するとき: `npm install && npm run dev`(http://localhost:5173)。`/api` は、バックエンド(既定 8000番。`ML_BACKEND_PORT` で変更)に中継されます。

- ビルドと型の確認: `npm run build`

## 画面(上から順に)
1. ヘッダー: 現在のモード(学習 / 予測)と、切り替えボタン
2. 実行状況: 学習・実験の実行中は、レーダー風の表示と進捗(エポック)を出す
3. シナリオ: 一覧と指標、「学習」ボタン、「全シナリオを比較」
4. 実験: シナリオ・評価計画・パラメータを選んで評価して記録する。**パラメータ欄には、日本語名・設定名・説明が出る**(説明は `models/*/*.descriptions.json`)。同じ条件の記録があれば、「過去の結果を表示 / もう一度実行」を選べる
5. 実験の記録: 平均 ± 標準偏差の一覧と、foldごとの詳細
6. シナリオ比較(棒グラフ)と、学習曲線(折れ線)
7. 散布図(色 = 状態、形 = サブタイプ)と、再構成誤差の分布(閾値つき)。選んだシナリオが学習済みで、データがあるときだけ表示
8. データの概要: 件数と、特徴量ごとの平均(状態別)
9. モデルの構成: 層ごとの入出力・パラメータ数

## 構成
```text
public/fonts/                      # Makinas フォント
src/
├── theme/tokens.css               # 色・間隔・角丸・影・文字(デザイントークン)。値は、ここだけで決める
├── styles/                        # global.css(リセットとタグの見た目) / layout.module.css / chart.module.css(共通のクラス)
├── functions/                     # 描画と関係のない関数
│   ├── api-client.ts              #   APIの呼び出し(名前で呼ぶ)
│   ├── api-types.ts               #   APIの入出力の型
│   ├── chart-scale.ts             #   グラフの目盛りの計算
│   ├── cx.ts                      #   CSSのクラス名の合成
│   ├── format-metrics.ts          #   指標の表示用の文字
│   └── group-style.ts             #   状態(通常・ストレス・疲労)の表示名と色
└── components/                    # アトミックデザイン。フォルダは「番号-名前」
    ├── 1-Atoms/      01-Button  02-StatusBadge  03-Panel
    ├── 2-Molecules/  01-ChartFrame  02-LineChart  03-BarChart  04-ParameterField  05-RadarIndicator
    │                 06-ScatterChart  07-Histogram
    ├── 3-Organisms/  01-ScenarioPanel  02-ArchitectureViewer  03-ExperimentForm  04-RecordHistory
    │                 05-ExistingRecordNotice  06-RunStatus  07-CompareChart  08-ScatterPanel
    │                 09-ErrorDistributionPanel  10-DataSummary
    ├── 4-Templates/  01-AppHeader
    └── 5-Pages/      01-Dashboard   # 画面全体(1枚)。useDashboard.ts / useExperiments.ts / useVisuals.ts が状態を持つ
```
`@/` は `src/`、`@shared/` は `../3-Shared/` を指します。

## グラフ
ライブラリは使わず、SVGで描きます。`ChartFrame` が、題・凡例・ホバーの吹き出し・「データがありません」の表示をまとめ、
`LineChart` / `BarChart` / `ScatterChart` / `Histogram` が、その中身を描きます。色は `theme/tokens.css` の `--chart-*` だけを使います。

## APIの呼び出し
APIのメソッドとパスは、`3-Shared/api-list.json` から**名前で引きます**(画面側に `/api/...` を書きません)。
```ts
callApi<ScenarioResult>("get_scenario_result", { name })   // パスの {name} を値で埋める
```
APIが増えたときは、`3-Shared/api-list.json` と `2-Backend/api/` に足したあと、`api-client.ts` に呼び出しの関数を足します。

## ルール(Knowledgeの `6-css` / `3-small-and-clear` に従う)
- 部品は、`名前.tsx` と `名前.module.css` を、同じフォルダに置く
- 色・間隔・文字の大きさは、`theme/tokens.css` のCSS変数だけを使う(CSSに色コードを直接書かない)
- CSSの宣言は、「大きさ → バックグラウンド → 要素配置 → 配置基準 → 余白 → 文字 → 装飾 → アニメーション」の区分コメントで区切って、この順に書く
- クラス名は、ビルド時に自動で変わる(`vite.config.ts`)。部品: `c<階層1桁><部品2桁>-<ファイル名>-<クラス名>`(例: `c101-Button-button`)、共通: `shared-<ファイル名>-<クラス名>`
- 1つの階層に置く部品は20個まで。まだ作っていない番号は空けておく
- 1ファイルは、150〜200行以内を目安にする

## 部品を足すとき
1. 階層に合うフォルダを `番号-名前` で作る(例: `2-Molecules/06-〇〇/`)
2. `〇〇.tsx` と `〇〇.module.css` を作る
3. 状態や通信が必要なら、描画から分けて、フックか `functions/` に置く
