import aiosqlite 

class Database:
    def __init__(self, data_base: str):
        self.data_base = data_base

    async def boom(self):
        async with aiosqlite.connect(self.data_base) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            
            #таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    tg_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    registered_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            #таблица заметок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    note_text TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (tg_id) ON DELETE CASCADE
                )
            """)
            #таблица дней рождения
            await db.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    bday_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    person_name TEXT NOT NULL,
                    bday_date TEXT NOT NULL, 
                    FOREIGN KEY (user_id) REFERENCES users (tg_id) ON DELETE CASCADE
                )
            """)
            #таблица долгов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS debts (
                    debt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    person_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    debt_type INTEGER NOT NULL, 
                    comment TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (tg_id) ON DELETE CASCADE
                )
            """)
            await db.commit()
    async def register_user(self, tg_id: int, first_name: str):  
        async with aiosqlite.connect(self.data_base) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute('''
                INSERT OR IGNORE INTO users (tg_id, first_name) 
                VALUES (?, ?)
                            ''', (tg_id, first_name))
            await db.commit()
    #блок заметок
    async def add_note(self, user_id: int, text: str):
        async with aiosqlite.connect(self.data_base) as db:
            await db.execute("INSERT INTO notes (user_id, note_text) VALUES (?, ?)", (user_id, text))
            await db.commit()
    async def get_notes(self, user_id: int) -> list:
        async with aiosqlite.connect(self.data_base) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT note_id, note_text FROM notes WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchall()
            
    #блок дней рождений
    async def add_birthday(self, user_id: int, name: str, date: str):
        async with aiosqlite.connect(self.data_base) as db:
            await db.execute("INSERT INTO birthdays (user_id, person_name, bday_date) VALUES (?, ?, ?)", (user_id, name, date))
            await db.commit()
    async def get_birthday(self, user_id: int) -> list:
        async with aiosqlite.connect(self.data_base) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT bday_id, person_name, bday_date FROM birthdays WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchall()
            
    #блок долгов
    async def add_debt(self, user_id: int, name: str, amount: float, debt_type: int, comment: str = None):
        async with aiosqlite.connect(self.data_base) as db:
            await db.execute("""
                INSERT INTO debts (user_id, person_name, amount, debt_type, comment) 
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, amount, debt_type, comment))
            await db.commit()
    async def get_debt(self, user_id: int) -> list:
        async with aiosqlite.connect(self.data_base) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT debt_id, person_name, amount, debt_type, comment FROM debts WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchall()
            
    #методы удаления
    async def delete_note(self, note_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.data_base) as db:
            async with db.execute(
                "DELETE FROM notes WHERE note_id = ? AND user_id = ?", 
                (note_id, user_id)
            ) as cursor:
                await db.commit()
                return cursor.rowcount > 0 
            
    async def delete_birthday(self, birthday_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.data_base) as db:
            async with db.execute(
                "DELETE FROM birthdays WHERE bday_id = ? AND user_id = ?",
                (birthday_id, user_id)
            ) as cursor:
                await db.commit()
                return cursor.rowcount > 0
    
    async def delete_debt(self, debt_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.data_base) as db:
            async with db.execute(
                "DELETE FROM debts WHERE debt_id = ? AND user_id = ?",
                (debt_id, user_id)
            ) as cursor:
                await db.commit()
                return cursor.rowcount > 0
