# models/

1フォルダ1モデル。パラメータは、モデルごとのJSONに切り出してあります(コードを直さずに、値だけ変えられます)。
どのモデルも、入力の次元数を決め打ちしません。`fit` に渡したデータの形から、自動で組み立てます
(1次元は「1サンプル」、3次元以上は「サンプルごとに平坦化」して扱います)。

```text
models/
├── common.py                       # 配列を2次元にそろえる・JSONの読み書き
├── autoencoder/  autoencoder.py + autoencoder.json
├── svm/          svm_classifier.py + svm.json
└── clustering/   clustering_model.py + clustering.json
```

## パラメータ
ここに書いたJSONの値が既定値です。シナリオJSONの `parameters`、または実験の実行時に、一部だけ上書きできます
(書かなかった値は、このJSONの値が使われます)。

### autoencoder.json(通常時のタイピングを学習し、乖離を測る)
| 名前 | 意味 |
|---|---|
| `latent_dim` | 圧縮後の次元数。入力の次元数より大きい値は、入力の次元数に切り詰める |
| `hidden_layers` | 入力と圧縮の間の中間層の数。大きさは、入力→圧縮へ等比で小さくなる(例: 入力16・圧縮2・`hidden_layers`=2 → 16, 8, 4, 2)。デコーダーは、その逆順 |
| `epochs` | 学習の回数 |
| `batch_size` | 1回の更新に使うサンプル数 |
| `learning_rate` | 学習率(Adam) |
| `anomaly_percentile` | 乖離とみなす閾値。通常データの再構成誤差の、このパーセンタイルを閾値にする(95 なら、通常データの5%程度が乖離と判定される) |
| `seed` | 乱数の種(同じ値なら、同じ結果になる) |

- 入力は、特徴量ごとに標準化してから学習する(平均・標準偏差は、モデルと一緒に保存される)
- 層は「全結合 + ReLU」で、各部分の最後の層だけ活性化なし
- 出力: `encode`(圧縮後)、`decode`(復号後)、`residual`(元の値 − 復号後)、`reconstruction_error`(標準化した二乗誤差の平均。サンプルごとに1つ)、`is_anomalous`

### svm.json(ストレスか疲労かを判定する)
| 名前 | 意味 |
|---|---|
| `kernel` | カーネル(`rbf` / `linear` / `poly` / `sigmoid`) |
| `C` | 誤分類へのペナルティ。大きいほど、学習データに合わせようとする |
| `gamma` | `rbf` などの広がり(`scale` / `auto` / 数値) |
| `class_weight` | `balanced` ならラベルの数の偏りを補正する。偏りを補正しないときは `null` |
| `seed` | 乱数の種 |

- 入力は標準化してから学習する
- クラスごとの確率は、確率較正(`CalibratedClassifierCV`)で出す。較正の分割数は、最もサンプルが少ないラベルの数(最大5、最小2)に合わせる

### clustering.json(状態ごとのサブタイプを分ける)
| 名前 | 意味 |
|---|---|
| `method` | `kmeans` か `gmm`(混合ガウス分布) |
| `n_clusters` | サブタイプの数。サンプル数より多い値は、サンプル数に切り詰める |
| `seed` | 乱数の種 |

- 入力は標準化してから学習する
- stress・fatigue など、状態ごとに別々のクラスタリングを学習する(`scenarios/scenario_runner.py`)

## 共通のメソッド
| メソッド | 内容 |
|---|---|
| `fit(...)` | 学習する(AEは通常データだけ。SVMは特徴量とラベル。クラスタリングは特徴量だけ) |
| `predict(...)` | 予測する(AEは `encode` など) |
| `save(...)` / `load(...)` | 学習済みモデルを保存・読み込みする |
| `describe()` | 層ごとの構成・パラメータ量などを返す(`artifacts/<シナリオ>/architecture.json` の元) |

## モデルを追加するとき
1. `models/<名前>/` に、`<名前>.py` と `<名前>.json` を作る(上の共通のメソッドをそろえる)
2. `scenarios/scenario_loader.py` の `DEFAULT_PARAMS_PATHS` と、`scenarios/scenario_runner.py` の `fit` / `predict` に、段として組み込む
3. シナリオJSONの `pipeline` に、`{"model": "<名前>"}` を書く
4. `tests/test_models.py` に、任意の次元で動くテストを足す
