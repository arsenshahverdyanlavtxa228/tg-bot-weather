from bot.services.i18n import I18n


def test_locales_discovered(i18n: I18n) -> None:
    assert set(i18n.available) == {"ru", "en"}


def test_interpolation(i18n: I18n) -> None:
    en = i18n.get("en")
    text = en(
        "card-details",
        humidity=50,
        wind=5.0,
        wind_unit="m/s",
        pressure=1013,
    )
    # Fluent applies CLDR number formatting, so 1013 may be rendered as "1,013"
    # or "1 013" depending on locale. Check the unit markers instead.
    assert "50" in text
    assert "m/s" in text
    assert "hPa" in text
