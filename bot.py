import aiohttp
import asyncio

async def load_recipes():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://raw.githubusercontent.com/Ioneovv/CheffBot/main/recipes_part1.json') as response:
            response.raise_for_status()  # Check for errors
            return await response.json()

async def main():
    recipes = await load_recipes()
    print(recipes)

if __name__ == '__main__':
    asyncio.run(main())
