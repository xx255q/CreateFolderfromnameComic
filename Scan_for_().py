import os
import re

def main():
    comics_folder = r"\\TOWER\Manga\Comics"
    unique_words = set()

    for root, dirs, files in os.walk(comics_folder):
        for file in files:
            print(f"Scanning: {file}")
            words_in_parentheses = re.findall(r'\((.*?)\)', file)
            for word in words_in_parentheses:
                unique_words.add(f'({word})')

    with open("unique_words_in_parentheses.txt", "w") as output_file:
        for word in sorted(unique_words):
            output_file.write(f"{word}\n")

    print("Unique words in parentheses have been saved to unique_words_in_parentheses.txt")

if __name__ == "__main__":
    main()
