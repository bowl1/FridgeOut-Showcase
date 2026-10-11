"""Synchronous, single-process teaching version of persistent delete tombstones.

The real app uses AsyncStorage, serialized writes, async HTTP and lifecycle
triggers. This JSON adapter deliberately leaves those integrations out.
Run: python3 -m examples.offline_deletions
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable


class DeleteError(Exception):
    def __init__(self, status: int | None):
        super().__init__(f'Delete failed: {status or "network unavailable"}')
        self.status = status


class DeletionQueue:
    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> list[dict]:
        return json.loads(self.path.read_text()) if self.path.exists() else []

    def _write(self, entries: list[dict]) -> None:
        # Atomic replacement for this single-process example, not a file lock.
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(entries))
        temporary.replace(self.path)

    def queue(self, owner: str, kind: str, item_id: str) -> None:
        if not owner or not item_id or kind not in {'inventory', 'favorite'}:
            raise ValueError('Owner, valid kind and item ID are required')
        entries = self._read()
        if not any((e['owner'], e['kind'], e['id']) == (owner, kind, item_id) for e in entries):
            entries.append({'owner': owner, 'kind': kind, 'id': item_id, 'pending': True})
            self._write(entries)  # Persist intent before hiding the UI row.

    def visible(self, owner: str, kind: str, rows: list[dict]) -> list[dict]:
        hidden = {e['id'] for e in self._read() if e['owner'] == owner and e['kind'] == kind}
        return [row for row in rows if row['id'] not in hidden]

    def pending(self, owner: str) -> int:
        return sum(e['pending'] for e in self._read() if e['owner'] == owner)

    def sync(self, owner: str, send: Callable[[str, str], None],
             is_current: Callable[[], bool] = lambda: True) -> int:
        """Only send entries for the captured owner; return permanent rejections.

        send must use that owner's authenticated session in a real application.
        A permanent rejection removes the tombstone; a caller then refetches
        authoritative rows. Completed tombstones continue filtering stale reads.
        """
        rejected = 0
        for entry in self._read():
            if entry['owner'] != owner or not entry['pending']:
                continue
            if not is_current():
                break
            invalid = False
            try:
                send(entry['kind'], entry['id'])
            except DeleteError as error:
                if error.status in {400, 403, 422}:
                    invalid = True
                elif error.status != 404:
                    break  # Network/auth/throttling/server failures stay pending.
            entries = self._read()
            matches = lambda e: (e['owner'], e['kind'], e['id']) == (owner, entry['kind'], entry['id'])
            if invalid:
                entries = [e for e in entries if not matches(e)]
                rejected += 1
            else:
                for row in entries:
                    if matches(row):
                        row['pending'] = False
            self._write(entries)
        return rejected


def main() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / 'deletions.json'
        queue = DeletionQueue(path)
        rows = [{'id': 'recipe-demo', 'name': 'Mushroom sauté'}]
        queue.queue('alice-demo', 'favorite', 'recipe-demo')
        print('Alice sees after delete:', queue.visible('alice-demo', 'favorite', rows))
        print('Bob remains unaffected:', queue.visible('bob-demo', 'favorite', rows))

        def offline(_kind: str, _item_id: str) -> None:
            raise DeleteError(None)
        queue.sync('alice-demo', offline)
        print('Still pending after network failure:', queue.pending('alice-demo'))

        reopened = DeletionQueue(path)
        def already_deleted(_kind: str, _item_id: str) -> None:
            raise DeleteError(404)
        reopened.sync('alice-demo', already_deleted)
        print('Pending after reconnect / 404:', reopened.pending('alice-demo'))
        print('Stale server row remains hidden:', reopened.visible('alice-demo', 'favorite', rows))


if __name__ == '__main__':
    main()
