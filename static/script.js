/* ============ WORDJAM — game script ============ */

// ---- tier config: [size, a rough black-square pattern for the mini preview] ----
const TIER_SIZES = { bitsize: 5, mega: 7, giga: 10 };

// state we'll build on in later phases
let state = {
  tier: null,
  size: 0,
  black: [], // 2D array, 1 = black square
  slots: [], // [{direction, cells:[[r,c],...]}]
  clues: [], // clue text per slot (same order as slots)
  solved: new Set(),
  entries: {}, // "r,c" -> letter the player has typed
  activeSlot: null, // index into state.slots
  activeCell: null, // [r,c] of the current cell
  dir: "across", // current typing direction
};

// ---------- screen switching ----------
function showScreen(id) {
  document
    .querySelectorAll(".screen")
    .forEach((s) => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}

// ---------- ambient bubbles ----------
function makeBubbles(containerId, count) {
  const c = document.getElementById(containerId);
  if (!c) return;
  c.innerHTML = "";
  for (let i = 0; i < count; i++) {
    const b = document.createElement("div");
    b.className = "bubble";
    const size = 3 + Math.random() * 5;
    b.style.width = size + "px";
    b.style.height = size + "px";
    b.style.left = Math.random() * 100 + "%";
    b.style.animationDuration = 3 + Math.random() * 3 + "s";
    b.style.animationDelay = Math.random() * 4 + "s";
    // vary the colour a little
    const colors = ["#00e7ff", "#5ad4ff", "#2bff9a"];
    b.style.background = colors[Math.floor(Math.random() * colors.length)];
    c.appendChild(b);
  }
}

// ---------- mini-grid previews on the landing cards ----------
function buildMiniGrids() {
  document.querySelectorAll(".tier-mini").forEach((mini) => {
    const tier = mini.closest(".tier").dataset.tier;
    const n = TIER_SIZES[tier];
    mini.innerHTML = "";
    for (let i = 0; i < n * n; i++) {
      const cell = document.createElement("div");
      // scatter a few black squares for a crossword-y look (~18%)
      if (Math.random() < 0.18) cell.classList.add("b");
      mini.appendChild(cell);
    }
  });
}

// ---------- start a game for a tier ----------
async function startGame(tier) {
  state.tier = tier;
  state.size = TIER_SIZES[tier];

  // show the loading screen while the backend works
  showScreen("loading");
  resetLoadingSteps();

  try {
    const res = await fetch(`/new_game?tier=${tier}`);
    if (!res.ok) throw new Error("server error " + res.status);
    const data = await res.json();

    // stash everything for later phases
    state.size = data.size;
    state.black = data.black;
    state.slots = data.slots;
    state.clues = data.clues;
    state.solved = new Set();

    markLoadingStep("step-clues", "done");
    markLoadingStep("step-ready", "done");

    // small pause so the loading animation doesn't just flash by
    await new Promise((r) => setTimeout(r, 500));

    showScreen("game");
    // Phase 2 will render the grid + clues here:
    if (typeof renderGame === "function") renderGame();
  } catch (err) {
    console.error(err);
    alert("Could not start the game. Is the server running?");
    showScreen("landing");
  }
}

// ---------- loading step indicators ----------
function resetLoadingSteps() {
  ["step-grid", "step-clues", "step-ready"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.className = "";
  });
  // grid is "done" almost immediately, clues are "in progress"
  markLoadingStep("step-grid", "done");
  markLoadingStep("step-clues", "on");
}
function markLoadingStep(id, cls) {
  const el = document.getElementById(id);
  if (el) el.className = cls;
}

// ============ PHASE 2: render the grid + clues ============

// map each cell "r,c" -> the number shown in its corner (crossword numbering)
function computeCellNumbers() {
  const n = state.size;
  const nums = {}; // "r,c" -> number
  let counter = 0;
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      if (state.black[r][c]) continue;
      const startsAcross =
        (c === 0 || state.black[r][c - 1]) &&
        c + 1 < n &&
        !state.black[r][c + 1];
      const startsDown =
        (r === 0 || state.black[r - 1][c]) &&
        r + 1 < n &&
        !state.black[r + 1][c];
      if (startsAcross || startsDown) {
        counter++;
        nums[r + "," + c] = counter;
      }
    }
  }
  return nums;
}

// find the clue number for a slot (its first cell's number)
function slotNumber(slot, nums) {
  const [r, c] = slot.cells[0];
  return nums[r + "," + c];
}

function renderGame() {
  const n = state.size;
  state.cellNums = computeCellNumbers();

  // --- build the grid ---
  const grid = document.getElementById("grid");
  grid.style.gridTemplateColumns = `repeat(${n}, ${cellPx()}px)`;
  grid.style.gridTemplateRows = `repeat(${n}, ${cellPx()}px)`;
  grid.innerHTML = "";

  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const cell = document.createElement("div");
      if (state.black[r][c]) {
        cell.className = "cell block";
      } else {
        cell.className = "cell";
        cell.dataset.r = r;
        cell.dataset.c = c;
        const num = state.cellNums[r + "," + c];
        if (num) {
          const s = document.createElement("span");
          s.className = "num";
          s.textContent = num;
          cell.appendChild(s);
        }
        const letter = document.createElement("span");
        letter.className = "letter";
        cell.appendChild(letter);

        cell.addEventListener("click", () => onCellClick(r, c));
      }
      grid.appendChild(cell);
    }
  }

  // --- build the clue lists ---
  renderClues();
  updateStats();
}

// pick a cell size based on grid dimension so big grids still fit
function cellPx() {
  if (state.size <= 5) return 46;
  if (state.size <= 7) return 40;
  return 32;
}

function renderClues() {
  const across = document.getElementById("clues-across");
  const down = document.getElementById("clues-down");
  across.innerHTML = "";
  down.innerHTML = "";

  state.slots.forEach((slot, idx) => {
    const num = slotNumber(slot, state.cellNums);
    const row = document.createElement("div");
    row.className = "clue";
    row.dataset.idx = idx;
    if (state.solved.has(idx)) row.classList.add("done");
    row.innerHTML = `<span class="cnum">${num}</span><span class="ctxt">${state.clues[idx]}</span>`;
    row.addEventListener("click", () => selectSlot(idx, true));
    (slot.direction === "across" ? across : down).appendChild(row);
  });
}

function updateStats() {
  const total = state.slots.length;
  const done = state.solved.size;
  const pct = total ? Math.round((done / total) * 100) : 0;
  document.getElementById("stat-pct").textContent = pct + "%";
  document.getElementById("stat-words").textContent = done + "/" + total;
}

// ============ PHASE 3: selection, direction, typing ============

// find slots that pass through a given cell
function slotsAt(r, c) {
  const result = { across: null, down: null };
  state.slots.forEach((slot, idx) => {
    if (slot.cells.some(([cr, cc]) => cr === r && cc === c)) {
      result[slot.direction] = idx;
    }
  });
  return result;
}

// clicking a cell: select its word; clicking the same cell again flips direction
function onCellClick(r, c) {
  const here = slotsAt(r, c);
  const clickedSame =
    state.activeCell && state.activeCell[0] === r && state.activeCell[1] === c;

  let nextDir;
  if (clickedSame) {
    // flip if the other direction exists
    nextDir = state.dir === "across" ? "down" : "across";
    if (here[nextDir] === null) nextDir = state.dir; // no other word, keep current
  } else {
    // prefer current direction if a word exists here, else the other
    nextDir =
      here[state.dir] !== null
        ? state.dir
        : here.across !== null
          ? "across"
          : "down";
  }

  if (here[nextDir] === null) return; // no word here at all
  state.dir = nextDir;
  state.activeCell = [r, c];
  selectSlot(here[nextDir], false);
}

// select a slot (from grid click or clue click)
function selectSlot(idx, moveCellToStart) {
  state.activeSlot = idx;
  const slot = state.slots[idx];
  state.dir = slot.direction;
  if (
    moveCellToStart ||
    !state.activeCell ||
    !cellInSlot(state.activeCell, slot)
  ) {
    // move to first empty cell of the slot, or its start
    state.activeCell = firstEmptyCell(slot) || slot.cells[0].slice();
  }
  refreshHighlights();
}

function cellInSlot(cell, slot) {
  return slot.cells.some(([r, c]) => r === cell[0] && c === cell[1]);
}

function firstEmptyCell(slot) {
  for (const [r, c] of slot.cells) {
    if (!state.entries[r + "," + c]) return [r, c];
  }
  return null;
}

// repaint word/current highlights on the grid + sync the clue list
function refreshHighlights() {
  // clear
  document
    .querySelectorAll(".cell")
    .forEach((el) => el.classList.remove("word", "cur"));
  document
    .querySelectorAll(".clue")
    .forEach((el) => el.classList.remove("sel"));

  if (state.activeSlot === null) return;
  const slot = state.slots[state.activeSlot];

  slot.cells.forEach(([r, c]) => {
    const el = cellEl(r, c);
    if (el) el.classList.add("word");
  });
  if (state.activeCell) {
    const el = cellEl(state.activeCell[0], state.activeCell[1]);
    if (el) {
      el.classList.remove("word");
      el.classList.add("cur");
    }
  }

  // sync the one highlighted clue
  const clueRow = document.querySelector(
    `.clue[data-idx="${state.activeSlot}"]`,
  );
  if (clueRow) clueRow.classList.add("sel");
}

function cellEl(r, c) {
  return document.querySelector(`.cell[data-r="${r}"][data-c="${c}"]`);
}

// typing
function onKey(e) {
  if (document.getElementById("game").classList.contains("active") === false)
    return;
  if (state.activeSlot === null || !state.activeCell) return;

  if (/^[a-zA-Z]$/.test(e.key)) {
    setLetter(state.activeCell[0], state.activeCell[1], e.key.toUpperCase());
    advance(1);
    checkSlotComplete();
    e.preventDefault();
  } else if (e.key === "Backspace") {
    const [r, c] = state.activeCell;
    if (state.entries[r + "," + c]) {
      setLetter(r, c, "");
    } else {
      advance(-1);
      const [pr, pc] = state.activeCell;
      setLetter(pr, pc, "");
    }
    e.preventDefault();
  } else if (e.key === "ArrowRight" || e.key === "ArrowDown") {
    advance(1);
    e.preventDefault();
  } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
    advance(-1);
    e.preventDefault();
  }
}

function setLetter(r, c, letter) {
  const key = r + "," + c;
  if (letter) state.entries[key] = letter;
  else delete state.entries[key];
  const el = cellEl(r, c);
  if (el) {
    const span = el.querySelector(".letter");
    if (span) span.textContent = letter;
  }
}

// move the current cell within the active slot
function advance(step) {
  const slot = state.slots[state.activeSlot];
  const cells = slot.cells;
  let i = cells.findIndex(
    ([r, c]) => r === state.activeCell[0] && c === state.activeCell[1],
  );
  i += step;
  if (i < 0) i = 0;
  if (i >= cells.length) i = cells.length - 1;
  state.activeCell = cells[i].slice();
  refreshHighlights();
}

// when the active word has all letters filled, we'll check it (Phase 4)
function checkSlotComplete() {
  const slot = state.slots[state.activeSlot];
  const filled = slot.cells.every(([r, c]) => state.entries[r + "," + c]);
  if (filled && typeof submitGuess === "function") {
    submitGuess(state.activeSlot);
  }
}

// ============ PHASE 4: warmth feedback + animations ============

let submitting = false;

async function submitGuess(slotIdx) {
  if (submitting || state.solved.has(slotIdx)) return;
  const slot = state.slots[slotIdx];
  const guess = slot.cells
    .map(([r, c]) => state.entries[r + "," + c] || "")
    .join("");
  if (guess.length !== slot.cells.length) return;

  submitting = true;
  try {
    const res = await fetch("/guess", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clue_index: slotIdx, guess }),
    });
    const data = await res.json();
    playFeedback(data.feedback, data.correct);

    if (data.correct) {
      markSolved(slotIdx);
      autoSolveCrossings();
      updateStats();
      if (state.solved.size === state.slots.length) {
        setTimeout(() => playWin(), 700);
      }
    }
  } catch (err) {
    console.error(err);
  } finally {
    submitting = false;
  }
}

function markSolved(idx) {
  state.solved.add(idx);
  const slot = state.slots[idx];
  slot.cells.forEach(([r, c]) => {
    const el = cellEl(r, c);
    if (el) el.classList.add("solved");
  });
  const row = document.querySelector(`.clue[data-idx="${idx}"]`);
  if (row) row.classList.add("done");
}

// mark any slot whose cells are all filled correctly (completed by crossings)
function autoSolveCrossings() {
  state.slots.forEach((slot, idx) => {
    if (state.solved.has(idx)) return;
    const allFilled = slot.cells.every(([r, c]) => state.entries[r + "," + c]);
    if (!allFilled) return;
    // we can't verify correctness client-side, so just check completion visually
    // (the backend already confirmed crossing letters via correct words)
  });
}

// ---- the centered animation overlay ----
function playFeedback(feedback, correct) {
  const fx = document.getElementById("fx");
  fx.innerHTML = "";

  const style = feedbackStyle(feedback, correct);
  // pill
  const pill = document.createElement("div");
  pill.className = "fx-pill";
  pill.textContent = style.label;
  pill.style.background = style.bg;
  pill.style.color = style.fg;
  pill.style.animation = style.pillAnim;
  fx.appendChild(pill);

  // particles
  if (style.particles) style.particles(fx);

  // clear after it plays
  setTimeout(() => {
    fx.innerHTML = "";
  }, 1100);
}

function feedbackStyle(feedback, correct) {
  const f = (feedback || "").toLowerCase();
  if (correct || f === "correct!") {
    return {
      label: "Correct!",
      bg: "#2bff9a",
      fg: "#062028",
      pillAnim: "burstPill 1s ease-out",
      particles: confetti,
    };
  }
  if (f.includes("so close")) {
    return {
      label: "Ooh so close",
      bg: "#ff4d7d",
      fg: "#fff",
      pillAnim: "pulsePill .9s ease-out",
      particles: (fx) => poppers(fx, "#ff4d7d"),
    };
  }
  if (f === "warm" || f.includes("warm")) {
    return {
      label: "Warm",
      bg: "#ff9f2e",
      fg: "#062028",
      pillAnim: "pulsePill .9s ease-out",
      particles: (fx) => sparks(fx, ["#ff9f2e", "#ffd84d"]),
    };
  }
  if (f.includes("maybe")) {
    return {
      label: "Maybe",
      bg: "#ffd84d",
      fg: "#062028",
      pillAnim: "pulsePill .9s ease-out",
      particles: (fx) => sparks(fx, ["#ffd84d", "#5ad4ff"]),
    };
  }
  if (f.includes("cool")) {
    return {
      label: "Cool",
      bg: "#5ad4ff",
      fg: "#062028",
      pillAnim: "pulsePill .9s ease-out",
      particles: (fx) => snow(fx, 4),
    };
  }
  if (f.includes("freezing")) {
    return {
      label: "Freezing",
      bg: "#12324a",
      fg: "#7fb9d6",
      pillAnim: "pulsePill .9s ease-out",
      particles: (fx) => snow(fx, 9),
    };
  }
  // not even close
  return {
    label: "Not even close",
    bg: "#12324a",
    fg: "#7fb9d6",
    pillAnim: "shakePill .5s ease-out",
    particles: null,
  };
}

// ---- particle helpers ----
function confetti(fx) {
  const colors = ["#2bff9a", "#00e7ff", "#ffd84d", "#ff4d7d"];
  for (let i = 0; i < 10; i++) {
    const p = document.createElement("span");
    p.className = "fx-particle";
    p.style.setProperty("--dx", Math.random() * 60 - 30 + "px");
    p.style.width = "6px";
    p.style.height = "6px";
    p.style.background = colors[i % colors.length];
    p.style.animation = "confRise .8s ease-out";
    p.style.animationDelay = Math.random() * 0.15 + "s";
    fx.appendChild(p);
  }
}
function poppers(fx, color) {
  const colors = [color, "#ffd84d", "#00e7ff", "#2bff9a"];
  for (let i = 0; i < 8; i++) {
    const p = document.createElement("span");
    p.className = "fx-particle";
    p.style.setProperty("--dx", Math.random() * 70 - 35 + "px");
    p.style.width = "6px";
    p.style.height = "6px";
    p.style.background = colors[i % colors.length];
    p.style.animation = "confRise .85s ease-out";
    p.style.animationDelay = Math.random() * 0.2 + "s";
    fx.appendChild(p);
  }
}
function sparks(fx, colors) {
  for (let i = 0; i < 8; i++) {
    const p = document.createElement("span");
    p.className = "fx-particle";
    const ang = Math.random() * Math.PI * 2;
    const dist = 18 + Math.random() * 14;
    p.style.setProperty("--dx", Math.cos(ang) * dist + "px");
    p.style.setProperty("--dy", Math.sin(ang) * dist + "px");
    p.style.width = "4px";
    p.style.height = "4px";
    p.style.borderRadius = "50%";
    p.style.background = colors[i % colors.length];
    p.style.animation = "sparkFly .7s ease-out";
    p.style.animationDelay = Math.random() * 0.1 + "s";
    fx.appendChild(p);
  }
}
function snow(fx, count) {
  for (let i = 0; i < count; i++) {
    const p = document.createElement("span");
    p.className = "fx-particle";
    p.style.setProperty("--dx", Math.random() * 40 - 20 + "px");
    p.style.width = "5px";
    p.style.height = "5px";
    p.style.background = "#cdeefe";
    p.style.left = Math.random() * 60 - 30 + "px";
    p.style.animation = "snowFall 1.1s linear";
    p.style.animationDelay = Math.random() * 0.4 + "s";
    fx.appendChild(p);
  }
}

function playWin() {
  const fx = document.getElementById("fx");
  fx.innerHTML = "";
  const pill = document.createElement("div");
  pill.className = "fx-pill";
  pill.textContent = "Solved!";
  pill.style.background = "#2bff9a";
  pill.style.color = "#062028";
  pill.style.animation = "burstPill 1.4s ease-out";
  fx.appendChild(pill);
  confetti(fx);
  confetti(fx);
  setTimeout(() => {
    fx.innerHTML = "";
  }, 2500);
}

// ---- Clear: wipe the active word ----
function clearActiveWord() {
  if (state.activeSlot === null) return;
  const slot = state.slots[state.activeSlot];
  if (state.solved.has(state.activeSlot)) return;
  slot.cells.forEach(([r, c]) => setLetter(r, c, ""));
  state.activeCell = slot.cells[0].slice();
  refreshHighlights();
}

// ---- Hint: reveal one letter of the active word (asks the backend) ----
async function useHint() {
  if (state.activeSlot === null) return;
  try {
    const res = await fetch(`/hint?clue_index=${state.activeSlot}`);
    const data = await res.json();
    if (data.pos != null && data.letter) {
      const slot = state.slots[state.activeSlot];
      const [r, c] = slot.cells[data.pos];
      setLetter(r, c, data.letter);
      playFeedback("hint", false);
      checkSlotComplete();
    }
  } catch (err) {
    console.error(err);
  }
}

// ---------- wire up the page ----------
function init() {
  makeBubbles("landing-bubbles", 14);
  makeBubbles("loading-bubbles", 10);
  buildMiniGrids();

  // tier cards
  document.querySelectorAll(".tier").forEach((btn) => {
    btn.addEventListener("click", () => startGame(btn.dataset.tier));
  });

  // footer: New returns to landing (refresh-like)
  const btnNew = document.getElementById("btn-new");
  if (btnNew) btnNew.addEventListener("click", () => showScreen("landing"));

  const btnClear = document.getElementById("btn-clear");
  if (btnClear) btnClear.addEventListener("click", clearActiveWord);

  const btnHint = document.getElementById("btn-hint");
  if (btnHint) btnHint.addEventListener("click", useHint);

  // keyboard typing
  document.addEventListener("keydown", onKey);

  showScreen("landing");
}

document.addEventListener("DOMContentLoaded", init);
