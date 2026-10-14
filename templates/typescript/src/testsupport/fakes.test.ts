import { FakeNoteStore } from './fakes.ts';
import { noteStoreContract } from './noteStoreContract.ts';

noteStoreContract('FakeNoteStore', () => new FakeNoteStore());
