import chess.pgn
import json
import requests
from base64 import b64encode



chess_username = "YoungLion64"


spotify_client_Id = "9e3d77fccf6844c19b9900c7c4fff376"
spotify_client_secret = "9b0b254207974b0d9c158b969becd261"

credentials = f"{spotify_client_Id}:{spotify_client_secret}"
encoded_credentials = b64encode(credentials.encode()).decode()




url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "client_credentials"
}

response = requests.post(url, headers=headers, data=data)


if response.status_code == 200:
    access_token = response.json().get("access_token")
else:
    print(f"Error: {response.status_code} - {response.text}")




game_results = {
    "date": [],
    "result": []
}
with open("lichess_YoungLion64_2024-11-26.pgn", "r") as pgn_file:
    while True:

        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break  


        date = game.headers.get("Date")
        time = game.headers.get("UTCTime")
        white_player = game.headers.get("White")
        black_player = game.headers.get("Black")
        result = game.headers.get("Result")


        if chess_username == white_player:
            if result == "1-0":
                outcome = "Win"
            elif result == "0-1":
                outcome = "Lose"
            else:
                outcome = "Draw"
        elif chess_username == black_player:
            if result == "1-0":
                outcome = "Lose"
            elif result == "0-1":
                outcome = "Win"
            else:
                outcome = "Draw"
        else:
            continue

        game_results["date"].append(date.replace(".", "-"))
        game_results["result"].append(outcome)


music_data = {
    "ts": [],
    "track": [],
    "ms_played": []
}

filenames = ["Streaming_History_Audio_2022-2023_1.json","Streaming_History_Audio_2023-2024_2.json","Streaming_History_Audio_2024_3.json"]

for filename in filenames:
    print(filename)
    with open("Spotify/"+filename, "r") as file:
        count = 0
        all_data = json.load(file)
        for data in all_data[2000:]:
            if data["ts"].split("T")[0] in game_results["date"]:
                if (data["spotify_track_uri"] == None):
                    continue
                music_data["ts"].append(data["ts"])
                music_data["track"].append(data["master_metadata_track_name"])
                music_data["ms_played"].append(data["ms_played"]/60000)
                count += 1
        print(count)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt




music_df = pd.DataFrame(music_data)
game_df = pd.DataFrame(game_results)


music_df['ts'] = pd.to_datetime(music_df['ts'])
game_df['date'] = pd.to_datetime(game_df['date'])


music_df['date_only'] = music_df['ts'].dt.date
game_df['date_only'] = game_df['date'].dt.date

df = pd.merge(music_df, game_df, left_on='date_only', right_on='date_only')



if df.empty:
    print("No matching dates between music data and game results.")
else:

    df['Hour'] = df['ts'].dt.hour


    heatmap_data = df.pivot_table(index='result', columns='Hour', values='ms_played', aggfunc='sum')


    print(heatmap_data)

    if not heatmap_data.empty:

        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data, cmap='Blues', annot=True, fmt=".2f", cbar_kws={'label': 'Music Duration (min)'})
        plt.title("Chess Results vs. Music Duration by Hour")
        plt.ylabel("Chess Result")
        plt.xlabel("Hour of Day")
        plt.show()
    else:
        print("No data available for the heatmap.")
        
    merged_df = pd.merge(music_df, game_df, left_on='ts', right_on='date', how='inner')


    result_counts = df.groupby(['ts', 'genres', 'result']).size().unstack(fill_value=0)

    # Create a bar plot
    result_counts.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.title('Game Results by Genre and Date')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Game Result')
    plt.tight_layout()
    plt.show()
    
    game_data = pd.DataFrame(game_results)
game_data["date"] = pd.to_datetime(game_data["date"]) 
game_data["result"] = game_data["result"].astype("category")  

grouped_data = game_data.groupby(["date", "result"]).size().unstack(fill_value=0)


plt.figure(figsize=(12, 6))

for result in grouped_data.columns:
    plt.plot(grouped_data.index, grouped_data[result], marker="o", label=result)

plt.title("Win/Loss/Draw Counts Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Game Count", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="Game Result", fontsize=10)
plt.grid(alpha=0.5)

plt.tight_layout()
plt.show()

        

game_data = pd.DataFrame(game_results)
game_data["date"] = pd.to_datetime(game_data["date"]) 

music_df = pd.DataFrame(music_data)
music_df["ts"] = pd.to_datetime(music_df["ts"])  
music_df["date"] = music_df["ts"].dt.date 
music_df["ms_played"] = music_df["ms_played"] 


music_aggregated = music_df.groupby("date")["ms_played"].sum().reset_index()
music_aggregated["date"] = pd.to_datetime(music_aggregated["date"])  


merged_data = pd.merge(
    game_data.groupby("date").size().reset_index(name="games_played"),
    music_aggregated,
    on="date",
    how="inner"
)


plt.figure(figsize=(12, 6))


plt.scatter(
    merged_data["games_played"],
    merged_data["ms_played"],
    c="blue",
    alpha=0.7,
    label="Music Listening vs. Games"
)


plt.title("Music Listening Time vs. Chess Games", fontsize=16)
plt.xlabel("Number of Chess Games Played", fontsize=12)
plt.ylabel("Music Listening Time (Minutes)", fontsize=12)
plt.grid(alpha=0.5)
plt.legend(fontsize=10)


plt.tight_layout()
plt.show()

    
music_df = pd.DataFrame(music_data)
music_df["ms_played"] = music_df["ms_played"]  


plt.figure(figsize=(12, 6))
plt.hist(
    music_df["ms_played"],
    bins=20,  
    color="skyblue",
    edgecolor="black",
    alpha=0.7
)


plt.title("Track Playtime Distribution", fontsize=16)
plt.xlabel("Track Playtime (Minutes)", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(axis="y", alpha=0.5)


plt.tight_layout()
plt.show()

game_data = pd.DataFrame(game_results)
game_data["date"] = pd.to_datetime(game_data["date"]) 
game_data["month"] = game_data["date"].dt.to_period('M')  

game_data["win"] = game_data["result"].apply(lambda x: 1 if x == "Win" else 0)
win_rate_per_month = game_data.groupby("month")["win"].mean()


music_df = pd.DataFrame(music_data)
music_df["ts"] = pd.to_datetime(music_df["ts"])
music_df["date"] = music_df["ts"].dt.date
music_df["month"] = music_df["ts"].dt.to_period('M') 


music_time_per_month = music_df.groupby("month")["ms_played"].sum()


monthly_data = pd.DataFrame({
    "win_rate": win_rate_per_month,
    "music_time": music_time_per_month
}).dropna() 


fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.set_xlabel("Month")
ax1.set_ylabel("Total Music Listening Time (Minutes)", color="blue")
ax1.plot(monthly_data.index.astype(str), monthly_data["music_time"], color="blue", label="Total Music Time", marker="o")
ax1.tick_params(axis="y", labelcolor="blue")


ax2 = ax1.twinx()
ax2.set_ylabel("Win Rate", color="green")
ax2.plot(monthly_data.index.astype(str), monthly_data["win_rate"], color="green", label="Win Rate", marker="s")
ax2.tick_params(axis="y", labelcolor="green")

plt.title("Music Listening Time and Win Rate by Month", fontsize=16)
ax1.grid(True)


plt.tight_layout()
plt.show()