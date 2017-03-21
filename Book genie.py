import pandas as pd
import json
import os
from collections import defaultdict
from nltk.corpus import wordnet

topic = 'night'  # books on this topic will be searched


def readFile():
    """Reads our excel file, removes duplicates and empty numbers. Returns a dataframe"""

    df = pd.ExcelFile(os.path.join(
        os.path.dirname(__file__), 'data', 'Book data.xlsx')).parse(0)
    df = df[np.isfinite(df['Author number'])].drop_duplicates()
    print('File read!\n')
    return df


def makeDictionary(df):
    """Reads dataframe and makes 2 dictionaries of tags"""

    print('Making database..\n')

    uselessTags = ['not yet released', 'to be released', 'wishlist',
                   'to read', 'to buy', 'currently reading', 'pdf', 'owned books', 'owned', 'books', 'ebook', 'ebooks', 'own', 'i own']
    allTags = defaultdict(int)  # stores tag: sum of tag in all books
    booksWithTag = defaultdict(int)  # stores tag:[books containing that tag]
    tagLimit = 5  # minimum value of tag required (to filter out random tags)
    # minimum value of sum of all the tags of a book (shows popularity)

    for book in range(len(df['Book tags'])):
        """Makes dictionary of allTags and booksWithTag"""

        bookTags = json.loads(df['Book tags'][book])
        impTags = [t for t in bookTags if bookTags[
            t] > tagLimit if t not in uselessTags]
        for tag in impTags:
            allTags[tag] += bookTags[tag]
            booksWithTag.setdefault(tag, []).append(bookTags[tag])

    return allTags, booksWithTag


def getSynonyms(topic):
    """Returns synonyms using wordnet"""

    synonyms = [topic]
    for syn in wordnet.synsets(topic):
        for synonym in syn.lemmas():
            if synonym.name() not in synonyms:
                synonyms.append(synonym.name())
    print('Synonyms are:', synonyms)
    return synonyms


def getBooks(topic, tagTotalLimit=500):
    """Main function to find the book on any topic from database"""

    df = readFile()
    allTags, booksWithTag = makeDictionary(df)

    print('Searching book on:', topic)

    synonyms = getSynonyms(topic)

    synonyms = [w for w in synonyms if w in booksWithTag]
    print('\nShowing books for words:', synonyms)
    books = defaultdict(int)
    # for every word in synonym
    for word in synonyms:
        # for every book related to word
        for book in booksWithTag[word]:
            # to avoid printing books common in synonym tags
            if df['Book title'][book] not in books:
                # to avoid printing books with less tag(hence less famous)
                if df['Tag count'][book] > tagTotalLimit:
                    books[df['Book title'][book]] = df['Tag count'][book]

    i = 0
    for book in sorted(books, key=books.get, reverse=True):
        i += 1
        bookTitle = book.replace('#', '').replace('.', '').title()
        bookURL = df['Book gURL'][np.where(df['Book title'] == book)[0][0]]

        print(i, '.', bookTitle, '\nURL-', bookURL, '\n')


if __name__ == '__main__':
    getBooks(topic, tagTotalLimit=500)
