"""Entry point for the get-site package."""
import asyncio
from .main import main

if __name__ == "__main__":
    asyncio.run(main())