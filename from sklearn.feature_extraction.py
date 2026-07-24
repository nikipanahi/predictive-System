from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "Machine learning is fascinating.",
    "I love learning new things.",
    "Machine learning algorithms are powerful."
]

# Initialize the vectorizer
vectorizer = TfidfVectorizer()

# Fit the model and transform the documents into a matrix
tfidf_matrix = vectorizer.fit_transform(documents)

# Get the list of words (features)
print(vectorizer.get_feature_names_out())

# View the TF-IDF scores
print(tfidf_matrix.toarray())
