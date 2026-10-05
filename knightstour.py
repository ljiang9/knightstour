#!/usr/bin/env python3
"""骑士周游 (Knight's Tour): 在棋盘上找到马走遍每个格子恰好一次的路线。

算法: Warnsdorff 启发式 —— 每次选择"后续出度最小"的候选落点。
纯标准库, 无第三方依赖。
"""

import argparse
import random
import sys

MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]


def parse_coord(text, size):
    """D4 -> (row, col)。A1 为左下角? 本实现: A1 = (0,0) 左上, 行号向下递增。"""
    text = text.strip().upper()
    if len(text) < 2 or not text[0].isalpha() or not text[1:].isdigit():
        raise ValueError(f"坐标无效: {text} (如 D4)")
    col = ord(text[0]) - ord("A")
    row = int(text[1:]) - 1
    if not (0 <= col < size and 0 <= row < size):
        raise ValueError(f"坐标 {text} 超出 {size}x{size} 棋盘")
    return row, col


def to_coord(r, c):
    return f"{chr(ord('A') + c)}{r + 1}"


def onward_degree(board, size, r, c):
    n = 0
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == 0:
            n += 1
    return n


def find_tour(size, start, rng, closed=False, max_attempts=200):
    """Warnsdorff 启发式搜索。返回步数列表 [(r,c)...] 或 None。"""
    sr, sc = start
    for _ in range(max_attempts):
        board = [[0] * size for _ in range(size)]
        path = [(sr, sc)]
        board[sr][sc] = 1
        r, c = sr, sc
        for step in range(2, size * size + 1):
            cands = []
            for dr, dc in MOVES:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == 0:
                    cands.append((nr, nc))
            if not cands:
                break
            # Warnsdorff: 出度最小优先; 同分随机打散(用 rng 保证可复现)
            scored = [(onward_degree(board, size, nr, nc), rng.random(), nr, nc)
                      for nr, nc in cands]
            scored.sort()
            r, c = scored[0][2], scored[0][3]
            board[r][c] = step
            path.append((r, c))
        else:
            if closed:
                er, ec = path[-1]
                if (abs(er - sr), abs(ec - sc)) not in ((1, 2), (2, 1)):
                    continue  # 非闭合, 重试
            return path
    return None


def render(path, size):
    num = {sq: i + 1 for i, sq in enumerate(path)}
    width = len(str(size * size))
    lines = []
    for r in range(size):
        row = []
        for c in range(size):
            row.append(str(num.get((r, c), "·")).rjust(width))
        lines.append(f"{r + 1:>2} " + " ".join(row))
    header = "   " + " ".join(chr(ord("A") + c).rjust(width) for c in range(size))
    return header + "\n" + "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="knightstour", description="骑士周游求解器 (Warnsdorff 启发式)")
    ap.add_argument("--size", type=int, default=8, help="棋盘边长 (默认 8)")
    ap.add_argument("--start", default="A1", help="起点坐标 (默认 A1)")
    ap.add_argument("--closed", action="store_true", help="要求闭合周游(终点能一步回到起点)")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    args = ap.parse_args(argv)

    if not 4 <= args.size <= 10:
        print("error: --size 需在 4 到 10 之间", file=sys.stderr)
        return 2
    try:
        start = parse_coord(args.start, args.size)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    import time
    t0 = time.perf_counter()
    path = find_tour(args.size, start, rng, closed=args.closed)
    dt = time.perf_counter() - t0
    if path is None:
        print("未找到周游路线(启发式在 200 次尝试内失败, 可换 --seed 重试)", file=sys.stderr)
        return 1
    print(f"找到{'闭合' if args.closed else ''}周游: {args.size}x{args.size}, "
          f"起点 {to_coord(*start)}, 共 {len(path)} 步, 用时 {dt:.2f}s")
    print(render(path, args.size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
