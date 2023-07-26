from typing import Any
import js
import pyodide
import random
import time
import json

colors = ["#F00", "#0F0", "#00F", "#F0F"]
count = 10

def draw(context):
    start = time.time()
    for n in range(count):
        for x in range(10):
            for y in range(10):
                context.fillStyle = random.choice(colors)
                context.fillRect(x * 30, y * 30, 30, 30)

                context.fillStyle = "white"
                context.font = "12px Arial"
                context.fillText(f"{x}-{y}", x * 30 + 2, y * 30 + 15, 30, 30)
    if hasattr(context, "flush"):
        context.flush()
    end = time.time()
    return end - start


class BufferedContext2D():
    def __init__(self, canvas):
        self.canvas = canvas
        self.operations = []
        self.__font = ""
        self.__fillStyle = ""

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "font":
            if self.__font != value:
                self.__font = value
                self.operations.extend([2, value])
        elif name == "fillStyle":
            if self.__fillStyle != value:
                self.__fillStyle = value
                self.operations.extend([3, value])
        else:
            self.__dict__[name] = value

    def fillRect(self, x, y, w, h):
        self.operations.extend([0, x, y, w, h])

    def fillText(self, text, x, y, w, h):
        self.operations.extend([1, text, x, y, w, h])

    def flush(self):
        js.drawBufferedOperations("canvas-buffered", json.dumps(self.operations))


canvas_direct = js.document.getElementById("canvas-direct")
canvas_buffered = js.document.getElementById("canvas-buffered")

info_direct = js.document.getElementById("info-direct")
info_buffered = js.document.getElementById("info-buffered")

duration_direct = []
duration_buffered = []

def compare(n=1):
    duration_direct.append(draw(canvas_direct.getContext("2d")))
    duration_buffered.append(draw(BufferedContext2D(canvas_buffered)))

    average_direct = round(sum(duration_direct) / len(duration_direct), 3)
    average_buffered = round(sum(duration_buffered) / len(duration_buffered), 3)

    info_direct.innerText = f"Run {n} - avg: {average_direct}s"
    info_buffered.innerText = f"Run {n} - avg: {average_buffered}s ({round(average_direct / average_buffered, 1)}X faster)"

    if n < 50:
        js.setTimeout(pyodide.ffi.create_proxy(lambda: compare(n + 1)), 1)


