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
        # Use a soft white background.
        self.bg_color = (245, 245, 245)
        # Text color is black.
        self.font_color = (0, 0, 0)
        self.x_margin = 50
        self.y_offset = 50
        self.base_font = ImageFont.truetype(REGULAR_FONT_PATH, FONT_SIZE)
        self.line_height = self.base_font.getsize("A")[1]
        self.line_margin = 10
        self.current_offset = 0

        # We'll maintain an accumulated text string across prompts.
        self.accumulated_text = ""

        if self.stream_mode:
            if stream_url is None:
                raise ValueError(
                    "stream_url must be provided when stream_mode is True."
                )
            self.process = self._start_ffmpeg(stream_url)
        else:
            self.process = None
            cv2.namedWindow("Live Stream", cv2.WINDOW_NORMAL)
            # Optionally set fullscreen here if desired:
            # cv2.setWindowProperty("Live Stream", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

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

    def append_text(self, new_text, chars_per_sec=50):
        """
        Appends new markdown-formatted text to the accumulated text and animates
        the revealing of the new portion. The previous text remains on screen.

        To optimize performance as the text grows, we clip the accumulated text to
        a maximum length (CLIP_THRESHOLD). This way, only a limited amount of text
        is re-laid out each frame.

        The reveal speed is time-based so that the new characters appear at a constant rate.
        """
        CLIP_THRESHOLD = (
            3000  # maximum number of characters to retain in the accumulated text
        )

        # Process the new markdown text.
        processed_new_text = preprocess_markdown(new_text)
        prev_length = len(self.accumulated_text)
        # Append a newline if there is already text.
        if self.accumulated_text:
            self.accumulated_text += "\n" + processed_new_text
        else:
            self.accumulated_text = processed_new_text
        new_total = len(self.accumulated_text)

        # If the accumulated text is too long, clip it.
        if new_total > CLIP_THRESHOLD:
            # Keep only the last CLIP_THRESHOLD characters.
            self.accumulated_text = self.accumulated_text[-CLIP_THRESHOLD:]
            # Adjust prev_length accordingly.
            prev_length = max(0, prev_length - (new_total - CLIP_THRESHOLD))
            new_total = len(self.accumulated_text)

        # Animate revealing only the new portion.
        start_time = time.time()
        delay = 1.0 / self.fps

        while True:
            elapsed = time.time() - start_time
            # Calculate how many characters into the new portion we should be.
            target_index = prev_length + min(
                new_total - prev_length, int(chars_per_sec * elapsed)
            )
            text_buffer = self.accumulated_text[:target_index]

            # Compute layout only on the (clipped) accumulated text.
            lines = layout_text(
                text_buffer, self.base_font, self.width - 2 * self.x_margin
            )
            total_text_height = len(lines) * (self.line_height + self.line_margin)
            available_height = self.height - self.y_offset - self.bottom_margin
            target_offset = max(0, total_text_height - available_height)
            # For simplicity, we directly set the scroll offset.
            self.current_offset = target_offset

            # Create an image and render the visible portion of the layout.
            img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
            draw = ImageDraw.Draw(img)
            current_y = self.y_offset - self.current_offset
            for line in lines:
                reg_font, ital_font, display_line = get_fonts_for_line(
                    line, self.base_font
                )
                draw_markdown_text(
                    draw, self.x_margin, current_y, display_line, reg_font, ital_font
                )
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
            if target_index >= new_total:
                break
        # After finishing, leave the final frame on screen.

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
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    return

    def close(self):
        """
        Closes resources: the FFmpeg process or the OpenCV window.
        """
        if self.stream_mode:
            self.process.stdin.close()
            self.process.wait()
        else:
            cv2.destroyAllWindows()
