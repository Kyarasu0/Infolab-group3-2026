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
├── models/               # 1フォルダ1モデル。パラメータはJSONに切り出し
│   ├── autoencoder/      #   autoencoder.py / autoencoder.json
│   ├── svm/              #   svm_classifier.py / svm.json
│   └── clustering/       #   clustering_model.py / clustering.json
├── scenarios/            # モデルの順番とパラメータを決めるシナリオ(JSON)と、実行・比較のコード
├── 2-Backend/            # FastAPI。学習/予測モードの切り替え、API
├── 1-Frontend/           # React。学習状況・シナリオ比較・層ごとの構成を表示
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
cd machine-learning
python3 -m venv .venv && .venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
PYTHONPATH=. .venv/bin/uvicorn main:app --app-dir 2-Backend --port 8000     # バックエンド
cd 1-Frontend && npm install && npm run dev                                 # フロント(http://localhost:5173)
PYTHONPATH=. .venv/bin/python -m pytest tests -q                            # テスト
```
環境変数: `ML_MODE`(起動時のモード。既定 train)、`ML_DEFAULT_SCENARIO`、`ML_TRAINING_DATA`、`ML_ARTIFACTS_DIR`、`ML_ALLOWED_ORIGINS`

## バックエンドのAPIとモード
| API | モード | 用途 |
|---|---|---|
| `GET/PUT /mode` | 両方 | モードの確認・切り替え(`{"mode": "train" or "predict"}`) |
| `POST /train` `POST /compare` | 学習のみ | 学習・全シナリオ比較(別スレッドで実行) |
| `GET /jobs/current` | 両方 | 学習の進捗(エポックごとの損失) |
| `GET /scenarios` `/scenarios/{name}/result` `/architecture` | 両方 | 一覧・指標と学習曲線・層ごとの構成 |
| `POST /predict` | 予測のみ | 予測。**通知用バックエンドから呼ばれる想定** |

モードに合わないAPIは `409` を返します。

### `POST /predict`(通知用バックエンド向けの契約)
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
