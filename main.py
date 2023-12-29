import argparse
import logging

from processes import default_process, face_process, frame_process

logging.basicConfig(filename='main.log', level=logging.ERROR,
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(relativeCreated)6d - %(name)s - %(message)s')


def main():
    parser = argparse.ArgumentParser(prog='FaceRipper', description="Extract faces from a dataset of videos/images",
                                     epilog="NOTE: This program was designed to work on multiple files, make sure to provide the absolute path to a directory and not an individual file")

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    parser.add_argument("Dataset Directory", type=str, help="Path to the dataset directory.")
    parser.add_argument("Frame Output Directory", type=str, nargs="?", default=None,
                        help="Path to the frame output directory.")
    parser.add_argument("Base Face Output Directory", type=str, nargs="?", default=None,
                        help="Path to the base face output directory.")
    parser.add_argument("--percent_of_frames_kept", type=float, default=0.5,
                        help="Percent of frames kept (between 0 and 1, default is 0.5).")

    frame_parser = subparsers.add_parser("split", help="Split video into frames")
    frame_parser.set_defaults(func=frame_process)

    face_parser = subparsers.add_parser("extract", help="Extract faces from provided image(s)")
    face_parser.set_defaults(func=face_process)

    args = parser.parse_args()

    if args.subcommand is None:
        default_process(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
