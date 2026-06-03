from pathlib import Path
import yaml

from ai_scout.init.utils import deep_merge


CONFIG_DIR = Path.home() / ".ai-scout"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
DEFAULT_CONFIG_PATH = Path("config/default.config.yaml")


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def prompt_user() -> dict:
    print("\n🚀 AI Scout Initialization\n")

    model = input("What model to use for generating sources? (default: gpt-5-mini): ").strip()
    if not model:
        model = "gpt-5-mini"

    interests_raw = input("What are your interests? (comma separated): ").strip()

    interests = [
        i.strip() for i in interests_raw.split(",") if i.strip()
    ]

    return {
        "llm": {
            "source_generation_model": model
        },
        "interests": interests
    }


def write_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(yaml.dump(config, sort_keys=False))


def run_init():
    print("Loading default configuration...")

    base_config = load_yaml(DEFAULT_CONFIG_PATH)
    user_input = prompt_user()
    existing_user_config = load_yaml(CONFIG_PATH)

    merged = deep_merge(base_config, existing_user_config)
    merged = deep_merge(merged, user_input)

    write_config(merged)

    print(f"\n✅ Config written to {CONFIG_PATH}")