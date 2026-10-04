from flask import Flask, render_template, request, jsonify
from summarizer import summarize

app = Flask(__name__)

# Sample texts for demonstration in college NLP lab
SAMPLE_TEXTS = {
    "ai_nlp": {
        "title": "Artificial Intelligence & NLP",
        "text": "Natural Language Processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language. In particular, NLP focuses on programming computers to process and analyze large amounts of natural language data. The goal is a computer capable of understanding the contents of documents, including the contextual nuances of the language within them. The technology can then accurately extract information and insights contained in the documents as well as categorize and organize the documents themselves. Modern NLP techniques leverage machine learning algorithms, statistical modeling, and deep neural networks to achieve high precision in tasks like machine translation, sentiment analysis, named entity recognition, and automatic text summarization. Extractive summarization algorithms analyze word frequency patterns and sentence similarity scores to extract key sentences directly from the source material without altering original phrasing."
    },
    "quantum": {
        "title": "Quantum Computing Frontiers",
        "text": "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve problems too complex for classical computers. Classical computers encode information into binary bits that exist as either 0s or 1s. In contrast, quantum computers leverage qubits, which can exist in superpositions of both states simultaneously. This fundamental property allows quantum processors to execute complex calculations at speeds unprecedented in human history. Entanglement is another core principle of quantum physics where qubits become interconnected, allowing instantaneous correlation regardless of distance. Scientists across academia and tech industries are applying quantum algorithms to drug discovery, cryptography, climate modeling, and financial risk evaluation. Despite these impressive theoretical advantages, building fault-tolerant quantum hardware remains a major challenge due to quantum decoherence and environmental noise."
    },
    "renewable": {
        "title": "Renewable Energy Transition",
        "text": "The global transition toward renewable energy sources is accelerating as nations strive to reduce carbon emissions and combat climate change. Solar and wind power have seen massive adoption due to plummeting installation costs and rapid technological advancements in efficiency. Energy storage systems, particularly lithium-ion and solid-state batteries, play a crucial role in stabilizing power grids by storing excess energy generated during peak output periods. Geothermal and hydroelectric energy provide dependable baseline power independent of weather variations. Moving away from fossil fuels requires significant capital investment in smart grid infrastructure, localized microgrids, and long-distance transmission lines. Policy incentives and international climate agreements continue to motivate governments to subsidize green energy initiatives. Ultimately, achieving a sustainable energy future depends on combining multiple renewable technologies with energy conservation and grid modernization."
    }
}

@app.route('/')
def index():
    return render_template('index.html', samples=SAMPLE_TEXTS)

@app.route('/api/summarize', methods=['POST'])
def handle_summarize():
    try:
        data = request.get_json() or {}
        text = data.get('text', '')
        compression = data.get('compression', 30)
        try:
            compression = int(compression)
        except (ValueError, TypeError):
            compression = 30
            
        num_sentences = data.get('num_sentences', None)
        if num_sentences is not None and str(num_sentences).isdigit() and int(num_sentences) > 0:
            num_sentences = int(num_sentences)
        else:
            num_sentences = None
            
        result = summarize(text, compression_percent=compression, num_sentences=num_sentences)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"An error occurred during summarization: {str(e)}"
        }), 500

@app.route('/api/samples/<sample_id>', methods=['GET'])
def get_sample(sample_id):
    sample = SAMPLE_TEXTS.get(sample_id)
    if sample:
        return jsonify({'success': True, 'data': sample})
    return jsonify({'success': False, 'error': 'Sample not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5003)

