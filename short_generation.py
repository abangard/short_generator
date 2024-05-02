import streamlit as st

# Input
# 1. video_id
# 2. Prompt for clipping

# Output
# 1. Render list of videos
from app import generate_clips
from constants import DIRECTORY


def main():
    column_width = 1500
    st.write(
        f'<style>.main .block-container{{max-width: {column_width}px;}}</style>',
        unsafe_allow_html=True,
    )

    st.title("Max Shorts")

    # Textbox to input video_id
    video_id = st.text_input("Enter video_id", "")
    if video_id:
        st.video(f"{DIRECTORY}/resources/videos/{video_id}.mp4")

    # Textbox to input prompt
    prompt = st.text_input("Enter prompt", "")

    # Button to generate short
    if st.button("Generate Short", key=f"generate_short_button"):
        # Generate short
        generate_short(video_id, prompt)


def generate_short(video_id, prompt):
    clip_data = generate_clips(video_id, prompt)
    print(clip_data)
    # Display videos side by side
    for idx, col in enumerate(st.columns(3)):
        with col:
            st.video(f"/Users/abangard/workplace/streamlit/max/resources/clips/{video_id}_clip_{idx+1}.mp4")
            st.info(clip_data[idx]['short_description'])


if __name__ == "__main__":
    main()



