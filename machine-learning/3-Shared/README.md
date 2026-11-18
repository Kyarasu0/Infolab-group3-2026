# 3-Shared

フロントエンド(TypeScript)とバックエンド(Python)の**両方が読むもの**を置く。
言語に依存しないよう、JSONで書く。片側だけが使うもの(`models/` など)は置かない(Knowledgeの `3-small-and-clear`)。

| ファイル | 中身 | 使い方 |
|---|---|---|
| `api-list.json` | API一覧(name・method・path・handler_file・mode・description) | バックエンドは、これを読んでルートを登録し、`name` の関数を実行する。フロントは、`name` でAPIを選んで呼ぶ |
| `concept/modes.json` | モード(`train` / `predict`)と表示名 | 両側で、同じ名前を使う |
| `concept/metrics.json` | 評価指標の名前と表示名 | フロントの表の見出しに使う |

API一覧を共有する方式は、KyamomeChick(`4-web-ui/3-Shared/api-list.json`)にならった。
JSONにコメントは書けないため、何をするAPIかの一言は `description` に書く。

## APIを追加するとき
1. `api-list.json` に1件足す(`handler_file` は `name` の「_」を「-」にしたもの + `.py`)
2. `2-Backend/api/` に、同じ名前のファイルと関数を作る(1 API = 1ファイル = 1関数)
3. フロントの `functions/api-client.ts` に、`callApi("name")` を呼ぶ関数を足す

一覧とファイル・登録されたルートの対応は、テスト(`tests/test_api_registry.py`)が確かめる。
