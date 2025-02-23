import cv2
from manager import Manager
from secret_keys import TWITCH_KEY
from video import VideoStreamer


def main():
    man = Manager("gpt-4o-mini", upload_online=True)
    VIDEO_MODE = True
    if not VIDEO_MODE:
        NUM_ITRS = 30
        for _ in range(NUM_ITRS):
            man.get_next_article()
    else:
        STREAM_MODE = False
        # Replace with your actual streaming URL and stream key.
        STREAM_URL = f"rtmp://live.twitch.tv/app/{TWITCH_KEY}"
        if STREAM_MODE:
            streamer = VideoStreamer(
                width=480, height=360, fps=30, stream_mode=True, stream_url=STREAM_URL
            )
        else:
            # cv2.namedWindow("Live Stream", cv2.WINDOW_NORMAL)
            streamer = VideoStreamer(width=1920, height=1080, fps=60, stream_mode=False)
        try:
            while True:
                article = man.get_next_article()
                ai_text = f"{article.title}\n\n{article.content}"
                print("Displaying text:", ai_text)
                streamer.stream_text(ai_text, typing_delay=0.0005)
                streamer.display_black_screen()
        except KeyboardInterrupt:
            print("Live stream stopped.")
        finally:
            streamer.close()


if __name__ == "__main__":
    main()
