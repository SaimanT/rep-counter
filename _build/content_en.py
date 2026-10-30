"""English pages — the main version of the site, served from the root."""

UI = {
    "lang": "en", "prefix": "", "og_locale": "en_US", "currency": "USD", "os": "Any (web browser)",
    "home_name": "Rep Counter", "og_title_suffix": " Online", "app_label": "Counter",
    "install": "Install app", "one": "“Just one” mode: hide the goal and reps left",
"sound": "Sound and vibration", "fullscreen": "Full screen",
    "plan": "Goal:",
    "info": 'Done <b id="done">0</b> of <b id="total">{plan}</b>\n    &nbsp;·&nbsp; '
            '<span class="left"><b id="left">{plan}</b> left</span>',
    "minus": "Remove one rep", "finish": "✓ Set", "reset": "Reset",
    "keys": "<kbd>Space</kbd> +1 &nbsp; <kbd>Backspace</kbd> −1 &nbsp; <kbd>Enter</kbd> finish set &nbsp;\n"
            "    <kbd>R</kbd> reset &nbsp; <kbd>F</kbd> full screen",
    "tap": "Tap the screen to add a rep", "howto_link": "How it works ↓",
    "faq_title": "FAQ", "more_title": "More counters", "footer_tail": "free, no sign-up",
    "switch": "Русский",
    # share preview card
    "og_tagline": "Press space after every rep — the counter shows how many are left",
    "og_badges": "Free · no sign-up · works offline", "og_of": "of", "og_left": "left",
}

COMMON_FAQ = [
    ("Is it free?", "Yes, completely free — no sign-up and no ads."),
    ("Does the counter work offline?",
     "Yes. After the first visit the page works without internet, and you can install it as an app on your computer or phone."),
    ("Will my count be saved if I close the tab?",
     "Yes. Your count, goal and sets are saved in your browser on this device. Nothing is sent anywhere."),
]

SHORT_FAQ = [
    ("Is it free, and does it work offline?",
     "Yes: no sign-up, no ads, and after the first visit the page works without internet. Your count is saved in the browser."),
]

CONTROLS = """
  <p><b>Controls:</b> Space +1, Backspace −1, Enter finishes a set, R resets.
  On a phone, tap the screen and use the buttons under the counter. <a href="{home}#about">More about the counter</a>.</p>"""

HOW_TO = """
  <h2>How to use it</h2>
  <ul>
    <li><b>Set a goal</b> — type a number or pick one of the presets.</li>
    <li><b>Press space</b> after every rep. On a phone, tap the screen.</li>
    <li><b>Miscounted?</b> Backspace removes one rep.</li>
    <li><b>Finished a set?</b> Press Enter. The set is saved, the count starts over,
      and you see the total below — for example “Sets: 20 · 20 · 18 — workout total: 58”.</li>
    <li><b>Goal reached</b> — the screen turns green and a sound plays.</li>
    <li><b>F</b> toggles full screen, <b>R</b> resets the whole workout.</li>
    <li><b>On a phone</b> the same actions are buttons under the counter: −1, Set, Reset,
      sound and vibration, full screen. The screen stays on while the page is open.</li>
  </ul>"""

PAGES = [
    {
        "id": "home", "slug": "", "store": "",
        "h1": "Rep Counter",
        "title": "Rep Counter Online — Count Reps with the Spacebar",
        "description": "Free online rep counter for workouts. Set a goal, press space after each rep and see big numbers, reps left and sets. No sign-up, works offline.",
        "plan": 10, "presets": [10, 20, 50, 100],
        "body": """
  <h2>A free online rep counter for your workouts</h2>
  <p>It's easy to lose count in your head — especially on rep 30 or your third set.
  This counter keeps track for you: set a goal, then press space after every rep
  (or tap your phone screen). The huge numbers are readable from across the room, and right
  below them you see how many you've done and how many are left.</p>
{how_to}
  <h2>Works for any exercise</h2>
  <p>Use it for anything you count: push-ups, squats, pull-ups, lunges, sit-ups, burpees,
  kettlebell swings. It's handy for challenges like “100 push-ups a day”: set a goal of 100,
  split it into sets, and the counter adds them up. Popular exercises have their own counters
  with ready-made goals and tips:</p>
{links}
  <h2>Install it as an app</h2>
  <p>You can install the counter on your computer or phone — it opens in its own window and works
  offline. In Chrome or Edge, click “Install app” at the top of the page or the install icon in
  the address bar. On iPhone: Share → Add to Home Screen.</p>
""",
        "faq": COMMON_FAQ + [
            ("Can I use it on my phone?", "Yes. Every tap on the screen adds one rep."),
        ],
    },
    {
        "id": "pushups", "slug": "push-up-counter", "store": "otzhimaniya",
        "h1": "Push-Up Counter",
        "title": "Push-Up Counter Online — Count Push-Ups and Sets",
        "description": "Free push-up counter: set a goal, press space or tap the screen after each push-up. See how many are left while your sets add up to a total.",
        "plan": 20, "presets": [10, 20, 30, 50, 100],
        "body": """
  <h2>How to count push-ups</h2>
  <p>Place your laptop or phone where you can see it from the plank position. Press space after
  every push-up — or put your phone on the floor in front of you and tap the screen. The big numbers
  are visible out of the corner of your eye, and the “left” line helps you finish the set.</p>
{how_to}
  <h2>How many push-ups should you do?</h2>
  <ul>
    <li><b>Beginner:</b> 3 sets of 5–10 reps, on your knees or against a bench if needed.</li>
    <li><b>Intermediate:</b> 3–4 sets of 15–25 reps.</li>
    <li><b>“100 push-ups a day” challenge:</b> set a goal of 100 and do it in sets throughout the
      day — press Enter after each one and the counter shows your daily total.</li>
  </ul>
  <p>Add 1–2 reps per set every few workouts for steady progress.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>Keep a straight line from head to heels — don't let your hips sag.</li>
    <li>Elbows at about 45° to your body, not flared out.</li>
    <li>Lower until your chest nearly touches the floor, then fully straighten your arms.</li>
    <li>Count only clean reps — that's what the counter is for.</li>
  </ul>
""",
        "faq": [
            ("How many push-ups should I do a day?",
             "It depends on your level. Beginners do well with 20–30 push-ups spread over a few sets, trained people with 50–100. Consistency and clean form matter more than a record number."),
            ("Can I count push-ups with my phone?",
             "Yes. Put your phone on the floor in front of you and tap the screen at the top of each rep — every tap counts one push-up."),
        ] + SHORT_FAQ,
    },
    {
        "id": "squats", "slug": "squat-counter", "store": "prisedaniya",
        "h1": "Squat Counter",
        "title": "Squat Counter Online — Count Squats with One Key",
        "description": "Online squat counter with big numbers: set a goal, press space or tap after each squat, and track reps left and sets. Free and works offline.",
        "plan": 30, "presets": [15, 20, 30, 50, 100],
        "body": """
  <h2>How to count squats</h2>
  <p>Stand facing the screen. A wireless keyboard or a remote with a spacebar in your hand works
  best — or put your phone nearby and tap it at the top of every squat. The numbers are readable
  from a couple of metres away, so you never have to bend down to check.</p>
{how_to}
  <h2>How many squats should you do?</h2>
  <ul>
    <li><b>Beginner:</b> 3 sets of 10–15 reps.</li>
    <li><b>Intermediate:</b> 3–4 sets of 20–30 reps.</li>
    <li><b>“100 squats a day” challenge:</b> goal of 100, sets of 20–25 with rest in between —
      the counter adds them up for you.</li>
  </ul>

  <h2>Form in brief</h2>
  <ul>
    <li>Feet shoulder-width apart, toes turned slightly out.</li>
    <li>Knees track over your toes and don't cave in.</li>
    <li>Keep your back straight and your heels on the floor.</li>
    <li>Go at least to parallel if your mobility allows.</li>
  </ul>
""",
        "faq": [
            ("How many squats should I do a day?",
             "Start with 30–50 squats over a few sets. Trained people do 100 or more. Increase the load gradually and watch your knees."),
            ("How do I count squats when my hands hold dumbbells?",
             "Do the set, then add the reps with the spacebar and save the set with Enter. Or ask a partner to press for you."),
        ] + SHORT_FAQ,
    },
    {
        "id": "pullups", "slug": "pull-up-counter", "store": "podtyagivaniya",
        "h1": "Pull-Up Counter",
        "title": "Pull-Up Counter Online — Track Sets and Total Reps",
        "description": "Count pull-ups set by set and see your workout total. Press space or tap the screen to add reps. A free online pull-up counter that works offline.",
        "plan": 10, "presets": [5, 8, 10, 15, 20],
        "body": """
  <h2>How to count pull-ups</h2>
  <p>Your hands are busy on the bar, so count after the set: drop down, press space for each rep and
  Enter to save the set. Or have a partner press for you. Either way, the counter adds up all your
  sets and shows how many pull-ups you did in the whole workout.</p>
{how_to}
  <h2>How many pull-ups should you do?</h2>
  <ul>
    <li><b>Can't do one yet:</b> negatives (slow lowering) and band-assisted pull-ups.</li>
    <li><b>1–5 reps:</b> 4–6 sets of 1–3 reps, stopping short of failure.</li>
    <li><b>5–10 reps:</b> 3–5 sets at 60–80% of your max.</li>
    <li><b>Ladder:</b> 1, 2, 3, 4… reps per set — save each step with Enter.</li>
  </ul>

  <h2>Form in brief</h2>
  <ul>
    <li>Start from a dead hang with straight arms, no swinging.</li>
    <li>Bring your chin above the bar.</li>
    <li>Squeeze your shoulder blades and drive your elbows down instead of just bending your arms.</li>
  </ul>
""",
        "faq": [
            ("How can I do more pull-ups?",
             "Train 2–3 times a week, do many sets with few reps each and don't take every set to failure. Save your sets to see your progress."),
            ("Can I track a ladder workout?",
             "Yes. Press Enter after each step — you'll see every set, like “1 · 2 · 3 · 4 · 5”, and the total."),
        ] + SHORT_FAQ,
    },
    {
        "id": "abs", "slug": "sit-up-counter", "store": "press",
        "h1": "Sit-Up and Crunch Counter",
        "title": "Sit-Up Counter Online — Crunches, Leg Raises and More",
        "description": "Count sit-ups, crunches and leg raises: set a goal, press space or tap the screen after each rep and see how many are left. Free and works offline.",
        "plan": 30, "presets": [15, 20, 30, 50],
        "body": """
  <h2>How to count ab exercises</h2>
  <p>Put your phone next to you on the mat and tap the screen after every crunch — or keep a keyboard
  within reach and press space. The numbers are big enough to read lying down. Save each exercise
  as a separate set with Enter.</p>
{how_to}
  <h2>How many reps?</h2>
  <ul>
    <li><b>Crunches or sit-ups:</b> 3 sets of 15–30 reps.</li>
    <li><b>Lying leg raises:</b> 3 sets of 10–20.</li>
    <li><b>Bicycle crunches:</b> 3 sets of 20–40 touches (each side is one rep).</li>
  </ul>

  <h2>Form in brief</h2>
  <ul>
    <li>Keep your lower back on the floor and don't pull on your head.</li>
    <li>Lift with your abs, slowly and without jerking.</li>
    <li>Breathe out on the effort, in on the way down.</li>
  </ul>
""",
        "faq": [
            ("How many sit-ups should I do a day?",
             "3–4 sets of 15–30 reps, 3–4 times a week, is usually enough. Your abs need rest between workouts too."),
            ("Do I count each side of a bicycle crunch?",
             "Usually each elbow-to-knee touch counts as one rep. What matters is counting the same way every workout so you can see progress."),
        ] + SHORT_FAQ,
    },
    {
        "id": "burpees", "slug": "burpee-counter", "store": "berpi",
        "h1": "Burpee Counter",
        "title": "Burpee Counter Online — Never Lose Count Again",
        "description": "Free burpee counter: press space or tap after each burpee and always know how many are left. Sets add up to a total — great for 100-burpee challenges.",
        "plan": 15, "presets": [10, 15, 20, 30, 50],
        "body": """
  <h2>How to count burpees</h2>
  <p>Burpees are fast, and almost everyone loses count halfway through a set. Put the screen in front
  of you and press space or tap your phone on the floor at the end of every jump — the counter
  shows how many are left until your goal.</p>
{how_to}
  <h2>How many burpees should you do?</h2>
  <ul>
    <li><b>Beginner:</b> 3 sets of 5–10 reps, without the push-up and jump if needed.</li>
    <li><b>Intermediate:</b> 3–5 sets of 10–20.</li>
    <li><b>“100 burpees” challenge:</b> goal of 100, split into sets and save each with Enter.</li>
  </ul>

  <h2>Form in brief</h2>
  <ul>
    <li>Squat → plank → push-up → back to squat → jump up with a clap overhead.</li>
    <li>Keep your body straight in the plank, don't sag.</li>
    <li>Land softly on slightly bent knees.</li>
  </ul>
""",
        "faq": [
            ("How many burpees should I do?",
             "Start with 3 sets of 10 and add 1–2 reps per set each week. Intense workouts go up to 50–100 burpees per session."),
            ("How do I stop losing count of burpees?",
             "Press space or tap the screen right after each jump — the counter keeps track for you, and the “left” line shows how many remain."),
        ] + SHORT_FAQ,
    },
    {
        "id": "lunges", "slug": "lunge-counter", "store": "vypady",
        "h1": "Lunge Counter",
        "title": "Lunge Counter Online — Count Reps for Each Leg",
        "description": "Count lunges with one key: track reps per leg as separate sets and see your workout total. A free online lunge counter, no sign-up, works offline.",
        "plan": 20, "presets": [10, 20, 30, 40],
        "body": """
  <h2>How to count lunges</h2>
  <p>Press space or tap the screen as you return to standing. For alternating lunges, count every
  step: a goal of 20 means 10 per leg. If you do one leg first and then the other, save them as
  separate sets with Enter.</p>
{how_to}
  <h2>How many lunges should you do?</h2>
  <ul>
    <li><b>Beginner:</b> 3 sets of 8–10 per leg.</li>
    <li><b>Intermediate:</b> 3–4 sets of 12–15 per leg, optionally with dumbbells.</li>
  </ul>

  <h2>Form in brief</h2>
  <ul>
    <li>Take a step long enough for both knees to bend to about 90°.</li>
    <li>Front knee stays over the foot — not far past the toes and not caving in.</li>
    <li>Keep your torso upright and lower straight down.</li>
  </ul>
""",
        "faq": [
            ("Do I count lunges per leg or both together?",
             "Whichever you prefer — just count the same way every workout. Most people count each leg separately: save the left and right legs as separate sets with Enter."),
            ("How many lunges should a beginner do?",
             "Start with 3 sets of 8–10 reps per leg and add 2 reps a week."),
        ] + SHORT_FAQ,
    },
]
