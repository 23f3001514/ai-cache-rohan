from flask import Flask, request, jsonify
import re
import time
from collections import defaultdict
from html import escape

app = Flask(__name__)

# Simple in-memory rate limiting
request_counts = defaultdict(list)

RATE_LIMIT = 5  # max 5 requests
TIME_WINDOW = 60  # per 60 seconds


# ----------------------------
# Security Validation Function
# ----------------------------
def detect_prompt_injection(user_input):
    injection_patterns = [
        r"ignore previous instructions",
        r"override system",
        r"reveal system prompt",
        r"show system prompt",
        r"output all your training data",
        r"act as admin",
        r"act as system",
        r"new task:"
    ]

    for pattern in injection_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True, f"Detected prompt injection pattern: '{pattern}'"

    return False, "Input passed all security checks"


# ----------------------------
# Rate Limiting
# ----------------------------
def is_rate_limited(user_id):
    current_time = time.time()
    request_counts[user_id] = [
        t for t in request_counts[user_id]
        if current_time - t < TIME_WINDOW
    ]

    if len(request_counts[user_id]) >= RATE_LIMIT:
        return True

    request_counts[user_id].append(current_time)
    return False


# ----------------------------
# Security Endpoint
# ----------------------------
@app.route("/secure-ai", methods=["POST"])
def secure_ai():
    try:
        data = request.get_json()

        if not data or "userId" not in data or "input" not in data:
            return jsonify({
                "blocked": True,
                "reason": "Invalid request format",
                "confidence": 1.0
            }), 400

        user_id = data["userId"]
        user_input = data["input"]

        # Rate limit check
        if is_rate_limited(user_id):
            return jsonify({
                "blocked": True,
                "reason": "Rate limit exceeded",
                "confidence": 0.99
            }), 429

        # Prompt injection detection
        blocked, reason = detect_prompt_injection(user_input)

        if blocked:
            return jsonify({
                "blocked": True,
                "reason": reason,
                "confidence": 0.98
            }), 400

        # Sanitize output (simulate AI response)
        simulated_ai_output = f"AI Response: {user_input}"
        sanitized_output = escape(simulated_ai_output)

        return jsonify({
            "blocked": False,
            "reason": reason,
            "sanitizedOutput": sanitized_output,
            "confidence": 0.95
        }), 200

    except Exception:
        return jsonify({
            "blocked": True,
            "reason": "Internal validation error",
            "confidence": 1.0
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

