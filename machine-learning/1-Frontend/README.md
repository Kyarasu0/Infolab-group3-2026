# 1-Frontend

学習の状況・シナリオの比較・実験の実行と記録を見るための画面です(React + Vite + TypeScript)。

## 起動
`machine-learning/start.sh` でバックエンドと一緒に起動するのが簡単です(初回は `setup.sh`)。
フロントだけ起動するとき: `npm install && npm run dev`(http://localhost:5173)。`/api` は、バックエンド(既定 8000番。`ML_BACKEND_PORT` で変更)に中継されます。

- ビルドと型の確認: `npm run build`

## 構成
```text
src/
├── components/                    # アトミックデザイン。フォルダは「番号-名前」
│   ├── 1-Atoms/      01-Button  02-StatusBadge
│   ├── 2-Molecules/  01-LossChart  02-ParameterField
│   ├── 3-Organisms/  01-ScenarioPanel  02-ArchitectureViewer  03-ExperimentForm
│   │                 04-RecordHistory  05-ExistingRecordNotice
│   ├── 4-Templates/  (まだ無い)
│   └── 5-Pages/      01-Dashboard   # 画面全体。useDashboard.ts / useExperiments.ts が状態を持つ
├── functions/                     # 描画と関係のない関数
│   ├── api-client.ts              #   APIの呼び出し(名前で呼ぶ)
│   ├── api-types.ts               #   APIの入出力の型
│   └── format-metrics.ts          #   指標の表示用の文字
├── theme/                         # 色・間隔の値(ColorPalette.ts / SizeScale.ts)と、CSS変数への設定
└── global.css                     # リセットだけ
```

## APIの呼び出し
APIのメソッドとパスは、`../3-Shared/api-list.json` から**名前で引きます**(画面側に `/api/...` を書きません)。
```ts
callApi<ScenarioResult>("get_scenario_result", { name })   // パスの {name} を値で埋める
```
APIが増えたときは、`3-Shared/api-list.json` と `2-Backend/api/` に足したあと、`api-client.ts` に呼び出しの関数を足します。

## ルール(Knowledgeの `6-css` / `3-small-and-clear` に従う)
- 部品は、`名前.tsx` と `名前.module.css` を、同じフォルダに置く
- 色・間隔・文字の大きさは、`theme/` のCSS変数だけを使う(CSSに色コードを直接書かない)
- CSSの宣言は、「大きさ → バックグラウンド → 要素配置 → 配置基準 → 余白 → 文字 → 装飾 → アニメーション」の区分コメントで区切って、この順に書く
- クラス名は、ビルド時に `c<階層1桁><部品2桁>-<ファイル名>-<クラス名>` へ自動で変わる(`vite.config.ts`)。例: `c101-Button-button`(ブラウザの検証で、先頭の数字から部品の場所が分かる)
- 1つの階層に置く部品は20個まで。まだ作っていない番号は空けておく

## 部品を足すとき
1. 階層に合うフォルダを `番号-名前` で作る(例: `2-Molecules/03-〇〇/`)
2. `〇〇.tsx` と `〇〇.module.css` を作る
3. 状態や通信が必要なら、描画から分けて、フックか `functions/` に置く
