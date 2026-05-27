from flask import Flask, render_template, Response, jsonify, request
from detection import generate_frames, get_states

app = Flask(__name__)

temp_value = None
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    global temp_value
    bulb1, bulb2, fan = get_states()
    try:
        temp_int = float(temp_value)
    except (TypeError, ValueError):
        temp_int = 0
    if temp_int>33 and fan:
        fan=True
    else:
        fan=False
    return jsonify({'bulb1': bulb1, 'bulb2': bulb2, "fan": fan, "temperature":  temp_value if temp_value is not None else 0})

@app.route('/sendTemp', methods=['POST'])
def temp_change():
    global temp_value
    data = request.get_json()
    if data and "temperature" in data:
        temp_value = data["temperature"]
        return f"Temperature received {temp_value}", 200
    else:
        return "Invalid data", 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
