# Nimbus Backup — Troubleshooting Guide

## Symptom: Backup job fails with "Authentication error (code 401)"

Your account's login token has expired or was revoked from another device.

**Fix:**
1. Open Nimbus Backup and go to **Account > Sign Out**.
2. Sign back in with your Nimbus credentials.
3. Retry the backup job. If it still fails, check **Account > Active Sessions**
   for a session limit conflict and remove old sessions.

## Symptom: Backup job fails with "Storage quota exceeded"

Your plan's storage allotment is full.

**Fix:**
1. Go to **Settings > Storage** to see which devices/snapshots are using the
   most space.
2. Delete old snapshots you no longer need, or exclude large temp/cache
   folders from the backup set under **Settings > Backup Sources**.
3. If you consistently need more room, upgrade to a higher plan (see the FAQ
   for tier limits).

## Symptom: Backups are running much slower than usual

This is almost always network-related or caused by a very large changeset.

**Fix:**
1. Check **Settings > Bandwidth** — if a bandwidth cap is set, temporarily
   raise or remove it.
2. Confirm no other large upload/download is competing for bandwidth on the
   same network.
3. If a single huge file (for example, a multi-gigabyte VM image) was just
   added to a watched folder, the first backup of that file will always be
   slow; subsequent backups only send the changed blocks.

## Symptom: Restore fails with "Snapshot not found"

The snapshot may have expired under your plan's retention policy, or it was
manually deleted.

**Fix:**
1. Check **Restore > History** for the actual list of available snapshots —
   the one you expected may have aged out (see the FAQ's retention section).
2. If the snapshot should still exist, contact support with the approximate
   date and device name so we can check the storage backend directly.

## Symptom: Nimbus Backup app won't start after an update

**Fix:**
1. Restart the machine — a pending update sometimes leaves a lock file in
   place until reboot.
2. If it still won't start, reinstall the latest version from the Nimbus
   website; your backup configuration and history are stored in the cloud,
   not locally, so reinstalling does not lose data.
