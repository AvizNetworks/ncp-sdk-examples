# Nimbus Backup — Glossary

**Snapshot** — A complete, point-in-time record of everything in a backup set
at the moment the backup ran. Restoring "a snapshot" restores every file to
exactly the state it was in at that time.

**Incremental backup** — A backup that only uploads the blocks of data that
changed since the last backup, rather than re-uploading entire files. Nimbus
Backup uses incremental backups after the first full backup of a device.

**Full backup** — The first backup of a newly added device or folder, which
uploads all data in its entirety. All later backups are incremental unless a
full backup is manually triggered.

**Retention policy** — The length of time old snapshots and deleted-file
versions are kept before being permanently purged. Retention length depends
on your plan tier (see the FAQ).

**Backup set** — The specific folders, drives, or applications configured to
be backed up on a given device. Configured under **Settings > Backup
Sources**.

**Versioning** — The ability to see and restore from multiple past versions of
the same file, not just the most recent one. Governed by the plan's retention
policy.

**Bandwidth cap** — An optional user-configured limit on how much network
bandwidth Nimbus Backup is allowed to use, to avoid competing with other
traffic on the same connection.

**Continuous backup** — Available on the Business plan only; backs up changed
files within seconds of the change instead of waiting for the next scheduled
backup window.
