import time

from manager import Manager
from secret_keys import TWITCH_KEY
from video import VideoStreamer


def main():
    man = Manager("gpt-4o-mini")
    # Replace with your actual streaming URL and stream key.
    STREAM_URL = f"rtmp://live.twitch.tv/app/{TWITCH_KEY}"
    streamer = VideoStreamer(stream_url=STREAM_URL)
    try:
        while True:
            article = man.get_next_article()
            ai_text = f"{article.title}\n\n{article.content}"
            print("Displaying text:", ai_text)
            streamer.stream_text(ai_text)
            streamer.display_black_screen()
    except KeyboardInterrupt:
        print("Live stream stopped.")
    finally:
        streamer.close()


if __name__ == "__main__":
    main()
