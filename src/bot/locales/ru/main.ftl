## Menu
start-welcome =
    🌦 <b>Погодный бот</b>

    Напиши название города или выбери из избранного.
    Хинт: в любом чате набери <code>@{ $botname } Москва</code> — пришлю карточку прямо туда.
start-welcome-no-name =
    🌦 <b>Погодный бот</b>

    Напиши название города или выбери из избранного.

menu-find = 🔍 Найти город
menu-favorites = ⭐ Избранное
menu-settings = ⚙️ Настройки

back = ⬅️ Назад
cancel = ✖️ Отмена

## Find
find-prompt = Введи название города (например, «Москва», «London», «São Paulo»):
find-results = Нашёл несколько вариантов. Выбери:
find-empty = По запросу «{ $query }» ничего не нашлось.
find-error = ⚠️ Не получилось сходить в OpenWeather. Проверь ключ и попробуй ещё раз.

## Favorites
favorites-empty = Избранное пустое. Найди город и добавь его.
favorite-added = ⭐ Добавлено в избранное.
favorite-removed = 🗑 Удалено из избранного.
favorite-exists = Этот город уже в избранном.

## Weather card
card-header = { $emoji } <b>{ $name }{ $flag }</b>
card-now = Сейчас: <b>{ $temp }</b> (ощущается как { $feels })
card-desc = { $desc }
card-details =
    💧 Влажность: { $humidity }%
    💨 Ветер: { $wind } { $wind_unit }
    🔽 Давление: { $pressure } hPa
card-forecast-header = <b>Прогноз на 5 дней</b>
card-forecast-line = { $emoji } <b>{ $date }</b>: { $tmin } … { $tmax }, { $desc }
updated-at = Обновлено: { $time }

btn-favorite-add = ⭐ В избранное
btn-favorite-remove = 🗑 Убрать из избранного
btn-refresh = 🔄 Обновить
btn-forecast = 📅 Прогноз на 5 дней

## Settings
settings-title = ⚙️ <b>Настройки</b>
settings-language = 🌐 Язык
settings-units = 🌡 Единицы измерения

units-metric = 🟦 Metric (°C, m/s)
units-imperial = 🟧 Imperial (°F, mph)
units-saved = ✅ Готово.

language-ru = 🇷🇺 Русский
language-en = 🇬🇧 English
language-set = 🌐 Язык переключён.

## Inline
inline-title = { $emoji } { $name }{ $flag } — { $temp }
inline-desc = { $desc }. Ощущается как { $feels }. Влажность { $humidity }%.
inline-empty-title = Введи название города
inline-empty-desc = Например: Москва, Tbilisi, New York.

## Misc
confirm-saved = ✅ Сохранено.
confirm-deleted = 🗑 Удалено.
error-generic = ⚠️ Что-то пошло не так. Попробуй ещё раз.
