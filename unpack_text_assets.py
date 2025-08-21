import json
import logging
from pathlib import Path
import UnityPy
from typing import Union, Any


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def process_text_asset(data: Any, dest_path: Path) -> None:
    try:
        json_data = json.loads(data.m_Script)
        dest_path = dest_path.with_suffix(".json")
        with open(dest_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        logging.info("Saved JSON file: %s", dest_path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        dest_path = dest_path.with_suffix(".txt")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(data.text)
        logging.info("Saved text file: %s", dest_path)


def unpack_text_assets(
    source_folder: Union[str, Path], destination_folder: Union[str, Path]
) -> None:
    setup_logging()
    source_path = Path(source_folder)
    dest_path = Path(destination_folder)

    if not source_path.exists():
        raise FileNotFoundError(f"Source folder not found: {source_path}")

    logging.info("Starting asset unpacking from %s to %s", source_path, dest_path)

    for file_path in source_path.rglob("*"):
        if file_path.is_file():
            try:
                env = UnityPy.load(str(file_path))

                for obj in env.objects:
                    if obj.type.name == "TextAsset":
                        data = obj.read()
                        relative_path = file_path.relative_to(source_path)
                        dest = dest_path / relative_path.parent / data.m_Name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        process_text_asset(data, dest)
            except Exception as e:
                logging.error("Error processing %s: %s", file_path, str(e))

    logging.info("Asset unpacking completed")


if __name__ == "__main__":
    unpack_text_assets("TextAssets/assets", "TextAssets/unpack_assets")
