import glob
import os

from FaceExtractor import FaceExtractor
from VideoSplitter import VideoSplitter
from FileExtensions import VIDEO_EXTENSIONS, IMAGE_EXTENSIONS


def chunk_distribution(files, cores) -> list[list[list[tuple]]]:
    chunk_size = max(len(files) // cores, 1)
    chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]
    return chunks


def process_image_files(base_face_output_path, dataset_dir) -> list[tuple[str, str]]:
    image_files: list[tuple[str, str]] = []
    for path, dirs, filenames in os.walk(dataset_dir):
        if not filenames:
            continue
        if any(f.lower().endswith(IMAGE_EXTENSIONS) for f in filenames):
            face_output_path = os.path.join(base_face_output_path, os.path.basename(path))
            os.makedirs(face_output_path, exist_ok=True)
            image_files.append((path, face_output_path))
    return image_files


def process_video_files(dataset_dir, frame_output_dir, percent_kept) -> list[tuple[str, str, float]]:
    video_files: list[tuple[str, str, float]] = []
    for file in glob.iglob(os.path.join(dataset_dir, '**', '*.*'), recursive=True):
        if file.lower().endswith(VIDEO_EXTENSIONS):
            video_files.append((file, frame_output_dir, percent_kept))
    return video_files


def process_video(video_file_path: str, frame_output_dir: str, percent_kept: float = 0.5) -> None:
    splitter = VideoSplitter(video_file_path=video_file_path, frame_output_path=frame_output_dir)
    splitter.split_video()
    splitter.extract_frames(percent_kept=percent_kept)


def process_image(image_file_path: str, face_output_path: str) -> None:
    extractor = FaceExtractor(image_path=image_file_path, output_dir=face_output_path)
    extractor.extract_humans()
    extractor.extract_faces()
    extractor.save_face()
