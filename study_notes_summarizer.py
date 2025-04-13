import gradio as gr
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# === Configure Gemini API ===
genai.configure(api_key="AIzaSyABjjtDkWlJTGYgy5mkagHlDAEhpPTm1JI")
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# === PDF Generator ===
def save_as_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    filename = f"Study_Notes_Summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def save_as_txt(text):
    filename = f"Study_Notes_Summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename

# === AI Summary Generator ===
def summarize_notes(notes, subject, style, length):
    prompt = (
        f"You are a smart academic assistant. Summarize the notes below for the subject '{subject}'.\n"
        f"Format: {style}\nLength: {length}\n\nNotes:\n{notes}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# === UI App ===
session_history = []

with gr.Blocks(title="Study Notes Summarizer") as app:
    gr.HTML("""
    <div style='text-align: center; padding: 20px; background-color: #222; color: white; border-radius: 12px;'>
        <h1 style='font-size: 2.3rem;'>Study Notes Summarizer</h1>
        <p style='max-width: 700px; margin: auto; font-size: 1rem; color: #ccc;'>
            Convert raw study notes into structured summaries. Choose your format, length, and get AI-powered results instantly.
        </p>
    </div>
    """)

    with gr.Tabs():
        with gr.Tab("Summarize Notes"):
            gr.Markdown("#### Input Your Details Below")

            subject = gr.Textbox(label="Subject or Topic")
            notes = gr.Textbox(label="Paste Study Notes", lines=10, placeholder="Enter your raw notes, copied text, or content...")

            style = gr.Radio(["Bullet Points", "Paragraph Summary", "Flashcard Q&A"], label="Summary Format", value="Bullet Points")
            length = gr.Radio(["Short", "Medium", "Detailed"], label="Summary Length", value="Medium")

            generate_btn = gr.Button("Generate Summary")

            gr.Markdown("#### AI-Generated Summary Output")
            output = gr.Textbox(label="Summary", lines=20)

            gr.Markdown("#### Export Options")
            with gr.Row():
                pdf_btn = gr.Button("Download as PDF")
                txt_btn = gr.Button("Download as TXT")
            file_output = gr.File(label="Download Link")

        with gr.Tab("Session History"):
            history_box = gr.Textbox(label="Previous Summaries", lines=15, interactive=False)

    def handle_generate(notes, subject, style, length):
        summary = summarize_notes(notes, subject, style, length)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        session_history.append(f"[{timestamp}] {subject} ({style}, {length})")
        return summary, "\n".join(session_history[-5:])

    generate_btn.click(fn=handle_generate, inputs=[notes, subject, style, length], outputs=[output, history_box])
    pdf_btn.click(fn=save_as_pdf, inputs=output, outputs=file_output)
    txt_btn.click(fn=save_as_txt, inputs=output, outputs=file_output)

app.launch()
