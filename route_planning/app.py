from flask import Flask, request, jsonify
import random
import requests
import json

app = Flask(__name__)

def get_real_distance_google(lat1, lon1, lat2, lon2, api_key):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    params = {
        "origin": f"{lat1},{lon1}",
        "destination": f"{lat2},{lon2}",
        "mode": "walking",
        "language": "zh-TW",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        # 距離（公尺）
        distance_meters = data["routes"][0]["legs"][0]["distance"]["value"]
        # 預估時間（分鐘）
        duration_text = data["routes"][0]["legs"][0]["duration"]["text"]
        return distance_meters, duration_text 
    else:
        raise Exception(f"Google API Error: {data['status']}")


@app.route('/route', methods=['POST'])
def route():
    data = request.get_json()
    start_lat = data.get("lat")
    start_lon = data.get("lon")
    api_key = "AIzaSyDKXAM7plFCNKpyPx6IJTwL-2tWOTnWXXA"
    print(f"Received location: {start_lat}, {start_lon}")

    selected_spots = random.sample(spots_data, 2)
    route_names = ["目前位置"] + [spot["name"] for spot in selected_spots]
    route_coords = [(start_lat, start_lon)] + [(spot["lat"], spot["lon"]) for spot in selected_spots]

    total_distance = 0
    total_duration = 0
    segment_info = []

    for i in range(2):
        d, dur = get_real_distance_google(route_coords[i][0], route_coords[i][1],
                                          route_coords[i+1][0], route_coords[i+1][1],
                                          api_key)
        segment_info.append((d, dur))
        total_distance += d
        total_duration += int(dur.split(" ")[0])

    difficulty = classify_difficulty(total_distance)

    result = f"從「{route_names[0]}」到「{route_names[1]}」到「{route_names[2]}」\n"
    result += "【Google 路線】\n"
    result += f"- 第一段：約 {segment_info[0][0]} 公尺，預計時間：{segment_info[0][1]}\n"
    result += f"- 第二段：約 {segment_info[1][0]} 公尺，預計時間：{segment_info[1][1]}\n"
    result += f"- 總距離：約 {total_distance} 公尺\n"
    result += f"- 預計時間：{total_duration} 分鐘\n"
    result += f"- 任務難度：{difficulty}"

    print(f"Generated route: {result}")

    return jsonify({"mission": result})

@app.route("/", methods=["GET"])
def home():    
    return "<h1>後端伺服器正在運行</h1>"


def classify_difficulty(distance):
    if distance < 400:
        return "🟢 簡單"
    elif distance < 700:
        return "🟡 中等"
    else:
        return "🔴 困難"

# def generate_route(api_key=None):
#     selected_spots = random.sample(spots_data, 3)
#     route_names = [spot["name"] for spot in selected_spots]
#     route_coords = [(spot["lat"], spot["lon"]) for spot in selected_spots]

#     total_distance_google = 0
#     total_duration_google = 0
#     segment_distances_google = []
#     segment_durations_google = []

#     for i in range(len(route_coords) - 1):
#         lat1, lon1 = route_coords[i]
#         lat2, lon2 = route_coords[i+1]

#         # 真實道路距離和預估時間（使用 Google API）
#         if api_key:
#             d_google, duration_google = get_real_distance_google(lat1, lon1, lat2, lon2, api_key)
#             segment_distances_google.append(round(d_google, 1))
#             segment_durations_google.append(duration_google)
#             total_distance_google += d_google
#             total_duration_google += int(duration_google.split(" ")[0])  # 取得分鐘數
#         else:
#             segment_distances_google.append("無API")
#             segment_durations_google.append("無API")

#     difficulty_google = classify_difficulty(total_distance_google) if total_distance_google else "無資料"

#     # 建立比較說明
#     mission = f"從「{route_names[0]}」到「{route_names[1]}」到「{route_names[2]}」\n\n"

#     if total_distance_google > 0:
#         mission += "【Google實際道路距離】\n"
#         mission += f"- 第一段：{segment_distances_google[0]} 公尺, 預計時間：{segment_durations_google[0]}\n"
#         mission += f"- 第二段：{segment_distances_google[1]} 公尺, 預計時間：{segment_durations_google[1]}\n"
#         mission += f"- 總距離：約 {round(total_distance_google, 1)} 公尺\n"
#         mission += f"- 預計時間：{total_duration_google} 分鐘\n"
#         mission += f"- 任務難度：{difficulty_google}\n"
#     else:
#         mission += "【Google實際道路距離】\n- 無API Key，無法取得實際距離與時間\n"

#     return mission

with open("spots.json", "r", encoding="utf-8") as f: # 抓景點(spots.json)
    spots_data = json.load(f)
# 轉成純文字描述
spot_descriptions = "\n".join(
    [f"{i+1}. {spot['name']}（{spot['lat']}, {spot['lon']}）: {spot['description']}"
     for i, spot in enumerate(spots_data)]
)

if __name__ == "__main__":
      if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5000, debug=True)
