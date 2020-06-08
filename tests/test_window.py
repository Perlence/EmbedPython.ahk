import subprocess
from functools import partial

import ahk


def test_windows(child_ahk):
    def windows():
        import ahk
        import sys

        ahk.hotkey("F24", sys.exit)

        @ahk.set_timer(countdown=0.1)
        def win1():
            ahk.message_box("win1", title="win1")

        @ahk.set_timer(countdown=0.2)
        def win2():
            ahk.message_box("win2", title="win2")

        ahk.sleep(1)
        sys.exit()

    child_ahk.popen_code(windows)
    ahk.set_win_delay(None)

    assert repr(ahk.windows) == "Windows()"

    msg_boxes = ahk.windows.filter(exe="AutoHotkey.exe")
    assert repr(msg_boxes) == "Windows(exe='AutoHotkey.exe')"

    wait_result = msg_boxes.wait(timeout=1)
    assert wait_result is not None
    assert isinstance(wait_result, ahk.Window)
    assert msg_boxes.wait(title="win1", timeout=1).title == "win1"
    assert msg_boxes.wait(title="win2", timeout=1).title == "win2"

    assert len(msg_boxes) == 2
    ahk_window_list = list(msg_boxes)
    assert ahk_window_list != []
    top = msg_boxes.first()
    assert ahk_window_list[0] == top
    assert ahk_window_list[-1] == msg_boxes.last()
    assert repr(top) == f"Window(id={top.id})"

    assert len(msg_boxes.filter(title="win2")) == 1
    assert msg_boxes.filter(title="win2").first().title == "win2"
    assert len(msg_boxes.exclude(title="win2")) == 1
    assert msg_boxes.exclude(title="win2").first().title == "win1"

    assert all(mb.is_restored for mb in msg_boxes)
    msg_boxes.minimize_all()
    assert all(mb.is_minimized for mb in msg_boxes)
    msg_boxes.maximize_all()
    assert all(mb.is_maximized for mb in msg_boxes)
    msg_boxes.restore_all()
    assert all(mb.is_restored for mb in msg_boxes)

    win1 = msg_boxes.first(title="win1")
    assert win1
    assert win1.exists

    win2 = msg_boxes.first(title="win2")
    win1.activate()
    assert not win2.is_active

    assert msg_boxes.wait_close(timeout=0.1) is False
    msg_boxes.close_all()
    assert msg_boxes.wait_close() is True
    assert not msg_boxes.first()

    ahk.send("{F24}")


def test_window(child_ahk):
    def window():
        import ahk
        import sys

        ahk.hotkey("F24", sys.exit)
        ahk.message_box("win1", title="win1")

    child_ahk.popen_code(window)
    ahk.set_win_delay(None)

    win1 = ahk.windows.wait(title="win1", exe="AutoHotkey.exe")
    assert win1

    _, _, width, height = win1.rect
    x, y = win1.position
    win1.y += 100
    assert win1.y == y + 100
    win1.x = win1.y
    assert win1.x == win1.y
    win1.height += 100
    assert win1.height == height + 100
    win1.height = win1.width
    assert win1.height == win1.width

    assert win1.title == "win1"
    win1.title = "win111"
    assert win1.title == "win111"

    assert win1.pid > 0

    assert ahk.windows.first(class_name="totally no such window").opacity is None
    assert win1.opacity is None
    win1.opacity = 128
    assert win1.opacity == 128
    win1.opacity = None
    assert win1.opacity is None

    assert win1.transparent_color is None
    win1.transparent_color = (255, 255, 255)
    assert win1.transparent_color == (255, 255, 255)
    win1.transparent_color = None
    assert win1.transparent_color is None

    win1.hide()
    win1.show()
    win1.maximize()
    assert win1.is_maximized
    win1.restore()
    assert win1.is_restored
    win1.minimize()
    assert win1.is_minimized
    win1.restore()
    assert win1.is_restored
    assert win1.wait_active() is True
    assert win1.wait_close(timeout=0.1) is False

    ahk.send("{F24}")


def test_status_bar():
    notepad_proc = subprocess.Popen(["notepad.exe"])
    notepad_win = ahk.windows.wait(pid=notepad_proc.pid)
    assert notepad_win

    assert "Ln 1, Col 1" in notepad_win.get_status_bar_text(2)

    notepad_win.send("q")
    ahk.sleep(0)
    assert "Ln 1, Col 2" in notepad_win.get_status_bar_text(2)

    ahk.set_timer(partial(notepad_win.send, "q"), countdown=0.5)
    assert notepad_win.wait_status_bar("  Ln 1, Col 3", part=2, timeout=1) is True
    assert notepad_win.get_status_bar_text(2) == "  Ln 1, Col 3"

    notepad_proc.terminate()