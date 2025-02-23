from manager import Manager

man = Manager("gpt-4o-mini")

for _ in range(5):
    text = man.get_next_article()
    # print(text.content)
