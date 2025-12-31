from models.csv_diamond import CSVDiamond
from models.csv_gemstones import CSVGemstone

# Get Stone Model
def get_stone_model(stone_type: str):
    stone_type = stone_type.lower()

    if stone_type in ["lab", "natural"]:
        return CSVDiamond
    elif stone_type == "gemstones":
        return CSVGemstone
    else:
        raise ValueError(f"Invalid stone type: {stone_type}")
