from sentence_transformers import SentenceTransformer, util

# Load the model once when this file is imported/run
model = SentenceTransformer("all-MiniLM-L6-v2")


def warmth(clue, guess, answer):
    if guess.lower() == answer.lower():
        return("Correct!")

    answer_score = util.cos_sim(model.encode(clue), model.encode(answer)).item()
    guess_score = util.cos_sim(model.encode(clue), model.encode(guess)).item()
    ratio = guess_score / answer_score

    if ratio >= 0.9:
        return("Ooh so close")
    elif ratio >= 0.8:
        return("Warm")
    elif ratio >= 0.6:
        return("Maybe")
    elif ratio >= 0.4:
        return("Cool")
    elif ratio >= 0.3:
        return("So cold it's freezing")
    else:
        return("Not even close, try again")

