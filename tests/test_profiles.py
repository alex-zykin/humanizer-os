from humanizer_os.profiles import build_voice_profile


def test_builds_observable_voice_profile() -> None:
    profile = build_voice_profile(
        [
            "I tested the parser. It broke twice, so I rolled it back.\n\nYou can reproduce it with the sample file."
        ],
        locale="en",
    )
    assert profile.locale == "en"
    assert profile.words > 10
    assert profile.sentences >= 3
    assert profile.first_person_per_1000 > 0
    assert profile.second_person_per_1000 > 0
