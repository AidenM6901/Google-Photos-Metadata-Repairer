import os
import zipfile
import tempfile
import shutil
import subprocess
import json
from datetime import datetime
from tqdm import tqdm

SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov', '.avi']

def move_to_failed(src_path, root_folder, failed_folder):
    rel_path = os.path.relpath(src_path, root_folder)
    dest_path = os.path.join(failed_folder, rel_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.move(src_path, dest_path)
    print(f"❌ Moved to Failed: {rel_path}")

def fix_metadata_and_copy(root_folder, final_folder, failed_folder):
    all_media_files = []

    # Find all supported media files
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in SUPPORTED_EXTENSIONS:
                all_media_files.append(os.path.join(dirpath, filename))

    for media_path in tqdm(all_media_files, desc="Processing files", unit="file"):
        dirpath = os.path.dirname(media_path)
        filename = os.path.basename(media_path)
        json_path = os.path.join(dirpath, filename + ".supplemental-metadata.json")

        try:
            # Try fixing metadata
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                photo_taken_time = data.get("photoTakenTime", {}).get("timestamp")
                latitude = data.get("geoData", {}).get("latitude")
                longitude = data.get("geoData", {}).get("longitude")

                if photo_taken_time:
                    dt = datetime.utcfromtimestamp(int(photo_taken_time))
                    dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")
                    ext = os.path.splitext(filename)[1].lower()
                    cmd = []

                    if ext in ['.jpg', '.jpeg', '.png', '.heic']:
                        cmd = ["exiftool", f"-DateTimeOriginal={dt_str}"]
                        if latitude is not None and longitude is not None:
                            cmd += [
                                f"-GPSLatitude={abs(latitude)}",
                                "-GPSLatitudeRef=N" if latitude >= 0 else "-GPSLatitudeRef=S",
                                f"-GPSLongitude={abs(longitude)}",
                                "-GPSLongitudeRef=E" if longitude >= 0 else "-GPSLongitudeRef=W",
                            ]
                    elif ext in ['.mp4', '.mov', '.avi']:
                        cmd = [
                            "exiftool",
                            f"-CreateDate={dt_str}",
                            f"-MediaCreateDate={dt_str}"
                        ]

                    cmd += ["-overwrite_original", media_path]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    print(f"No timestamp in metadata: {json_path}")
            else:
                print(f"No metadata file for: {filename}")

            # Copy to Final
            rel_path = os.path.relpath(media_path, root_folder)
            dest_path = os.path.join(final_folder, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(media_path, dest_path)

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            move_to_failed(media_path, root_folder, failed_folder)

def process_all_zips_in_start():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    start_folder = os.path.join(script_dir, "Start")
    final_folder = os.path.join(script_dir, "Final")
    failed_folder = os.path.join(script_dir, "Failed")
    os.makedirs(final_folder, exist_ok=True)
    os.makedirs(failed_folder, exist_ok=True)

    if not os.path.exists(start_folder):
        print(f"'Start' folder does not exist at {start_folder}")
        return

    zip_files = [f for f in os.listdir(start_folder) if f.lower().endswith(".zip")]
    if not zip_files:
        print("No ZIP files found in 'Start' folder.")
        return

    for zip_file in zip_files:
        zip_path = os.path.join(start_folder, zip_file)
        print(f"\n📦 Processing ZIP: {zip_file}")

        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"📂 Extracting to temporary folder: {tmpdir}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            fix_metadata_and_copy(tmpdir, final_folder, failed_folder)

    print(f"\n✅ All done!\n✔️ Final files in: {final_folder}\n❌ Failed files in: {failed_folder}")

if __name__ == "__main__":
    process_all_zips_in_start()
