"""Tests for chat_reader module."""

from delware_speech.chat_reader import (
    clean_chat_utterance,
    parse_age,
    parse_participant_header,
    parse_cha_file,
)

SAMPLE_CHA = """@UTF8
@PID:\t11312/a-00088341-0
@Begin
@Languages:\teng
@Participants:\tINV Investigator, PAR Participant
@ID:\teng|Delaware|INV|||||Investigator|||
@ID:\teng|Delaware|PAR|87;00.|female|Control||Participant|||
@Media:\t01-2, audio
*INV:\tokay so we can get started .  1395_2996
*PAR:\tdo I press okay@q ?  6318_7341
*INV:\tnope I'm gonna press everything .  7899_9600
@G:\tCookie
*INV:\tplease tell me everything that you see going on .  17853_20859
*PAR:\tokay , I see two kids trying to reach the cookie jar up in [//] on the top shelf .  22301_28488
*PAR:\tthe girl is standing reaching for the cookie .  28729_31395
@G:\tCat
*PAR:\tthe cat is stuck in a big tree .  35000_39000
@End
"""


def test_clean_chat_utterance():
    # Test timestamps removal
    raw = "okay , I see two kids trying to reach the cookie jar up in [//] on the top shelf .  22301_28488"
    cleaned = clean_chat_utterance(raw)
    assert "22301_28488" not in cleaned
    assert "[//]" not in cleaned
    assert "cookie jar" in cleaned

    # Test CHAT tags removal
    raw2 = "yes . [+ exc] &*PAR:okay &~th this is nice@q"
    cleaned2 = clean_chat_utterance(raw2)
    assert "[+ exc]" not in cleaned2
    assert "&*PAR:okay" not in cleaned2
    assert "@q" not in cleaned2
    assert "this is nice" in cleaned2


def test_parse_age():
    assert parse_age("87;00.") == 87.0
    assert parse_age("72;06.") == 72.5
    assert parse_age("65") == 65.0
    assert parse_age("") is None


def test_parse_participant_header():
    header = parse_participant_header(SAMPLE_CHA, "01-2")
    assert header.corpus == "Delaware"
    assert header.age == 87.0
    assert header.sex == "female"
    assert header.diagnosis == "Control"


def test_parse_cha_file(tmp_path):
    cha_path = tmp_path / "01-2.cha"
    cha_path.write_text(SAMPLE_CHA, encoding="utf-8")

    parsed = parse_cha_file(cha_path)
    assert parsed.file_id == "01-2"
    assert parsed.participant_header.age == 87.0
    assert "Cookie" in parsed.tasks
    assert "Cat" in parsed.tasks
    assert len(parsed.tasks["Cookie"]) == 2
    assert len(parsed.tasks["Cat"]) == 1

    cookie_text = parsed.get_task_text("Cookie")
    assert "cookie jar" in cookie_text
    assert "the girl is standing" in cookie_text

    pic_tasks = parsed.get_all_picture_tasks()
    assert "Cookie" in pic_tasks
    assert "Cat" in pic_tasks
