"""Test the translations API."""

from pathlib import Path

import pytest

from napari.utils.translations import (
    DEFAULT_LOCALE,
    _is_valid_locale,
    translator,
)

TEST_LOCALE = "es_CO"
HERE = Path(__file__).parent
TEST_LANGUAGE_PACK_PATH = HERE / "napari-language-pack-es_CO"


def _get_display_name(
    locale: str, display_locale: str = DEFAULT_LOCALE
) -> str:
    """
    Return the language name to use with a `display_locale` for a given language locale.
    Parameters
    ----------
    locale: str
        The language name to use.
    display_locale: str, optional
        The language to display the `locale`.
    Returns
    -------
    str
        Localized `locale` and capitalized language name using `display_locale` as language.
    """
    # This is a dependency of the language packs to keep out of core
    import babel

    locale = locale if _is_valid_locale(locale) else DEFAULT_LOCALE
    display_locale = (
        display_locale if _is_valid_locale(display_locale) else DEFAULT_LOCALE
    )
    loc = babel.Locale.parse(locale)
    return loc.get_display_name(display_locale).capitalize()


es_CO_po = r"""msgid ""
msgstr ""
"Project-Id-Version: \n"
"POT-Creation-Date: 2021-02-18 19:00\n"
"PO-Revision-Date:  2021-02-18 19:00\n"
"Language-Team: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"X-Generator: Poedit 2.4.2\n"
"Last-Translator: \n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
"Language: es_CO\n"

#: /
msgid "MORE ABOUT NAPARI"
msgstr "Más sobre napari"
"""

es_CO_mo = (
    b"\xde\x12\x04\x95\x00\x00\x00\x00\x02\x00\x00\x00\x1c\x00\x00\x00,"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00<\x00"
    b"\x00\x00\x11\x00\x00\x00=\x00\x00\x00[\x01\x00\x00O\x00\x00\x00\x11"
    b"\x00\x00\x00\xab\x01\x00\x00\x00"
    b"MORE ABOUT NAPARI\x00Project-Id-Version:  \n"
    b"Report-Msgid-Bugs-To: EMAIL@ADDRESS\n"
    b"POT-Creation-Date: 2021-02-18 19:00+0000\n"
    b"PO-Revision-Date: 2021-02-18 19:00+0000\n"
    b"Last-Translator: \nLanguage: es_CO\nLanguage-Team: \n"
    b"Plural-Forms: nplurals=2; plural=(n != 1)\nMIME-Version: 1.0\n"
    b"Content-Type: text/plain; charset=utf-8\nContent-Transfer-Encoding: 8bit"
    b"\nGenerated-By: Babel 2.9.0\n\x00M\xc3\xa1s sobre napari\x00"
)


@pytest.fixture
def trans(tmp_path):
    """A good plugin that uses entry points."""
    distinfo = tmp_path / "napari_language_pack_es_CO-0.1.0.dist-info"
    distinfo.mkdir()
    (distinfo / "top_level.txt").write_text('napari_language_pack_es_CO')
    (distinfo / "entry_points.txt").write_text(
        "[napari.languagepack]\nes_CO = napari_language_pack_es_CO\n"
    )
    (distinfo / "METADATA").write_text(
        "Metadata-Version: 2.1\n"
        "Name: napari-language-pack-es-CO\n"
        "Version: 0.1.0\n"
    )
    pkgdir = tmp_path / 'napari_language_pack_es_CO'
    msgs = pkgdir / 'locale' / 'es_CO' / 'LC_MESSAGES'
    msgs.mkdir(parents=True)
    (pkgdir / '__init__.py').touch()
    (msgs / "napari.po").write_text(es_CO_po)
    (msgs / "napari.mo").write_bytes(es_CO_mo)

    from napari_plugin_engine.manager import temp_path_additions

    with temp_path_additions(tmp_path):
        # Load translator and force a locale for testing
        translator._set_locale(TEST_LOCALE)
        return translator.load()


def test_get_display_name_valid():
    assert _get_display_name("en", "en") == "English"
    assert _get_display_name("en", "es") == "Inglés"
    assert _get_display_name("en", "es_CO") == "Inglés"
    assert _get_display_name("en", "fr") == "Anglais"
    assert _get_display_name("es", "en") == "Spanish"
    assert _get_display_name("fr", "en") == "French"


def test_get_display_name_invalid():
    assert _get_display_name("en", "foo") == "English"
    assert _get_display_name("foo", "en") == "English"
    assert _get_display_name("foo", "bar") == "English"


def test_is_valid_locale_valid():
    assert _is_valid_locale("en")
    assert _is_valid_locale("es")
    assert _is_valid_locale("es_CO")


def test_is_valid_locale_invalid():
    assert not _is_valid_locale("foo_SPAM")
    assert not _is_valid_locale("bar")


def test_locale_valid_singular(trans):
    # Test singular method
    expected_result = "Más sobre napari"
    result = trans.gettext("MORE ABOUT NAPARI")
    assert result == expected_result

    # Test singular method shorthand
    result = trans._("MORE ABOUT NAPARI")
    assert result == expected_result


def test_locale_invalid():
    with pytest.warns(UserWarning):
        translator._set_locale(TEST_LOCALE)
        trans = translator.load()
        result = trans._("BOO")
        assert result == "BOO"


def test_locale_n_runs(trans):
    # Test plural method
    n = 2
    string = "MORE ABOUT NAPARI"
    plural = "MORE ABOUT NAPARIS"
    result = trans.ngettext(string, plural, n)
    assert result == plural

    # Test plural method shorthand
    result = trans._n(string, plural, n)
    assert result == plural


def test_locale_p_runs(trans):
    # Test context singular method
    context = "context"
    string = "MORE ABOUT NAPARI"
    result = trans.pgettext(context, string)
    assert result == string

    # Test context singular method shorthand
    result = trans._p(context, string)
    assert result == string


def test_locale_np_runs(trans):
    # Test plural context method
    n = 2
    context = "context"
    string = "MORE ABOUT NAPARI"
    plural = "MORE ABOUT NAPARIS"
    result = trans.npgettext(context, string, plural, n)
    assert result == plural

    # Test plural context method shorthand
    result = trans._np(context, string, plural, n)
    assert result == plural
