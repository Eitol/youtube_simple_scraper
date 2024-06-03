import os

FILE_WITH_PAGE_HEADER_RENDERER = "example_1.json5"
EXPECTED_VIDEOS = "expected_videos.json"


def read_test_file(file_name: str) -> str:
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data", file_name)
    with open(file_path, 'r') as file:
        return file.read()
