import json
import os
from typing import Any, Dict


def deep_merge(existing: Any, new: Any) -> Any:

    if isinstance(existing, dict) and isinstance(new, dict):
        result = existing.copy()
        for key, new_value in new.items():
            if key in result:
                result[key] = deep_merge(result[key], new_value)
            else:
                result[key] = new_value
        return result

    elif isinstance(existing, list) and isinstance(new, list):
        result = existing.copy()
        for item in new:
            if item not in result:
                result.append(item)
        return result

    else:
        return new


def json_file_merge(file_path: str, new_data: Dict, indent: int = 2) -> bool:
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding="utf-8") as f:
                existing_data = json.load(f)
            merged_data = deep_merge(existing_data, new_data)
        else:
            merged_data = new_data

        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=indent)

        return True

    except json.JSONDecodeError:
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=indent)
        return True

    except Exception:
        return False