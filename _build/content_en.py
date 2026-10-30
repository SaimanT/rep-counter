"""English pages — the main version of the site, served from the root.

The texts follow the one-rep method: when even one rep is hard, think only of the
next one, press, and let the counter remember the rest.
"""

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
    "og_tagline": "Just one rep. Press. Then just one more — the counter remembers the rest",
    "og_badges": "Free · no sign-up · works offline", "og_of": "of", "og_left": "left",
}

SHORT_FAQ = [
    ("Is it free, and does it work offline?",
     "Yes: no sign-up, no ads, and after the first visit the page works without internet. Your count is saved in the browser."),
]

CONTROLS = """
  <p><b>Controls:</b> Space +1, Backspace −1, Enter finishes a set, R resets, the 1× button hides
  the goal. On a phone, tap the screen. <a href="{home}#about">About the one-rep method</a>.</p>"""

HOW_TO = """
  <h2>How to use the counter</h2>
  <ul>
    <li><b>Set a goal</b> if you like — or don’t look at it at all (see “Just one” mode below).</li>
    <li><b>Do one rep, then press space.</b> On a phone, tap anywhere on the screen.</li>
    <li><b>Miscounted?</b> Backspace removes one rep.</li>
    <li><b>Finished a set?</b> Press Enter. The set is saved and you start again from one.
      Your sets add up below: “Sets: 5 · 4 · 4 — workout total: 13”.</li>
    <li><b>“Just one” mode</b> (the 1× button at the top) hides the goal, the countdown and the
      progress bar. Only the number of reps you’ve done stays on screen.</li>
    <li><b>On a phone</b> the same actions are buttons under the counter, and the screen stays on
      while the page is open.</li>
  </ul>"""

PAGES = [
    {
        "id": "home", "slug": "", "store": "",
        "h1": "Rep Counter",
        "title": "Rep Counter Online — Count Reps with the Spacebar",
        "description": "Free online rep counter for workouts. Set a goal, press space after each rep and see big numbers, reps left and sets. No sign-up, works offline.",
        "plan": 10, "presets": [10, 20, 50, 100],
        "body": """
  <h2>When even one rep is hard</h2>
  <p>Some days the hard part isn’t counting. It’s that every single rep takes everything you have.
  You gather all your willpower for one push-up — and then your head says “and nineteen more”.
  That thought is heavier than the rep itself.</p>
  <p>This counter is built for those days. You don’t have to hold the number in your head or look
  at how far the goal is. Do one rep. Press. The counter remembers it. Now there is only the next one.</p>

  <h2>The one-rep method</h2>
  <ol>
    <li><b>Gather yourself for one rep</b> — not for ten. Just this one.</li>
    <li><b>Do it and press.</b> That rep is done and counted. It can’t be taken away.</li>
    <li><b>Start again from “just one”.</b> Not “eight to go” — one. The counter keeps the rest.</li>
  </ol>
  <p>Ten reps done this way aren’t ten. They are one, ten times.</p>

  <h2>Why it helps</h2>
  <ul>
    <li><b>One rep feels possible.</b> A big number feels like a wall; a single rep is a step.</li>
    <li><b>Every press closes a loop.</b> You get a small finished thing, again and again — that’s
      what progress feels like.</li>
    <li><b>Nothing to keep in your head.</b> All your attention goes to the rep, not to arithmetic.</li>
    <li><b>You choose whether to see the goal.</b> On good days the “left” line pulls you to the
      finish. On hard days turn on “Just one” mode and see only what you’ve already done.</li>
  </ul>
{how_to}
  <h2>Counters for popular exercises</h2>
  <p>Each one has a ready-made goal and tips for the days when even one rep is too much:</p>
{links}
  <h2>Install it as an app</h2>
  <p>In Chrome or Edge, click “Install app” at the top of the page. On iPhone: Share → Add to Home
  Screen. It opens in its own window and works offline.</p>
""",
        "faq": [
            ("What if I can’t do even one rep?",
             "Make the rep easier, not the number bigger: push-ups against a wall, squats onto a chair, a dead hang instead of a pull-up. One easy rep beats zero, and each exercise page lists easier versions."),
            ("Should I set a goal?",
             "Yes, but you don’t have to look at it. Turn on “Just one” mode and the counter keeps the goal for you, showing only how many reps you’ve done."),
            ("Can I use it on my phone?",
             "Yes. Every tap on the screen adds one rep, and the screen stays on while the page is open."),
        ] + SHORT_FAQ,
    },
    {
        "id": "pushups", "slug": "push-up-counter", "store": "otzhimaniya",
        "h1": "Push-Up Counter",
        "title": "Push-Up Counter Online — Count Push-Ups and Sets",
        "description": "Free push-up counter: set a goal, press space or tap the screen after each push-up. See how many are left while your sets add up to a total.",
        "plan": 20, "presets": [10, 20, 30, 50, 100],
        "body": """
  <h2>One push-up at a time</h2>
  <p>Put your phone on the floor in front of your hands, or your laptop where you can see it from
  the plank. Do one push-up and tap the screen (or press space). Then think only about the next one.
  The counter holds the number, so your head is free for the push-up itself.</p>
{how_to}
  <h2>If even one push-up is hard</h2>
  <p>Make the push-up easier instead of skipping it. Each step up is real progress:</p>
  <ol>
    <li><b>Wall push-ups</b> — hands on a wall, body straight.</li>
    <li><b>Incline push-ups</b> — hands on a table, then a bench, then a low step.</li>
    <li><b>Knee push-ups</b> — on the floor, from your knees.</li>
    <li><b>Full push-ups</b> — even one is a win.</li>
  </ol>

  <h2>How many push-ups should you do?</h2>
  <p>Start with what you can do today — five clean reps are worth more than twenty sloppy ones.
  A common path: 3 sets of what you can, then add one rep per set every few workouts. For the
  “100 push-ups a day” challenge, spread the hundred over the day in small sets — the counter adds
  them up.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>A straight line from head to heels; don’t let your hips sag.</li>
    <li>Elbows at about 45° to your body, not flared out.</li>
    <li>Chest close to the floor, then arms fully straight.</li>
  </ul>
""",
        "faq": [
            ("I can’t do a single push-up. Where do I start?",
             "Start against a wall. Do one, tap, then one more. When ten wall push-ups feel easy, move your hands lower — a table, then a bench, then your knees."),
            ("How many push-ups should I do a day?",
             "Beginners do well with 10–30 spread over a few sets, trained people with 50–100. Consistency matters more than the number."),
        ] + SHORT_FAQ,
    },
    {
        "id": "squats", "slug": "squat-counter", "store": "prisedaniya",
        "h1": "Squat Counter",
        "title": "Squat Counter Online — Count Squats with One Key",
        "description": "Online squat counter with big numbers: set a goal, press space or tap after each squat, and track reps left and sets. Free and works offline.",
        "plan": 30, "presets": [15, 20, 30, 50, 100],
        "body": """
  <h2>One squat at a time</h2>
  <p>Stand facing the screen, phone in your hand or on a shelf. Squat once, stand up, tap. That’s it —
  one done. Now just the next one. The numbers are readable from a couple of metres away, so you
  never have to stop and check.</p>
{how_to}
  <h2>If even one squat is hard</h2>
  <ol>
    <li><b>Chair squats</b> — sit down onto a chair and stand back up.</li>
    <li><b>Assisted squats</b> — hold a door frame or a table for balance.</li>
    <li><b>Half squats</b> — go only as deep as feels steady.</li>
    <li><b>Full squats</b> — thighs to parallel or lower.</li>
  </ol>

  <h2>How many squats should you do?</h2>
  <p>Start with what you can do with good form — even 5 chair squats count. Then add a couple of reps
  per set every week. For a “100 squats a day” challenge, use sets of 10–25 with rest in between;
  the counter keeps the total.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>Feet shoulder-width apart, toes slightly out.</li>
    <li>Knees follow your toes and don’t cave in.</li>
    <li>Back straight, heels on the floor.</li>
  </ul>
""",
        "faq": [
            ("Squats hurt my knees. What can I do?",
             "Try chair squats with a shallower depth and keep your knees in line with your toes. If pain continues, check with a doctor or physiotherapist."),
            ("How many squats should I do a day?",
             "30–50 over a few sets is a good start; trained people do 100 or more. Increase gradually."),
        ] + SHORT_FAQ,
    },
    {
        "id": "pullups", "slug": "pull-up-counter", "store": "podtyagivaniya",
        "h1": "Pull-Up Counter",
        "title": "Pull-Up Counter Online — Track Sets and Total Reps",
        "description": "Count pull-ups set by set and see your workout total. Press space or tap the screen to add reps. A free online pull-up counter that works offline.",
        "plan": 10, "presets": [5, 8, 10, 15, 20],
        "body": """
  <h2>One pull-up at a time</h2>
  <p>Pull-ups are where “just one” matters most: for many people one rep is the whole set. Do one,
  drop down, tap the counter. Rest if you need to. Then one more. Save each set with Enter, and the
  counter adds up how many pull-ups you did in the whole workout — often more than you expected.</p>
{how_to}
  <h2>If even one pull-up is hard</h2>
  <ol>
    <li><b>Dead hang</b> — just hang from the bar; count seconds or hangs.</li>
    <li><b>Scapular pulls</b> — from the hang, pull your shoulders down without bending your arms.</li>
    <li><b>Negatives</b> — jump or step up to the top and lower yourself slowly.</li>
    <li><b>Assisted pull-ups</b> — with a band or a foot on a chair.</li>
  </ol>

  <h2>How many pull-ups should you do?</h2>
  <p>Many short sets beat one hard one. If you can do 1–3, do 5–6 sets of a single rep with rest in
  between. A ladder (1, 2, 3…) works well too — save each step with Enter.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>Start from a dead hang with straight arms, no swinging.</li>
    <li>Chin above the bar.</li>
    <li>Drive your elbows down; don’t just bend your arms.</li>
  </ul>
""",
        "faq": [
            ("I can’t do a single pull-up. How do I get my first one?",
             "Practise negatives and dead hangs 2–3 times a week. Count every negative as a rep — they build the strength for the first real pull-up."),
            ("Can I track a ladder workout?",
             "Yes. Press Enter after each step — you’ll see every set, like “1 · 2 · 3 · 4”, and the total."),
        ] + SHORT_FAQ,
    },
    {
        "id": "abs", "slug": "sit-up-counter", "store": "press",
        "h1": "Sit-Up and Crunch Counter",
        "title": "Sit-Up Counter Online — Crunches, Leg Raises and More",
        "description": "Count sit-ups, crunches and leg raises: set a goal, press space or tap the screen after each rep and see how many are left. Free and works offline.",
        "plan": 30, "presets": [15, 20, 30, 50],
        "body": """
  <h2>One crunch at a time</h2>
  <p>Put your phone on the mat next to you. Do one crunch, tap the screen, lie back. Then only the
  next one. The numbers are big enough to read lying down, and you don’t have to count under your
  breath while your abs are burning.</p>
{how_to}
  <h2>If even one sit-up is hard</h2>
  <ol>
    <li><b>Dead bug</b> — on your back, slowly lower the opposite arm and leg.</li>
    <li><b>Partial crunches</b> — lift only your shoulder blades off the floor.</li>
    <li><b>Seated knee raises</b> — on the edge of a chair, pull your knees up.</li>
    <li><b>Full sit-ups or leg raises</b> — when the above feel easy.</li>
  </ol>

  <h2>How many reps?</h2>
  <p>3 sets of what you can do with control, 3–4 times a week, then add a few reps per set. Save each
  exercise as its own set with Enter.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>Lower back on the floor; don’t pull on your head.</li>
    <li>Lift with your abs, slowly, without jerking.</li>
    <li>Breathe out on the effort.</li>
  </ul>
""",
        "faq": [
            ("Sit-ups strain my neck. What should I do?",
             "Switch to partial crunches or dead bugs and keep your chin slightly tucked. Your hands support your head; they don’t pull it."),
            ("How many sit-ups should I do a day?",
             "3–4 sets of 15–30 controlled reps, 3–4 times a week, is usually enough. Your abs need rest days too."),
        ] + SHORT_FAQ,
    },
    {
        "id": "burpees", "slug": "burpee-counter", "store": "berpi",
        "h1": "Burpee Counter",
        "title": "Burpee Counter Online — Never Lose Count Again",
        "description": "Free burpee counter: press space or tap after each burpee and always know how many are left. Sets add up to a total — great for 100-burpee challenges.",
        "plan": 15, "presets": [10, 15, 20, 30, 50],
        "body": """
  <h2>One burpee at a time</h2>
  <p>Burpees are where the head gives up before the body: “fifteen?!” Don’t think about fifteen.
  Do one, stand up, tap the phone on the floor. Breathe. Now just one more. The counter keeps the
  score, and “Just one” mode hides the goal if it feels too far.</p>
{how_to}
  <h2>If even one burpee is hard</h2>
  <ol>
    <li><b>Step-back burpee</b> — step back into the plank and step in again, no jump.</li>
    <li><b>Incline burpee</b> — hands on a bench or a low table.</li>
    <li><b>No push-up</b> — plank only, then back up.</li>
    <li><b>Full burpee</b> — with the push-up and the jump.</li>
  </ol>

  <h2>How many burpees should you do?</h2>
  <p>Start with sets of 5 at an easy version and add a rep or two each week. For a 100-burpee
  challenge, split it into small sets and save each one with Enter.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>Squat → plank → (push-up) → back to squat → jump.</li>
    <li>Keep your body straight in the plank.</li>
    <li>Land softly on slightly bent knees.</li>
  </ul>
""",
        "faq": [
            ("I’m out of breath after two burpees. Is that normal?",
             "Yes — burpees are hard on everyone. Use the step-back version and rest between reps; one at a time still counts."),
            ("How many burpees should I do?",
             "Start with 3 sets of 5–10 and add 1–2 reps per set each week. Intense workouts go up to 50–100."),
        ] + SHORT_FAQ,
    },
    {
        "id": "lunges", "slug": "lunge-counter", "store": "vypady",
        "h1": "Lunge Counter",
        "title": "Lunge Counter Online — Count Reps for Each Leg",
        "description": "Count lunges with one key: track reps per leg as separate sets and see your workout total. A free online lunge counter, no sign-up, works offline.",
        "plan": 20, "presets": [10, 20, 30, 40],
        "body": """
  <h2>One lunge at a time</h2>
  <p>Step, lower, come back up, tap. One done. With alternating lunges every step counts, so a goal
  of 20 means 10 per leg. If you do one leg first and then the other, save them as separate sets
  with Enter — and still think only about the next step.</p>
{how_to}
  <h2>If even one lunge is hard</h2>
  <ol>
    <li><b>Supported split squat</b> — hold a chair or a wall, feet staggered, move only up and down.</li>
    <li><b>Short reverse lunge</b> — a small step back, shallow depth.</li>
    <li><b>Full reverse lunge</b> — both knees close to 90°.</li>
    <li><b>Forward or walking lunges</b> — the hardest version.</li>
  </ol>

  <h2>How many lunges should you do?</h2>
  <p>Start with 2–3 sets of 5–8 per leg and add two reps a week. Balance first, numbers second.</p>

  <h2>Form in brief</h2>
  <ul>
    <li>A step long enough for both knees to bend to about 90°.</li>
    <li>Front knee over the foot, not caving in.</li>
    <li>Torso upright; lower straight down.</li>
  </ul>
""",
        "faq": [
            ("Do I count lunges per leg or both together?",
             "Whichever you prefer — just count the same way every workout. Most people save each leg as its own set with Enter."),
            ("I lose my balance in lunges. What helps?",
             "Hold a chair or a wall and start with split squats, where your feet don’t move. Balance improves quickly with practice."),
        ] + SHORT_FAQ,
    },
]
