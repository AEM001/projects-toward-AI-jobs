import asyncio
import datetime
async def fetch_user(user_id):
    print(f"Fetching user {user_id}...")
    await asyncio.sleep(2)  # pretend this is a database query taking 2 seconds
    print(f"Got user {user_id}!")
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    # Fetch 3 users at the same time instead of one by one
    time1=datetime.datetime.now()
    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )
    print(users)
    time2=datetime.datetime.now()
    print(f"Time taken: {time2-time1}")

asyncio.run(main())

# Takes 2 seconds total, not 6!