import base64
import os
import json
import time
from moviepy.editor import VideoFileClip
import moviepy.editor as mp

from clip_video import *
from ddb_llm import *

video_directory = f"{DIRECTORY}/resources/videos/"
clips_directory = f"{DIRECTORY}/resources/clips/"
llm_scenes_directory = f"{DIRECTORY}/resources/llm_scenes/"
transcripts_directory = f"{DIRECTORY}/resources/transcripts/"


def generate_clips(video_id, user_input, max_clips=3):
    template = "Given the transcript of the video, generate clips with " + user_input + """. Give me 3 best scenes in a single json output with keys start_time, end_time, short_description, scene_description. Each scene should be atleast 15 seconds long strictly. The scene_description should describe the full scene. % START OF TRANSCRIPT {transcript} %END OF TRANSCRIPT"""

    print(template)
    prompt = PromptTemplate(
        input_variables=["transcript"],
        template=template,
    )


    ts = int(time.time())
    video_file = f"{video_directory}{video_id}.mp4"
    json_file = f"{llm_scenes_directory}{video_id}_scene_{ts}.json"
    output_json_file = f"{clips_directory}{video_id}_scene_clips_{ts}.json"

    transcript_file = f"{transcripts_directory}{video_id}_transcript.txt"
    transcript_dict = video_transcript_input(transcript_file, video_id)

    scene_list = get_scenes_from_llm(transcript_dict, prompt)

    sorted_scenes = sorted(scene_list, key=lambda x: x['end_time'] - x['start_time'], reverse=True)

    # max_clips = min(max_clips, len(scene_list))
    final_scenes = sorted_scenes[:max_clips]

    with open(json_file, 'w') as f:
        json.dump(final_scenes, f, indent=2)

    json_data = ""
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    clips_data = create_clips(json_data, video_file, video_id, clips_directory)

    with open(output_json_file, 'w') as f:
        json.dump(clips_data, f, indent=2)

    return clips_data


if __name__ == "__main__":
    start_time = time.time()

    # Call the method
    generate_clips("Tm7DcVtwrQE", "clips contain joey and bird")
    # Record the end time
    end_time = time.time()
    # Compute the elapsed time
    elapsed_time = end_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")

