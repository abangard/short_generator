from youtube_transcript_api import YouTubeTranscriptApi
import json
import os
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatDatabricks

from constants import DIRECTORY

DATABRICKS_TOKEN = "XXX" # HS
DATABRICKS_HOST = "XXXX"


os.environ['DATABRICKS_TOKEN'] = DATABRICKS_TOKEN
os.environ['DATABRICKS_HOST'] = DATABRICKS_HOST

MIXTRAL_DATABRICKS_ENDPOINT = "databricks-mixtral-8x7b-instruct"
DBRX_DATABRICKS_ENDPOINT = "databricks-dbrx-instruct"
LLAMA_3_DATABRICKS_ENDPOINT = "databricks-meta-llama-3-70b-instruct"

dbx_llm = ChatDatabricks(
    endpoint=LLAMA_3_DATABRICKS_ENDPOINT,
    max_tokens=4096
)


def list_files_in_directory(directory):
    try:
        # Get a list of all files in the directory
        files = os.listdir(directory)
        return files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def extract_text(input_list):
    text_list = []
    for item in input_list:
        text_list.append(item['text'])
    return text_list


def read_input_list_from_file(filename):
    input_list = []
    with open(filename, 'r') as file:
        for line in file:
            # Remove newline character and convert string representation of dictionary to dictionary
            item = eval(line.strip())
            input_list.append(item)
    return input_list


def save_input_list_to_file(input_list, filename):
    with open(filename, 'w') as file:
        for item in input_list:
            file.write(str(item) + '\n')


def generate_save_transcript(youtube_id, transcripts_directory= ""):
    transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
    save_input_list_to_file(transcript, f"{transcripts_directory}{youtube_id}_transcript.txt")
    return f"{youtube_id}_transcript.txt"


def transform_for_llm(transcript_list):
    result_list = [ f"{item['start']} {item['text']}" for item in transcript_list]
    result_list = [ item.replace('\"', '').replace('\'', '') for item in result_list]
    return result_list


def group_transcript(input_llm,chunk_length=100):
    grouped = []
    start = 0
    while start < len(input_llm):
        end = min(start+chunk_length, len(input_llm))
        grouped.append(input_llm[start:end])
        start += chunk_length
    return grouped


def video_transcript_input(file_name, video_key, chunk_length=125):
    transcript_dict = {}
    input_for_llm = transform_for_llm(read_input_list_from_file(file_name))
    transcript_dict[video_key] = group_transcript(input_for_llm, chunk_length)
    return transcript_dict


def get_scenes_from_llm(transcript_dict, prompt):
    scene_list = []
    responses = []
    for video_id in transcript_dict.keys():
        for transcript in transcript_dict[video_id]:
            response = dbx_llm.invoke(prompt.format(transcript=transcript).replace("'", ""))
            responses.append(response)
            # response_json = dbx_llm.invoke("Convert the response into a single json output. Response : " + response.content)

    if responses:
        response_json = dbx_llm.invoke(f"Reduce the responses into a single json output with 3 responses which are closest to the original query i.e. `{prompt.template}`. Response : " + str(responses))
        print(response_json.content)

        out = "[" + response_json.content.lower().strip().split('[')[1].split(']')[0] + "]"
        json_output = json.loads(out)
        scene_list += json_output
    return scene_list


if __name__ == "__main__":
    template = """
    Given the transcript of a video split the transcript into different topics in the video. Give me 3 best scenes as a json output with keys start_time, end_time, short_description, scene_description. Each scene should be atleast 15 seconds long. The scene_description should describe the full scene. % START OF TRANSCRIPT {transcript} %END OF TRANSCRIPT
    """

    prompt = PromptTemplate(
        input_variables=["transcript"],
        template=template,
    )

    get_transcript = False
    video_directory = f"{DIRECTORY}/resources/videos/"
    transcripts_directory = f"{DIRECTORY}/resources/transcripts/"
    clips_directory = f"{DIRECTORY}/resources/clips/"
    llm_scenes_directory = f"{DIRECTORY}/resources/llm_scenes/"

    files = list_files_in_directory(video_directory)
    youtube_id_list = [file.replace(".mp4", "") for file in files]
    video_id = youtube_id_list[0]
    if get_transcript :
        for id in youtube_id_list:
            generate_save_transcript(id, transcripts_directory)

    transcript_file = f"{transcripts_directory}{video_id}_transcript.txt"
    transcript_dict = video_transcript_input(transcript_file, video_id)
    scene_list = get_scenes_from_llm(transcript_dict, prompt)

    with open(f"{llm_scenes_directory}{video_id}_scene.json", 'w') as f:
        json.dump(scene_list, f, indent=2)