WORDJAM is an interactive crossword game with three levels of difficulty — Bitsize (5×5), Mega (7×7), and Giga (10×10).

## Tech Stack

Python · Flask · gunicorn · JavaScript · HTML/CSS · sentence-transformers · PyTorch · Groq API · Render

**Algorithms:** Backtracking, MRV heuristic, flood-fill, set-intersection word matching


The app generates a crossword in real time using a backtracking algorithm. It selects which slot to fill next using the MRV (Minimum Remaining Values) heuristic, and uses set intersection to quickly filter the words that can fit a given slot.

The program first generates a connected grid of white squares, then attempts to fill them with valid interlocking words using the backtracking algorithm, retrying with a fresh grid if the current one can't be filled in time. If the algorithm can't produce a valid grid within the time limit, WORDJAM falls back to a pre-generated backup grid, so the player never hits a failure.

Once the grid is filled, the warmth engine embeds the words using the all-MiniLM-L6-v2 Hugging Face model (via sentence-transformers) and uses cosine similarity to measure how close the player's guess is to the correct answer — giving warm/cold feedback instead of a plain right/wrong.

The clues are generated using the Groq API, guided by a set of rules coded into the program (NYT-style clues that never leak the answer or its letter count).

WORDJAM is an interactive crossword game with three levels of difficulty — Bitsize (5×5), Mega (7×7), and Giga (10×10).

The app generates a crossword in real time using a backtracking algorithm. It selects which slot to fill next using the MRV (Minimum Remaining Values) heuristic, and uses set intersection to quickly filter the words that can fit a given slot.

The program first generates a connected grid of white squares, then attempts to fill them with valid interlocking words using the backtracking algorithm, retrying with a fresh grid if the current one can't be filled in time. If the algorithm can't produce a valid grid within the time limit, WORDJAM falls back to a pre-generated backup grid, so the player never hits a failure.

Once the grid is filled, the warmth engine embeds the words using the all-MiniLM-L6-v2 Hugging Face model (via sentence-transformers) and uses cosine similarity to measure how close the player's guess is to the correct answer — giving warm/cold feedback instead of a plain right/wrong.

The clues are generated using the Groq API, guided by a set of rules coded into the program (NYT-style clues that never leak the answer or its letter count).


The frontend is a responsive single-page app built with plain HTML, CSS, and JavaScript.



Landing Page/Home Page 
<img width="2452" height="1266" alt="image" src="https://github.com/user-attachments/assets/9573c7d7-c024-4bd9-873c-4abf2d6cb033" />

Loading/Generating Page 
<img width="1962" height="1040" alt="image" src="https://github.com/user-attachments/assets/189bced4-eb10-4f80-af92-743c7e3d0dd5" />

5X5 CrossWord 
<img width="2316" height="1060" alt="image" src="https://github.com/user-attachments/assets/4ac6399d-c39a-4731-a4cb-37fb2243c166" />

Warm/Cold Feedback:
Whenever a word is filled in, the warmth engine lets you know how close the word is to the actual answer 
<img width="2142" height="1140" alt="image" src="https://github.com/user-attachments/assets/3eaeecf2-3015-4f5c-852b-ac4c3e1a1cca" />

Hint: Reveals one letter of the selected word 
<img width="1990" height="1134" alt="image" src="https://github.com/user-attachments/assets/4bd6dc24-3299-41b5-8cc6-3860057aeba2" />

7X7 CrossWord 
<img width="2102" height="1422" alt="image" src="https://github.com/user-attachments/assets/7c11c3cf-8bd3-4054-8b3a-6c9700ced9f5" />

10x10 CrossWord 
<img width="2292" height="1374" alt="image" src="https://github.com/user-attachments/assets/23e5cfa1-7ece-4e6a-97a7-58ca63ee9507" />


Credits
App icon by cube29 from Flaticon
Color palette: "Deepsea" from Paleto (CC0)
Fonts: VT323 & Nunito (Google Fonts, SIL Open Font License)
Word list: 2of12 from the 12dicts project
Clue generation: Groq
Embeddings: sentence-transformers (all-MiniLM-L6-v2)
