// クラス名の合成: CSS Modules のクラス名(ハッシュつき)を、名前で引いてつなぐ
// 使い方: const cx = bind(styles); className={cx("row", active && "on")}
// 対応表に無い名前は、親から渡された(すでにハッシュ済みの)クラス名として、そのまま通す
type ClassMap = Record<string, string>;

export function bind(...maps: ClassMap[]) {
  return (...values: unknown[]): string => {
    const names: string[] = [];
    for (const value of values) {
      if (typeof value !== "string") continue;
      for (const token of value.split(/\s+/).filter(Boolean)) {
        const hashed = maps.map((map) => map[token]).filter(Boolean);
        names.push(...(hashed.length ? hashed : [token]));
      }
    }
    return names.join(" ");
  };
}
