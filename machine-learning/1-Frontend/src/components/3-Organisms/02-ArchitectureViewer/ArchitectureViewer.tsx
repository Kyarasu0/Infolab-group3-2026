import type { Architecture } from "../../../functions/api-types";
import styles from "./ArchitectureViewer.module.css";

interface ArchitectureViewerProps {
  architecture: Architecture | null;
}

export function ArchitectureViewer({ architecture }: ArchitectureViewerProps) {
  if (!architecture) {
    return <p className={styles.empty}>学習済みのシナリオを選ぶと、層ごとの構成を表示します</p>;
  }
  const autoencoder = architecture.autoencoder;
  return (
    <section className={styles.viewer}>
      <h3 className={styles.title}>モデルの構成</h3>
      <p>入力次元: {architecture.input_dim}</p>
      {architecture.svm && (
        <p>SVM サポートベクター: {architecture.svm.total_support_vectors}個(
          {Object.entries(architecture.svm.support_vectors_per_class).map(([label, count]) => `${label}: ${count}`).join(", ")})
        </p>
      )}
      <p>クラスタリング: {Object.entries(architecture.clustering).map(([label, info]) => `${label} → ${info.cluster_count}タイプ`).join(", ") || "なし"}</p>
      {autoencoder && (
        <>
          <p>オートエンコーダー: 入力 {autoencoder.input_dim} → 圧縮 {autoencoder.latent_dim} / 合計パラメータ {autoencoder.total_parameters}個</p>
          <table className={styles.table}>
            <thead>
              <tr><th>層</th><th>部分</th><th>種類</th><th>入力→出力</th><th>パラメータ数</th><th>重みの平均 / 標準偏差</th></tr>
            </thead>
            <tbody>
              {autoencoder.layers.map((layer) => (
                <tr key={layer.layer_number}>
                  <td>{layer.layer_number}</td>
                  <td>{layer.part}</td>
                  <td>{layer.type}</td>
                  <td>{layer.in_features !== undefined ? `${layer.in_features} → ${layer.out_features}` : "-"}</td>
                  <td>{layer.parameter_count}</td>
                  <td>{layer.weight ? `${layer.weight.mean.toFixed(3)} / ${layer.weight.std.toFixed(3)}` : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
