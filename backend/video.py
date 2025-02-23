import subprocess
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Global video parameters
WIDTH = 854
HEIGHT = 480
FPS = 10
SCROLL_SPEED = 5
BLACK_SCREEN_DURATION = 2

# Font settings for PIL
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"  # Ensure this font file is available
FONT_SIZE = 32


def wrap_text(text, pil_font, max_width):
    """
    Wrap text into lines that fit within max_width.
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
    def __init__(self, stream_url, width=WIDTH, height=HEIGHT, fps=FPS):
        self.width = width
        self.height = height
        self.fps = fps
        self.stream_url = stream_url
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
        self.process = self._start_ffmpeg()

    def _start_ffmpeg(self):
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
            self.stream_url,
        ]
        return subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    def stream_text(self, text, typing_delay=0.05):
        """
        "Types" the text one character at a time.
        The text is wrapped and, if too tall, scrolled upward (Star Wars crawl style).
        """
        text_buffer = ""
        for char in text:
            text_buffer += char
            lines = wrap_text(text_buffer, self.font, self.width - 2 * self.x_margin)
            total_text_height = len(lines) * (self.line_height + self.line_margin)
            available_height = self.height - self.y_offset
            target_offset = max(0, total_text_height - available_height)
            # Adjust the scroll offset smoothly.
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
            self.process.stdin.write(frame.tobytes())
            time.sleep(1.0 / self.fps)
        # Reset scroll offset for the next text message.
        self.current_offset = 0

    def display_black_screen(self, duration=BLACK_SCREEN_DURATION):
        """
        Displays a black screen for the specified duration (in seconds).
        """
        img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        num_frames = int(duration * self.fps)
        for _ in range(num_frames):
            self.process.stdin.write(frame.tobytes())
            time.sleep(1.0 / self.fps)

    def close(self):
        self.process.stdin.close()
        self.process.wait()
