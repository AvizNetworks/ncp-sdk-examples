# Nimbus Backup — Frequently Asked Questions

## What operating systems does Nimbus Backup support?

Nimbus Backup runs on Windows 10/11, Windows Server 2016+, macOS 12+, and any
Linux distribution with kernel 5.4 or later. There is no support for 32-bit
operating systems.

## What are the pricing tiers?

- **Starter** — 1 device, 50 GB cloud storage, daily backups.
- **Pro** — up to 5 devices, 500 GB cloud storage, hourly backups, versioning
  (30-day history).
- **Business** — unlimited devices, 5 TB pooled storage, continuous backup,
  versioning (1-year history), centralized admin console.

## How do I restore a file from a backup?

Open the Nimbus Backup app, go to **Restore**, pick the device and the point
in time you want to restore from, then select individual files or an entire
snapshot. Restores can go to the original location or to a new folder.

## Can I restore to a different computer?

Yes. Install Nimbus Backup on the new machine, sign in with the same account,
and choose **Restore from another device** during setup. You'll see every
device backed up under your account and can browse its snapshots.

## How long does Nimbus Backup keep old versions of a file?

Version history depends on your plan: Starter keeps only the latest backup,
Pro keeps 30 days of history, and Business keeps a full year. Deleted files
follow the same retention window before being purged permanently.

## Does Nimbus Backup encrypt my data?

Yes. All data is encrypted with AES-256 in transit and at rest. You can
optionally enable a private encryption key in **Settings > Security**, but if
you lose that key, Nimbus Support cannot recover your data.
