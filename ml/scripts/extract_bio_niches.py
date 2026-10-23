"""Profile bios -> niche keyword counts, written next to the data as bio_niches.csv.

Bios are personal text, so they are never stored or copied: only the number of niche keywords per niche is
written, keyed by the same salted pseudonym as everywhere else.

    python scripts/extract_bio_niches.py "<dataset folder>/users_influencers_SPOD"
"""
import csv
import hashlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mlrec.config import DATA_DIR

# Words people use to describe themselves in a bio; deliberately broader than the hashtag keywords.
BIO_KEYWORDS = {
    "fashion": {"fashion", "style", "stylist", "ootd", "outfit", "outfits", "fashionblogger", "styleblogger", "model",
                "modeling"},
    "beauty": {"beauty", "makeup", "mua", "skincare", "makeupartist", "beautyblogger", "hair", "hairstylist", "nails",
               "lashes", "cosmetics"},
    "fitness": {"fitness", "fit", "trainer", "workout", "gym", "yoga", "pilates", "athlete", "runner", "running",
                "crossfit", "nutrition", "coach"},
    "food": {"food", "foodie", "recipes", "recipe", "chef", "cook", "cooking", "baker", "baking", "foodblogger", "vegan",
             "eats"},
    "travel": {"travel", "traveler", "traveller", "wanderlust", "travelblogger", "adventure", "explorer", "nomad"},
    "family": {"mom", "mama", "mommy", "mother", "momblogger", "motherhood", "dad", "father", "family", "twins", "kids",
               "boymom", "girlmom"},
    "home": {"home", "interior", "interiors", "decor", "homedecor", "diy", "design", "designer", "renovation"},
}
BIO_FIELD = 7   # position of the bio in the dataset's tab-separated profile files


def main(src: str) -> None:
    salt = (DATA_DIR / "pseudonym_salt.txt").read_text().strip()
    out = DATA_DIR / "bio_niches.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["creator_id", "has_bio", *BIO_KEYWORDS])
        for n in sorted(os.listdir(src)):
            try:
                p = open(os.path.join(src, n), encoding="utf-8", errors="replace").read().rstrip("\n").split("\t")
            except OSError:
                continue
            bio = p[BIO_FIELD] if len(p) > BIO_FIELD and p[BIO_FIELD] != "NULL" else ""
            words = set(re.findall(r"[a-z]+", bio.lower()))
            cid = "c_" + hashlib.sha256((salt + n).encode()).hexdigest()[:10]
            w.writerow([cid, int(bool(bio)), *(len(words & kw) for kw in BIO_KEYWORDS.values())])
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1])
