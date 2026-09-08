import subprocess


class Converter:

    @staticmethod
    def convert(input_file, output_file):

        command = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-vf",
            "format=nv12",
            "-c:v",
            "h264_mediacodec",
            "-g",
            "120",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_file
        ]

        subprocess.run(
            command,
            check=True
        )

        return output_file
