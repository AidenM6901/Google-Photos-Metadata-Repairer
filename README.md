# 📸 Google Photos Takeout Metadata Repairer

This Python script processes ZIP files downloaded from **Google Takeout**, extracts media files (photos & videos), and restores their original metadata — including **timestamps** and **GPS coordinates** — using the accompanying `.json` metadata files. The restored files are organized into a `Final` folder, and any problematic files are moved to a `Failed` folder.

---

## ✨ Features

* ✅ Supports common image and video formats: `.jpg`, `.jpeg`, `.png`, `.heic`, `.mp4`, `.mov`, `.avi`
* 🕒 Restores original **creation date** (EXIF `DateTimeOriginal`, `CreateDate`, etc.)
* 🌍 Re-applies **GPS metadata** if available
* ⚖️ Automatically uses `.json` metadata from Google Takeout
* 📁 Processes multiple ZIP archives at once
* 📦 Separates successful and failed files

---

## 📂 Folder Structure

Place your ZIP files inside a folder called `Start`:

```
project-directory/
├── Start/
│   ├── takeout1.zip
│   └── takeout2.zip
├── Final/          ← Output folder (auto-created)
├── Failed/         ← Files that failed to process (auto-created)
└── repairer.py      ← This script
```

---

## ▶️ Usage

1. **Install Dependencies:**

Make sure you have Python 3 and [ExifTool](https://exiftool.org/) installed.

### 📦 How to Install ExifTool

#### On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install libimage-exiftool-perl
```

#### On macOS (using Homebrew):

```bash
brew install exiftool
```

#### On Windows:

* Download from [ExifTool Downloads](https://exiftool.org/)
* Extract and place the executable in a directory listed in your `PATH`, or run it from the extracted location directly.

2. **Place ZIP Files:**

Put your Google Takeout `.zip` files in the `Start` folder.

3. **Run the Script:**

```bash
python restore.py
```

4. **Results:**

* ✅ Processed files will appear in the `Final` folder with corrected metadata.
* ❌ Any files that failed will be moved to the `Failed` folder for review.

---

## 🧠 How It Works

* Extracts ZIPs to a temporary directory
* Matches each media file with its `.json` metadata (e.g., `IMG_1234.jpg` → `IMG_1234.jpg.supplemental-metadata.json`)
* Uses `exiftool` to inject:

  * `DateTimeOriginal` / `CreateDate`
  * `GPSLatitude` / `GPSLongitude` (with Ref)
* Copies fixed media into `Final/`
* Moves any errors into `Failed/`

---

## 📌 Notes

* Only ZIP files are supported; Google Takeout often splits exports into multiple ZIPs — place them all in `Start`.
* No changes are made to the original ZIP files or input media.
* Metadata is written **in-place** with `-overwrite_original`.

---

## 🛠️ Troubleshooting

* Make sure `exiftool` is installed and available in your PATH.
* Double-check your Takeout includes the `JSON` metadata alongside media.
* If a file has no metadata, it will still be copied but without modifications.

---

## 📄 License

This script is provided under the MIT License. Feel free to modify or contribute!

---

## 🤝 Credits

Built with ❤️ to bring order back to your exported Google Photos memories.
