from flask import Flask, request, jsonify, render_template
import json
import re
import os

app = Flask(__name__)

def clean_json(content):
    content = re.sub(r',\s*(?=})', '', content)
    content = re.sub(r',\s*(?=])', '', content)
    return content

def reverse_and_scale_waypoints(data, scale_mode, reverse=True):
    scale_factors = {0: 1.0, 1: 1.5, 2: 2.0}
    scale_factor = scale_factors.get(scale_mode, 1.0)
    
    suffix_parts = []
    if reverse:
        suffix_parts.append('R')
    if scale_mode != 0:
        suffix_parts.append(f'S{int(scale_factor * 100)}')
    
    if "routeName" in data and suffix_parts:
        base_name = data["routeName"].rsplit('_', 1)[0] if '_' in data["routeName"] else data["routeName"]
        data["routeName"] = f"{base_name}_{'_'.join(suffix_parts)}"
    
    if "waypoints" in data and isinstance(data["waypoints"], list):
        waypoints = data["waypoints"][::-1] if reverse else data["waypoints"].copy()
        
        if scale_mode != 0:
            for wp in waypoints:
                if "scale3D" in wp and "y" in wp["scale3D"]:
                    wp["scale3D"]["y"] *= scale_factor
        data["waypoints"] = waypoints
        return data
    else:
        return {"error": "Invalid data. No waypoints found."}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        json_data = request.form.get('json_data')
        scale_mode = int(request.form.get('scale_mode'))
        reverse = request.form.get('reverse', 'true').lower() == 'true'
        data = json.loads(clean_json(json_data))
        result = reverse_and_scale_waypoints(data, scale_mode, reverse)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))