import base64
import os
import json

from moviepy.editor import VideoFileClip
import moviepy.editor as mp


def list_files_in_directory(directory):
    try:
        # Get a list of all files in the directory
        files = os.listdir(directory)
        return files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def generate_video_id():
    chars_to_replace = {'/': 'a', '+': 'a', '=': '', '-': 'a'}
    random_bytes = os.urandom(8)
    base64_hash = base64.b64encode(random_bytes).decode('utf-8')
    for char, replacement in chars_to_replace.items():
        base64_hash = base64_hash.replace(char, replacement)
    return base64_hash


def extract_scene_audio_opt(clip, start_time, end_time, output_path, fade_out=2):
    try:
        # Set the start and end times for the scene
        start_time = min(start_time, clip.duration)
        end_time = min(end_time, clip.duration)

        # Extract the scene
        scene = clip.subclip(start_time, end_time - fade_out).fadeout(fade_out)
        # scene = clip.subclip(start_time, end_time)

        # Write the scene to a file
        scene.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=clip.fps)
    except Exception as e:
        # Handle the exception (print an error message, log the exception, etc.)
        print(f"An error occurred: {e}")


def extract_scene_audio(video_path, start_time, end_time, output_path, fade_out=2):
    try:
        # Load the video clip
        clip = mp.VideoFileClip(video_path)

        # Set the start and end times for the scene
        start_time = min(start_time, clip.duration)
        end_time = min(end_time, clip.duration)

        # Extract the scene
        scene = clip.subclip(start_time, end_time - fade_out).fadeout(fade_out)

        # Write the scene to a file
        scene.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=clip.fps)
    except Exception as e:
        # Handle the exception (print an error message, log the exception, etc.)
        print(f"An error occurred: {e}")
    finally:
        # Close the clip in the finally block to ensure it's always closed
        if 'clip' in locals():
            clip.close()


def create_clips(json_data, video_file, video_id, clips_directory, timeformat="sec"):
    clips_data = []
    index = 1
    clip = mp.VideoFileClip(video_file)
    for entry in json_data:
        start_time = entry['start_time']
        end_time = entry['end_time']
        # scene_summary = entry['scene_summary']
        short_description = entry["short_description"]
        scene_description = entry["scene_description"]
        clip_id = f"{video_id}_clip_{index}"
        index += 1

        if timeformat != "sec":
            start_seconds = sum(x * int(t) for x, t in
                zip([3600, 60, 1] if len(start_time.split(":")) == 3 else [60, 1], start_time.split(":")))

            end_seconds = sum(x * int(t) for x, t in
                       zip([3600, 60, 1] if len(end_time.split(":")) == 3 else [60, 1], end_time.split(":")))
        else:
            start_seconds = start_time
            end_seconds = end_time

        # Create clip
        clip_file = f"{clips_directory}{clip_id}.mp4"
        try:
            # extract_scene_audio(video_file, start_seconds, end_seconds, clip_file)
            extract_scene_audio_opt(clip, start_seconds, end_seconds, clip_file)
            # Append clip data
            clips_data.append({
                'start_time': start_time,
                'end_time': end_time,
                'video_id': clip_id,
                # 'scene_summary': scene_summary
                "short_description":short_description,
                "scene_description":scene_description
            })
        except Exception as e:
            print(f"An unexpected error occurred: {e} for clip {clip_file}")

    return clips_data


if __name__ == "__main__":

    video_directory = "./resources/videos/"
    clips_directory = "./resources/clips/"
    llm_scenes_directory = "./resources/llm_scenes/"

    files = list_files_in_directory(video_directory)
    youtube_id_list = [file.replace(".mp4", "") for file in files]
    # ids = [youtube_id_list[0]]
    for video_id in youtube_id_list:
        video_file = f"{video_directory}{video_id}.mp4"
        json_file = f"{llm_scenes_directory}{video_id}_scene.json"
        output_json_file = f"{clips_directory}{video_id}_scene_clips.json"
        json_data = ""
        with open(json_file, 'r') as f:
            json_data = json.load(f)

        clips_data = create_clips(json_data, video_file, video_id, clips_directory)

        with open(output_json_file, 'w') as f:
            json.dump(clips_data, f, indent=2)
