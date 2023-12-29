import multiprocessing

from utils import process_image_files, process_video_files, process_image, process_video, chunk_distribution


def default_process(args) -> None:
    dataset_dir = args.dataset_dir
    frame_output_dir = args.frame_output_dir
    base_face_output_path = args.base_face_output_path
    percent_kept = args.percent_of_frames_kept

    cores = multiprocessing.cpu_count()

    video_files = process_video_files(dataset_dir, frame_output_dir, percent_kept)
    video_chunks = chunk_distribution(video_files, cores)

    image_files = process_image_files(base_face_output_path, frame_output_dir)
    image_chunks = chunk_distribution(image_files, cores)

    with multiprocessing.Pool(processes=cores) as pool:
        pool.starmap(process_video, video_chunks)
        pool.starmap(process_image, image_chunks)


def frame_process(args) -> None:
    dataset_dir = args.dataset_dir
    frame_output_dir = args.frame_output_dir
    percent_kept = args.percent_of_frames_kept

    cores = multiprocessing.cpu_count()

    video_files = process_video_files(dataset_dir, frame_output_dir, percent_kept)
    video_chunks = chunk_distribution(video_files, cores)

    with multiprocessing.Pool(processes=cores) as pool:
        pool.starmap(process_video, video_chunks)


def face_process(args) -> None:
    dataset_dir = args.dataset_dir
    base_face_output_path = args.base_face_output_path

    cores = multiprocessing.cpu_count()

    image_files = process_image_files(base_face_output_path, dataset_dir)
    image_chunks = chunk_distribution(image_files, cores)

    with multiprocessing.Pool(processes=cores) as pool:
        pool.starmap(process_image, image_chunks)
