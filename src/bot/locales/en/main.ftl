## Menu
start-welcome =
    🌦 <b>Weather bot</b>

    Type a city name or pick one from favorites.
    Hint: in any chat, type <code>@{ $botname } London</code> — I'll send a card right there.
start-welcome-no-name =
    🌦 <b>Weather bot</b>

    Type a city name or pick one from favorites.

menu-find = 🔍 Find city
menu-favorites = ⭐ Favorites
menu-settings = ⚙️ Settings

back = ⬅️ Back
cancel = ✖️ Cancel

## Find
find-prompt = Enter a city name (e.g., "London", "Tokyo", "São Paulo"):
find-results = Here's what I found. Pick one:
find-empty = Nothing matched "{ $query }".
find-error = ⚠️ Couldn't reach OpenWeather. Check the API key and try again.

## Favorites
favorites-empty = No favorites yet. Find a city and add it.
favorite-added = ⭐ Added to favorites.
favorite-removed = 🗑 Removed from favorites.
favorite-exists = This city is already in favorites.

## Weather card
card-header = { $emoji } <b>{ $name }{ $flag }</b>
card-now = Now: <b>{ $temp }</b> (feels like { $feels })
card-desc = { $desc }
card-details =
    💧 Humidity: { $humidity }%
    💨 Wind: { $wind } { $wind_unit }
    🔽 Pressure: { $pressure } hPa
card-forecast-header = <b>5-day forecast</b>
card-forecast-line = { $emoji } <b>{ $date }</b>: { $tmin } … { $tmax }, { $desc }
updated-at = Updated: { $time }

btn-favorite-add = ⭐ Add to favorites
btn-favorite-remove = 🗑 Remove from favorites
btn-refresh = 🔄 Refresh
btn-forecast = 📅 5-day forecast

## Settings
settings-title = ⚙️ <b>Settings</b>
settings-language = 🌐 Language
settings-units = 🌡 Units

units-metric = 🟦 Metric (°C, m/s)
units-imperial = 🟧 Imperial (°F, mph)
units-saved = ✅ Saved.

language-ru = 🇷🇺 Русский
language-en = 🇬🇧 English
language-set = 🌐 Language switched.

## Inline
inline-title = { $emoji } { $name }{ $flag } — { $temp }
inline-desc = { $desc }. Feels like { $feels }. Humidity { $humidity }%.
inline-empty-title = Type a city name
inline-empty-desc = e.g., London, Tbilisi, New York.

## Misc
confirm-saved = ✅ Saved.
confirm-deleted = 🗑 Deleted.
error-generic = ⚠️ Something went wrong. Try again.
