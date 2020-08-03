# dataeng-code-challenge

Rune Labs coding challenge for data engineers.


## Summary

You are part of a team building an app for dental hygiene enthusiasts. The app
talks to a *smart toothbrush* via Bluetooth, and records information about
each user's brushing sessions. The raw data is collected into files on the
user's phone, and shipped off in batches to your team's cloud backend.

The toothbrush streams a few different types of data, and we'll refer to all
the data collected during a single 1-2min brushing session as a **dataset**.

Your job is to use Python to parse the individual data points from each
dataset, and write them into your team's time-series database, LlamaDB.

This is a little tricky, so read carefully before getting started!

### Datasets

A brushing dataset is made up of two **streams**: files containing "points"
or "events" of a specific type. Hereafter, we'll refer to "events" and
"points" interchangeably.


#### Stream 1: Tooth brushing progress

This is a CSV file where each line is an update event from the toothbrush
telling us:
1. Time when the update event was recorded, in a strange format we'll call a
   **tick**. Explained below.
2. Which tooth the user was brushing at the time. This is the integer *index*
   of the tooth, 0 through however many teeth humans have these days.
3. The percent clean, as a floating point `0.0` (0%) through `1.0` (100%). I
   told you the toothbrush was smart!

Check out the sample stream in `sample/brushing.csv`

A **tick** is how the toothbrush keeps track of time internally. It should
have a normal clock, but it doesn't. Instead, it counts starting from `0` when
the user starts a new brushing session. So `1` means one tick after brushing
began, `42` means 42 ticks after start, and so on.

Ideally these events should come in at a regular interval, and will for the
most part, but hardware can fail and things can go wrong.

How long is a tick in regular human time? Read on!


#### Stream 2: Toothbrush settings

This is a file with a slightly custom format. It contains one JSON object per
line. *The stream as a whole is not valid JSON, but each individual line is.*

Each JSON object represent an **update** ("diff") to the current *state* of
the toothbrush. The toothbrush keeps track of two things in its internal
state. Whenever one or both change, it spits out an event containing the
following:
1. The current time as a UNIX timestamp (seconds since UNIX epoch, with
   fraction for sub-second precision)
2. The current tick (same concept as with Stream 1)
3. Current battery level: `0.0` (0%) through `1.0` (100%)
4. Current tick interval, in seconds.

Check out the sample stream in `sample/settings.jsonlines`

The very first toothbrush settings event will contain the initial state of
both battery level and tick interval. Subsequent events may contain only
one, the other, or again both.

Every settings event will always have the current time as both a UNIX
timestamp and tick-time. Ticks are also aligned between the two streams, so
a settings event at tick `16` and tooth brushing data point at tick `16`
occurred effectively at the exact same time.

Whenever you get a new update event to a state (e.g. tick interval or battery
level), assume that value will remain the same until the next update event you
read, if any. In other words, if you read that the tick interval is 0.25 at
tick 6, and your next tick interval update event is not until tick 56, assume
all ticks in between are at that tick interval. Same with battery.


### The Challenge

1. For each dataset, for each stream, insert each event into LlamaDB.
    1. The details of interacting with LlammaDB's API are below.
    2. Insert every piece of information you encounter, every detail may be
       useful for us to have, so no need to picky now.
    3. Assume this is basically a NoSQL-like database. There is no predefined
       schema, for every "column" you store, pick a name. We'll roll with
       whatever you choose, as long as it's not too far fetched.
2. Keep track of the following ingestion statistics to report at the end of
   each job (see `Job` interface):
    1. Start time, *inclusive*, of the dataset. This is the UNIX timestamp of
       the very first event (of either type).
    2. End time, *exclusive*, of the dataset. This is *one tick after* the
       UNIX timestamp of the very last event (of either type).
    3. Total number of seconds of **tooth brushing progress data lost**.
       Don't expect data sampling to be perfect. Whenever you detect that the
       stream "skips" point(s), record how much real time was lost.
3. You are NOT allowed to parse the entire stream (either one) into memory.
    1. This will run on a server with 512MB of memory, but a stream can be
       tens of gigabytes total (I know, its just brushing data, there's a leap
       imagination)
4. LlamaDB only accepts UNIX timestamps, but only stream #2 has them.
    1. You will need to figure out how to iterate through the two streams
       together to correctly translate ticks to UNIX timestamps.
    2. Remember, you can only read the streams once, and can't go back!


#### Hints

1. We can't stress this one enough: DON'T TRUST INPUT DATA.
    1. Expect the data to conform to the specs above most of the time, but
       also expect complete garbage, and everything in between.
    2. Code defensively so that your code catches all possible errors and
       either recovers by skipping corrupt data segments, or reports the input
       data is unsalvageable and moves on to the next.
2. Assume the contents of each stream comes over the network. This means two
   things:
    1. You can only read byte data in sequence. You can't scan back and forth
       like with a local file.
    2. Network connection fail unexpectedly. Expect exceptions to interrupt
       your processing, and handle them gracefully so the whole thing doesn't
       crash. See API details below.
3. Assume your calls to LlamaDB are over a network API.
    1. This mean the same thing as with your input streams, it can fail.
       See API details below.
4. A lot of this challenge is devil in the details. Read carefully and make no
   assumptions.
    1. Any question you may have of the form "can I assume that...", the
       answer is NO. That said, limit your fantasies to the plausible,
       otherwise you'll be coding this all week.
    2. Any question you may have in the form of "am I allowed to use..." when
       it comes to Python features, libraries, etc, is YES. That said, your
       goal is to get us to hire you, and we're not impressed by finding a
       clever way around actually doing any work.


### Scoring and Rules

Put your solution in `solution/main.py`. You may add as many other modules
under `solution/` as you like (in fact we encourage you, to organize your
code). Just make sure you keep `main.py` and `process_next_job()`, which is
your entrypoint.

Put your unit tests in `tests/*.py`. Testing is very important to your score.

Your solution won't be evaluated as a black box. Here's what we're looking
for:
1. Code organization and readability
2. Unit tests
3. Documentation and comments
4. Fault tolerance
5. Good version control etiquette (frequent commits with checkpoints). Treat
   this is a real GitHub project where you are collaborating with others.

Please write your code in Python 3.

You may use any 3rd party libraries/packages you like. Try to keep within Pip
packages for our sake (we'll have to run your code, and we don't want to have
to compile anything).

Feel free to Google the s^#t out of any part of this challenge, use
StackOverflow, whatever. It's what we do day-to-day, so you can too. However,
be prepared to explain your code in detail, so if you do copy+paste most of
it, you better spend the time you saved understanding what's actually going
on.


## APIs

The APIs represent parts of this fictitious job processing framework that are
done for you. We have provided classes that represent the clients and
components you need, but will notice their methods are empty! However, their
documentation comments are NOT.

Write your code against the described behavior of the framework classes. Your
unit tests should be where you test different edge cases with mocks. Don't
rely solely on manually running your code.


### Job API

All the work of receiving and managing the raw datasets is done. There's a
neat queue where jobs are queued for processing, and our job is to pull out
one job at a time, do it, commit, and repeat.

The **Job Queue** interface is available in `framework/queue.py`.

You will use the queue client to pull new jobs. Pull one job at a time, and
process it per the challenge instructions without crashing. If you want to
show off and do some multithreaded parallel processing, that's fine, but we
suggest you nail the basic synchronous case first.

```python
# This try-catch is a freebie. You'll have to figure out
# all the other places where error checking is necessary
# yourself.
try:
    job = JobQueue.poll()
except IOError as error:
    log.failure("Failed to get a job", exc=error)

...do stuff...

job.commit()
```

Each job returned by the queue is an instance of `framework/job.py`.

`job.dataset` is an instance of `framework/dataset.py`

`dataset.brushing` is an instance of `framework/stream.py`

`dataset.settings` is an instance of `framework/stream.py`

Use the framework modules as your official documentation. They're well
documented, and your code should strive to be the same.


### LlamaDB API

Whenever you're ready to write a new data point from your code, use the
LlamaDB client to connect and insert your data.

The LlamaDB client can be found in `framework/llamadb.py`.

To make sure we know to which user data belongs, be sure to include the
following with each inserted event:
1. The measurement, which is either `brushing` for brushinng data, or
   `settings` for settings events.
2. The toothbrush ID as the `toothbrush_id` tag value

```python
db = LlamaDB.connect()

... enter a loop to do stuff ...

    db.insert(
        measurement='brushing',
        timestamp=1595896877.6374981,
        tags={
            'toothbrush_id': job.dataset.toothbrush_id,
            'other_tag': 'other_tag_value',
        },
        fields={
            'some_field': 3,
            'some_other_field': 0.5,
        }
    )

... do more stuff and exit loop ...

db.close()
```


