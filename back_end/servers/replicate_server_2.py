from flask import Flask, send_file, abort, jsonify, request
import os

app = Flask(__name__)


@app.route('/video/<filename>')
def stream_video(filename):
    path = os.path.join('../videos2', filename)

    if os.path.exists(path):
        return send_file(path, as_attachment=False)
    else:
        return jsonify({"error": "Video not found"}), 404


@app.route('/cache_video/<filename>', methods=['POST'])
def cache_video(filename):
    path = os.path.join('./videos2', filename)
    with open(path, 'wb') as f:
        f.write(request.files['file'].read)
    return jsonify({"message": "Video cached successfully"}), 200


if __name__ == "main":
    app.run(host='0.0.0.0', port=9003)
