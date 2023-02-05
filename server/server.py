from final import RESOURCE_DIR as RES
from flask import Flask, render_template


app = Flask(__name__)


@app.route('/index')
def index():
    return render_template('index.html', res=RES)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
