
import os
import requests

FONTS = {
    "dialogue": [
        ("ComicNeue-Bold.ttf", "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf"),
        ("KomikaAxis.ttf", "https://dl.dafont.com/dl/?f=komika_axis") # Direct link might fail if not zip, checking valid direct TTF links
    ],
    "sfx": [
        ("Bangers-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/bangers/Bangers-Regular.ttf")
    ],
    "narrator": [
        ("Roboto-Medium.ttf", "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Medium.ttf")
    ]
}

# Use reliable raw github links for Google Fonts
FIXED_FONTS = {
    "dialogue": [
        ("ComicNeue-Bold.ttf", "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf"),
        ("MangaTemple.ttf", "https://github.com/google/fonts/raw/main/ofl/kosugi/Kosugi-Regular.ttf") # Using Kosugi as placeholder for Manga style
    ],
    "sfx": [
        ("Bangers-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/bangers/Bangers-Regular.ttf")
    ],
    "narrator": [
         ("Roboto-Medium.ttf", "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Medium.ttf")
    ]
}

def download_fonts():
    base_dir = "backend/fonts"
    for category, fonts in FIXED_FONTS.items():
        cat_dir = os.path.join(base_dir, category)
        os.makedirs(cat_dir, exist_ok=True)
        
        for name, url in fonts:
            path = os.path.join(cat_dir, name)
            if not os.path.exists(path):
                print(f"Downloading {name}...")
                try:
                    r = requests.get(url)
                    if r.status_code == 200:
                        with open(path, 'wb') as f:
                            f.write(r.content)
                        print(f"✅ Saved {path}")
                    else:
                        print(f"❌ Failed {url} - {r.status_code}")
                except Exception as e:
                    print(f"❌ Error {url} - {e}")
            else:
                 print(f"⏭️  Exists {name}")

if __name__ == "__main__":
    download_fonts()
