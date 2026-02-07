#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from filelock import FileLock
from typing import Optional, List
import os
import re
import pathlib

# ===== Configuration =====
WORDS_FILE = "/Users/Mac/Desktop/Progrow/Notes/words.md"
AUTH_TOKEN = "f8a3b7e6d2c1a0b9e8f7d6c5b4a32109"

TASK_PATTERN = re.compile(r'^(\s*-\s*\[)([xX ])(\]\s*(.*))$')

def _read_words_file() -> str:
    if not os.path.exists(WORDS_FILE):
        return ""
    with open(WORDS_FILE, "r", encoding="utf-8") as fp:
        return fp.read()

def _write_words_file(content: str):
    pathlib.Path(os.path.dirname(WORDS_FILE)).mkdir(parents=True, exist_ok=True)
    lock = FileLock(WORDS_FILE + ".lock")
    with lock:
        with open(WORDS_FILE, "w", encoding="utf-8") as fp:
            fp.write(content)

def _parse_words(text: str) -> List[dict]:
    words = []
    for i, line in enumerate(text.splitlines()):
        m = TASK_PATTERN.match(line)
        if m:
            checked = m.group(2).lower() == "x"
            word = m.group(4).strip()
            words.append({"index": i, "word": word, "checked": checked})
    return words

# ===== FastAPI =====
app = FastAPI(title="Words Memorization Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _auth_or_403(x_auth: Optional[str]):
    if x_auth != AUTH_TOKEN:
        raise HTTPException(403, detail="Forbidden")

class WordsResp(BaseModel):
    file: str
    exists: bool
    total: int
    checked: int
    unchecked: int
    words: List[dict]

@app.get("/words", response_model=WordsResp)
def get_words(x_auth: Optional[str] = Header(None)):
    _auth_or_403(x_auth)
    text = _read_words_file()
    exists = os.path.exists(WORDS_FILE)
    words = _parse_words(text)
    checked = sum(1 for w in words if w["checked"])
    return WordsResp(
        file=WORDS_FILE,
        exists=exists,
        total=len(words),
        checked=checked,
        unchecked=len(words) - checked,
        words=words,
    )

class ToggleReq(BaseModel):
    index: int  # line index in the file

@app.post("/words/toggle")
def toggle_word(req: ToggleReq, x_auth: Optional[str] = Header(None)):
    _auth_or_403(x_auth)
    text = _read_words_file()
    lines = text.splitlines()
    if req.index < 0 or req.index >= len(lines):
        raise HTTPException(400, detail="Invalid line index")
    line = lines[req.index]
    m = TASK_PATTERN.match(line)
    if not m:
        raise HTTPException(400, detail="Line is not a task")
    if m.group(2).lower() == "x":
        lines[req.index] = f"{m.group(1)} {m.group(3)}"
    else:
        lines[req.index] = f"{m.group(1)}x{m.group(3)}"
    _write_words_file("\n".join(lines) + ("\n" if text.endswith("\n") else ""))
    return JSONResponse({"ok": True})

class AddWordsReq(BaseModel):
    words: List[str]

@app.post("/words/add")
def add_words(req: AddWordsReq, x_auth: Optional[str] = Header(None)):
    _auth_or_403(x_auth)
    text = _read_words_file()
    new_lines = [f"- [ ] {w.strip()}" for w in req.words if w.strip()]
    if not new_lines:
        raise HTTPException(400, detail="No words provided")
    if text and not text.endswith("\n"):
        text += "\n"
    text += "\n".join(new_lines) + "\n"
    _write_words_file(text)
    return JSONResponse({"ok": True, "added": len(new_lines)})
