#!/usr/bin/env python3
"""Validate amap-lead-keyword-planner JSON output using only the stdlib."""

import argparse
import json
import re
import sys
from pathlib import Path

TOP_KEYS = {"business_summary", "priority_1", "priority_2", "priority_3"}
ITEM_KEYS = {"keyword", "logic", "market_size", "trend"}
LEVELS = ("priority_1", "priority_2", "priority_3")
TRENDS = ("上涨", "温和上涨", "结构性分化", "下行")
DEFAULT_COUNTS = {"priority_1": 16, "priority_2": 20, "priority_3": 20}


def validate(data, require_default_counts=False):
    errors = []
    if not isinstance(data, dict):
        return ["顶层必须是 JSON object。"]
    if set(data) != TOP_KEYS:
        errors.append(f"顶层字段必须且只能是 {sorted(TOP_KEYS)}；实际为 {sorted(data)}。")
    summary = data.get("business_summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("business_summary 必须是非空字符串。")

    seen = {}
    for level in LEVELS:
        items = data.get(level)
        if not isinstance(items, list):
            errors.append(f"{level} 必须是数组。")
            continue
        if require_default_counts and len(items) != DEFAULT_COUNTS[level]:
            errors.append(f"{level} 应有 {DEFAULT_COUNTS[level]} 条，实际 {len(items)} 条。")
        for index, item in enumerate(items, 1):
            location = f"{level}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{location} 必须是 object。")
                continue
            if set(item) != ITEM_KEYS:
                errors.append(f"{location} 字段必须且只能是 {sorted(ITEM_KEYS)}。")
            for field in ITEM_KEYS:
                if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                    errors.append(f"{location}.{field} 必须是非空字符串。")
            keyword = item.get("keyword")
            if isinstance(keyword, str) and keyword.strip():
                normalized = re.sub(r"\s+", "", keyword).lower()
                if normalized in seen:
                    errors.append(f"关键词重复：{seen[normalized]} 与 {location} 都是“{keyword}”。")
                else:
                    seen[normalized] = location
            trend = item.get("trend")
            if isinstance(trend, str) and trend.strip() and not trend.startswith(TRENDS):
                errors.append(f"{location}.trend 必须以 {TRENDS} 之一开头；实际为“{trend}”。")
    return errors


def main():
    parser = argparse.ArgumentParser(description="校验地图获客行业关键词 JSON")
    parser.add_argument("json_file", type=Path, help="待校验的 JSON 文件")
    parser.add_argument("--require-default-counts", action="store_true", help="要求三级数量分别为 16、20、20")
    args = parser.parse_args()
    try:
        with args.json_file.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"读取或解析失败：{exc}", file=sys.stderr)
        return 2
    errors = validate(data, args.require_default_counts)
    if errors:
        print(f"校验失败，共 {len(errors)} 项：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    counts = {level: len(data[level]) for level in LEVELS}
    print(f"校验通过：{counts}，共 {sum(counts.values())} 个关键词。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
