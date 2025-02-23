import subprocess
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Global video parameters
WIDTH = 1280
HEIGHT = 720
FPS = 10  # frames per second for video output timing
BLACK_SCREEN_DURATION = 2  # seconds to display black screen between messages

# Font settings for PIL
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"  # Ensure this font file is available or update to an absolute path.
FONT_SIZE = 32


def layout_text(text, pil_font, max_width):
    """
    Pre-calculate the layout of text given a maximum width.
    The text is split into paragraphs at each newline.
    Then, each paragraph is wrapped word-by-word:
      - If adding the next word would exceed max_width, start a new line.
      - Forced newlines are preserved.
    Returns a list of lines.
    """
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        words = para.split()
        if not words:
            lines.append("")
            continue
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + " " + word
            line_width, _ = pil_font.getsize(test_line)
            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    return lines


class VideoStreamer:
    def __init__(
        self,
        stream_mode=False,
        stream_url=None,
        width=WIDTH,
        height=HEIGHT,
        fps=FPS,
        bottom_margin=100,
    ):
        """
        Initializes the VideoStreamer.
        stream_mode: Boolean toggle. True to stream via FFmpeg; False to play locally.
        stream_url: Required if stream_mode is True.
        bottom_margin: Minimum number of pixels to leave at the bottom edge.
        """
        self.stream_mode = stream_mode
        self.width = width
        self.height = height
        self.fps = fps
        self.bottom_margin = bottom_margin
        self.bg_color = (0, 0, 0)
        self.font_color = (255, 255, 255)
        self.x_margin = 50
        self.y_offset = 50
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        self.line_height = self.font.getsize("A")[1]
        self.line_margin = 10
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

    def stream_text(self, text, chars_per_sec=50, average_chars_per_line=50):
        """
        "Types" the text by outputting a specified number of characters per second.
        Instead of wrapping text live each frame, we calculate the layout (word-wrapped)
        once for the current buffer. If adding a word would cross the right edge, it is
        placed on the next line.

        The typewriter effect reveals the text gradually, using a dynamic scroll speed
        that depends on the window height (with a bottom margin) and chars_per_sec.

        Parameters:
            text (str): The full text to be rendered.
            chars_per_sec (float): Number of characters that should be output per second.
            average_chars_per_line (int): Average number of characters per line (for scroll speed calculation).
        """
        full_text = text  # The complete text to be eventually displayed.
        text_buffer = ""
        index = 0
        char_accumulator = 0.0  # Fractional accumulator for characters
        delay = 1.0 / self.fps  # Frame delay based on fps

        # Pre-calculate the final layout for consistency (if needed).
        final_lines = layout_text(full_text, self.font, self.width - 2 * self.x_margin)

        # Compute dynamic scroll speed (in pixels per frame):
        # - lines_per_sec = chars_per_sec / average_chars_per_line
        # - pixels_per_sec = lines_per_sec * (line_height + line_margin)
        # - scroll_speed_per_frame = pixels_per_sec / fps
        dynamic_scroll_speed = (
            (
                (chars_per_sec / average_chars_per_line)
                * (self.line_height + self.line_margin)
            )
            / self.fps
            * 1.5
        )

        # Gradually reveal the text.
        while index < len(full_text):
            char_accumulator += chars_per_sec / self.fps
            num_to_add = int(char_accumulator)
            if num_to_add > 0:
                text_buffer += full_text[index : index + num_to_add]
                index += num_to_add
                char_accumulator -= num_to_add

            # Calculate layout for the current text.
            lines = layout_text(text_buffer, self.font, self.width - 2 * self.x_margin)
            total_text_height = len(lines) * (self.line_height + self.line_margin)
            # Adjust available height to include a bottom margin.
            available_height = self.height - self.y_offset - self.bottom_margin
            target_offset = max(0, total_text_height - available_height)

            # Use the dynamic scroll speed.
            if self.current_offset < target_offset:
                self.current_offset = min(
                    self.current_offset + dynamic_scroll_speed, target_offset
                )
            elif self.current_offset > target_offset:
                self.current_offset = target_offset

            # Create an image and draw the text.
            img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
            draw = ImageDraw.Draw(img)
            for j, line in enumerate(lines):
                y = (
                    self.y_offset
                    + j * (self.line_height + self.line_margin)
                    - self.current_offset
                )
                # Only draw if within visible region.
                if -self.line_height < y < self.height - self.bottom_margin:
                    draw.text(
                        (self.x_margin, y), line, font=self.font, fill=self.font_color
                    )
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if self.stream_mode:
                self.process.stdin.write(frame.tobytes())
            else:
                cv2.imshow("Live Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    return

            time.sleep(delay)
        self.current_offset = 0

    def close(self):
        """
        Closes resources: the FFmpeg process or OpenCV window.
        """
        if self.stream_mode:
            self.process.stdin.close()
            self.process.wait()
        else:
            cv2.destroyAllWindows()
