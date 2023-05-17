import argparse
import exifread


def get_creation_date(tags):
    if 'Image DateTime' in tags:
        return str(tags['Image DateTime'])
    elif 'EXIF DateTimeOriginal' in tags:
        return str(tags['EXIF DateTimeOriginal'])
    else:
        return "Unknown"


def get_image_metadata(file_path):
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f)
        return tags


def display_image_metadata(file_paths):
    for file_path in file_paths:
        print(f"File: {file_path}")
        metadata = get_image_metadata(file_path)

        # Basic attributes
        creation_date = get_creation_date(metadata)
        print(f"Creation Date: {creation_date}")

        # EXIF data
        print("EXIF Data:")
        for tag, value in metadata.items():
            if tag.startswith('EXIF ') or tag.startswith('Image '):
                print(f"{tag}: {value}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Scorpion - Image Metadata Parser')
    parser.add_argument('files', metavar='FILE', nargs='+', help='Image files to parse')
    args = parser.parse_args()

    display_image_metadata(args.files)


if __name__ == '__main__':
    main()
