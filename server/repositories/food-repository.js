import { readFile } from 'node:fs/promises';

// Replace this repository with database queries when the database is available.
export async function getFood() {
  return JSON.parse(await readFile(new URL('../../data/food.json', import.meta.url), 'utf8'));
}
