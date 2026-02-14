from flask import Flask, request, jsonify
import hashlib
import time
import collections

app = Flask(__name__)

# FIXED: These are now normal dictionaries, not functions
exact_cache = collections.OrderedDict()
stats = {'total': 0, 'hits': 0}
MAX_CACHE = 1000
TTL = 3600  # 1 hour

def normalize(text):
    return ' '.join(text.lower().replace(',', '').replace('.', '').split())

def get_hash(text):
    return hashlib.md5(normalize(text).encode()).hexdigest()

def is_alive(entry):
    return time.time() - entry['time'] < TTL

@app.route('/', methods=['POST'])
def chat():
    data = request.get_json()  # FIXED: Proper JSON parsing
    question = data['query']
    
    key = get_hash(question)
    
    # Check cache first
    if key in exact_cache and is_alive(exact_cache[key]):
        exact_cache.move_to_end(key)
        stats['hits'] += 1
        return jsonify({
            'answer': exact_cache[key]['answer'],
            'cached': True,
            'latency': 20,
            'cacheKey': key[:8]
        })
    
    # Cache MISS - fake AI response
    answer = f"🤖 Answer to: {question}"
    
    # Save to cache
    entry = {
        'answer': answer,
        'time': time.time()
    }
    exact_cache[key] = entry
    
    # LRU eviction
    if len(exact_cache) > MAX_CACHE:
        exact_cache.popitem(last=False)
    
    stats['total'] += 1
    
    return jsonify({
        'answer': answer,
        'cached': False,
        'latency': 500,
        'cacheKey': key[:8]
    })

@app.route('/analytics', methods=['GET'])
def stats_page():
    hit_rate = stats['hits'] / max(stats['total'], 1)
    return jsonify({
        'hitRate': round(hit_rate, 3),
        'totalRequests': stats['total'],
        'cacheHits': stats['hits'],
        'cacheMisses': stats['total'] - stats['hits'],
        'cacheSize': len(exact_cache),
        'costSavings': round(hit_rate * 2.5, 2),
        'savingsPercent': round(hit_rate * 100),
        'strategies': ['exact match', 'LRU eviction', 'TTL expiration']
    })

if __name__ == '__main__':
    print("🚀 AI Cache Server Starting (FIXED VERSION)...")
    print("📱 Test: Invoke-RestMethod -Uri 'http://localhost:5000' -Method POST -ContentType 'application/json' -Body '{\"query\":\"hello\"}'")
    app.run(debug=True, port=5000)




