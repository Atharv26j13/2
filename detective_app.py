
import gradio as gr
import detective as d
import requests
import re
import time

from langdetect import detect as detect_statistical
from langdetect import DetectorFactory, LangDetectException

DetectorFactory.seed = 0


LANGUAGES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Kannada": "kn",
    "Japanese": "ja",
    "Chinese": "zh-CN",
    "Italian": "it",
    "Portuguese": "pt"
}

CODE_NAMES = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "hi": "Hindi",
    "kn": "Kannada",
    "ja": "Japanese",
    "zh-cn": "Chinese",
    "it": "Italian",
    "pt": "Portuguese"
}


# ---------------------------------
# LANGUAGE DETECTION
# ---------------------------------

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def investigate(text):

    if not text.strip():
        return {}, "Type or paste a message above."

    # Method 1: Original fingerprint detector
    ranking = d.rank_languages(text)
    verdict = d.detect(text)

    # Method 2: Statistical language detector
    statistical = "Unknown"

    try:
        code = detect_statistical(text)
        statistical = CODE_NAMES.get(code.lower(), code)

    except LangDetectException:
        pass

    except Exception:
        pass

    # Display fingerprint evidence
    if verdict == "Unknown":
        evidence_report = "Not enough fingerprint evidence."
    else:
        evidence = d.clues(text, verdict, n=8)

        evidence_report = (
            "**Fingerprint evidence:** "
            + "  ".join(
                f"`{g.replace(' ', '_')}`"
                for g in evidence
            )
        )

    # Compare the two detection methods
    if verdict == statistical and verdict != "Unknown":

        comparison = (
            "### Both detectors agree!\n"
            f"Both methods identify the language as **{verdict}**."
        )

    elif verdict == "Unknown":

        comparison = (
            "### Statistical result\n"
            f"Statistical detector suggests **{statistical}**.\n\n"
            "The fingerprint detector needs more evidence."
        )

    elif statistical == "Unknown":

        comparison = (
            "### Fingerprint result\n"
            f"Fingerprint detector suggests **{verdict}**.\n\n"
            "Statistical detection could not identify the language."
        )

    else:

        comparison = (
            "### Detectors disagree!\n"
            f"- Fingerprint detector: **{verdict}**\n"
            f"- Statistical detector: **{statistical}**\n\n"
            "Try entering a longer message."
        )

    # Short-message warning
    warning = ""

    if len(text.strip()) < 20:
        warning = (
            "\n\n<small>Warning: This message is very short. "
            "Language detection may be unreliable.</small>"
        )

    report = (
        comparison
        + "\n\n"
        + evidence_report
        + warning
    )

    return dict(ranking), report


# ---------------------------------
# LANGUAGES THE DETECTIVE KNOWS
# ---------------------------------

def languages_known():

    lines = [
        f"- **{name}**: {len(profile)} different 3-letter chunks"
        for name, profile in d.PROFILES.items()
    ]

    return (
        f"The detective knows **{len(d.PROFILES)}** languages:\n\n"
        + "\n".join(lines)
    )


# ---------------------------------
# TRANSLATION
# ---------------------------------


def translate_text(text, language):

    if not text.strip():
        return "Enter a message to translate."

    if not language:
        return ""

    try:
        # Automatically identify the source language
        source = detect_statistical(text)

        # No translation needed if both languages match
        if source.lower() == language.lower():
            return text

        # Translate from detected source to selected target
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={
                "q": text,
                "langpair": f"{source}|{language}"
            },
            timeout=20
        )

        data = response.json()

        if data.get("responseStatus") != 200:
            return "Translation unavailable: " + str(
                data.get("responseDetails", "Unknown error")
            )

        translated = data["responseData"]["translatedText"]

        return translated

    except LangDetectException:
        return "Could not identify the original language. Try a longer message."

    except Exception as e:
        print("TRANSLATION ERROR:", e)
        return f"Translation failed: {e}"



# ---------------------------------
# EXPERIMENTAL TRANSLATION DETECTION
# ---------------------------------


def detect_by_translation(text):

    if not text.strip():
        return "Enter a message first."

    if len(text.encode("utf-8")) > 450:
        return "Message too long for this experiment."

    results = []

    original = normalize(text)

    for name, code in LANGUAGES.items():

        # English does not need translation
        if code == "en":
            try:
                detected = detect_statistical(text)

                if detected == "en":
                    results.append(
                        "**English:** Statistical detector agrees."
                    )
                else:
                    results.append(
                        "**English:** Statistical detector does not agree."
                    )

            except Exception:
                results.append(
                    "**English:** Could not determine."
                )

            continue

        try:

            response = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q": text,
                    "langpair": f"{code}|en"
                },
                timeout=20
            )

            data = response.json()

            if data.get("responseStatus") != 200:
                results.append(
                    f"**{name}:** Translation unavailable"
                )
                continue

            translated = data["responseData"]["translatedText"]

            if normalize(translated) == original:
                results.append(
                    f"**{name}:** Inconclusive (original text returned)"
                )
            else:
                results.append(
                    f"**{name}:** {translated}"
                )

            time.sleep(0.5)

        except Exception as e:
            results.append(
                f"**{name}:** Error - {e}"
            )

    return (
        "### Translation comparison results\n\n"
        + "\n\n".join(results)
    )



# ---------------------------------
# GRADIO INTERFACE
# ---------------------------------

with gr.Blocks(title="Language Detective") as demo:

    gr.Markdown("# Language Detective")

    gr.Markdown(
        "Enter a mystery message and let the detective "
        "figure out its language!"
    )

    with gr.Tab("Investigate"):

        text = gr.Textbox(
            lines=3,
            label="Mystery message",
            placeholder="Type or paste a message here..."
        )

        language = gr.Dropdown(
            choices=[
                (name, code)
                for name, code in LANGUAGES.items()
            ],
            label="Translate into",
            value="en"
        )

        translation = gr.Textbox(
            label="Translated text",
            interactive=False
        )

        scores = gr.Label(
            num_top_classes=10,
            label="Fingerprint match for every language"
        )

        report = gr.Markdown()

        gr.Examples(
            [
                ["Je voudrais un croissant et un chocolat chaud, s'il vous plait."],
                ["Yaar aaj bahut garmi hai, chalo ice cream khaane chalte hain."],
                ["la pasta e buona"],
                ["pizza"],
                ["Hello, how are you?"],
                ["Guten Morgen! Wie geht es dir?"]
            ],
            inputs=text
        )

        # Run both language detectors
        text.change(
            investigate,
            inputs=text,
            outputs=[scores, report]
        )

        # Translate when a language is selected
        language.change(
            translate_text,
            inputs=[text, language],
            outputs=translation
        )

        # Translate when Enter is pressed
        text.submit(
            translate_text,
            inputs=[text, language],
            outputs=translation
        )

        gr.Markdown("---")

        gr.Markdown("## Experimental Language Detection")

        gr.Markdown(
            "Test the message against all supported languages "
            "by assuming each one is the source language "
            "and translating it into English."
        )

        detect_button = gr.Button(
            "Test All Languages"
        )

        detection_results = gr.Markdown()

        detect_button.click(
            detect_by_translation,
            inputs=text,
            outputs=detection_results
        )

    with gr.Tab("Languages I know"):

        known = gr.Markdown()

    demo.load(
        languages_known,
        inputs=None,
        outputs=known
    )


if __name__ == "__main__":

    demo.launch(
        share=False,
        inbrowser=True
    )
