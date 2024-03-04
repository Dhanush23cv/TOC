import tkinter as tk
from tkinter import filedialog, messagebox
import re
import urllib.request
from collections import defaultdict
import string

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_end_of_word = False

def insert_word(root, word):
    node = root
    for char in word:
        node = node.children[char]
    node.is_end_of_word = True

def build_trie(wordlist):
    root = TrieNode()
    for word in wordlist:
        insert_word(root, word)
    return root

def get_wordlist(url):
    try:
        response = urllib.request.urlopen(url)
        if response.getcode() == 200:
            data = response.read().decode('utf-8')
            wordlist = data.split('\n')
        else:
            print("Failed to fetch wordlist:", response.getcode())
            wordlist = []
    except Exception as e:
        print("Error:", e)
        wordlist = []
    return wordlist

def create_bigram(word):
    return [word[i] + word[i+1] for i in range(len(word)-1)]

def levenshtein_distance(word1, word2):
    if len(word1) < len(word2):
        return levenshtein_distance(word2, word1)

    if len(word2) == 0:
        return len(word1)

    previous_row = range(len(word2) + 1)
    for i, char1 in enumerate(word1):
        current_row = [i + 1]
        for j, char2 in enumerate(word2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (char1 != char2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def find_similar_words(root, word):
    similar_words = set()

    def dfs(node, path):
        if node.is_end_of_word:
            similar_words.add(''.join(path))
        for char, child_node in node.children.items():
            dfs(child_node, path + [char])

    for i in range(len(word) + 1):
        path = []
        dfs(root, path)

    return similar_words

def correct_word(word, wordlist):
    corrected_word = word
    min_distance = float('inf')

    for correct_word in wordlist:
        distance = levenshtein_distance(word, correct_word)
        if distance < min_distance:
            corrected_word = correct_word
            min_distance = distance

    return corrected_word

def correct_sentence(sentence, wordlist):
    words = re.findall(r'\b\w+\b', sentence)
    corrected_sentence = []

    root = build_trie(wordlist)

    for word in words:
        if word.lower() not in wordlist:
            similar_words = find_similar_words(root, word.lower())
            if similar_words:
                corrected_word = correct_word(word, similar_words)
            else:
                corrected_word = word
        else:
            corrected_word = word
        corrected_sentence.append(corrected_word)

    return ' '.join(corrected_sentence)

def process_document(file_path, wordlist):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            corrected_content = correct_sentence(content, wordlist)
            with open('corrected_document.txt', 'w') as corrected_file:
                corrected_file.write(corrected_content)
            messagebox.showinfo("Success", "Document has been corrected and saved as 'corrected_document.txt'")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def upload_document():
    file_path = filedialog.askopenfilename()
    if file_path:
        process_document(file_path, wordlist)

# Fetch wordlist
url = "https://www.mit.edu/~ecprice/wordlist.10000"
wordlist = set(get_wordlist(url))

# Preprocess wordlist to lowercase and remove punctuation
wordlist = {word.translate(str.maketrans('', '', string.punctuation)).lower() for word in wordlist}

# Create UI
root = tk.Tk()
root.title("Text Correction")

# Add a button to upload a document
upload_button = tk.Button(root, text="Upload Document", command=upload_document)
upload_button.pack(pady=20)

root.mainloop()
