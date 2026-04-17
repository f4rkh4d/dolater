# dolater

three slots. that's the whole tool.

a command-line todo list that refuses a fourth item. if the list is full you have to finish one or drop one before adding anything else. no backlog, no "maybe next week" bucket, no snooze. the friction is the feature — i wrote it for myself because my old todo file had 47 items and i was lying to all of them.

## install

```
pip install git+https://github.com/f4rkh4d/dolater
```

needs python 3.10+. sqlite ships with python so there's nothing else to set up.

## use it

```
$ dolater add "fix the auth race"
+ added slot 1 · fix the auth race
 1 · fix the auth race
 2 · —
 3 · —

$ dolater add "reply to morgan"
$ dolater add "finish the cram readme"
$ dolater add "bake a loaf"
! blocked — list is full

$ dolater done 2
done: reply to morgan
 1 · fix the auth race
 2 · —
 3 · finish the cram readme

$ dolater add "bake a loaf"
 1 · fix the auth race
 2 · bake a loaf
 3 · finish the cram readme
```

other commands: `dolater ls`, `dolater drop <n>`, `dolater log --tail 20`, `dolater clear`. `dolater --help` lists all of them.

state lives at `~/.dolater/state.db`. one sqlite file, two tables (`items`, `log`). you can `sqlite3` into it if something looks off, which has happened to me once or twice.

## why three

four is where i stop picking. with three slots i either finish something or i honestly admit one of them was never real and drop it. nothing clever about the number, it just works on me.

## dev

python 3.10+, sqlite3 ships with python, tests with pytest. `pip install -e ".[dev]" && pytest -q` and you're set. ci runs on ubuntu and macos across 3.10 / 3.11 / 3.12. haven't tested on windows, probably fine but don't quote me.

## license

mit.
