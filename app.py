import gradio as gr
from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not client.api_key:
    raise ValueError("Please set the OPENAI_API_KEY in your .env file")

def generate_versions(text):
    prompt = f"""Given the original text: "{text}"
    Generate two rephrased versions:
    1. A slightly more emotional version (ex. "위험해요" -> "위험해요!!")
    2. An exaggerated, highly emotional version (ex. "위험해요" -> "잠깐만요! 안돼, 위험해요!!")
    Output format:
    Original: [original text]
    Emotional: [emotional version]
    Exaggerated: [exaggerated version]"""

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content

    versions = full_response.split('\n')
    return [v.split(': ', 1)[1] for v in versions if ': ' in v]

def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    return response.content

def process_and_generate(text):
    versions = generate_versions(text)
    audio_contents = [text_to_speech(v) for v in versions]
    return versions + audio_contents + ["All versions generated successfully!"]

with gr.Blocks(title="Emotional TTS Comparison") as demo:
    gr.Markdown("# Emotional TTS Comparison")
    gr.Markdown("Enter text to generate three versions with varying emotional intensity.")
    
    input_text = gr.Textbox(label="Original Text", lines=3)
    generate_btn = gr.Button("Generate Versions and Speech")
    
    with gr.Row():
        text1 = gr.Textbox(label="Original Version")
        text2 = gr.Textbox(label="Emotional Version")
        text3 = gr.Textbox(label="Exaggerated Version")
    
    with gr.Row():
        audio1 = gr.Audio(label="Original Speech")
        audio2 = gr.Audio(label="Emotional Speech")
        audio3 = gr.Audio(label="Exaggerated Speech")
    
    status = gr.Textbox(label="Status")
    
    generate_btn.click(
        process_and_generate,
        inputs=[input_text],
        outputs=[text1, text2, text3, audio1, audio2, audio3, status]
    )

if __name__ == "__main__":
    demo.launch()
else:
    demo.launch(share=True)