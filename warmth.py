from sentence_transformers import SentenceTransformer, util

# Load the model once when this file is imported/run
model = SentenceTransformer("all-MiniLM-L6-v2")


def warmth(clue, guess, answer):
    if guess.lower() == answer.lower():
        print("Correct!")
        return

    answer_score = util.cos_sim(model.encode(clue), model.encode(answer)).item()
    guess_score = util.cos_sim(model.encode(clue), model.encode(guess)).item()
    ratio = guess_score / answer_score

    if ratio >= 0.9:
        print("Ooh so close")
    elif ratio >= 0.8:
        print("Warm")
    elif ratio >= 0.6:
        print("Maybe")
    elif ratio >= 0.4:
        print("Cool")
    elif ratio >= 0.3:
        print("So cold it's freezing")
    else:
        print("Not even close, try again")


# Test calls — run when this file is executed directly
if __name__ == "__main__":
    warmth("Archimedes exclamation", "eureka", "eureka")   # correct → top band
    warmth("Archimedes exclamation", "aha", "eureka")      # close
    warmth("Archimedes exclamation", "hello", "eureka")    # unrelated → cold
    warmth("Archimedes exclamation", "banana", "eureka")   # nonsense → cold