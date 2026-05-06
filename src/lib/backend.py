"""Бэкенд клиента."""

import asyncio

try:
    from . import status_client_support
    from .frontend import Manager
    from .main_function_for_client import CLIENT_GAMES
    from .server import Client, ClientServerError, run_with_client
except ImportError:
    import status_client_support
    from frontend import Manager
    from main_function_for_client import CLIENT_GAMES
    from server import Client, ClientServerError, run_with_client


async def play_game(game: Client.Game):
    """Запускает игру.

    Args:
        game (Client.Game): игра клиента.
    """

    manager = Manager()

    try:
        await game.run()
    except status_client_support.Error_game as error:
        manager.push_status(None, error=error)
    except ClientServerError as error:
        manager.push_status(
            None,
            error=status_client_support.Error_game(str(error), 1),
        )


async def _run_client_loop(client: Client):
    """Основной цикл бэкенда с уже подключённым клиентом."""

    manager = Manager()

    while True:
        await asyncio.sleep(0.01)

        message = manager.pop_message()

        if message is None:
            continue

        if not isinstance(message, tuple):
            manager.push_status(
                None,
                error=status_client_support.Error_game("", 1),
            )
            continue

        match message[0]:
            case 0:
                break

            case "login":
                await client.login(message[1])
                continue

            case "create_game":
                game = await client.init_game(message[1])
                game.set_run(CLIENT_GAMES[message[1]])

            case 1:
                game = await client.connect_game(message[1])
                game.set_run(CLIENT_GAMES["X_O"])

            case code if 1 < code < len(status_client_support._STATUS_):
                game_name = message[1][22:]
                game = await client.init_game(game_name)
                game.set_run(CLIENT_GAMES[game_name])

            case _:
                manager.push_status(
                    None,
                    error=status_client_support.Error_game("", 1),
                )
                continue

        await play_game(game)


async def run():
    """Основной цикл бэкенда."""

    await run_with_client(_run_client_loop)
