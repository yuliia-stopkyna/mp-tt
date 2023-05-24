## MacPaw Test Task

Implementation of 3 tasks for Analytics Developer vacancy.

Each task solution is in the file of the same name (`task1.py`, `task2.py`, and
`task3.py`).

## How to run

1. Clone the project and create virtual environment

```shell
git clone https://github.com/yuliia-stopkyna/mp-tt.git
cd mp-tt
python -m venv venv
source venv/bin/activate # on MacOS
venv\Scripts\activate # on Windows
pip install -r requirements.txt
```

2. Create `.env` file in the project directory 
with your environment variables (look at `.env.example`).

3. Run each task by the following commands:
```shell
python task1.py
python task2.py
python task3.py
```

### Task 1 

Manual calculation for this task is in the comments of `task1.py`. 
I also implemented a function which prints the task answer.

**Answer:**

**Installations needed**: 12 297

**Amount of money**: $12 174

_Task completion took 30 minutes: 15 minutes for manual calculations 
and 15 minutes for converting to a function._

### Task 2

When running `task2.py`, an automated Selenium browser is opening and all links
are scraped one by one. After completing, the browser will be closed automatically.

For the first run of `task2.py` the first report `task2_report.csv` is created in the 
project directory and notification about first report creation is sent to Telegram.

For the next runs of `task2.py` the changes are evaluated and if changes detected,
corresponding message is sent to Telegram. If no changes detected, "No changes detected"
is sent.

_Task completion took 5 hours._

### Task 3

_Task completion took 4 hours._