import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core'

export const passwords = sqliteTable('passwords', {
    id: integer('id').primaryKey({ autoIncrement: true }),
    value: text('value').notNull(),
    iv: text('iv').notNull(),
})
