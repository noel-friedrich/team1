import re
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

# Font settings (paths)
REGULAR_FONT_PATH = "./fonts/LinLibertine_R.ttf"
BOLD_FONT_PATH = "./fonts/LinLibertine_RB.ttf"
ITALIC_FONT_PATH = "./fonts/LinLibertine_RI.ttf"
FONT_SIZE = 32


def preprocess_markdown(text):
    """
    Preprocess markdown headers.
    Lines starting with '#' are converted into a header marker of the form:
      HEADER{level}: content
    """
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            if stripped[:3] == "###":
                header_level = 0
            else:
                header_level = 4
            # Only because the minimum level is 2
            # header_level = len(stripped) - len(stripped.lstrip("#")) - 2
            content = stripped.lstrip("#").strip()
            new_lines.append(f"HEADER{header_level}: {content}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def layout_text(text, pil_font, max_width):
    """
    Pre-calculate the layout of text given a maximum width.
    Splits each paragraph (by newline) and wraps word-by-word.
    Returns a list of lines (which may include header markers).
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


def get_fonts_for_line(line, base_font):
    """
    Determines the fonts to use for a given line.
    If the line is a header (marked with "HEADERn:"), return:
      (header_font, header_italic, content)
    where header_font is created from the bold font, and header_italic is
    an italic version (for inline formatting inside the header).
    Otherwise, return:
      (regular_font, italic_font, line)
    where regular_font is the provided base_font and italic_font is created
    from the italic font file at the same size.
    """
    match = re.match(r"HEADER(\d+):\s*(.*)", line)
    if match:
        header_level = int(match.group(1))
        content = match.group(2)
        # Example scaling: header size increases with lower header_level.
        new_size = FONT_SIZE + (14 - 2 * header_level)
        header_font = ImageFont.truetype(BOLD_FONT_PATH, new_size)
        header_italic = ImageFont.truetype(ITALIC_FONT_PATH, new_size)
        return header_font, header_italic, content
    else:
        regular = base_font
        italic = ImageFont.truetype(ITALIC_FONT_PATH, FONT_SIZE)
        return regular, italic, line


def draw_markdown_text(draw, x, y, text, regular_font, italic_font):
    """
    Draws a single line of text with inline markdown formatting.
    For inline formatting:
      - Any text enclosed in **...** or *...* is rendered with the italic font.
    Other text is rendered with the regular font.
    """
    # Split text by markers that denote bold or italic segments.
    segments = re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    current_x = x
    for seg in segments:
        if (seg.startswith("**") and seg.endswith("**")) or (
            seg.startswith("*") and seg.endswith("*")
        ):
            # Remove the markers.
            seg_text = seg[2:-2] if seg.startswith("**") else seg[1:-1]
            draw.text((current_x, y), seg_text, font=italic_font, fill=(0, 0, 0))
            w, _ = draw.textsize(seg_text, font=italic_font)
            current_x += w
        else:
            draw.text((current_x, y), seg, font=regular_font, fill=(0, 0, 0))
            w, _ = draw.textsize(seg, font=regular_font)
            current_x += w


class VideoStreamer:
    def __init__(
        self,
        stream_mode=False,
        stream_url=None,
        width=WIDTH,
        height=HEIGHT,
        fps=FPS,
        bottom_margin=50,
    ):
        """
        Initializes the VideoStreamer.

        stream_mode: True to stream via FFmpeg; False to play locally.
        stream_url: Required if stream_mode is True.
        bottom_margin: Minimum number of pixels to leave at the bottom edge.
        """
        self.stream_mode = stream_mode
        self.width = width
        self.height = height
        self.fps = fps
        self.bottom_margin = bottom_margin
        # Soft white background.
        self.bg_color = (245, 245, 245)
        # Text color is black.
        self.font_color = (0, 0, 0)
        self.x_margin = 50
        self.y_offset = 50
        self.base_font = ImageFont.truetype(REGULAR_FONT_PATH, FONT_SIZE)
        self.line_height = self.base_font.getsize("A")[1]
        self.line_margin = 10
        self.current_offset = 0

        if self.stream_mode:
            if stream_url is None:
                raise ValueError(
                    "stream_url must be provided when stream_mode is True."
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
        Reveals markdown-formatted text gradually with a typewriter effect.
        The markdown is preprocessed so that:
          - Headers (lines beginning with '#') are transformed into "HEADERn:" markers.
          - Inline **bold** and *italic* segments are rendered using the italic font.
        For header lines, the header is rendered using the bold font.
        Dynamic scroll speed is computed based on window height and chars_per_sec.
        """
        processed_text = preprocess_markdown(text)
        full_text = processed_text
        text_buffer = ""
        index = 0
        char_accumulator = 0.0
        delay = 1.0 / self.fps

        # Pre-calculate final layout (using base font for wrapping).
        final_lines = layout_text(
            full_text, self.base_font, self.width - 2 * self.x_margin
        )

        # Compute dynamic scroll speed (pixels per frame):
        dynamic_scroll_speed = (
            (chars_per_sec / average_chars_per_line)
            * (self.line_height + self.line_margin)
        ) / self.fps

        while index < len(full_text):
            char_accumulator += chars_per_sec / self.fps
            num_to_add = int(char_accumulator)
            if num_to_add > 0:
                text_buffer += full_text[index : index + num_to_add]
                index += num_to_add
                char_accumulator -= num_to_add

            # Calculate layout for the current text.
            lines = layout_text(
                text_buffer, self.base_font, self.width - 2 * self.x_margin
            )
            total_text_height = len(lines) * (self.line_height + self.line_margin)
            available_height = self.height - self.y_offset - self.bottom_margin
            target_offset = max(0, total_text_height - available_height)

            if self.current_offset < target_offset:
                self.current_offset = min(
                    self.current_offset + dynamic_scroll_speed, target_offset
                )
            elif self.current_offset > target_offset:
                self.current_offset = target_offset

            # Create a new image and draw each line.
            img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
            draw = ImageDraw.Draw(img)
            current_y = self.y_offset - self.current_offset
            for line in lines:
                # Determine which fonts to use for this line.
                reg_font, ital_font, display_line = get_fonts_for_line(
                    line, self.base_font
                )
                # Draw the line with inline markdown formatting.
                draw_markdown_text(
                    draw, self.x_margin, current_y, display_line, reg_font, ital_font
                )
                # Advance current_y by the height of the used font plus margin.
                line_h = reg_font.getsize("A")[1]
                current_y += line_h + self.line_margin
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

    def display_black_screen(self, duration=BLACK_SCREEN_DURATION):
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
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    return

    def close(self):
        if self.stream_mode:
            self.process.stdin.close()
            self.process.wait()
        else:
            cv2.destroyAllWindows()
