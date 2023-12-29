import logging
import os
import subprocess as sp

logger = logging.getLogger(__name__)


class VideoSplitter:
    def __init__(self, video_file_path: str | None, frame_output_path: str, img_format: str = "png",
                 audio_format: str = "pcm_s16le") -> None:
        """
        :parameter: video_file_path: Absolute path to a video file
        :parameter: frame_output_path: Absolute path to frame output directory
        :parameter: img_format: Any cv2 supported image format
        :parameter: audio_format: Any ffmpeg supported audio format
        """
        self.cap = None
        if video_file_path is not None:
            self.video_file_path = video_file_path
            self.video_file_name = os.path.basename(video_file_path)
        else:
            pass
        self.frame_output_path = frame_output_path
        self.img_format = img_format
        self.audio_format = audio_format

    def split_video(self, audio_dir: str = None, video_dir: str = None) -> None:
        """
        :parameter: audio_dir: Absolute path to an optional audio output directory
        :parameter: video_dir: Absolute path to an optional video output directory
        :exception: CalledProcessError: Returns exit status of ffmpeg command
        """
        audio_file_path, video_file_path = self._get_files(audio_dir, video_dir)

        sub_dir = os.path.join(os.path.dirname(os.path.splitext(audio_file_path)[0]), os.path.splitext(self.video_file_path)[0])
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        audio_file_path = os.path.join(sub_dir, os.path.basename(audio_file_path))

        isffmpeg = self.is_ffmpeg_installed()
        if not isffmpeg:
            logger.exception("ffmpeg not installed")
            raise RuntimeError("ffmpeg not installed")

        try:
            command = [
                    "ffmpeg",
                    "-i", video_file_path,
                    "-vn",
                    "-y",
                    "-acodec", self.audio_format,
                    "-ar", "44100",
                    audio_file_path
                    ]
            sp.run(command, check=True, stdout=sp.PIPE, stderr=sp.PIPE)
        except sp.CalledProcessError as e:
            logger.exception(f"There was an error splitting the video {video_file_path}: {e}")

            
    def extract_frames(self, percent_kept: float = 0.5) -> None:
        """
        :parameter: Percent_kept: Value ranging from 0.0 to 1.0 that specifies the number of frames kept
        :exception: CalledProcessError: Returns exit status of ffmpeg command
        """
        video_path = self._get_files()[1]

        isffmpeg = self.is_ffmpeg_installed()
        if not isffmpeg:
            logger.exception("ffmpeg not installed")
            raise RuntimeError("ffmpeg not installed")

        if percent_kept > 1:
            percent_kept = 1.0
            logger.warning("Percentage of kept frames cannot be higher than total frame count")

        sub_dir = os.path.join(self.frame_output_path, os.path.splitext(self.video_file_name)[0])
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        try:
            command = [
                    "ffmpeg",
                    "-i", video_path,
                    "-vf", f"select=not(mod(n\,{int(1 / percent_kept)})),setpts=N/FRAME_RATE/TB",
                    "-vsync", "vfr",
                    "-y",
                    f"{sub_dir}/{os.path.splitext(self.video_file_name)[0]}_frame_%d.{self.img_format}"
                    ]
            sp.run(command, check=True, stdout=sp.PIPE, stderr=sp.PIPE)
        except sp.CalledProcessError as e:
            logger.exception(f"There was an error extracting frames from {video_path}: {e}")

    @staticmethod
    def is_ffmpeg_installed() -> bool:
        """
        :returns: Boolean based on if ffmpeg is installed or not
        """
        try:
            sp.run(["ffmpeg"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            return True
        except:
            return False

    def _on_path_set(self) -> None:
        """
        :exception: Missing File
        """
        if self.video_file_path is not None:
            self.video_file_name = os.path.basename(self.video_file_path)
        else:
            logger.exception("File not found")
            raise FileNotFoundError

    def _get_files(self, audio_dir: str = None, video_dir: str = None) -> tuple[str, str]:
        """
        Gets the file paths for the audio and video files.

        :parameter: audio_dir: Absolute path to an optional audio output directory
        :parameter: video_dir: Optional absolute path to a video directory
        :returns: tuple[str, str]
        """
        self._on_path_set()
        if not hasattr(self, '_audio_dir'):
            self._audio_dir = audio_dir or os.path.dirname(self.video_file_path)
        if not hasattr(self, '_video_dir'):
            self._video_dir = video_dir or self.video_file_path
        audio_file_path = os.path.join(self._audio_dir, os.path.splitext(self.video_file_name)[0] + ".wav")
        video_file_path = self._video_dir

        return audio_file_path, video_file_path
