import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from examples.recipe_constraints import Food, Recipe, validate
from examples.offline_deletions import DeletionQueue, DeleteError


class InventoryConstraints(unittest.TestCase):
    def test_cumulative_usage_is_checked_across_duplicate_rows(self):
        inventory = (Food('mushroom', 100, 'g'), Food(' Mushroom ', 50, 'G'))
        recipe = Recipe('Sauté', (Food('mushroom', 90, 'g'), Food('mushroom', 70, 'g')), 10)
        self.assertEqual(validate(recipe, inventory, 15), ['Cumulative quantity exceeds stock: mushroom (g)'])

    def test_unit_conversion_is_not_guessed(self):
        recipe = Recipe('Sauté', (Food('mushroom', 1, 'bag'),), 10)
        self.assertIn('Unavailable food/unit: mushroom (bag)', validate(recipe, (Food('mushroom', 100, 'g'),), 15))

    def test_matching_stock_and_approved_staple_pass(self):
        recipe = Recipe('Sauté', (Food('mushroom', 100, 'g'), Food('cooking oil', 1, 'tsp')), 10)
        self.assertEqual(validate(recipe, (Food('mushroom', 100, 'g'),), 15), [])

    def test_nonpositive_and_nonfinite_quantities_cannot_bypass_stock(self):
        for value in (0, -1, float('nan'), float('inf')):
            with self.subTest(value=value):
                recipe = Recipe('Sauté', (Food('mushroom', value, 'g'),), 10)
                self.assertTrue(validate(recipe, (Food('mushroom', 100, 'g'),), 15))

    def test_time_limit_and_empty_recipe_are_rejected(self):
        self.assertEqual(validate(Recipe('Empty', (), 20), (), 15),
                         ['No ingredients', 'Cooking time outside allowed range'])


class PersistentDeletions(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'queue.json'
        self.queue = DeletionQueue(self.path)
        self.rows = [{'id': 'one'}, {'id': 'two'}]

    @staticmethod
    def failing(status):
        def send(_kind, _item):
            raise DeleteError(status)
        return send

    def test_restart_deduplication_and_account_kind_isolation(self):
        self.queue.queue('alice', 'favorite', 'one')
        reopened = DeletionQueue(self.path)
        reopened.queue('alice', 'favorite', 'one')
        self.assertEqual(reopened.pending('alice'), 1)
        self.assertEqual(reopened.visible('alice', 'favorite', self.rows), [{'id': 'two'}])
        self.assertEqual(reopened.visible('bob', 'favorite', self.rows), self.rows)
        self.assertEqual(reopened.visible('alice', 'inventory', self.rows), self.rows)
        calls = []
        reopened.sync('bob', lambda kind, item: calls.append((kind, item)))
        self.assertEqual(calls, [])
        self.assertEqual(reopened.pending('alice'), 1)

    def test_lost_acknowledgement_then_404_converges_and_filters_stale_rows(self):
        self.queue.queue('alice', 'favorite', 'one')
        self.queue.sync('alice', self.failing(None))
        self.assertEqual(self.queue.pending('alice'), 1)
        self.queue.sync('alice', self.failing(404))
        self.assertEqual(self.queue.pending('alice'), 0)
        self.assertEqual(self.queue.visible('alice', 'favorite', self.rows), [{'id': 'two'}])

    def test_transient_failures_preserve_work(self):
        for status in (None, 401, 429, 500):
            with self.subTest(status=status):
                self.queue.queue('alice', 'favorite', 'one')
                self.queue.sync('alice', self.failing(status))
                self.assertEqual(self.queue.pending('alice'), 1)

    def test_permanent_rejection_restores_authoritative_visibility(self):
        for status in (400, 403, 422):
            with self.subTest(status=status):
                self.queue.queue('alice', 'favorite', 'one')
                self.assertEqual(self.queue.sync('alice', self.failing(status)), 1)
                self.assertEqual(self.queue.pending('alice'), 0)
                self.assertEqual(self.queue.visible('alice', 'favorite', self.rows), self.rows)

    def test_session_change_stops_before_next_send(self):
        self.queue.queue('alice', 'favorite', 'one')
        self.queue.queue('alice', 'favorite', 'two')
        calls = []
        self.queue.sync('alice', lambda kind, item: calls.append(item), lambda: not calls)
        self.assertEqual(calls, ['one'])
        self.assertEqual(self.queue.pending('alice'), 1)


if __name__ == '__main__':
    unittest.main()
