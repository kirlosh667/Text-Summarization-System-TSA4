import re
import string
from collections import Counter

# Standard list of English stopwords for robust extractive NLP summarization
DEFAULT_STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot',
    'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few',
    'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll",
    "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll",
    "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 'let', "let's", 'me', 'more',
    'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought',
    'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should',
    "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves',
    'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through',
    'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were',
    "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom',
    'why', "why's", 'with', "won't", 'would', "wouldn me", 'you', "you'd", "you'll", "you're", "you've", 'your',
    'yours', 'yourself', 'yourselves', 'also', 'said', 'one', 'two', 'us', 'may', 'many', 'also', 'however', 'thus'
}

def tokenize_sentences(text):
    """Splits text into sentences using regular expressions."""
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    if not cleaned_text:
        return []
    
    # Split by sentence boundaries (. ! ?) followed by whitespace or end
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    return [s.strip() for s in sentences if s.strip()]

def calculate_word_frequencies(sentences):
    """Calculates normalized term frequency for non-stop words."""
    word_counts = Counter()
    
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z0-9\'-]+\b', sentence.lower())
        for word in words:
            word = word.strip("'-")
            if word and word not in DEFAULT_STOPWORDS and len(word) > 1 and not word.isdigit():
                word_counts[word] += 1
                
    if not word_counts:
        return {}, {}
        
    max_freq = max(word_counts.values())
    word_freq = {word: freq / max_freq for word, freq in word_counts.items()}
    
    return word_freq, dict(word_counts.most_common(8))

def score_sentences(sentences, word_freq):
    """Scores sentences based on sum of word frequency scores."""
    sentence_scores = []
    
    for idx, sentence in enumerate(sentences):
        words = re.findall(r'\b[a-zA-Z0-9\'-]+\b', sentence.lower())
        word_count = len(words)
        
        if word_count == 0:
            sentence_scores.append({'index': idx, 'sentence': sentence, 'score': 0.0, 'word_count': 0, 'matched_keywords': []})
            continue
            
        raw_score = 0.0
        matched_words = []
        for word in words:
            word = word.strip("'-")
            if word in word_freq:
                raw_score += word_freq[word]
                matched_words.append(word)
                
        # Length normalization factor so long sentences don't dominate unfairly
        score = raw_score / (word_count ** 0.5) if word_count > 0 else 0
        
        sentence_scores.append({
            'index': idx,
            'sentence': sentence,
            'score': round(score, 4),
            'word_count': word_count,
            'matched_keywords': list(set(matched_words))
        })
        
    return sentence_scores

def summarize(text, compression_percent=30, num_sentences=None):
    """
    Extractive text summarizer based on word frequency and sentence scoring.
    """
    if not text or not text.strip():
        return {
            'success': False,
            'error': 'Please enter or paste some text into the box to summarize.'
        }
        
    sentences = tokenize_sentences(text)
    total_sentences = len(sentences)
    
    if total_sentences == 0:
        return {
            'success': False,
            'error': 'No valid sentences detected in the provided text.'
        }
        
    original_word_count = len(re.findall(r'\b\w+\b', text))
    
    if original_word_count < 15:
        return {
            'success': False,
            'error': f'Text is too short to generate a meaningful summary ({original_word_count} words). Please provide at least 15-20 words.'
        }
        
    word_freq, top_keywords = calculate_word_frequencies(sentences)
    
    if not word_freq:
        # Fallback if text consists only of stopwords or single letters
        selected_count = max(1, int(total_sentences * (compression_percent / 100.0)))
        selected_sentences = sentences[:selected_count]
        summary_text = ' '.join(selected_sentences)
        summary_word_count = len(re.findall(r'\b\w+\b', summary_text))
        return {
            'success': True,
            'summary': summary_text,
            'original_text': text,
            'sentences': sentences,
            'original_sentence_count': total_sentences,
            'summary_sentence_count': len(selected_sentences),
            'original_word_count': original_word_count,
            'summary_word_count': summary_word_count,
            'compression_ratio': round((1 - (summary_word_count / original_word_count)) * 100, 1),
            'retained_ratio': round((summary_word_count / original_word_count) * 100, 1),
            'top_keywords': {},
            'sentence_scores': [{'index': i, 'sentence': s, 'score': 1.0, 'word_count': len(s.split()), 'matched_keywords': []} for i, s in enumerate(sentences)],
            'selected_indices': list(range(selected_count))
        }

    sentence_scores = score_sentences(sentences, word_freq)
    
    if num_sentences is not None and num_sentences > 0:
        target_count = min(num_sentences, total_sentences)
    else:
        target_count = max(1, round(total_sentences * (compression_percent / 100.0)))
        
    target_count = max(1, min(target_count, total_sentences))
    
    # Sort by score descending to get top target_count sentences
    sorted_sentences = sorted(sentence_scores, key=lambda x: x['score'], reverse=True)
    top_sentences = sorted_sentences[:target_count]
    
    # Re-sort by original index order
    selected_in_order = sorted(top_sentences, key=lambda x: x['index'])
    
    summary_sentences = [item['sentence'] for item in selected_in_order]
    summary_text = ' '.join(summary_sentences)
    
    summary_word_count = len(re.findall(r'\b\w+\b', summary_text))
    reduction_percentage = round((1 - (summary_word_count / original_word_count)) * 100, 1) if original_word_count > 0 else 0
    if reduction_percentage < 0:
        reduction_percentage = 0.0
        
    selected_indices = [item['index'] for item in selected_in_order]
    
    return {
        'success': True,
        'summary': summary_text,
        'original_text': text,
        'sentences': sentences,
        'original_sentence_count': total_sentences,
        'summary_sentence_count': len(summary_sentences),
        'original_word_count': original_word_count,
        'summary_word_count': summary_word_count,
        'compression_ratio': reduction_percentage,
        'retained_ratio': round((summary_word_count / original_word_count) * 100, 1) if original_word_count > 0 else 100.0,
        'top_keywords': top_keywords,
        'sentence_scores': sentence_scores,
        'selected_indices': selected_indices
    }
