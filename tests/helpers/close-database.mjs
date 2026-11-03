import { after } from 'node:test';
import { closeDatabase } from '../../server/config/database.js';
after(closeDatabase);
