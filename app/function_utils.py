import json
import subprocess


def type_check_raise(obj, *cls):
    is_correct = any([isinstance(obj, c) for c in cls])
    if is_correct:
        return True
    raise ValueError(f"obj is not type of any {cls} but a {type(obj)}")

def sanitize_string(value: str) -> str:
    """Dosya sistemi uyumluluğu için geçersiz karakterleri temizler."""
    for char in ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']:
        value = value.replace(char, '_')
    return value.strip()

def run_process(args:list[str], return_json:bool = False):
    if not return_json:
        subprocess.run(args, check=True)
        return
    result = subprocess.run(args, text=True, check=True, capture_output=True)
    return json.loads(result.stdout)