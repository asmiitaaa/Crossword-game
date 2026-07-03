import os
from dotenv import load_dotenv
from groq import Groq

# Load the .env file so the API key becomes available
load_dotenv()

# Create the Groq client, authenticated with your key (read from .env)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def generate_clue(word, style="plain"):
    # build the instruction based on style
    if style == "popculture":
        extra = ("Include a well-known, non-ambiguous pop culture reference to the word. "
             "If unable to find a genuinely well-known reference, write a straightforward clue instead.")
    elif style == "synonym":
        extra = ("If the word has two distinct meanings, hint at both without revealing it. "
             "If it does not, write a straightforward clue instead.")
    elif style == "quote":
        extra = ("Base the clue on a famous, well-documented quote containing or relating to the word. "
             "Only use a quote you are confident is real and correctly attributed. "
             "If unsure, write a straightforward clue instead.")
    else:  # plain
        extra = "Write a descriptive clue."

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You write concise crossword clues. "
                                           "Give exactly one clue and nothing else. "
                                           "Never include the answer word directly in the clue, under any circumstances, even as a proper noun. "
                                           "Never include the letter-count of the word in the clue. "
                                           "Do not give antonyms/opposites as clues. "
                                           "Follow the New York Times crossword style, but never copy directly. "},

            {"role": "user", "content": f"Write a crossword clue for the word: {word}. {extra}"},
        ],
    )
    return response.choices[0].message.content
print(generate_clue("OCEAN", "plain"))
print(generate_clue("PIANO", "popculture"))
print(generate_clue("SHELL", "synonym"))
print(generate_clue("LIGHT", "quote"))