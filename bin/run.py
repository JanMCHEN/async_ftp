import asyncio

from ..core import server


# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == "__main__":
    try:
        asyncio.run(server.main())
    except KeyboardInterrupt:
        pass
