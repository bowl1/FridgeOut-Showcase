# Engineering challenges and design decisions

[Back to the showcase](../README.md)

These are implemented mechanisms and known limits. They are not claims of incident-free operation or measured speedups.

## 1. Repeated image generation is a billing bug

**Scenario:** a card remounts, the signed URL expires, or the HTTP response is lost. A naive “generate on render” implementation pays again for the same recipe.

**Design:** image status belongs to the recipe in the database; a lease with its own identity coordinates generators. Already stored image output is reused. Original and thumbnail images live in private cloud storage. Signed URLs authorize reads, while a per-account mobile file cache handles repeat visits. The client and backend each limit image concurrency to two within their respective process/instance.

**Why it matters:** cache eviction, download failure and paid generation failure are different events. A file missing locally should be downloaded again. A failed paid generation needs deliberate retry rather than an endless automatic spending loop. Not-yet-reserved “busy” work can return queued and be checked later.

**Limit:** leases are coordination, not exactly-once guarantees across all provider/network failures. An expired lease needs recovery, and a remote call may have consumed money before timing out. Private storage cleanup needs a durable retry path.

## 2. Offline deletion must survive stale reads

**Scenario:** delete a favorite without a connection, restart the app, then fetch an older server list. Without a persistent marker, the favorite reappears.

**Design:** persist a deletion tombstone before hiding the row. Queue entries are scoped by account and item type. Merge/fetch paths filter tombstones. Retry when connectivity returns, the app enters the foreground, and on a foreground retry timer. A 404 means deletion already succeeded. Network failures, expired authentication, throttling and 5xx keep the operation pending. Permanent validation/permission rejection removes the tombstone so authoritative data can be shown again.

**Why it matters:** an acknowledgement can be lost after the server deleted the row. Retry must converge safely. A logout/account change must not replay one user's deletion under another user's session. Completed tombstones also suppress late stale responses.

**Limit:** this is an offline deletion feature, not a complete offline-first editing engine. No synchronization runs while the app is closed. Tombstone retention and conflict UX are deliberate future review areas.

Try the [runnable account-isolation example](../examples/offline_deletions.py).

## 3. Paid operations need more than a counter

**Scenario:** two requests both read “one use remaining”; both proceed and exceed allowance. A user retries a timeout and pays for duplicate model work.

**Design:** authenticated requests carry persistent idempotency keys. Database reservations coordinate account allowance, concurrent operation limits and a global budget before paid work. Result/job state can be reused for repeated requests. Failed user-visible operations do not consume the successful-run allowance, but internal cost accounting must still represent attempted provider work.

**Why it matters:** “not charging a user a run” and “the model provider did not charge us” are different facts. Token-based estimates and conservative reservations are operational controls, not an exact invoice.

**Limit:** subscription verification depends on an external service and budget estimates can drift. Financial reconciliation and production-scale load testing are separate work.

## 4. Client purchase success is not entitlement authority

**Scenario:** a client reports a successful purchase, but the transaction belongs to a different account, has expired, was refunded, or came from a disallowed test environment.

**Design:** Apple processes payment through the RevenueCat SDK. Backend verification checks subscriber state, trusted product IDs and billing periods; database state determines allowance. Webhooks and explicit synchronization update server state. Public SDK keys can be packaged into the app; secret API and webhook credentials remain server-side.

**Limit:** RevenueCat integration still requires store configuration and sandbox/device acceptance testing. The showcase contains no credentials or complete billing implementation. Subscription setup is not evidence that the app passed App Store review.

## 5. Fast feedback without charging another generation

**Scenario:** one recipe passes in the first round but later rounds take longer. Waiting for the full batch makes the app feel unresponsive.

**Design:** persist accepted progress in the same operation and poll a user-scoped job endpoint. Reading progress does not trigger another generation. Save/image actions wait for final completion so tentative progress is not mistaken for a finalized billable result.

**Limit:** polling trades repeated reads for simpler reconnection. API process shutdown can interrupt graph execution; this does not replace a durable background worker.

## 6. Deletion crosses several systems

**Scenario:** deleting a user removes database rows but leaves private images, result-cache content or billable operations running.

**Design:** deletion coordinates an account-deletion intent, AI-operation isolation, storage removal and Supabase account deletion. Ownership foreign keys cascade account data. Accounting records can be de-linked rather than reused as recipe content. Recoverable cleanup work has a queue.

**Limit:** account deletion does not cancel an Apple subscription and cannot instantly erase provider logs/backups. Partial failures are reported for retry rather than presenting a guaranteed global erase.

## How to talk about these decisions

For each feature, explain one concrete failure, the state transition that fixes it, a test that exercises that failure, and one remaining limitation. “Added a cache” is less informative than explaining why a cache miss cannot authorize a second paid model call.
