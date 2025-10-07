"""
Normalize duplicate Category and Responsible rows created by migration.

Usage:
  python normalize_lookup_duplicates.py       # dry-run (preview)
  python normalize_lookup_duplicates.py --apply  # apply changes (destructive)

Behavior:
- Groups rows by a normalized key (lowercase, stripped). For each group with >1 rows,
  selects a canonical row to keep (priority: active True, contains '@', longest name, lowest id).
- Reassigns FK references from merged rows to the canonical row and deletes merged rows.
- Operates within Django ORM (transactional where possible).

This script prints detailed preview before making changes. Always backup DB before applying.
"""
import os
import sys
from collections import defaultdict
import argparse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

import django
from django.db import transaction
from django.db.models import Count

django.setup()

from apps.incidents.models import Category, Responsible, Incident


def norm_key(s):
    if s is None:
        return ''
    return ''.join(s.lower().split())


def choose_canonical(rows):
    # rows: list of model instances
    # priority: active True, contains @, longest name, lowest pk
    def score(r):
        s = 0
        try:
            name = getattr(r, 'name', '') or ''
        except Exception:
            name = ''
        if getattr(r, 'active', False):
            s += 1000
        if '@' in name:
            s += 500
        s += len(name)
        # lower pk preferred, add tiny inverse
        s += 1.0 / (r.pk + 1)
        return s
    return max(rows, key=score)


def find_duplicates(model, key_attr='name'):
    groups = defaultdict(list)
    for obj in model.objects.all():
        key = norm_key(getattr(obj, key_attr, None))
        groups[key].append(obj)
    # filter groups with more than 1 and non-empty key
    dup_groups = {k: v for k, v in groups.items() if k and len(v) > 1}
    return dup_groups


def preview_and_apply(apply_changes=False):
    results = {'Category': [], 'Responsible': []}

    # Categories
    cat_dups = find_duplicates(Category, 'name')
    if cat_dups:
        print('\nFound duplicate Category groups:')
    for key, rows in cat_dups.items():
        keep = choose_canonical(rows)
        merge = [r for r in rows if r.pk != keep.pk]
        results['Category'].append({'key': key, 'keep': keep, 'merge': merge})
        print(f"\nCategory key='{key}': keep id={keep.pk} name='{keep.name}' merge={[ (r.pk, r.name) for r in merge ]}")

    # Responsibles
    res_dups = find_duplicates(Responsible, 'name')
    if res_dups:
        print('\nFound duplicate Responsible groups:')
    for key, rows in res_dups.items():
        keep = choose_canonical(rows)
        merge = [r for r in rows if r.pk != keep.pk]
        results['Responsible'].append({'key': key, 'keep': keep, 'merge': merge})
        print(f"\nResponsible key='{key}': keep id={keep.pk} name='{keep.name}' merge={[ (r.pk, r.name) for r in merge ]}")

    # Show counts that would change
    print('\n--- Preview FK impacts ---')
    for entry in results['Category']:
        keep_pk = entry['keep'].pk
        merge_pks = [r.pk for r in entry['merge']]
        if not merge_pks:
            continue
        cnt = Incident.objects.filter(categoria_id__in=merge_pks).count()
        print(f"Category id {keep_pk} will receive {cnt} incidents from {merge_pks}")

    for entry in results['Responsible']:
        keep_pk = entry['keep'].pk
        merge_pks = [r.pk for r in entry['merge']]
        if not merge_pks:
            continue
        cnt = Incident.objects.filter(responsable_id__in=merge_pks).count()
        print(f"Responsible id {keep_pk} will receive {cnt} incidents from {merge_pks}")

    if not apply_changes:
        print('\nDry-run complete. No changes were made. To apply, re-run with --apply')
        return results

    # Apply changes
    print('\nApplying changes...')
    with transaction.atomic():
        for entry in results['Category']:
            keep = entry['keep']
            merge_pks = [r.pk for r in entry['merge']]
            if not merge_pks:
                continue
            print(f"Reassigning Category incidents from {merge_pks} -> {keep.pk}")
            Incident.objects.filter(categoria_id__in=merge_pks).update(categoria_id=keep.pk)
            # delete merged categories
            Category.objects.filter(pk__in=merge_pks).delete()

        for entry in results['Responsible']:
            keep = entry['keep']
            merge_pks = [r.pk for r in entry['merge']]
            if not merge_pks:
                continue
            print(f"Reassigning Responsible incidents from {merge_pks} -> {keep.pk}")
            Incident.objects.filter(responsable_id__in=merge_pks).update(responsable_id=keep.pk)
            Responsible.objects.filter(pk__in=merge_pks).delete()

    print('Apply complete.')
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Apply the changes (destructive).')
    args = parser.parse_args()

    print('Running normalize_lookup_duplicates.py (apply=%s)' % args.apply)
    results = preview_and_apply(apply_changes=args.apply)

if __name__ == '__main__':
    main()
