from flask import Flask, render_template
app = Flask(__name__)

# Global variable to hold the latest sensor value
latest_gas_level = 0.0

@app.route('/')
def index():
    return f"<h1>Current Gas Level: {latest_gas_level} ppm</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
