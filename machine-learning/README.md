# machine-learning

キーボード入力から、疲労・ストレスの度合いを推定する機械学習の置き場です。

## 推定の流れ
```text
入力(任意の次元) → オートエンコーダー(通常時を学習。再構成誤差で乖離を検知)
  → 乖離あり → SVM(stress / fatigue) → クラスタリング(状態ごとのサブタイプ)
  → 乖離なし → normal
```
どのモデルをどの順につなぎ、SVMに何を入れるか(圧縮後 / 復号後 / 残差 / 圧縮後+残差 / 元の値)は、
`scenarios/*.json` で決めます。次元数・層数なども、シナリオの `parameters` で上書きできます。

## フォルダ構成
```text
machine-learning/
├── data/                 # 取得データ(空)。形式は data/README.md
├── models/               # 1フォルダ1モデル。パラメータはJSONに切り出し(各パラメータの意味は models/README.md)
│   ├── autoencoder/      #   autoencoder.py / autoencoder.json
│   ├── svm/              #   svm_classifier.py / svm.json
│   └── clustering/       #   clustering_model.py / clustering.json
├── scenarios/            # モデルの順番とパラメータを決めるシナリオ(JSON)と、実行・比較のコード
├── experiments/          # 記録者: 評価して、結果を記録する(詳細は experiments/README.md)
│   ├── evaluation_plans/ #   評価計画(k交差検証・holdoutなど。kの値はここのJSON)
│   ├── records/          #   実験の記録(1実行1JSON。git管理外)
│   └── recorder/         #   分割・交差検証・記録のプログラム
├── 3-Shared/             # フロントとバックの両方が読むもの(api-list.json など)
├── 2-Backend/            # FastAPI。server.py / api/(1 API = 1ファイル = 1関数) / functions/
├── 1-Frontend/           # React。学習状況・シナリオ比較・実験の実行と記録の表示(1-Frontend/README.md)
├── tests/                # pytest(合成データを使用)
└── artifacts/            # 学習済みモデルと結果(自動生成・git管理外)
```

## シナリオJSONの書き方
```json
{
  "description": "説明",
  "anomaly_gate": true,
  "parameters": { "autoencoder": { "latent_dim": 4, "hidden_layers": 2 } },
  "pipeline": [
    { "model": "autoencoder" },
    { "model": "svm", "input": "latent" },
    { "model": "clustering", "input": "latent" }
  ]
}
```
- `input`: `raw` / `latent` / `decoded` / `residual` / `latent_and_residual`(AE以外は、AEより後ろの段でのみ使える)
- `clustering` は `svm` の後に置く(状態ごとにサブタイプを分けるため)
- `anomaly_gate`: AEの乖離が閾値未満なら normal とし、SVMに渡さない(既定 true)
- `parameters` に書かない値は、`models/*/*.json` の既定値を使う

## 学習済みモデルの構成JSON
学習すると `artifacts/<シナリオ名>/architecture.json` ができ、各層の入出力数・パラメータ数・重みの統計、
SVMのサポートベクター数、クラスタ数が見られます(API: `GET /scenarios/{name}/architecture`)。

## 起動
```bash
machine-learning/setup.sh              # 初回だけ: Python環境(.venv)とnpmの依存を用意する(何度実行してもよい)
machine-learning/start.sh              # 2回目以降: バックエンドとフロントをまとめて起動(学習モード)
machine-learning/start.sh predict      # 予測モードで起動
```
- フロント: http://localhost:5173 / バックエンド: http://localhost:8000(`ML_BACKEND_PORT` で変えられる)。止めるときは Ctrl+C
- 別々に起動するとき:
  ```bash
  cd machine-learning
  PYTHONPATH=. .venv/bin/uvicorn server:app --app-dir 2-Backend --port 8000   # バックエンド
  cd 1-Frontend && npm run dev                                                 # フロント
  ```
- テスト: `PYTHONPATH=. .venv/bin/python -m pytest tests -q`
- 環境変数: `ML_MODE`(起動時のモード。既定 train)、`ML_BACKEND_PORT`、`ML_DEFAULT_SCENARIO`、`ML_TRAINING_DATA`、`ML_ARTIFACTS_DIR`、`ML_RECORDS_DIR`、`ML_ALLOWED_ORIGINS`

## 実験の記録(experiments/)
シナリオ・評価計画・パラメータを選んで評価し、結果を `experiments/records/` に1実行1JSONで残します
(フロントの「実験」から実行。同じ条件の記録があれば、実行せず「過去の結果を表示 / もう一度実行」を選べます)。
- **評価計画** `experiments/evaluation_plans/*.json`: `kfold`(`k`・`stratified`・`seed`)か `holdout`(`test_ratio`・`seed`)
  - 通常データとラベル付きデータは、別々に分割する。kfold は、ラベルの比率をそろえる(層化)
  - TODO: 人・日ごとの `group_id` を同じfoldに入れる分割は、データ形式が決まってから対応する
- **パラメータ**: モデルの既定JSON → シナリオの `parameters` → 実行時の上書き、の順に重ねる。記録には、実際に使った全パラメータが残る
- **実行キー**: 合成後パラメータ・pipeline・評価計画・データのハッシュから作る。同じなら「実行済み」とみなす
- **記録の中身**: 日時・シナリオ・全パラメータ・評価計画・データ情報(件数・ハッシュ)・gitのcommit・foldごとの指標と平均±標準偏差・学習時間・メモ
- 交差検証は「設定の良し悪し」を測るもので、予測用モデルは作らない。予測用のモデルを作る(データの7割で学習し、残り3割で評価して、保存する)のは `POST /api/train`

## API(3-Shared/api-list.json)
API一覧は `3-Shared/api-list.json` に1か所だけ書き、フロントとバックの両方が読みます(KyamomeChickの `3-Shared/api-list.json` と同じ方式)。
- バックエンド: `server.py` が一覧を読み、各APIを `2-Backend/api/<handler_file>` の `<name>` 関数に、`method` と `path` で登録する。`mode` に合わないモードで呼ばれたら409
- フロント: `functions/api-client.ts` の `callApi(name, パスの値, 本文)` が、名前からメソッドとパスを引く。フロントに `/api/...` を直接書かない
- APIを足すとき: 一覧に1件足し(`description` に一言の説明)、`2-Backend/api/` に同じ名前のファイルと関数を作る。`tests/test_api_registry.py` が食い違いを見つける

| name | モード | 用途 |
|---|---|---|
| `get_mode` / `put_mode` | 両方 | モードの確認・切り替え(`{"mode": "train" or "predict"}`) |
| `post_train` / `post_compare` | 学習のみ | 全データでの学習・全シナリオ比較(別スレッドで実行) |
| `post_experiment_run` | 学習のみ | 評価して記録する(実行済みなら `{"status":"exists"}` と過去の記録。`force: true` で再実行) |
| `get_current_job` | 両方 | 進捗(エポックごとの損失) |
| `get_scenarios` `get_scenario_result` `get_scenario_architecture` `get_scenario_parameters` | 両方 | 一覧・指標と学習曲線・層ごとの構成・パラメータ |
| `get_evaluation_plans` `get_experiment_records` `get_experiment_record` | 両方 | 評価計画・実験の記録の一覧と詳細 |
| `get_parameter_descriptions` | 両方 | パラメータの日本語名と説明(画面の入力欄に表示) |
| `post_predict` | 予測のみ | 予測。**通知用バックエンドから呼ばれる想定** |

モードに合わないAPIは `409` を返します。

### `POST /api/predict`(通知用バックエンド向けの契約)
```json
// リクエスト: scenario は省略可(省略時は ML_DEFAULT_SCENARIO)。samples は何次元でもよいが、学習時と同じ特徴量数
{ "scenario": "01-latent-to-svm", "samples": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]] }

// レスポンス
{ "scenario": "01-latent-to-svm",
  "results": [ { "state": "stress",            // "normal" / "stress" / "fatigue"
                 "subtype": 1,                 // サブタイプ番号(normalのときは null)
                 "anomaly_score": 3.2,         // 通常時からの乖離(AEを使わないシナリオでは null)
                 "state_probabilities": { "fatigue": 0.1, "stress": 0.9 } } ] }
```
エラー: `400` 特徴量数が学習時と違う / `404` 未知のシナリオ / `409` 予測モードでない・未学習
