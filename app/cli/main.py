from __future__ import annotations
from .api import ApiClient
from .ui import main_menu

def run() -> None:
    client = ApiClient()
    try:
        main_menu(client)
    finally:
        client.close()

if __name__ == "__main__":
    run()
