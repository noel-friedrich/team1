import subprocess
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Global video parameters
WIDTH = 1280
HEIGHT = 720
FPS = 10  # frames per second for video output timing
SCROLL_SPEED = 5  # pixels per frame to scroll text upward
BLACK_SCREEN_DURATION = 2  # seconds to display black screen between messages

# Font settings for PIL
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"  # Ensure this font file is available or update to an absolute path.
FONT_SIZE = 32


def wrap_text(text, pil_font, max_width):
    """
    Wraps the text into lines that fit within max_width.
    Respects forced newlines ("\n") and breaks very long words letter-by-letter.
    """
    lines = []
    paragraphs = text.split("\n")
    for paragraph in paragraphs:
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            test_line = word if current_line == "" else current_line + " " + word
            text_width, _ = pil_font.getsize(test_line)
            if text_width > max_width:
                if current_line == "":
                    # Break a very long word letter by letter.
                    for i in range(len(word)):
                        test_word = word[: i + 1]
                        text_width, _ = pil_font.getsize(test_word)
                        if text_width > max_width:
                            lines.append(word[:i])
                            current_line = word[i:]
                            break
                    else:
                        current_line = word
                else:
                    lines.append(current_line)
                    current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    return lines


class VideoStreamer:
    def __init__(
        self, stream_mode=False, stream_url=None, width=WIDTH, height=HEIGHT, fps=FPS
    ):
        """
        Initializes the VideoStreamer.
        stream_mode: Boolean toggle. True to stream via FFmpeg; False to play locally.
        stream_url: Required if stream_mode is True.
        """
        self.stream_mode = stream_mode
        self.width = width
        self.height = height
        self.fps = fps
        self.bg_color = (0, 0, 0)
        self.font_color = (255, 255, 255)
        self.x_margin = 50
        self.y_offset = 50
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        self.line_height = self.font.getsize("A")[1]
        self.line_margin = 10
        self.max_lines = (self.height - self.y_offset) // (
            self.line_height + self.line_margin
        )
        self.current_offset = 0

        if self.stream_mode:
            if stream_url is None:
                raise ValueError(
                    "A stream_url must be provided when stream_mode is True."
                )
            self.process = self._start_ffmpeg(stream_url)
        else:
            self.process = None
            cv2.namedWindow("Live Stream", cv2.WINDOW_NORMAL)

    def _start_ffmpeg(self, stream_url):
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            f"{self.width}x{self.height}",
            "-r",
            str(self.fps),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-b:v",
            "3000k",
            "-preset",
            "ultrafast",
            "-f",
            "flv",
            stream_url,
        ]
        return subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    def stream_text(self, text, typing_delay=0.03):
        """
        "Types" the text one character at a time.
        The text is wrapped and, if too tall, scrolls upward like a crawl.
        In stream_mode, frames are piped to FFmpeg; in local mode, frames are shown in a window.
        The typing_delay controls the delay between each character.
        """
        text_buffer = ""
        for char in text:
            text_buffer += char
            lines = wrap_text(text_buffer, self.font, self.width - 2 * self.x_margin)
            total_text_height = len(lines) * (self.line_height + self.line_margin)
            available_height = self.height - self.y_offset
            target_offset = max(0, total_text_height - available_height)
            # Smoothly adjust the scroll offset.
            if self.current_offset < target_offset:
                self.current_offset = min(
                    self.current_offset + SCROLL_SPEED, target_offset
                )
            elif self.current_offset > target_offset:
                self.current_offset = target_offset

            # Create a new image and draw the text.
            img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
            draw = ImageDraw.Draw(img)
            for i, line in enumerate(lines):
                y = (
                    self.y_offset
                    + i * (self.line_height + self.line_margin)
                    - self.current_offset
                )
                if -self.line_height < y < self.height:
                    draw.text(
                        (self.x_margin, y), line, font=self.font, fill=self.font_color
                    )
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if self.stream_mode:
                self.process.stdin.write(frame.tobytes())
                time.sleep(1.0 / self.fps)
            else:
                cv2.imshow("Live Stream", frame)
                # Process window events and allow exit on pressing 'q'
                if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord("q"):
                    return
            time.sleep(typing_delay)  # Delay between characters (typewriter effect)
        self.current_offset = 0

    def display_black_screen(self, duration=BLACK_SCREEN_DURATION):
        """
        Displays a black screen for the specified duration.
        """
        img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        num_frames = int(duration * self.fps)
        for _ in range(num_frames):
            if self.stream_mode:
                self.process.stdin.write(frame.tobytes())
                time.sleep(1.0 / self.fps)
            else:
                cv2.imshow("Live Stream", frame)
                if cv2.waitKey(int(1000 / self.fps)) & 0xFF == ord("q"):
                    return

    def close(self):
        """
        Closes resources: the FFmpeg process or OpenCV window.
        """
        if self.stream_mode:
            self.process.stdin.close()
            self.process.wait()
        else:
            cv2.destroyAllWindows()
