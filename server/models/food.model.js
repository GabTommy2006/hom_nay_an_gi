import { readFile } from 'node:fs/promises';

// Replace JSON loading here with database queries when the database is ready.
export async function getFood() {
  return JSON.parse(await readFile(new URL('../../data/food.json', import.meta.url), 'utf8'));
}
