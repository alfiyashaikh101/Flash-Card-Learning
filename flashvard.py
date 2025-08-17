import csv
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import random

FILENAME = "flashcards.csv"
TOTAL_TIME = 15  # seconds for each question

# --- bootstrap sample csv if missing ---
if not os.path.exists(FILENAME):
    with open(FILENAME, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        writer.writerow(["Capital of France?", "Paris"])
        writer.writerow(["2 + 2?", "4"])
        writer.writerow(["Python creator?", "Guido van Rossum"])
        writer.writerow(["Largest planet?", "Jupiter"])
        writer.writerow(["Color of the sky?", "Blue"])
    print("Sample flashcards.csv created! Restart the program.")
    exit()

# --- data helpers ---
def load_flashcards():
    cards = []
    with open(FILENAME, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("Question") and row.get("Answer"):
                cards.append({"Question": row["Question"], "Answer": row["Answer"]})
    return cards

flashcards = load_flashcards()
used_cards = []
score = 0
streak = 0
total_questions = len(flashcards)
round_id = 0  # guard for countdown per round

# --- UI setup ---
root = tk.Tk()
root.title("Flashcard Learning App 📚")
root.geometry("560x560")
root.configure(bg="#f5f5f5")

# Score + Streak
topbar = tk.Frame(root, bg="#f5f5f5")
topbar.pack(pady=(10, 0))

score_label = tk.Label(topbar, text=f"Score: {score}/{total_questions}",
                       font=("Arial", 12, "bold"), bg="#f5f5f5", fg="#333")
score_label.pack(side="left", padx=10)

streak_label = tk.Label(topbar, text=f"Streak: {streak} 🔥",
                        font=("Arial", 12, "bold"), bg="#f5f5f5", fg="#e67e22")
streak_label.pack(side="left", padx=10)

# Progress bar
progress_bar = tk.Frame(root, bg="#ddd", height=18, width=360)
progress_bar.pack(pady=10)
progress_fill = tk.Frame(progress_bar, bg="#4caf50", height=18, width=0)
progress_fill.pack(side="left", fill="y")

# Timer canvas (circular)
canvas = tk.Canvas(root, width=170, height=170, bg="#f5f5f5", highlightthickness=0)
canvas.pack(pady=8)
canvas.create_oval(15, 15, 155, 155, outline="#ccc", width=4, tags="ring")

# Question
question_label = tk.Label(root, text="", font=("Arial", 18, "bold"),
                          wraplength=500, bg="#f5f5f5", fg="#222")
question_label.pack(pady=(12, 6))

# Answer input
entry_frame = tk.Frame(root, bg="#f5f5f5")
entry_frame.pack(pady=4)

answer_entry = tk.Entry(entry_frame, font=("Arial", 14), width=32)
answer_entry.grid(row=0, column=0, padx=6)

submit_btn = tk.Button(entry_frame, text="Submit ✅", font=("Arial", 12, "bold"),
                       bg="#2196f3", fg="white", width=12, command=lambda: check_answer())
submit_btn.grid(row=0, column=1, padx=6)

# Control buttons
control_frame = tk.Frame(root, bg="#f5f5f5")
control_frame.pack(pady=6)

hint_btn = tk.Button(control_frame, text="Hint 💡", font=("Arial", 12, "bold"),
                     bg="#ffd54f", width=12, command=lambda: show_hint())
hint_btn.grid(row=0, column=0, padx=6)

skip_btn = tk.Button(control_frame, text="Skip ⏭", font=("Arial", 12, "bold"),
                     bg="#ef5350", fg="white", width=12, command=lambda: skip_question())
skip_btn.grid(row=0, column=1, padx=6)

# Add card button
add_btn = tk.Button(root, text="➕ Add Flashcard", font=("Arial", 12, "bold"),
                    bg="#9ccc65", fg="white", width=20, command=lambda: add_flashcard())
add_btn.pack(pady=6)

# Result label
result_label = tk.Label(root, text="", font=("Arial", 14),
                        wraplength=520, bg="#f5f5f5")
result_label.pack(pady=8)

# --- helpers ---
def update_progress():
    if total_questions == 0:
        w = 0
    else:
        w = int((len(used_cards) / total_questions) * 360)
    progress_fill.config(width=w)

def set_controls_state(active: bool):
    state = "normal" if active else "disabled"
    submit_btn.config(state=state)
    hint_btn.config(state=state)
    skip_btn.config(state=state)
    answer_entry.config(state="normal" if active else "disabled")

def mask_answer(ans: str, reveal=1):
    if not ans:
        return ""
    revealed = 0
    out = []
    for ch in ans:
        if ch.isspace():
            out.append(ch)
        elif revealed < reveal:
            out.append(ch)
            revealed += 1
        else:
            out.append("_")
    return "".join(out)

def choose_next_card():
    """Pick a random unused flashcard (unempted mode)."""
    if len(used_cards) == len(flashcards):
        return None
    available = [c for c in flashcards if c not in used_cards]
    return random.choice(available)

# --- app logic ---
current_card = None

def next_flashcard():
    global current_card, round_id
    card = choose_next_card()
    if card is None:
        finish_quiz()
        return

    used_cards.append(card)
    current_card = card
    round_id += 1
    result_label.config(text="")
    question_label.config(text=current_card["Question"])

    # reset UI
    answer_entry.delete(0, tk.END)
    set_controls_state(True)
    answer_entry.focus_set()
    update_progress()

    # start timer
    start_timer(TOTAL_TIME, round_id)

def finish_quiz():
    global used_cards, score, streak
    messagebox.showinfo("Quiz Finished",
                        f"Final Score: {score}/{total_questions}\nStreak: {streak}")
    used_cards = []
    score = 0
    streak = 0
    score_label.config(text=f"Score: {score}/{total_questions}")
    streak_label.config(text=f"Streak: {streak} 🔥")
    update_progress()
    next_flashcard()

def start_timer(seconds, rid):
    countdown(seconds, rid)

def countdown(seconds, rid):
    if rid != round_id:
        return
    canvas.delete("timer_arc", "timer_text")
    if seconds > 0:
        frac = seconds / TOTAL_TIME
        red = int((1 - frac) * 255)
        green = int(frac * 255)
        color = f"#{red:02x}{green:02x}00"
        extent = frac * 360
        canvas.create_arc(15, 15, 155, 155, start=90, extent=-extent,
                          fill=color, outline="", tags="timer_arc")
        canvas.create_text(85, 85, text=f"{seconds}",
                           font=("Arial", 22, "bold"), fill="#222",
                           tags="timer_text")
        root.after(1000, countdown, seconds - 1, rid)
    else:
        canvas.create_text(85, 85, text="⏳", font=("Arial", 20),
                           fill="red", tags="timer_text")
        time_up()

def time_up():
    global streak
    set_controls_state(False)
    result_label.config(text=f"⏰ Time's up! Correct: {current_card['Answer']}", fg="#d32f2f")
    streak = 0
    streak_label.config(text=f"Streak: {streak} 🔥")
    root.after(1800, next_flashcard)

def check_answer():
    set_controls_state(False)
    user = answer_entry.get().strip().lower()
    correct = current_card["Answer"].strip().lower()
    global score, streak
    if user == correct:
        score += 1
        streak += 1
        score_label.config(text=f"Score: {score}/{total_questions}")
        streak_label.config(text=f"Streak: {streak} 🔥")
        result_label.config(text="✅ Correct!", fg="#2e7d32")
    else:
        streak = 0
        streak_label.config(text=f"Streak: {streak} 🔥")
        result_label.config(text=f"❌ Wrong! Correct: {current_card['Answer']}",
                            fg="#d32f2f")
    root.after(1000, next_flashcard)

def show_hint():
    ans = current_card["Answer"]
    reveal = 2 if len(ans.replace(" ", "")) >= 6 else 1
    hint = mask_answer(ans, reveal=reveal)
    result_label.config(text=f"Hint: {hint}", fg="#6a1b9a")

def skip_question():
    global streak
    set_controls_state(False)
    streak = 0
    streak_label.config(text=f"Streak: {streak} 🔥")
    result_label.config(text=f"⏭ Skipped! Correct: {current_card['Answer']}", fg="#555")
    root.after(800, next_flashcard)

def add_flashcard():
    q = simpledialog.askstring("New Flashcard", "Enter the question:")
    if not q:
        return
    a = simpledialog.askstring("New Flashcard", "Enter the answer:")
    if not a:
        return
    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([q, a])
    messagebox.showinfo("Added", "New flashcard added!")
    global flashcards, total_questions
    flashcards = load_flashcards()
    total_questions = len(flashcards)
    score_label.config(text=f"Score: {score}/{total_questions}")

root.bind("<Return>", lambda e: check_answer())
next_flashcard()
root.mainloop()
