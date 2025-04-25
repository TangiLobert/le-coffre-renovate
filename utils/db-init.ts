import {
  type Generated,
  type Insertable,
  type Selectable,
  type Updateable,
  Kysely, SqliteDialect
} from 'kysely'
import Database from 'better-sqlite3'

interface UserTable {
  id: Generated<number>
  name: string
  email: string
}

interface PermissionTable {
  id: Generated<number>
  user_id: number
  folder_id: number
  canUpdate: boolean
  canDelete: boolean
  canRead: boolean
}

interface FolderTable {
  id: Generated<number>
  name: string
  parent_id: number | null
  icon: string
  color: string
}

interface PasswordTable {
  id: Generated<number>
  value: string
  iv: string
  folder_id: number
}

interface passwordMetaDataTable {
  id: Generated<number>
  password_id: number
  url: string
  description: string
}

export interface DatabaseTable {
  user: UserTable,
  permission: PermissionTable,
  folder: FolderTable,
  password: PasswordTable,
  passwordMetaData: passwordMetaDataTable
}

export type User = Selectable<UserTable>
export type InsertableUser = Insertable<UserTable>
export type UpdateableUser = Updateable<UserTable>

export type Permission = Selectable<PermissionTable>
export type InsertablePermission = Insertable<PermissionTable>
export type UpdateablePermission = Updateable<PermissionTable>

export type Folder = Selectable<FolderTable>
export type InsertableFolder = Insertable<FolderTable>
export type UpdateableFolder = Updateable<FolderTable>

export type Password = Selectable<PasswordTable>
export type InsertablePassword = Insertable<PasswordTable>
export type UpdateablePassword = Updateable<PasswordTable>

export type PasswordMetaData = Selectable<passwordMetaDataTable>
export type InsertablePasswordMetaData = Insertable<passwordMetaDataTable>
export type UpdateablePasswordMetaData = Updateable<passwordMetaDataTable>


const dialect = new SqliteDialect({
  database: new Database('./database.sqlite'),
})

const db = new Kysely<DatabaseTable>({
  dialect
})

export default db